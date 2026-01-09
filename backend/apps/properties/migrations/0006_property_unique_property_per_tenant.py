# Generated manually on 2026-01-09 21:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0005_alter_propertyimage_image_url'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='property',
            constraint=models.UniqueConstraint(
                condition=models.Q(('source_url__isnull', False)),
                fields=('tenant', 'source_url'),
                name='unique_property_per_tenant',
                violation_error_message='This property URL already exists for this tenant'
            ),
        ),
    ]
