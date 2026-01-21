#!/usr/bin/env python
"""
Script to delete LocalTips records for re-extraction testing

RECOMMENDED: Run via Django shell:
python manage.py shell -c "from apps.properties.models_content import LocalTipsGeneral, LocalTipsSpecific; g=LocalTipsGeneral.objects.all().delete(); s=LocalTipsSpecific.objects.all().delete(); print(f'✅ Deleted {g[0]} general + {s[0]} specific = {g[0]+s[0]} total LocalTips records')"

If you need to run this file directly, use:
python manage.py shell < delete_local_tips.py
"""

# This code runs in Django shell context
from apps.properties.models_content import LocalTipsGeneral, LocalTipsSpecific

# Delete LocalTipsGeneral
general_deleted, _ = LocalTipsGeneral.objects.all().delete()
print(f"✅ Deleted {general_deleted} LocalTipsGeneral records")

# Delete LocalTipsSpecific
specific_deleted, _ = LocalTipsSpecific.objects.all().delete()
print(f"✅ Deleted {specific_deleted} LocalTipsSpecific records")

print(f"\n✅ Total deleted: {general_deleted + specific_deleted} records")
print("🔄 Ready for fresh extraction with new serializer!")
