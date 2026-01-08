"""
Conversation and Message models for chat history.
"""

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.tenants.models import Tenant
from apps.users.models import CustomUser


class Conversation(models.Model):
    """
    Conversation thread for chat interactions.
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='conversations',
        verbose_name=_('Tenant')
    )
    
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='conversations',
        verbose_name=_('User'),
        null=True,
        blank=True
    )
    
    user_role = models.CharField(
        _('User Role'),
        max_length=20,
        help_text=_('User role at conversation start')
    )
    
    title = models.CharField(
        _('Title'),
        max_length=255,
        help_text=_('Conversation title (auto-generated or custom)')
    )
    
    summary = models.TextField(
        _('Summary'),
        blank=True,
        help_text=_('AI-generated summary of conversation')
    )
    
    total_tokens = models.IntegerField(
        _('Total Tokens'),
        default=0,
        help_text=_('Total tokens used in this conversation')
    )
    
    total_cost_usd = models.DecimalField(
        _('Total Cost (USD)'),
        max_digits=10,
        decimal_places=6,
        default=0,
        help_text=_('Estimated total cost in USD')
    )
    
    is_archived = models.BooleanField(
        _('Archived'),
        default=False,
        help_text=_('Is this conversation archived?')
    )
    
    created_at = models.DateTimeField(
        _('Created At'),
        auto_now_add=True
    )
    
    updated_at = models.DateTimeField(
        _('Updated At'),
        auto_now=True
    )
    
    class Meta:
        db_table = 'conversations'
        verbose_name = _('Conversation')
        verbose_name_plural = _('Conversations')
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['tenant', 'user', '-updated_at']),
            models.Index(fields=['user', 'is_archived']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
    def get_message_count(self):
        """Get total number of messages in conversation."""
        return self.messages.count()
    
    def get_last_message_at(self):
        """Get timestamp of last message."""
        last_message = self.messages.order_by('-created_at').first()
        return last_message.created_at if last_message else self.created_at
    
    def update_costs(self):
        """Update total tokens and cost from messages."""
        from django.db.models import Sum
        
        aggregates = self.messages.aggregate(
            total_input=Sum('tokens_input'),
            total_output=Sum('tokens_output')
        )
        
        input_tokens = aggregates['total_input'] or 0
        output_tokens = aggregates['total_output'] or 0
        self.total_tokens = input_tokens + output_tokens
        
        # Rough cost estimation (adjust based on actual model pricing)
        # GPT-4o-mini: $0.15/1M input, $0.60/1M output
        input_cost = (input_tokens / 1_000_000) * 0.15
        output_cost = (output_tokens / 1_000_000) * 0.60
        self.total_cost_usd = input_cost + output_cost
        
        self.save(update_fields=['total_tokens', 'total_cost_usd'])


class Message(models.Model):
    """
    Individual message in a conversation.
    """
    
    class Role:
        USER = 'user'
        ASSISTANT = 'assistant'
        SYSTEM = 'system'
        
        CHOICES = [
            (USER, _('User')),
            (ASSISTANT, _('Assistant')),
            (SYSTEM, _('System')),
        ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name=_('Conversation')
    )
    
    role = models.CharField(
        _('Role'),
        max_length=20,
        choices=Role.CHOICES,
        help_text=_('Message sender role')
    )
    
    content = models.TextField(
        _('Content'),
        help_text=_('Message content')
    )
    
    tokens_input = models.IntegerField(
        _('Input Tokens'),
        null=True,
        blank=True,
        help_text=_('Number of input tokens')
    )
    
    tokens_output = models.IntegerField(
        _('Output Tokens'),
        null=True,
        blank=True,
        help_text=_('Number of output tokens')
    )
    
    model_used = models.CharField(
        _('Model Used'),
        max_length=50,
        blank=True,
        help_text=_('LLM model that generated this message')
    )
    
    retrieved_documents = models.JSONField(
        _('Retrieved Documents'),
        default=list,
        blank=True,
        help_text=_('Documents retrieved from RAG for this message')
    )
    
    latency_ms = models.IntegerField(
        _('Latency (ms)'),
        null=True,
        blank=True,
        help_text=_('Response latency in milliseconds')
    )
    
    error_message = models.TextField(
        _('Error Message'),
        blank=True,
        help_text=_('Error message if generation failed')
    )
    
    metadata = models.JSONField(
        _('Metadata'),
        default=dict,
        blank=True,
        help_text=_('Additional metadata')
    )
    
    created_at = models.DateTimeField(
        _('Created At'),
        auto_now_add=True
    )
    
    class Meta:
        db_table = 'messages'
        verbose_name = _('Message')
        verbose_name_plural = _('Messages')
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['conversation', 'created_at']),
            models.Index(fields=['role', 'created_at']),
        ]
    
    def __str__(self):
        content_preview = self.content[:50] + '...' if len(self.content) > 50 else self.content
        return f"{self.get_role_display()}: {content_preview}"
    
    def get_sources(self):
        """Extract source documents with their relevance."""
        sources = []
        for doc in self.retrieved_documents:
            if isinstance(doc, dict):
                sources.append({
                    'id': doc.get('id'),
                    'content': doc.get('content', '')[:200],
                    'relevance': doc.get('relevance_score'),
                    'source_ref': doc.get('source_reference', 'N/A')
                })
        return sources
    
    def save(self, *args, **kwargs):
        """Override save to update conversation timestamp."""
        super().save(*args, **kwargs)
        # Update conversation's updated_at timestamp
        self.conversation.save(update_fields=['updated_at'])
