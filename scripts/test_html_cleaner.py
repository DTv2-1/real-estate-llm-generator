#!/usr/bin/env python
"""
Test HTML Cleaner with Coldwell Banker property.
Demonstrates size reduction and optimization.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.utils.html_cleaner import clean_html_for_extraction


def test_coldwell_banker_cleaning():
    """Test HTML cleaning with actual Coldwell Banker property."""
    
    # Read the HTML file
    html_file = project_root / 'coldwell_banker_property.html'
    
    if not html_file.exists():
        print(f"❌ Error: {html_file} not found")
        return
    
    print("=" * 80)
    print("HTML CLEANER TEST - Coldwell Banker Property")
    print("=" * 80)
    print()
    
    with open(html_file, 'r', encoding='utf-8') as f:
        original_html = f.read()
    
    print(f"📄 Original HTML file: {html_file.name}")
    print(f"📏 Original size: {len(original_html):,} characters")
    print()
    
    # Test generic cleaner
    print("🧹 Testing GENERIC HTML Cleaner...")
    print("-" * 80)
    result_generic = clean_html_for_extraction(original_html, source_website='other')
    
    print(f"✂️  Original size:     {result_generic['original_size']:>10,} chars")
    print(f"✂️  Cleaned size:      {result_generic['cleaned_size']:>10,} chars")
    print(f"✂️  Reduction:         {result_generic['reduction_percent']:>10.2f}%")
    print(f"✂️  Bytes saved:       {result_generic['reduction_bytes']:>10,} bytes")
    print(f"🎯 Original tokens:    ~{result_generic['estimated_original_tokens']:>9,}")
    print(f"🎯 Cleaned tokens:     ~{result_generic['estimated_cleaned_tokens']:>9,}")
    print(f"🎯 Token savings:      ~{result_generic['estimated_token_savings']:>9,}")
    print(f"💰 Cost savings:       ${result_generic['estimated_cost_savings_usd']:>10.4f} USD")
    print()
    
    # Test Coldwell Banker-specific cleaner
    print("🏠 Testing COLDWELL BANKER Specific Cleaner...")
    print("-" * 80)
    result_specific = clean_html_for_extraction(original_html, source_website='coldwellbanker')
    
    print(f"✂️  Original size:     {result_specific['original_size']:>10,} chars")
    print(f"✂️  Cleaned size:      {result_specific['cleaned_size']:>10,} chars")
    print(f"✂️  Reduction:         {result_specific['reduction_percent']:>10.2f}%")
    print(f"✂️  Bytes saved:       {result_specific['reduction_bytes']:>10,} bytes")
    print(f"🎯 Original tokens:    ~{result_specific['estimated_original_tokens']:>9,}")
    print(f"🎯 Cleaned tokens:     ~{result_specific['estimated_cleaned_tokens']:>9,}")
    print(f"🎯 Token savings:      ~{result_specific['estimated_token_savings']:>9,}")
    print(f"💰 Cost savings:       ${result_specific['estimated_cost_savings_usd']:>10.4f} USD")
    print()
    
    # Compare both approaches
    print("📊 COMPARISON: Generic vs Website-Specific")
    print("-" * 80)
    generic_size = result_generic['cleaned_size']
    specific_size = result_specific['cleaned_size']
    
    if specific_size < generic_size:
        additional_reduction = ((generic_size - specific_size) / generic_size) * 100
        print(f"✅ Website-specific cleaner is MORE efficient")
        print(f"   Additional reduction: {additional_reduction:.2f}% smaller")
        print(f"   Extra bytes saved: {generic_size - specific_size:,}")
    elif specific_size > generic_size:
        print(f"ℹ️  Generic cleaner is more aggressive")
        print(f"   Difference: {specific_size - generic_size:,} bytes larger")
    else:
        print(f"➡️  Both cleaners produced same result")
    print()
    
    # Save cleaned versions for inspection
    print("💾 Saving cleaned HTML files...")
    
    output_generic = project_root / 'coldwell_banker_property.cleaned_generic.html'
    with open(output_generic, 'w', encoding='utf-8') as f:
        f.write(result_generic['cleaned_html'])
    print(f"   ✓ Generic cleaned:  {output_generic.name}")
    
    output_specific = project_root / 'coldwell_banker_property.cleaned_specific.html'
    with open(output_specific, 'w', encoding='utf-8') as f:
        f.write(result_specific['cleaned_html'])
    print(f"   ✓ Specific cleaned: {output_specific.name}")
    print()
    
    # Show preview of cleaned HTML
    print("👀 Preview of cleaned HTML (first 500 chars):")
    print("-" * 80)
    print(result_specific['cleaned_html'][:500])
    print("...")
    print()
    
    # Summary
    print("=" * 80)
    print("✨ SUMMARY")
    print("=" * 80)
    print(f"🎯 Recommended: Use {'WEBSITE-SPECIFIC' if specific_size <= generic_size else 'GENERIC'} cleaner")
    print(f"💰 Expected savings per property: ~${result_specific['estimated_cost_savings_usd']:.4f} USD")
    print(f"📊 At 1000 properties/month: ~${result_specific['estimated_cost_savings_usd'] * 1000:.2f} USD saved")
    print(f"🚀 Extraction speed improvement: ~{result_specific['reduction_percent']:.0f}% faster")
    print()


if __name__ == '__main__':
    test_coldwell_banker_cleaning()
