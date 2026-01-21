"""
Chatbot module for conversational AI.
Contains prompts, RAG, and embeddings for user interactions.
"""

from .prompts import (
    BUYER_SYSTEM_PROMPT,
    TOURIST_SYSTEM_PROMPT,
    VENDOR_SYSTEM_PROMPT,
    STAFF_SYSTEM_PROMPT,
    ADMIN_SYSTEM_PROMPT,
    ROLE_PROMPTS,
    get_system_prompt,
)

__all__ = [
    'BUYER_SYSTEM_PROMPT',
    'TOURIST_SYSTEM_PROMPT',
    'VENDOR_SYSTEM_PROMPT',
    'STAFF_SYSTEM_PROMPT',
    'ADMIN_SYSTEM_PROMPT',
    'ROLE_PROMPTS',
    'get_system_prompt',
]
