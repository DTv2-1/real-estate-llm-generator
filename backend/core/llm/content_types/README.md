# Content Types - Modular Structure

## 📁 Directory Structure

```
core/llm/content_types/
├── __init__.py              # Main registry and helper functions
├── base.py                  # Base classes and shared utilities
│
├── tour/                    # Tour content type
│   ├── __init__.py
│   ├── prompts.py          # TOUR_SPECIFIC_PROMPT, TOUR_GENERAL_PROMPT
│   ├── config.py           # TourConfig (domains, keywords, critical_fields)
│   └── schema.py           # Field definitions and mappings
│
├── restaurant/              # Restaurant content type
│   ├── __init__.py
│   ├── prompts.py          # RESTAURANT_SPECIFIC_PROMPT, RESTAURANT_GENERAL_PROMPT
│   ├── config.py           # RestaurantConfig
│   └── schema.py           # Field definitions and mappings
│
├── real_estate/             # Real Estate content type
│   ├── __init__.py
│   ├── config.py           # RealEstateConfig
│   └── schema.py           # Field definitions
│
├── transportation/          # Transportation content type
│   ├── __init__.py
│   └── config.py           # TransportationConfig
│
└── local_tips/              # Local Tips content type
    ├── __init__.py
    └── config.py           # LocalTipsConfig
```

## 🎯 Design Goals

### ✅ **Separation of Concerns**
Each content type is in its own directory with:
- **prompts.py**: Extraction prompts (not mixed with other types)
- **config.py**: Domain lists, keywords, validation rules
- **schema.py**: Field definitions and data structure

### ✅ **Easy to Extend**
To add a new content type:
1. Create directory: `core/llm/content_types/my_type/`
2. Add `config.py` with MyTypeConfig class
3. Add `prompts.py` with extraction prompts
4. Register in `__init__.py`

### ✅ **Backward Compatible**
The new structure maintains compatibility with existing code:
```python
# Old way (still works)
from core.llm.content_types import get_extraction_prompt, CONTENT_TYPES

# New way (recommended)
from core.llm.content_types import get_content_type_config, TourConfig
```

## 📚 Usage Examples

### Get Extraction Prompt
```python
from core.llm.content_types import get_extraction_prompt

# Get specific tour prompt
prompt = get_extraction_prompt('tour', page_type='specific')

# Get general restaurant guide prompt
prompt = get_extraction_prompt('restaurant', page_type='general')
```

### Get Configuration
```python
from core.llm.content_types import get_content_type_config

# Get tour configuration
config = get_content_type_config('tour')
print(config.DOMAINS)          # ['viator.com', 'getyourguide.com', ...]
print(config.KEYWORDS)         # ['tour', 'activity', 'adventure', ...]
print(config.CRITICAL_FIELDS)  # ['description', 'price_usd', ...]
```

### Get Critical Fields (for web search logic)
```python
from core.llm.content_types import get_critical_fields

critical = get_critical_fields('restaurant')
# Returns: ['description', 'price_range', 'signature_dishes', 'amenities', 'atmosphere']
```

### Get Allowed Fields (for validation)
```python
from core.llm.content_types import get_allowed_fields

allowed = get_allowed_fields('restaurant')
# Returns: ['restaurant_name', 'cuisine_type', ..., 'rating', 'number_of_reviews']
```

### List All Content Types
```python
from core.llm.content_types import get_all_content_types

types = get_all_content_types()
# Returns: [
#   {'key': 'tour', 'label': 'Tour / Actividad', 'icon': '🗺️', 'description': '...'},
#   {'key': 'restaurant', 'label': 'Restaurante / Comida', 'icon': '🍴', ...},
#   ...
# ]
```

## 🔧 Adding a New Content Type

### Step 1: Create Directory
```bash
mkdir -p core/llm/content_types/my_type
```

### Step 2: Create config.py
```python
# core/llm/content_types/my_type/config.py

from ..base import ContentTypeConfig

class MyTypeConfig(ContentTypeConfig):
    KEY = 'my_type'
    LABEL = 'My Type Label'
    ICON = '🎯'
    DESCRIPTION = 'Description of what this extracts'
    
    DOMAINS = ['example.com', 'another.com']
    KEYWORDS = ['keyword1', 'keyword2']
    CRITICAL_FIELDS = ['field1', 'field2']
    ALLOWED_FIELDS = ['field1', 'field2', 'field3']
```

