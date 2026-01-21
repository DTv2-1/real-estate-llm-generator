#!/usr/bin/env python3
"""
Script para probar la extracción de TODOS los tipos de contenido.
Procesa URLs de ejemplo y guarda los resultados en JSON.

Usage:
    python test_all_content_types_extraction.py              # Procesa todas las URLs
    python test_all_content_types_extraction.py --random     # Procesa 1 URL aleatoria (para medir tiempo)
    python test_all_content_types_extraction.py --count 5    # Procesa 5 URLs aleatorias
    python test_all_content_types_extraction.py --verbose    # Muestra logs detallados
"""

import asyncio
import json
import sys
import argparse
import random
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles datetime objects."""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


# CRITICAL: Load .env FIRST before anything else
from dotenv import load_dotenv
env_file = Path(__file__).parent / '.env'
if env_file.exists():
    load_dotenv(env_file, override=True)
    print(f"✓ Loaded environment from {env_file}")
else:
    print("⚠️  Warning: .env file not found")

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

# Django setup - AFTER loading .env
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
print("✓ Django initialized")

from core.llm.extraction.extractor import PropertyExtractor, extract_content_data
from core.llm.extraction.content_detection import detect_content_type
from core.llm.extraction.page_type_detection import detect_page_type
from core.llm.content_types import get_extraction_prompt


# ============================================================================
# TEST URLS POR TIPO DE CONTENIDO
# ============================================================================

TEST_URLS = {
    'real_estate': {
        'specific': [
            'https://www.encuentra24.com/costa-rica-es/bienes-raices-proyectos-nuevos/venta-de-apartamento-en-jaco/31553057',
            'https://www.encuentra24.com/costa-rica-es/bienes-raices-venta-de-propiedades-casas/casa-en-venta-con-vista-panoramica-lourdes-naranjo-alajuela/31739294',
            'https://brevitas.com/p/5jTTF1iWpO/oceanview-estate-ideal-for-residence-retreats-or-boutique-use-esparza',
            'https://brevitas.com/p/HGAdjDu/multi-unit-retreat-ready-property-central-pacific-costa-rica',
            'https://www.coldwellbankercostarica.com/property/land-for-sale-in-samara/2660',
            'https://www.coldwellbankercostarica.com/property/2-bed-land-for-sale-in-dominical/13235',
        ],
        'general': [
            'https://www.coldwellbankercostarica.com/properties-for-sale/',
            'https://brevitas.com/propiedades/casas-en-venta-san-jose',
        ],
    },
    'tour': {
        'specific': [
            'https://www.desafiocostarica.com/tour-detail/rafting-balsa-river-costa-rica-2-3',
            'https://www.desafiocostarica.com/tour-detail/lost-canyon-canyoning-costa-rica',
            'https://www.anywhere.com/costa-rica/tours/canopy-tour',
            'https://www.anywhere.com/costa-rica/tours/rafting',
            'https://www.getyourguide.com/costa-rica-l123/from-san-jose-arenal-volcano-tour-t123456/',
            'https://www.tripadvisor.com/AttractionProductReview-g309293-d11452345-Arenal_Volcano_Tour',
        ],
        'general': [
            'https://costarica.org/tours/',
            'https://costarica.org/tours/arenal/',
            'https://www.desafiocostarica.com/',
            'https://www.anywhere.com/costa-rica/tours',
        ],
    },
    'restaurant': {
        'specific': [
            'https://www.tripadvisor.com/Restaurant_Review-g309293-d4471802-Reviews-Tenedor_Argentino-San_Jose_San_Jose_Metro_Province_of_San_Jose.html',
        ],
        'general': [
            'https://www.tripadvisor.com/Restaurants-g309293-San_Jose_San_Jose_Metro_Province_of_San_Jose.html',
        ],
    },
    'transportation': {
        'specific': [
            'https://www.rome2rio.com/map/San-Jos%C3%A9-Costa-Rica/Manuel-Antonio-National-Park',
            'https://www.rome2rio.com/map/Liberia-Airport-LIR/Tamarindo',
        ],
        'general': [
            'https://www.interbusonline.com/?_gl=1%2Aalfzyo%2A_gcl_au%2ANTUxOTM0ODM1LjE3Njg5NjI0OTQ.%2A_ga%2AMTI5NzQ3OTkyNy4xNzY4OTYyNDk0%2A_ga_E5MXGWYYW2%2AczE3Njg5NjI0OTQkbzEkZzEkdDE3Njg5NjI1MjckajI3JGwwJGgxNDU1NTYwNjQ0#services',
            'https://www.rome2rio.com/map/Costa-Rica',
        ],
    },
    'local_tips': {
        'specific': [
            'https://www.lonelyplanet.com/articles/costa-rica-best-places-to-visit',
        ],
        'general': [
            'https://en.wikivoyage.org/wiki/Costa_Rica',
        ],
    },
}


class ExtractionTester:
    """Clase para probar la extracción de todos los tipos de contenido."""
    
    def __init__(self, verbose: bool = False):
        self.results = []
        self.verbose = verbose
        
    def log(self, message: str, level: str = 'info'):
        """Log condicional basado en verbose mode."""
        if level == 'critical':
            print(message)
        elif level == 'important':
            print(message)
        elif self.verbose:
            print(message)
        
    async def test_url(self, url: str, expected_type: str = None, expected_page_type: str = None) -> Dict[str, Any]:
        """
        Prueba la extracción de una URL completa.
        
        Args:
            url: URL a procesar
            expected_type: Tipo de contenido esperado (opcional)
            expected_page_type: Tipo de página esperado (opcional)
            
        Returns:
            Dict con todos los detalles del procesamiento
        """
        start_time = time.time()
        
        self.log(f"\n{'='*80}", 'critical')
        self.log(f"🔍 Procesando: {url}", 'critical')
        self.log(f"{'='*80}", 'critical')
        
        result = {
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'expected_content_type': expected_type,
            'expected_page_type': expected_page_type,
            'steps': {},
            'errors': [],
            'timing': {},
        }
        
        try:
            # PASO 1: Scraping de la página
            self.log("\n🌐 PASO 1: Descargando contenido de la página...", 'important')
            step_start = time.time()
            
            try:
                # scrape_url es síncrona, no async
                from core.scraping.scraper import scrape_url
                loop = asyncio.get_event_loop()
                scrape_result = await loop.run_in_executor(None, scrape_url, url)
                
                html_content = scrape_result.get('html', '')
                cleaned_text = scrape_result.get('text', '')
                scrape_method = scrape_result.get('method', 'unknown')
                
                if not html_content:
                    raise ValueError("No se pudo obtener el HTML de la página")
                
                step_time = time.time() - step_start
                result['timing']['scraping'] = round(step_time, 2)
                
                # Mostrar método usado con emojis
                method_emoji = {
                    'httpx': '⚡',
                    'playwright': '🎭',
                    'scrapfly': '💰',
                }.get(scrape_method, '❓')
                
                self.log(f"   ✓ Método: {method_emoji} {scrape_method.upper()} ({step_time:.1f}s)", 'important')
                self.log(f"   ✓ HTML: {len(html_content):,} chars, Texto: {len(cleaned_text):,} chars", 'important')
                
                result['steps']['scraping'] = {
                    'method': scrape_method,
                    'html_length': len(html_content),
                    'text_length': len(cleaned_text),
                    'success': True,
                }
            except Exception as e:
                error_msg = f"Error en scraping: {str(e)}"
                self.log(f"   ❌ {error_msg}", 'critical')
                result['errors'].append(error_msg)
                result['final_status'] = 'error'
                return result
            
            # PASO 2: Detectar tipo de contenido
            self.log("\n📋 PASO 2: Detectando tipo de contenido...", 'important')
            step_start = time.time()
            
            detection_result = detect_content_type(url, html_content)
            detected_type = detection_result.get('content_type', 'unknown')
            
            step_time = time.time() - step_start
            result['timing']['content_detection'] = round(step_time, 2)
            
            result['steps']['content_detection'] = {
                'detected_type': detected_type,
                'confidence': detection_result.get('confidence', 0),
                'method': detection_result.get('method', 'unknown'),
                'reasoning': detection_result.get('reasoning', ''),
                'matches_expected': detected_type == expected_type if expected_type else None,
            }
            self.log(f"   ✓ Tipo: {detected_type} | Confianza: {detection_result.get('confidence', 0):.2f} | Tiempo: {step_time:.1f}s", 'important')
            if expected_type and detected_type != expected_type:
                self.log(f"   ⚠️  Esperado: {expected_type}", 'important')
            
            # PASO 3: Detectar si es específico o general
            self.log("\n📄 PASO 3: Detectando tipo de página...", 'important')
            step_start = time.time()
            
            page_type_result = detect_page_type(url, html_content, detected_type)
            page_type = page_type_result.get('page_type', 'specific')
            
            step_time = time.time() - step_start
            result['timing']['page_type_detection'] = round(step_time, 2)
            
            result['steps']['page_type_detection'] = {
                'page_type': page_type,
                'confidence': page_type_result.get('confidence', 0),
                'reasoning': page_type_result.get('reasoning', ''),
                'matches_expected': page_type == expected_page_type if expected_page_type else None,
            }
            self.log(f"   ✓ Tipo: {page_type} | Confianza: {page_type_result.get('confidence', 0):.2f} | Tiempo: {step_time:.1f}s", 'important')
            
            # PASO 4: Obtener el prompt apropiado
            self.log("\n📝 PASO 4: Obteniendo prompt de extracción...", 'important')
            prompt = get_extraction_prompt(detected_type, page_type)
            result['steps']['prompt_selection'] = {
                'content_type': detected_type,
                'page_type': page_type,
                'prompt_length': len(prompt),
            }
            self.log(f"   ✓ Prompt: {detected_type}/{page_type} ({len(prompt):,} chars)", 'important')
            
            # PASO 5: Extraer información
            self.log("\n🔄 PASO 5: Extrayendo información con LLM...", 'important')
            step_start = time.time()
            
            # Usar la función extract_content_data (no async)
            extraction_result = extract_content_data(
                content=html_content,
                content_type=detected_type,
                page_type=page_type,
                url=url
            )
            
            step_time = time.time() - step_start
            result['timing']['extraction'] = round(step_time, 2)
            
            extraction_confidence = extraction_result.get('extraction_confidence', 0)
            
            result['steps']['extraction'] = {
                'success': bool(extraction_result),
                'content_type': detected_type,
                'page_type': page_type,
                'data': extraction_result,
                'confidence': extraction_confidence,
                'method': 'llm',
                'errors': [],
            }
            
            # Criterio de éxito
            has_data = bool(extraction_result)
            confidence = extraction_confidence
            is_successful = has_data and confidence >= 0.5
            
            if is_successful:
                self.log(f"   ✅ Extracción exitosa! Confianza: {confidence:.2f} | Tiempo: {step_time:.1f}s", 'critical')
                
                # Contar campos extraídos
                non_null_fields = {k: v for k, v in extraction_result.items() 
                                   if v is not None 
                                   and not k.endswith('_evidence') 
                                   and k not in ['source_url', 'raw_html', 'tokens_used', 'content_type', 'page_type', 'confidence_reasoning']}
                
                self.log(f"   📊 Campos extraídos: {len(non_null_fields)}", 'critical')
                
                # Mostrar primeros campos con valores
                for key, value in list(non_null_fields.items())[:10]:
                    if isinstance(value, list):
                        value_str = f"[{len(value)} items]" if value else "[]"
                    elif isinstance(value, dict):
                        value_str = f"{{{len(value)} keys}}"
                    else:
                        value_str = str(value)[:60]
                    self.log(f"      • {key}: {value_str}", 'verbose')
                if len(non_null_fields) > 10:
                    self.log(f"      ... y {len(non_null_fields) - 10} campos más", 'verbose')
            else:
                if confidence < 0.5:
                    self.log(f"   ⚠️  Confianza baja ({confidence:.2f}) | Tiempo: {step_time:.1f}s", 'critical')
                else:
                    self.log(f"   ⚠️  Sin datos extraídos | Tiempo: {step_time:.1f}s", 'critical')
            
            # Estado final
            has_meaningful_data = bool(extraction_result)
            final_confidence = extraction_result.get('extraction_confidence', 0)
            result['final_status'] = 'success' if (has_meaningful_data and final_confidence >= 0.5) else 'failed'
            
        except Exception as e:
            error_msg = f"Error procesando URL: {str(e)}"
            self.log(f"\n❌ {error_msg}", 'critical')
            result['errors'].append(error_msg)
            result['final_status'] = 'error'
            import traceback
            result['traceback'] = traceback.format_exc()
        
        # Tiempo total
        total_time = time.time() - start_time
        result['timing']['total'] = round(total_time, 2)
        
        self.log(f"\n⏱️  TIEMPO TOTAL: {total_time:.2f}s", 'critical')
        self.log(f"   • Scraping: {result['timing'].get('scraping', 0):.1f}s", 'critical')
        self.log(f"   • Detección tipo: {result['timing'].get('content_detection', 0):.1f}s", 'critical')
        self.log(f"   • Detección página: {result['timing'].get('page_type_detection', 0):.1f}s", 'critical')
        self.log(f"   • Extracción LLM: {result['timing'].get('extraction', 0):.1f}s", 'critical')
        
        return result
    
    async def test_all_content_types(self, random_count: int = None):
        """
        Prueba todas las URLs de todos los tipos de contenido.
        
        Args:
            random_count: Si se especifica, prueba solo N URLs aleatorias
        """
        self.log("\n" + "="*80, 'critical')
        self.log("🚀 INICIANDO PRUEBAS DE EXTRACCIÓN", 'critical')
        self.log("="*80, 'critical')
        self.log(f"\n📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 'critical')
        
        # Construir lista completa de URLs
        all_urls = []
        for content_type, page_types in TEST_URLS.items():
            for page_type, urls in page_types.items():
                for url in urls:
                    all_urls.append({
                        'url': url,
                        'content_type': content_type,
                        'page_type': page_type,
                    })
        
        # Si random_count está especificado, seleccionar URLs aleatorias
        if random_count is not None:
            random.shuffle(all_urls)
            all_urls = all_urls[:random_count]
            self.log(f"🎲 Modo aleatorio: Probando {len(all_urls)} URL(s) de {sum(len(urls['specific']) + len(urls['general']) for urls in TEST_URLS.values())} totales", 'critical')
        else:
            self.log(f"🔢 Modo completo: Probando {len(all_urls)} URLs", 'critical')
        
        # Procesar URLs
        for i, url_info in enumerate(all_urls, 1):
            self.log(f"\n\n{'#'*80}", 'critical')
            self.log(f"# URL {i}/{len(all_urls)}: {url_info['content_type'].upper()} - {url_info['page_type'].upper()}", 'critical')
            self.log(f"{'#'*80}", 'critical')
            
            result = await self.test_url(
                url=url_info['url'],
                expected_type=url_info['content_type'],
                expected_page_type=url_info['page_type'],
            )
            self.results.append(result)
            
            # Pequeña pausa entre requests (solo si hay más URLs)
            if i < len(all_urls):
                await asyncio.sleep(2)
        
        return self.results
    
    def generate_summary(self) -> Dict[str, Any]:
        """Genera un resumen de todos los resultados."""
        summary = {
            'total_urls': len(self.results),
            'successful': sum(1 for r in self.results if r['final_status'] == 'success'),
            'failed': sum(1 for r in self.results if r['final_status'] == 'failed'),
            'errors': sum(1 for r in self.results if r['final_status'] == 'error'),
            'by_content_type': {},
            'by_page_type': {},
            'by_scraping_method': {},  # NUEVO: estadísticas por método de scraping
            'all_extracted_fields': set(),
        }
        
        for result in self.results:
            # Por tipo de contenido
            expected_type = result.get('expected_content_type', 'unknown')
            if expected_type not in summary['by_content_type']:
                summary['by_content_type'][expected_type] = {
                    'total': 0,
                    'successful': 0,
                    'failed': 0,
                }
            summary['by_content_type'][expected_type]['total'] += 1
            if result['final_status'] == 'success':
                summary['by_content_type'][expected_type]['successful'] += 1
            else:
                summary['by_content_type'][expected_type]['failed'] += 1
            
            # Por tipo de página
            expected_page = result.get('expected_page_type', 'unknown')
            if expected_page not in summary['by_page_type']:
                summary['by_page_type'][expected_page] = {
                    'total': 0,
                    'successful': 0,
                }
            summary['by_page_type'][expected_page]['total'] += 1
            if result['final_status'] == 'success':
                summary['by_page_type'][expected_page]['successful'] += 1
            
            # Por método de scraping (NUEVO)
            scrape_method = result.get('steps', {}).get('scraping', {}).get('method', 'unknown')
            if scrape_method not in summary['by_scraping_method']:
                summary['by_scraping_method'][scrape_method] = 0
            summary['by_scraping_method'][scrape_method] += 1
            
            # Campos extraídos
            if result.get('steps', {}).get('extraction', {}).get('data'):
                fields = result['steps']['extraction']['data'].keys()
                summary['all_extracted_fields'].update(fields)
        
        # Convertir set a lista para JSON
        summary['all_extracted_fields'] = sorted(list(summary['all_extracted_fields']))
        
        return summary
    
    def save_results(self, output_file: str = 'extraction_test_results.json'):
        """Guarda los resultados en un archivo JSON."""
        summary = self.generate_summary()
        
        output = {
            'test_info': {
                'timestamp': datetime.now().isoformat(),
                'total_urls_tested': len(self.results),
                'script_version': '1.0',
            },
            'summary': summary,
            'detailed_results': self.results,
        }
        
        output_path = Path(__file__).parent / output_file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False, cls=DateTimeEncoder)
        
        self.log(f"\n\n{'='*80}", 'critical')
        self.log(f"💾 RESULTADOS GUARDADOS", 'critical')
        self.log(f"{'='*80}", 'critical')
        self.log(f"📁 Archivo: {output_path}", 'critical')
        self.log(f"📊 Total URLs: {summary['total_urls']}", 'critical')
        self.log(f"✅ Exitosas: {summary['successful']}", 'critical')
        self.log(f"❌ Fallidas: {summary['failed']}", 'critical')
        self.log(f"⚠️  Errores: {summary['errors']}", 'critical')
        
        # Calcular tiempo promedio
        timings = [r.get('timing', {}).get('total', 0) for r in self.results if r.get('timing', {}).get('total')]
        if timings:
            avg_time = sum(timings) / len(timings)
            min_time = min(timings)
            max_time = max(timings)
            self.log(f"\n⏱️  TIEMPOS:", 'critical')
            self.log(f"   • Promedio: {avg_time:.1f}s", 'critical')
            self.log(f"   • Mínimo: {min_time:.1f}s", 'critical')
            self.log(f"   • Máximo: {max_time:.1f}s", 'critical')
        
        self.log(f"\n📋 Resumen por tipo:", 'critical')
        for content_type, stats in summary['by_content_type'].items():
            self.log(f"   • {content_type}: {stats['successful']}/{stats['total']} exitosas", 'critical')
        
        self.log(f"\n🌐 Métodos de scraping:", 'critical')
        method_emojis = {'httpx': '⚡', 'playwright': '🎭', 'scrapfly': '💰'}
        for method, count in summary['by_scraping_method'].items():
            emoji = method_emojis.get(method, '❓')
            self.log(f"   • {emoji} {method.upper()}: {count} URLs", 'critical')
        
        self.log(f"\n🏷️  Campos únicos extraídos: {len(summary['all_extracted_fields'])}", 'critical')
        
        return output_path


async def main():
    """Función principal."""
    # Parsear argumentos
    parser = argparse.ArgumentParser(
        description='Test de extracción de contenido multi-tipo',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python test_all_content_types_extraction.py                 # Todas las URLs
  python test_all_content_types_extraction.py --random        # 1 URL aleatoria
  python test_all_content_types_extraction.py --count 5       # 5 URLs aleatorias
  python test_all_content_types_extraction.py --verbose       # Logs detallados
  python test_all_content_types_extraction.py --random -v     # 1 URL aleatoria con logs
        """
    )
    parser.add_argument('--random', '-r', action='store_true',
                        help='Procesar solo 1 URL aleatoria (útil para medir tiempo)')
    parser.add_argument('--count', '-c', type=int, metavar='N',
                        help='Procesar N URLs aleatorias')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Mostrar logs detallados de cada paso')
    
    args = parser.parse_args()
    
    # Determinar modo
    if args.random:
        random_count = 1
    elif args.count:
        random_count = args.count
    else:
        random_count = None
    
    tester = ExtractionTester(verbose=args.verbose)
    
    try:
        # Ejecutar pruebas
        await tester.test_all_content_types(random_count=random_count)
        
        # Guardar resultados
        output_path = tester.save_results()
        
        print(f"\n\n{'='*80}")
        print("✅ PRUEBAS COMPLETADAS")
        print(f"{'='*80}")
        print(f"\n📝 Revisa el archivo {output_path} para ver todos los detalles.")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Pruebas interrumpidas por el usuario")
    except Exception as e:
        print(f"\n\n❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    asyncio.run(main())
