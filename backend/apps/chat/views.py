"""
Views for Chat API with RAG.
"""

import logging
import json
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.http import StreamingHttpResponse

from core.llm.chatbot.rag import RAGPipeline, RAGError
from apps.conversations.models import Conversation, Message

logger = logging.getLogger(__name__)


class ChatView(APIView):
    """
    Main chat endpoint with RAG.
    
    POST /chat
    {
        "message": "What's the ROI for Villa Mar?",
        "conversation_id": "uuid" (optional),
        "stream": false (optional)
    }
    """
    
    # Temporarily allow access without authentication for testing
    # permission_classes = [IsAuthenticated]
    permission_classes = []
    
    def post(self, request):
        """Process chat message with RAG."""
        
        # DEBUG LOGS
        print(f"🎯 ChatView POST - Path: {request.path}")
        print(f"🎯 ChatView POST - Full Path: {request.get_full_path()}")
        print(f"🎯 ChatView POST - Headers: {dict(request.headers)}")
        print(f"🎯 ChatView POST - Data: {request.data}")
        logger.info(f"Chat request received: path={request.path}, data={request.data}")
        
        message_text = request.data.get('message')
        conversation_id = request.data.get('conversation_id')
        stream = request.data.get('stream', True)  # Default to streaming
        
        if not message_text:
            return Response(
                {'error': 'Message is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # If streaming is requested, return SSE response
        if stream:
            return self._stream_response(request, message_text, conversation_id)
        
        # Otherwise, return regular response
        return self._regular_response(request, message_text, conversation_id)
    
    def _stream_response(self, request, message_text, conversation_id):
        """Stream response using Server-Sent Events."""
        
        def event_stream():
            try:
                # Setup user and tenant
                tenant, user, user_role = self._get_user_context(request)
                
                # Get or create conversation
                conversation = self._get_or_create_conversation(
                    tenant, user, user_role, conversation_id, message_text
                )
                
                # Save user message
                user_message = Message.objects.create(
                    conversation=conversation,
                    role=Message.Role.USER,
                    content=message_text
                )
                
                # Send conversation ID first
                yield f"data: {json.dumps({'type': 'conversation_id', 'conversation_id': str(conversation.id)})}\n\n"
                
                # Initialize RAG
                rag = RAGPipeline(
                    tenant_id=str(tenant.id),
                    user_role=user_role
                )
                
                # Stream response
                full_response = ""
                for chunk in rag.query_stream(message_text, conversation):
                    if chunk.get('type') == 'content':
                        content = chunk.get('content', '')
                        full_response += content
                        yield f"data: {json.dumps({'type': 'content', 'content': content})}\n\n"
                    elif chunk.get('type') == 'sources':
                        sources = chunk.get('sources', [])
                        yield f"data: {json.dumps({'type': 'sources', 'sources': sources})}\n\n"
                
                # Save assistant message
                assistant_message = Message.objects.create(
                    conversation=conversation,
                    role=Message.Role.ASSISTANT,
                    content=full_response,
                    model_used='gpt-4',
                    tokens_input=0,
                    tokens_output=0
                )
                
                # Send completion
                yield f"data: {json.dumps({'type': 'done', 'message_id': str(assistant_message.id)})}\n\n"
                
            except Exception as e:
                logger.error(f"❌ Streaming error: {e}", exc_info=True)
                yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
        
        response = StreamingHttpResponse(
            event_stream(),
            content_type='text/event-stream'
        )
        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no'
        return response
    
    def _regular_response(self, request, message_text, conversation_id):
        """Regular non-streaming response."""
    def _regular_response(self, request, message_text, conversation_id):
        """Regular non-streaming response."""
        
        try:
            # Setup user and tenant
            tenant, user, user_role = self._get_user_context(request)
            
            # Get or create conversation
            conversation = self._get_or_create_conversation(
                tenant, user, user_role, conversation_id, message_text
            )
            
            # Save user message
            user_message = Message.objects.create(
                conversation=conversation,
                role=Message.Role.USER,
                content=message_text
            )
            
            # Initialize RAG pipeline
            rag = RAGPipeline(
                tenant_id=str(tenant.id),
                user_role=user_role
            )
            
            # Query RAG
            username = user.username if user else 'anonymous'
            logger.info(f"Processing query for user {username}")
            result = rag.query(
                query=message_text,
                conversation=conversation,
                stream=stream
            )
            
            # Save assistant message
            assistant_message = Message.objects.create(
                conversation=conversation,
                role=Message.Role.ASSISTANT,
                content=result['response'],
                model_used=result.get('model', 'unknown'),
                tokens_input=result.get('tokens_used', 0) // 2,  # Rough estimate
                tokens_output=result.get('tokens_used', 0) // 2,
                retrieved_documents=result.get('sources', []),
                latency_ms=result.get('latency_ms')
            )
            
            # Update conversation costs
            conversation.update_costs()
            
            # Format sources for response
            sources = []
            for doc in result.get('sources', [])[:5]:  # Top 5 sources
                sources.append({
                    'document_id': doc['id'],
                    'content_type': doc['content_type'],
                    'excerpt': doc['content'][:200] + '...' if len(doc['content']) > 200 else doc['content'],
                    'relevance_score': round(doc['relevance_score'], 3),
                    'source_reference': doc.get('source_reference', 'N/A'),
                    'updated_at': doc.get('freshness_date'),
                    'metadata': doc.get('metadata', {})
                })
            
            return Response({
                'conversation_id': str(conversation.id),
                'message_id': str(assistant_message.id),
                'response': result['response'],
                'sources': sources,
                'model': result.get('model'),
                'latency_ms': result.get('latency_ms'),
                'cached': result.get('cached', False),
                'tokens_used': result.get('tokens_used', 0)
            }, status=status.HTTP_200_OK)
            
        except RAGError as e:
            logger.error(f"RAG error: {e}")
            return Response(
                {'error': f'RAG processing failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        except Exception as e:
            logger.error(f"❌ Unexpected error in ChatView: {e}", exc_info=True)
            logger.error(f"❌ Error type: {type(e).__name__}")
            logger.error(f"❌ Error details: {str(e)}")
            import traceback
            logger.error(f"❌ Traceback:\n{traceback.format_exc()}")
            return Response(
                {'error': f'An unexpected error occurred: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _get_user_context(self, request):
        """Get user, tenant, and role context."""
        if request.user and request.user.is_authenticated:
            user = request.user
            tenant = request.user.tenant
            user_role = request.user.role
            logger.info(f"✅ Authenticated user: {user.username}, tenant: {tenant}")
        else:
            # Anonymous access for testing
            from apps.tenants.models import Tenant
            from apps.users.models import CustomUser
            
            logger.info("🔍 Anonymous user - looking for tenant...")
            tenant = Tenant.objects.first()
            logger.info(f"🔍 Found tenant: {tenant}")
            
            if not tenant:
                logger.error("❌ No tenant found in database")
                raise Exception('No tenant configured')
            
            logger.info(f"🔍 Looking for user with tenant_id: {tenant.id}")
            user = CustomUser.objects.filter(tenant=tenant).first()
            logger.info(f"🔍 Found user: {user}")
            
            if not user:
                logger.info(f"🔨 Creating test user for tenant: {tenant.slug}")
                user = CustomUser.objects.create(
                    username=f'test_user_{tenant.slug}',
                    email=f'test@{tenant.slug}.com',
                    tenant=tenant,
                    role='buyer',
                    is_active=True
                )
                logger.info(f"✅ Created test user: {user.username}")
            
            user_role = 'buyer'
            logger.info(f"✅ Using anonymous mode - user: {user.username if user else None}, role: {user_role}")
        
        return tenant, user, user_role
    
    def _get_or_create_conversation(self, tenant, user, user_role, conversation_id, message_text):
        """Get existing or create new conversation."""
        if conversation_id:
            logger.info(f"🔍 Looking for existing conversation: {conversation_id}")
            try:
                conversation = Conversation.objects.get(
                    id=conversation_id,
                    tenant=tenant
                )
                logger.info(f"✅ Found conversation: {conversation.id}")
                return conversation
            except Conversation.DoesNotExist:
                logger.error(f"❌ Conversation not found: {conversation_id}")
                raise Exception('Conversation not found')
        else:
            # Create new conversation
            title = message_text[:100] + ('...' if len(message_text) > 100 else '')
            logger.info(f"🔨 Creating new conversation with title: {title}")
            conversation = Conversation.objects.create(
                tenant=tenant,
                user=user if user else None,
                user_role=user_role,
                title=title
            )
            logger.info(f"✅ Created new conversation: {conversation.id}")
            return conversation


class ConversationListView(APIView):
    """
    List user's conversations.
    
    GET /chat/conversations
    """
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get user's conversations."""
        
        conversations = Conversation.objects.filter(
            user=request.user,
            tenant=request.user.tenant,
            is_archived=False
        ).order_by('-updated_at')[:50]
        
        results = []
        for conv in conversations:
            results.append({
                'id': str(conv.id),
                'title': conv.title,
                'user_role': conv.user_role,
                'message_count': conv.get_message_count(),
                'total_tokens': conv.total_tokens,
                'total_cost_usd': float(conv.total_cost_usd),
                'created_at': conv.created_at.isoformat(),
                'updated_at': conv.updated_at.isoformat()
            })
        
        return Response({
            'conversations': results,
            'count': len(results)
        }, status=status.HTTP_200_OK)


class ConversationDetailView(APIView):
    """
    Get conversation with messages.
    
    GET /chat/conversations/{id}
    """
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request, conversation_id):
        """Get conversation details."""
        
        try:
            conversation = Conversation.objects.get(
                id=conversation_id,
                user=request.user,
                tenant=request.user.tenant
            )
        except Conversation.DoesNotExist:
            return Response(
                {'error': 'Conversation not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get messages
        messages = conversation.messages.order_by('created_at')
        
        message_list = []
        for msg in messages:
            message_list.append({
                'id': str(msg.id),
                'role': msg.role,
                'content': msg.content,
                'model_used': msg.model_used,
                'tokens_input': msg.tokens_input,
                'tokens_output': msg.tokens_output,
                'sources': msg.get_sources() if msg.role == Message.Role.ASSISTANT else [],
                'created_at': msg.created_at.isoformat()
            })
        
        return Response({
            'id': str(conversation.id),
            'title': conversation.title,
            'user_role': conversation.user_role,
            'total_tokens': conversation.total_tokens,
            'total_cost_usd': float(conversation.total_cost_usd),
            'messages': message_list,
            'created_at': conversation.created_at.isoformat(),
            'updated_at': conversation.updated_at.isoformat()
        }, status=status.HTTP_200_OK)
    
    def delete(self, request, conversation_id):
        """Archive conversation."""
        
        try:
            conversation = Conversation.objects.get(
                id=conversation_id,
                user=request.user,
                tenant=request.user.tenant
            )
            conversation.is_archived = True
            
        except Conversation.DoesNotExist:
            return Response(
                {'error': 'Conversation not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class ConversationListView(APIView):
    """
    Get list of user's conversations.
    
    GET /chat/conversations
    """
    permission_classes = []
    
    def get(self, request):
        """Get all conversations for current user/tenant."""
        try:
            tenant, user, user_role = self._get_user_context(request)
            
            # Get conversations
            conversations = Conversation.objects.filter(
                tenant=tenant,
                is_archived=False
            ).order_by('-updated_at')[:50]  # Last 50 conversations
            
            result = []
            for conv in conversations:
                # Get first message as title preview
                first_msg = conv.messages.filter(role=Message.Role.USER).first()
                title = first_msg.content[:50] + "..." if first_msg and len(first_msg.content) > 50 else (first_msg.content if first_msg else "New conversation")
                
                result.append({
                    'id': str(conv.id),
                    'title': title,
                    'created_at': conv.created_at.isoformat(),
                    'updated_at': conv.updated_at.isoformat(),
                    'message_count': conv.messages.count()
                })
            
            return Response({
                'conversations': result
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting conversations: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _get_user_context(self, request):
        """Get tenant and user from request."""
        from apps.tenants.models import Tenant
        from apps.users.models import CustomUser
        
        tenant = Tenant.objects.first()
        user = None
        user_role = 'buyer'
        
        if request.user and request.user.is_authenticated:
            user = request.user
            tenant = user.tenant
            user_role = user.role
        
        return tenant, user, user_role


class ConversationDetailView(APIView):
    """
    Get messages for a specific conversation.
    
    GET /chat/conversations/{id}
    """
    permission_classes = []
    
    def get(self, request, conversation_id):
        """Get all messages for a conversation."""
        try:
            # Get conversation
            conversation = Conversation.objects.get(id=conversation_id)
            
            # Get messages
            messages = conversation.messages.order_by('created_at')
            
            result = []
            for msg in messages:
                result.append({
                    'id': str(msg.id),
                    'role': msg.role,
                    'content': msg.content,
                    'sources': msg.retrieved_documents if msg.retrieved_documents else [],
                    'created_at': msg.created_at.isoformat()
                })
            
            return Response({
                'conversation_id': str(conversation.id),
                'messages': result
            }, status=status.HTTP_200_OK)
            
        except Conversation.DoesNotExist:
            return Response(
                {'error': 'Conversation not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error getting conversation: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