### Step 3: Create prompts.py
```python
# core/llm/content_types/my_type/prompts.py

MY_TYPE_SPECIFIC_PROMPT = """
Your extraction prompt for specific items...

**Content to extract from:**
{content}
"""

MY_TYPE_GENERAL_PROMPT = """
Your extraction prompt for general guides...

**Content to extract from:**
{content}
"""
```

### Step 4: Create __init__.py
```python
# core/llm/content_types/my_type/__init__.py

from .prompts import MY_TYPE_SPECIFIC_PROMPT, MY_TYPE_GENERAL_PROMPT
from .config import MyTypeConfig

__all__ = [
    'MY_TYPE_SPECIFIC_PROMPT',
    'MY_TYPE_GENERAL_PROMPT',
    'MyTypeConfig',
]
```

### Step 5: Register in main __init__.py
```python
# core/llm/content_types/__init__.py

from .my_type import MyTypeConfig, MY_TYPE_SPECIFIC_PROMPT, MY_TYPE_GENERAL_PROMPT

CONTENT_TYPE_REGISTRY = {
    # ... existing types
    'my_type': MyTypeConfig,
}

PROMPT_REGISTRY = {
    # ... existing prompts
    ('my_type', 'specific'): MY_TYPE_SPECIFIC_PROMPT,
    ('my_type', 'general'): MY_TYPE_GENERAL_PROMPT,
}
```

## 🔄 Migration Status

### ✅ Migrated
- **Tour**: Fully modularized with prompts, config, schema
- **Restaurant**: Fully modularized with prompts, config, schema
- **Real Estate**: Config and schema (prompts in legacy prompts.py)

### ⏳ Pending Migration
- **Transportation**: Config only, prompts in content_types_legacy.py
- **Local Tips**: Config only, prompts in content_types_legacy.py

### 📝 Legacy File
- `content_types_legacy.py`: Old monolithic file (764 lines)
  - Contains transportation and local_tips prompts
  - Contains real estate guide prompt
  - Will be fully deprecated once all prompts are migrated

## 🎉 Benefits

### Before (Monolithic)
```
content_types.py (764 lines)
  ├─ TOUR_EXTRACTION_PROMPT (60 lines)
  ├─ TOUR_GUIDE_EXTRACTION_PROMPT (140 lines)
  ├─ REAL_ESTATE_GUIDE_EXTRACTION_PROMPT (55 lines)
  ├─ RESTAURANT_EXTRACTION_PROMPT (102 lines)
  ├─ LOCAL_TIPS_EXTRACTION_PROMPT (40 lines)
  ├─ TRANSPORTATION_EXTRACTION_PROMPT (55 lines)
  ├─ TRANSPORTATION_GUIDE_EXTRACTION_PROMPT (110 lines)
  ├─ CONTENT_TYPES dict with all configs mixed together
  └─ Helper functions
```

❌ **Problems:**
- Hard to find specific prompts
- Merge conflicts when multiple people edit
- No clear ownership per content type
- Difficult to test individual types

### After (Modular)
```
content_types/
  ├─ tour/
  │   ├─ prompts.py (200 lines - only tour prompts)
  │   ├─ config.py (40 lines - tour config)
  │   └─ schema.py (50 lines - tour schema)
  ├─ restaurant/
  │   ├─ prompts.py (120 lines - only restaurant prompts)
  │   ├─ config.py (40 lines - restaurant config)
  │   └─ schema.py (40 lines - restaurant schema)
  └─ ... (other types)
```

✅ **Benefits:**
- Each type is self-contained
- Easy to find and edit prompts
- Clear separation of concerns
- Can work on different types in parallel
- Easy to add new types without touching others

## 📖 Documentation

For more details, see:
- `base.py`: Base classes and shared utilities
- Each content type's `__init__.py`: Usage examples
- `../extraction.py`: How PropertyExtractor uses this system
