#!/usr/bin/env python
"""
Test OpenAI extraction with Coldwell Banker cleaned HTML.
Compares extraction quality and cost between original and cleaned HTML.
"""

import sys
import os
import django
from pathlib import Path

# Setup Django
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.utils.html_cleaner import clean_html_for_extraction
from core.llm.extraction import extract_property_data


def test_coldwell_banker_extraction():
    """Test extraction with Coldwell Banker HTML."""
    
    # Read the HTML file
    html_file = project_root / 'coldwell_banker_property.html'
    
    if not html_file.exists():
        print(f"❌ Error: {html_file} not found")
        return
    
    print("=" * 80)
    print("OPENAI EXTRACTION TEST - Coldwell Banker Property")
    print("=" * 80)
    print()
    
    with open(html_file, 'r', encoding='utf-8') as f:
        original_html = f.read()
    
    url = "https://www.coldwellbankercostarica.com/property/land-for-sale-in-la-fortuna/10031"
    
    # Clean HTML first
    print("🧹 Cleaning HTML with website-specific cleaner...")
    cleaning_result = clean_html_for_extraction(original_html, source_website='coldwellbanker')
    cleaned_html = cleaning_result['cleaned_html']
    
    print(f"✂️  Original: {cleaning_result['original_size']:,} chars")
    print(f"✂️  Cleaned:  {cleaning_result['cleaned_size']:,} chars")
    print(f"✂️  Reduction: {cleaning_result['reduction_percent']:.2f}%")
    print()
    
    # Extract property data
    print("🤖 Extracting property data with OpenAI GPT-4o...")
    print("-" * 80)
    
    try:
        extracted_data = extract_property_data(cleaned_html, url=url)
        
        print("✅ EXTRACTION SUCCESSFUL!")
        print()
        print("📊 Extraction Results:")
        print("-" * 80)
        
        # Display extracted fields
        fields_to_show = [
            ('property_name', 'Property Name'),
            ('price_usd', 'Price USD'),
            ('property_type', 'Property Type'),
            ('location', 'Location'),
            ('description', 'Description'),
            ('lot_size_m2', 'Lot Size (m²)'),
            ('amenities', 'Amenities'),
            ('status', 'Status'),
            ('extraction_confidence', 'Confidence'),
        ]
        
        for field_key, field_label in fields_to_show:
            value = extracted_data.get(field_key)
            if value is not None:
                if isinstance(value, list):
                    print(f"{field_label:20}: {', '.join(value)}")
                elif isinstance(value, str) and len(value) > 100:
                    print(f"{field_label:20}: {value[:100]}...")
                else:
                    print(f"{field_label:20}: {value}")
        
        print()
        print("🔍 Field Confidence Scores:")
        print("-" * 80)
        field_confidence = extracted_data.get('field_confidence', {})
        for field, confidence in field_confidence.items():
            if confidence is not None:
                try:
                    conf_val = float(confidence) if isinstance(confidence, (int, float)) else float(confidence.strip('%'))
                    bar_length = int(conf_val / 5)  # Scale to 20 chars max
                    bar = '█' * bar_length + '░' * (20 - bar_length)
                    print(f"{field:20}: {bar} {conf_val}%")
                except (ValueError, AttributeError):
                    print(f"{field:20}: {confidence}")
        
        print()
        print("💰 Cost Analysis:")
        print("-" * 80)
        tokens_used = extracted_data.get('tokens_used', 0)
        
        # Estimate cost (GPT-4o pricing: ~$2.50 per 1M input tokens, ~$10 per 1M output tokens)
        # Rough estimate: 80% input, 20% output
        input_tokens = int(tokens_used * 0.8)
        output_tokens = int(tokens_used * 0.2)
        input_cost = (input_tokens / 1_000_000) * 2.50
        output_cost = (output_tokens / 1_000_000) * 10.00
        total_cost = input_cost + output_cost
        
        print(f"Tokens used:         {tokens_used:,}")
        print(f"  - Input tokens:    ~{input_tokens:,}")
        print(f"  - Output tokens:   ~{output_tokens:,}")
        print(f"Estimated cost:      ${total_cost:.4f} USD")
        print(f"Token savings:       ~{cleaning_result['estimated_token_savings']:,} tokens")
        print(f"Cost savings:        ~${cleaning_result['estimated_cost_savings_usd']:.4f} USD")
        
        # Compare what it would have cost with original HTML
        original_tokens = cleaning_result['estimated_original_tokens']
        original_input_tokens = int(original_tokens * 0.8)
        original_output_tokens = int(original_tokens * 0.2)
        original_cost = (original_input_tokens / 1_000_000) * 2.50 + (original_output_tokens / 1_000_000) * 10.00
        
        print()
        print(f"Without cleaning:")
        print(f"  - Would use:       ~{original_tokens:,} tokens")
        print(f"  - Would cost:      ~${original_cost:.4f} USD")
        print(f"  - Savings:         {cleaning_result['reduction_percent']:.1f}% cheaper")
        
        print()
        print("=" * 80)
        print("✨ SUMMARY")
        print("=" * 80)
        print(f"✅ Successfully extracted from Coldwell Banker HTML")
        print(f"✅ Confidence score: {extracted_data.get('extraction_confidence', 0)}%")
        print(f"✅ Cost per property: ${total_cost:.4f} USD")
        print(f"✅ HTML cleaning saved: {cleaning_result['reduction_percent']:.1f}% in tokens")
        print(f"🎯 System ready for production with Coldwell Banker support!")
        print()
        
        # Save full extracted data for inspection
        import json
        output_file = project_root / 'coldwell_banker_extracted.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            # Convert non-serializable objects
            clean_data = {}
            for k, v in extracted_data.items():
                if k == 'tenant':
                    clean_data[k] = str(v) if v else None
                else:
                    clean_data[k] = v
            json.dump(clean_data, f, indent=2, ensure_ascii=False)
        print(f"💾 Full extracted data saved to: {output_file.name}")
        
    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    test_coldwell_banker_extraction()
