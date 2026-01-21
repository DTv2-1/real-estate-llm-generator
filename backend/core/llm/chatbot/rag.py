"""
RAG (Retrieval Augmented Generation) pipeline using LangChain.
Implements hybrid search, semantic caching, and role-based filtering.
"""

import hashlib
import logging
from typing import List, Dict, Optional, Tuple
from decimal import Decimal

import numpy as np
from django.conf import settings
from django.core.cache import caches
from django.db.models import Q
from pgvector.django import CosineDistance

from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from apps.documents.models import Document
from apps.properties.models import Property
from apps.conversations.models import Conversation, Message
from .prompts import get_system_prompt

logger = logging.getLogger(__name__)


class RAGError(Exception):
    """Base exception for RAG errors."""
    pass


class RAGPipeline:
    """
    Complete RAG pipeline with:
    - Hybrid vector + keyword search
    - Semantic caching
    - Role-based filtering
    - LLM routing (GPT-4o-mini vs Claude)
    - Citation tracking
    """
    
    def __init__(self, tenant_id: str, user_role: str):
        self.tenant_id = tenant_id
        self.user_role = user_role
        
        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(
            model=settings.OPENAI_EMBEDDING_MODEL,
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        # Initialize LLMs
        self.simple_llm = ChatOpenAI(
            model=settings.OPENAI_MODEL_CHAT,
            temperature=settings.OPENAI_TEMPERATURE,
            max_tokens=settings.OPENAI_MAX_TOKENS,
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        self.complex_llm = ChatAnthropic(
            model=settings.ANTHROPIC_MODEL,
            temperature=settings.OPENAI_TEMPERATURE,
            max_tokens=settings.ANTHROPIC_MAX_TOKENS,
            anthropic_api_key=settings.ANTHROPIC_API_KEY
        )
        
        # Cache
        self.cache = caches['default']
        self.embedding_cache = caches['embeddings']
    
    def _get_query_embedding(self, query: str) -> List[float]:
        """Get embedding for query with caching."""
        
        # Create cache key
        cache_key = f"emb:{hashlib.md5(query.encode()).hexdigest()}"
        
        # Check cache
        cached = self.embedding_cache.get(cache_key)
        if cached:
            logger.debug("Embedding cache hit")
            return cached
        
        # Generate embedding
        logger.debug("Generating query embedding...")
        embedding = self.embeddings.embed_query(query)
        
        # Cache it
        self.embedding_cache.set(cache_key, embedding, timeout=86400 * 7)  # 7 days
        
        return embedding
    
    def _vector_search(self, query_embedding: List[float], k: int = 10) -> List[Tuple[any, float, str]]:
        """
        Perform vector similarity search on both documents and properties.
        
        Returns:
            List of (object, similarity_score, type) tuples where type is 'document' or 'property'
        """
        results = []
        
        # Search documents
        logger.debug(f"🔍 Searching documents: tenant_id={self.tenant_id}, user_role={self.user_role}")
        documents = Document.objects.filter(
            tenant_id=self.tenant_id,
            is_active=True,
            user_roles__contains=[self.user_role]
        ).filter(
            embedding__isnull=False
        ).annotate(
            similarity=1 - CosineDistance('embedding', query_embedding)
        ).order_by('-similarity')[:k]
        
        logger.info(f"📄 Found {documents.count()} documents with embeddings")
        for doc in documents:
            results.append((doc, float(doc.similarity), 'document'))
        
        # Search properties
        logger.debug(f"🔍 Searching properties: tenant_id={self.tenant_id}, user_role={self.user_role}")
        
        # First check total properties
        total_properties = Property.objects.filter(tenant_id=self.tenant_id).count()
        logger.info(f"🏠 Total properties for tenant: {total_properties}")
        
        properties_with_roles = Property.objects.filter(
            tenant_id=self.tenant_id,
            user_roles__contains=[self.user_role]
        ).count()
        logger.info(f"🏠 Properties with user_role '{self.user_role}': {properties_with_roles}")
        
        properties_with_embeddings = Property.objects.filter(
            tenant_id=self.tenant_id,
            user_roles__contains=[self.user_role],
            embedding__isnull=False
        ).count()
        logger.info(f"🏠 Properties with embeddings: {properties_with_embeddings}")
        
        properties = Property.objects.filter(
            tenant_id=self.tenant_id,
            user_roles__contains=[self.user_role]
        ).filter(
            embedding__isnull=False
        ).annotate(
            similarity=1 - CosineDistance('embedding', query_embedding)
        ).order_by('-similarity')[:k]
        
        logger.info(f"🏠 Retrieved {properties.count()} properties for comparison")
        for prop in properties:
            logger.debug(f"  - Property: {prop.property_name}, similarity: {prop.similarity}")
            results.append((prop, float(prop.similarity), 'property'))
        
        # Sort all results by similarity and take top k
        results.sort(key=lambda x: x[1], reverse=True)
        results = results[:k]
        
        logger.info(f"Vector search found {len(results)} items ({sum(1 for r in results if r[2]=='document')} docs, {sum(1 for r in results if r[2]=='property')} properties)")
        return results
    
    def _keyword_search(self, query: str, k: int = 10) -> List[Tuple[any, float, str]]:
        """
        Perform BM25-style keyword search using PostgreSQL full-text search on documents and properties.
        
        Returns:
            List of (object, relevance_score, type) tuples
        """
        from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
        
        results = []
        search_query = SearchQuery(query, search_type='websearch')
        
        # Search documents
        documents = Document.objects.filter(
            tenant_id=self.tenant_id,
            is_active=True,
            user_roles__contains=[self.user_role]
        ).annotate(
            rank=SearchRank('content', search_query)
        ).filter(
            rank__gt=0
        ).order_by('-rank')[:k]
        
        for doc in documents:
            results.append((doc, float(doc.rank), 'document'))
        
        # Search properties (search in property_name and description)
        properties = Property.objects.filter(
            tenant_id=self.tenant_id,
            user_roles__contains=[self.user_role]
        ).annotate(
            search=SearchVector('property_name', 'description', 'location'),
            rank=SearchRank(SearchVector('property_name', 'description', 'location'), search_query)
        ).filter(
            rank__gt=0
        ).order_by('-rank')[:k]
        
        for prop in properties:
            results.append((prop, float(prop.rank), 'property'))
        
        # Sort all results by rank and take top k
        results.sort(key=lambda x: x[1], reverse=True)
        results = results[:k]
        
        logger.info(f"Keyword search found {len(results)} items ({sum(1 for r in results if r[2]=='document')} docs, {sum(1 for r in results if r[2]=='property')} properties)")
        return results
    
    def _hybrid_search(self, query: str, query_embedding: List[float], 
                      k: int = None) -> List[Dict]:
        """
        Combine vector and keyword search with alpha blending.
        
        Args:
            query: Search query string
            query_embedding: Query embedding vector
            k: Number of results (default from settings)
            
        Returns:
            List of document dictionaries with scores
        """
        
        if k is None:
            k = settings.VECTOR_SEARCH_TOP_K
        
        alpha = settings.HYBRID_SEARCH_ALPHA
        
        # Get results from both methods
        vector_results = self._vector_search(query_embedding, k=k * 2)
        keyword_results = self._keyword_search(query, k=k * 2)
        
        # Combine scores
        doc_scores = {}
        
        # Add vector scores
        for obj, score, obj_type in vector_results:
            key = f"{obj_type}_{obj.id}"
            doc_scores[key] = {
                'object': obj,
                'type': obj_type,
                'vector_score': score,
                'keyword_score': 0.0
            }
        
        # Add keyword scores
        for obj, score, obj_type in keyword_results:
            key = f"{obj_type}_{obj.id}"
            if key in doc_scores:
                doc_scores[key]['keyword_score'] = score
            else:
                doc_scores[key] = {
                    'object': obj,
                    'type': obj_type,
                    'vector_score': 0.0,
                    'keyword_score': score
                }
        
        # Calculate combined scores
        combined_results = []
        for key, scores in doc_scores.items():
            combined_score = (
                alpha * scores['vector_score'] + 
                (1 - alpha) * scores['keyword_score']
            )
            
            obj = scores['object']
            obj_type = scores['type']
            
            if obj_type == 'document':
                result = {
                    'id': str(obj.id),
                    'type': 'document',
                    'content': obj.content,
                    'metadata': obj.metadata,
                    'content_type': obj.content_type,
                    'source_reference': obj.source_reference,
                    'freshness_date': obj.freshness_date.isoformat(),
                    'relevance_score': combined_score,
                    'vector_score': scores['vector_score'],
                    'keyword_score': scores['keyword_score']
                }
            else:  # property
                # Build property content for LLM
                property_content = f"Property: {obj.property_name}\n"
                if obj.price_usd:
                    property_content += f"Price: ${obj.price_usd:,.2f} USD\n"
                if obj.location:
                    property_content += f"Location: {obj.location}\n"
                if obj.property_type:
                    property_content += f"Type: {obj.property_type}\n"
                if obj.bedrooms:
                    property_content += f"Bedrooms: {obj.bedrooms}\n"
                if obj.bathrooms:
                    property_content += f"Bathrooms: {obj.bathrooms}\n"
                if obj.square_meters:
                    property_content += f"Area: {obj.square_meters} m²\n"
                if obj.description:
                    property_content += f"Description: {obj.description}\n"
                if obj.source_url:
                    property_content += f"URL: {obj.source_url}\n"
                
                result = {
                    'id': str(obj.id),
                    'type': 'property',
                    'content': property_content,
                    'metadata': {
                        'property_name': obj.property_name,
                        'price_usd': float(obj.price_usd) if obj.price_usd else None,
                        'location': obj.location,
                        'property_type': obj.property_type,
                        'bedrooms': obj.bedrooms,
                        'bathrooms': float(obj.bathrooms) if obj.bathrooms else None,
                        'square_meters': float(obj.square_meters) if obj.square_meters else None,
                        'source_url': obj.source_url
                    },
                    'content_type': 'property',
                    'source_reference': obj.source_url or f"Property {obj.property_name}",
                    'relevance_score': combined_score,
                    'vector_score': scores['vector_score'],
                    'keyword_score': scores['keyword_score']
                }
            
            combined_results.append(result)
        
        # Sort by combined score
        combined_results.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        # Return top k
        top_results = combined_results[:k]
        
        logger.info(f"Hybrid search returning {len(top_results)} documents")
        
        # Track retrieval
        for result in top_results:
            if result.get('type') == 'document':
                doc = Document.objects.get(id=result['id'])
                doc.increment_retrieved(relevance_score=Decimal(str(result['relevance_score'])))
            # Properties don't have retrieval tracking yet
        
        return top_results
    
    def _check_semantic_cache(self, query: str, query_embedding: List[float]) -> Optional[Dict]:
        """Check if we have a cached response for similar query."""
        
        if not settings.ENABLE_SEMANTIC_CACHE:
            return None
        
        cache_key_prefix = f"semantic_cache:{self.tenant_id}:{self.user_role}"
        
        # Get all cached queries (this is simplified - in production use vector DB)
        # For now, just check exact match
        cache_key = f"{cache_key_prefix}:{hashlib.md5(query.encode()).hexdigest()}"
        cached = self.cache.get(cache_key)
        
        if cached:
            logger.info("Semantic cache hit!")
            return cached
        
        return None
    
    def _cache_response(self, query: str, response: str, sources: List[Dict]):
        """Cache response for future similar queries."""
        
        if not settings.ENABLE_SEMANTIC_CACHE:
            return
        
        cache_key_prefix = f"semantic_cache:{self.tenant_id}:{self.user_role}"
        cache_key = f"{cache_key_prefix}:{hashlib.md5(query.encode()).hexdigest()}"
        
        cache_data = {
            'response': response,
            'sources': sources,
            'cached_at': str(timezone.now())
        }
        
        # Different TTL based on content type
        ttl = settings.LLM_CACHE_TTL_HOURS * 3600
        
        self.cache.set(cache_key, cache_data, timeout=ttl)
    
    def _should_use_complex_model(self, query: str) -> bool:
        """Determine if query requires complex model (Claude)."""
        
        complex_keywords = [
            'invest', 'investment', 'roi', 'return',
            'legal', 'law', 'regulation', 'tax',
            'compare', 'comparison', 'versus', 'vs',
            'analyze', 'analysis', 'calculate',
            'risk', 'forecast', 'predict'
        ]
        
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in complex_keywords)
    
    def _build_context(self, retrieved_docs: List[Dict], 
                      conversation_history: List[Message]) -> str:
        """Build context from retrieved documents and conversation history."""
        
        context_parts = []
        
        # Add retrieved documents
        if retrieved_docs:
            context_parts.append("=== RELEVANT INFORMATION ===\n")
            for i, doc in enumerate(retrieved_docs, 1):
                context_parts.append(f"[Document {i}]")
                context_parts.append(f"Type: {doc['content_type']}")
                if doc.get('freshness_date'):
                    context_parts.append(f"Updated: {doc['freshness_date']}")
                if doc.get('source_reference'):
                    context_parts.append(f"Source: {doc['source_reference']}")
                context_parts.append(f"Content: {doc['content']}")
                context_parts.append("")
        
        # Add recent conversation
        if conversation_history:
            context_parts.append("=== RECENT CONVERSATION ===\n")
            for msg in conversation_history[-5:]:  # Last 5 messages
                role = msg.role.upper()
                context_parts.append(f"{role}: {msg.content}\n")
        
        return "\n".join(context_parts)
    
    def query(self, 
             query: str,
             conversation: Optional[Conversation] = None,
             stream: bool = False) -> Dict:
        """
        Main RAG query method.
        
        Args:
            query: User question
            conversation: Optional conversation for history
            stream: Whether to stream response
            
        Returns:
            Dictionary with response and metadata
        """
        
        import time
        start_time = time.time()
        
        logger.info(f"RAG query from {self.user_role}: {query[:100]}...")
        
        # 1. Generate query embedding
        query_embedding = self._get_query_embedding(query)
        
        # 2. Check semantic cache
        cached = self._check_semantic_cache(query, query_embedding)
        if cached:
            return {
                'response': cached['response'],
                'sources': cached['sources'],
                'cached': True,
                'latency_ms': int((time.time() - start_time) * 1000)
            }
        
        # 3. Retrieve relevant documents
        retrieved_docs = self._hybrid_search(query, query_embedding)
        
        # 4. Get conversation history
        conversation_history = []
        if conversation:
            # Get last N messages (Django QuerySet doesn't support negative indexing)
            all_messages = conversation.messages.order_by('created_at')
            total_count = all_messages.count()
            start_index = max(0, total_count - settings.MAX_CONVERSATION_HISTORY)
            conversation_history = list(all_messages[start_index:])
        
        # 5. Build context
        context = self._build_context(retrieved_docs, conversation_history)
        
        # 6. Choose LLM
        use_complex = self._should_use_complex_model(query)
        llm = self.complex_llm if use_complex else self.simple_llm
        model_name = settings.ANTHROPIC_MODEL if use_complex else settings.OPENAI_MODEL_CHAT
        
        logger.info(f"Using model: {model_name}")
        
        # 7. Build messages
        system_prompt = get_system_prompt(self.user_role)
        
        messages = [
            SystemMessage(content=system_prompt),
        ]
        
        # Add conversation history
        for msg in conversation_history:
            if msg.role == 'user':
                messages.append(HumanMessage(content=msg.content))
            elif msg.role == 'assistant':
                messages.append(AIMessage(content=msg.content))
        
        # Add current query with context
        user_message = f"{context}\n\n=== USER QUESTION ===\n{query}"
        messages.append(HumanMessage(content=user_message))
        
        # Log the full context being sent to LLM
        logger.info("=" * 80)
        logger.info("📤 CONTEXT SENT TO LLM:")
        logger.info(f"Context length: {len(context)} characters")
        logger.info(context[:2000])  # First 2000 chars
        if len(context) > 2000:
            logger.info(f"... (truncated, total {len(context)} chars)")
        logger.info("=" * 80)
        
        # 8. Generate response
        try:
            response = llm.invoke(messages)
            response_text = response.content
            
            latency_ms = int((time.time() - start_time) * 1000)
            
            logger.info(f"Response generated in {latency_ms}ms")
            
            # 9. Cache response
            self._cache_response(query, response_text, retrieved_docs)
            
            # 10. Return result
            return {
                'response': response_text,
                'sources': retrieved_docs,
                'model': model_name,
                'latency_ms': latency_ms,
                'cached': False,
                'tokens_used': getattr(response, 'usage', {}).get('total_tokens', 0)
            }
            
        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            raise RAGError(f"Failed to generate response: {str(e)}")
    
    def query_stream(self, query: str, conversation: Optional[Conversation] = None):
        """
        Stream RAG query response using generator.
        
        Args:
            query: User question
            conversation: Optional conversation for history
            
        Yields:
            Dictionary chunks with type and content
        """
        import time
        start_time = time.time()
        
        logger.info(f"RAG streaming query from {self.user_role}: {query[:100]}...")
        
        try:
            # 1. Generate query embedding
            query_embedding = self._get_query_embedding(query)
            
            # 2. Retrieve relevant documents
            retrieved_docs = self._hybrid_search(query, query_embedding)
            
            # 3. Send sources first
            yield {
                'type': 'sources',
                'sources': retrieved_docs[:5]  # Top 5 sources
            }
            
            # 4. Get conversation history
            conversation_history = []
            if conversation:
                all_messages = conversation.messages.order_by('created_at')
                total_count = all_messages.count()
                start_index = max(0, total_count - settings.MAX_CONVERSATION_HISTORY)
                conversation_history = list(all_messages[start_index:])
            
            # 5. Build context
            context = self._build_context(retrieved_docs, conversation_history)
            
            # 6. Choose LLM
            use_complex = self._should_use_complex_model(query)
            llm = self.complex_llm if use_complex else self.simple_llm
            
            # 7. Build messages
            system_prompt = get_system_prompt(self.user_role)
            
            messages = [
                SystemMessage(content=system_prompt),
            ]
            
            # Add conversation history
            for msg in conversation_history:
                if msg.role == 'user':
                    messages.append(HumanMessage(content=msg.content))
                elif msg.role == 'assistant':
                    messages.append(AIMessage(content=msg.content))
            
            # Add current query with context
            user_message = f"{context}\n\n=== USER QUESTION ===\n{query}"
            messages.append(HumanMessage(content=user_message))
            
            # 8. Stream response
            for chunk in llm.stream(messages):
                if hasattr(chunk, 'content') and chunk.content:
                    yield {
                        'type': 'content',
                        'content': chunk.content
                    }
            
            latency_ms = int((time.time() - start_time) * 1000)
            logger.info(f"Streaming completed in {latency_ms}ms")
            
        except Exception as e:
            logger.error(f"LLM streaming error: {e}")
            yield {
                'type': 'error',
                'error': str(e)
            }


from django.utils import timezone
