#!/usr/bin/env python
"""
Test script for the chatbot RAG system.
Tests various queries to ensure the system works end-to-end.
"""

import os
import sys
import django
import json
from decimal import Decimal

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.properties.models import Property
from apps.documents.models import Document
from apps.tenants.models import Tenant
from core.llm.rag import RAGPipeline


def print_section(title):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def check_database_state():
    """Check the current state of the database."""
    print_section("Database State Check")
    
    # Check tenants
    tenant_count = Tenant.objects.count()
    print(f"✓ Tenants: {tenant_count}")
    if tenant_count == 0:
        print("  ⚠️  WARNING: No tenants found. Run: python manage.py create_test_data.py")
        return False
    
    # Check properties
    property_count = Property.objects.filter(is_active=True).count()
    print(f"✓ Active Properties: {property_count}")
    if property_count == 0:
        print("  ⚠️  WARNING: No properties found. Please add properties via Data Collector.")
        return False
    
    # Check properties with embeddings
    embedded_properties = Property.objects.filter(is_active=True, embedding__isnull=False).count()
    print(f"✓ Properties with Embeddings: {embedded_properties}/{property_count}")
    if embedded_properties == 0:
        print("  ⚠️  WARNING: No embeddings. Run: python manage.py generate_embeddings --properties")
        return False
    
    # Check documents
    document_count = Document.objects.filter(is_active=True).count()
    property_docs = Document.objects.filter(content_type='property', is_active=True).count()
    print(f"✓ Total Documents: {document_count}")
    print(f"✓ Property Documents: {property_docs}")
    if property_docs == 0:
        print("  ⚠️  WARNING: No property documents. Run: python manage.py create_property_documents")
        return False
    
    return True


def test_rag_query(query_text, tenant_id, user_role='client'):
    """Test a single RAG query."""
    print(f"\n📝 Query: {query_text}")
    print(f"   Tenant: {tenant_id}, Role: {user_role}\n")
    
    try:
        rag = RAGPipeline(tenant_id=tenant_id, user_role=user_role)
        result = rag.query(query=query_text)
        
        print(f"✅ Response ({result.get('model', 'unknown')}):")
        print(f"   {result['response'][:200]}..." if len(result['response']) > 200 else f"   {result['response']}")
        print(f"\n📊 Stats:")
        print(f"   • Latency: {result.get('latency_ms', 0):.0f}ms")
        print(f"   • Tokens: {result.get('tokens_used', 0)}")
        print(f"   • Cached: {result.get('cached', False)}")
        print(f"   • Sources: {len(result.get('sources', []))}")
        
        if result.get('sources'):
            print(f"\n📚 Top Sources:")
            for i, source in enumerate(result['sources'][:3], 1):
                metadata = source.get('metadata', {})
                name = metadata.get('property_name', source['content_type'])
                score = source['relevance_score']
                print(f"   {i}. {name} (relevance: {score:.3f})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_test_suite():
    """Run the complete test suite."""
    print_section("RAG Chatbot Test Suite")
    
    # Check database state
    if not check_database_state():
        print("\n❌ Database not ready. Please complete setup steps first.")
        return
    
    # Get tenant for testing
    tenant = Tenant.objects.first()
    tenant_id = str(tenant.id)
    
    print_section("Running Test Queries")
    
    test_queries = [
        "¿Qué propiedades tienes disponibles?",
        "¿Propiedades en Tamarindo?",
        "Casas con 3 cuartos bajo $300,000",
        "¿Propiedades con piscina?",
        "¿Cuál es la propiedad más cara?",
    ]
    
    passed = 0
    failed = 0
    
    for query in test_queries:
        if test_rag_query(query, tenant_id):
            passed += 1
        else:
            failed += 1
        print()  # Separator
    
    # Summary
    print_section("Test Results")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Success Rate: {passed/(passed+failed)*100:.0f}%\n")
    
    if failed == 0:
        print("🎉 All tests passed! The chatbot is ready to use.")
        print("\n📝 Next steps:")
        print("   1. Start Django: python manage.py runserver")
        print("   2. Open chatbot: web/chat.html")
        print("   3. Test in browser!\n")
    else:
        print("⚠️  Some tests failed. Please review errors above.\n")


if __name__ == '__main__':
    run_test_suite()
