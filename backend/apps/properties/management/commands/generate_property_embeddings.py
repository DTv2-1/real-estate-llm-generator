"""
Django management command to generate embeddings for properties
Usage: python manage.py generate_property_embeddings
"""

from django.core.management.base import BaseCommand
from apps.properties.models import Property
from core.llm.embeddings import generate_property_embedding
import time


class Command(BaseCommand):
    help = 'Generates embeddings for all properties without embeddings'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Regenerate embeddings even if they already exist',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=10,
            help='Number of properties to process before pausing (default: 10)',
        )

    def handle(self, *args, **options):
        force = options.get('force', False)
        batch_size = options.get('batch_size', 10)
        
        self.stdout.write(self.style.SUCCESS('🔮 Generating property embeddings...'))
        self.stdout.write('')

        # Get properties that need embeddings
        if force:
            properties = Property.objects.all()
            self.stdout.write(f'🔄 Force mode: Regenerating ALL {properties.count()} properties')
        else:
            properties = Property.objects.filter(embedding__isnull=True)
            self.stdout.write(f'📊 Found {properties.count()} properties without embeddings')

        if not properties.exists():
            self.stdout.write(self.style.SUCCESS('✅ All properties already have embeddings!'))
            return

        success_count = 0
        error_count = 0
        total = properties.count()
        
        self.stdout.write('')
        self.stdout.write(f'Processing in batches of {batch_size} to avoid rate limits...')
        self.stdout.write('')
        
        for i, property_obj in enumerate(properties, 1):
            try:
                # Generate embedding
                embedding = generate_property_embedding(property_obj)
                
                if embedding:
                    property_obj.embedding = embedding
                    property_obj.save(update_fields=['embedding'])
                    
                    success_count += 1
                    property_name = property_obj.property_name[:60] if property_obj.property_name else 'Unnamed'
                    self.stdout.write(f'  ✅ [{i}/{total}] {property_name}')
                else:
                    error_count += 1
                    self.stdout.write(
                        self.style.WARNING(f'  ⚠️  [{i}/{total}] Failed to generate embedding for: {property_obj.id}')
                    )
                
                # Pause after each batch to avoid rate limits
                if i % batch_size == 0 and i < total:
                    self.stdout.write(f'  ⏸️  Pausing for 2 seconds...')
                    time.sleep(2)
                    
            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(f'  ❌ [{i}/{total}] Error: {str(e)[:100]}')
                )

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('✅ Embedding generation complete!'))
        self.stdout.write(f'   ✅ Success: {success_count}')
        
        if error_count > 0:
            self.stdout.write(self.style.WARNING(f'   ❌ Errors: {error_count}'))
        
        self.stdout.write('')
        
        # Show statistics
        total_with_embeddings = Property.objects.filter(embedding__isnull=False).count()
        total_properties = Property.objects.count()
        percentage = (total_with_embeddings / total_properties * 100) if total_properties > 0 else 0
        
        self.stdout.write(f'📊 Embedding Coverage:')
        self.stdout.write(f'   Total Properties: {total_properties}')
        self.stdout.write(f'   With Embeddings: {total_with_embeddings}')
        self.stdout.write(f'   Coverage: {percentage:.1f}%')
        self.stdout.write('')
        self.stdout.write('🎉 Properties are now ready for semantic search!')
