"""
Management command to create Document records for all properties.
This links Properties to the Document table for RAG search.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from tqdm import tqdm

from apps.properties.models import Property
from apps.documents.models import Document


class Command(BaseCommand):
    help = 'Create Document records for all properties with embeddings'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force recreate documents even if they exist',
        )

    def handle(self, *args, **options):
        force = options.get('force', False)
        
        self.stdout.write(self.style.SUCCESS('\n📄 Creating Property Documents for RAG...\n'))
        
        # Get all properties with embeddings
        properties = Property.objects.filter(
            is_active=True,
            embedding__isnull=False
        ).select_related('tenant')
        
        if not properties.exists():
            self.stdout.write(self.style.WARNING(
                '⚠️  No properties with embeddings found. '
                'Run: python manage.py generate_embeddings --properties'
            ))
            return
        
        created_count = 0
        updated_count = 0
        skipped_count = 0
        
        for property_obj in tqdm(properties, desc="Processing properties"):
            # Check if document already exists
            existing_doc = Document.objects.filter(
                content_type='property',
                metadata__property_id=str(property_obj.id)
            ).first()
            
            if existing_doc and not force:
                skipped_count += 1
                continue
            
            # Prepare metadata
            metadata = {
                'property_id': str(property_obj.id),
                'property_name': property_obj.property_name,
                'price_usd': float(property_obj.price_usd),
                'location': property_obj.location,
                'property_type': property_obj.property_type,
                'bedrooms': property_obj.bedrooms,
                'bathrooms': float(property_obj.bathrooms) if property_obj.bathrooms else None,
                'square_meters': float(property_obj.square_meters) if property_obj.square_meters else None,
                'source_url': property_obj.source_url,
                'source_website': property_obj.source_website,
            }
            
            if existing_doc:
                # Update existing document
                existing_doc.content = property_obj.content_for_search
                existing_doc.embedding = property_obj.embedding
                existing_doc.metadata = metadata
                existing_doc.user_roles = property_obj.user_roles
                existing_doc.updated_at = timezone.now()
                existing_doc.save()
                updated_count += 1
            else:
                # Create new document
                Document.objects.create(
                    tenant=property_obj.tenant,
                    content=property_obj.content_for_search,
                    content_type='property',
                    source_url=property_obj.source_url or '',
                    source_reference=f"Property: {property_obj.property_name}",
                    metadata=metadata,
                    embedding=property_obj.embedding,
                    user_roles=property_obj.user_roles,
                    is_active=True,
                    freshness_date=property_obj.updated_at,
                )
                created_count += 1
        
        # Summary
        self.stdout.write(self.style.SUCCESS('\n✅ Property Documents Created!\n'))
        self.stdout.write(f'  Created: {created_count}')
        self.stdout.write(f'  Updated: {updated_count}')
        self.stdout.write(f'  Skipped: {skipped_count}')
        self.stdout.write(f'  Total: {created_count + updated_count + skipped_count}\n')
        
        if created_count + updated_count > 0:
            self.stdout.write(self.style.SUCCESS(
                '🎉 Properties are now searchable via RAG!\n'
            ))
