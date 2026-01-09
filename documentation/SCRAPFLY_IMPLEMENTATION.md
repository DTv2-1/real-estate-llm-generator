# 🚀 Guía de Implementación Scrapfly

## ✅ Cambios Implementados

### 1. **Dependencias** (`requirements.txt`)
```bash
scrapfly-sdk==1.1.1
```

### 2. **Configuración** (`config/settings/base.py`)
```python
# Scrapfly API for advanced anti-bot bypass
SCRAPFLY_API_KEY = env('SCRAPFLY_API_KEY', default=None)
SCRAPFLY_ENABLED = env.bool('SCRAPFLY_ENABLED', default=True)
```

### 3. **Scraper Inteligente** (`core/scraping/scraper.py`)

Ahora el scraper elige automáticamente el mejor método:

1. **Scrapfly** → Sitios con Cloudflare (encuentra24.com)
2. **Playwright** → Sitios JS-heavy sin Cloudflare
3. **httpx** → Sitios HTML estáticos

---

## 📦 Instalación

### Paso 1: Instalar dependencias

```bash
cd backend
pip install scrapfly-sdk==1.1.1
```

O instala todas las dependencias:

```bash
pip install -r requirements.txt
```

### Paso 2: Configurar API Key

1. Regístrate en Scrapfly: https://scrapfly.io/register
2. Obtén tu API key del dashboard: https://scrapfly.io/dashboard
3. Agrega a tu archivo `.env`:

```bash
# Scrapfly API
SCRAPFLY_API_KEY=scp-live-YOUR_KEY_HERE
SCRAPFLY_ENABLED=True
```

---

## 🎯 Uso

El scraper funciona igual que antes, pero ahora usa Scrapfly automáticamente para sitios protegidos:

```python
from core.scraping.scraper import WebScraper

scraper = WebScraper()

# Scrapea encuentra24 (usará Scrapfly automáticamente)
result = await scraper.scrape('https://encuentra24.com/...')

# Scrapea Coldwell Banker (usará Playwright o httpx)
result = await scraper.scrape('https://coldwellbanker.cr/...')

print(result['html'])
print(result['method'])  # 'scrapfly', 'playwright', o 'httpx'
print(result.get('api_cost'))  # Costo en credits de Scrapfly
```

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────┐
│ URL Request                                         │
└─────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────┐
│ WebScraper._should_use_scrapfly(url)                │
│ ¿Es encuentra24.com u otro con Cloudflare?          │
└─────────────────────────────────────────────────────┘
        ✅ YES              │              ❌ NO
         ↓                  │                ↓
┌──────────────────┐        │    ┌────────────────────┐
│ Scrapfly API     │        │    │ ¿JS-heavy site?    │
│ - Cloudflare✅   │        │    └────────────────────┘
│ - Residential    │        │       YES │      NO
│ - JS rendering   │        │           ↓      ↓
│ $30/mes          │        │    Playwright  httpx
└──────────────────┘        │    (free)      (free)
         ↓                  │
┌─────────────────────────────────────────────────────┐
│ Scraped HTML → BeautifulSoup → OpenAI → Property    │
└─────────────────────────────────────────────────────┘
```

---

### 💰 Costos

**Plan Discovery: $30/mes**

- 200,000 API credits
- Para Cloudflare bypass: 31 credits/página
- **Capacidad:** 6,451 páginas/mes
- **Tu uso:** ~1,000 páginas/mes = **$30/mes**

---

## 🧪 Testing

### Test 1: Verificar instalación

```bash
python manage.py shell
```

```python
from core.scraping.scraper import WebScraper

scraper = WebScraper()
# Debe mostrar: "🚀 Scrapfly enabled - Anti-bot bypass ready"
```

### Test 2: Scrapear encuentra24

```python
import asyncio
from core.scraping.scraper import WebScraper

async def test():
    scraper = WebScraper()
    result = await scraper.scrape('https://encuentra24.com/costa-rica-es/bienes-raices-venta-casas')
    print(f"Method: {result['method']}")  # Should be 'scrapfly'
    print(f"Cost: {result.get('api_cost')} credits")
    print(f"HTML length: {len(result['html'])} chars")
    return result

result = asyncio.run(test())
```

### Test 3: Verificar que sitios simples no usan Scrapfly

```python
async def test_simple_site():
    scraper = WebScraper()
    result = await scraper.scrape('https://httpbin.org/html')
    print(f"Method: {result['method']}")  # Should be 'httpx' or 'playwright'
    # No debe usar Scrapfly (no gastar credits)
    
asyncio.run(test_simple_site())
```

---

## 🔍 Logs

El scraper loggeará automáticamente qué método usa:

```
🚀 Scrapfly enabled - Anti-bot bypass ready
🛡️ Cloudflare-protected site detected: encuentra24.com
🚀 Using Scrapfly for Cloudflare bypass: https://encuentra24.com/...
✅ Scrapfly success - API cost: 31 credits
```

---

## 🛠️ Troubleshooting

### Error: "Scrapfly SDK not installed"

```bash
pip install scrapfly-sdk
```

### Error: "Invalid API key"

Verifica tu `.env`:
```bash
SCRAPFLY_API_KEY=scp-live-YOUR_ACTUAL_KEY
```

### Error: "Quota limit reached"

Has consumido los 200k credits del mes. Opciones:
1. Espera al próximo ciclo de facturación
2. Upgrade a plan Professional ($75/mes)
3. Desactiva Scrapfly temporalmente:
   ```bash
   SCRAPFLY_ENABLED=False
   ```

### Scrapfly no se usa para encuentra24

Verifica que el dominio esté en la lista:
```python
# core/scraping/scraper.py
CLOUDFLARE_PROTECTED_DOMAINS = [
    'encuentra24.com',  # ✅ Debe estar aquí
]
```

---

## 📊 Monitoreo

### Ver uso actual

Dashboard de Scrapfly: https://scrapfly.io/dashboard/monitoring

### Ver credits restantes

```python
from scrapfly import ScrapflyClient

client = ScrapflyClient(key='YOUR_KEY')
account = client.account()
print(account)
```

---

## 🔐 Seguridad

**Importante:** No commitees tu API key al repositorio.

Verifica que `.env` esté en `.gitignore`:

```bash
# .gitignore
.env
.env.local
*.env
```

---

## 🚀 Deployment

### DigitalOcean App Platform

Agrega la variable de entorno en el dashboard:

1. Ve a Settings → Environment Variables
2. Agrega:
   ```
   SCRAPFLY_API_KEY = scp-live-YOUR_KEY
   SCRAPFLY_ENABLED = true
   ```

3. Redeploy la app

### Docker

En tu `docker-compose.yml`:

```yaml
services:
  backend:
    environment:
      - SCRAPFLY_API_KEY=${SCRAPFLY_API_KEY}
      - SCRAPFLY_ENABLED=true
```

---

## ✨ Features Adicionales

### Screenshot de páginas (gratis con el plan)

```python
scrape_config = ScrapeConfig(
    url=url,
    asp=True,
    render_js=True,
    screenshots={
        'main': 'fullpage'  # Screenshot de página completa
    }
)
```

### Extraer datos con LLM integrado

```python
scrape_config = ScrapeConfig(
    url=url,
    asp=True,
    extraction_prompt="Extract property price, bedrooms, and location"
)
# Scrapfly usará su propio LLM para extraer datos
```

---

## 📚 Documentación Oficial

- Scrapfly Docs: https://scrapfly.io/docs
- Python SDK: https://scrapfly.io/docs/sdk/python
- Pricing: https://scrapfly.io/pricing
- Dashboard: https://scrapfly.io/dashboard

---

## ✅ Checklist de Implementación

- [x] Instalar `scrapfly-sdk` en requirements.txt
- [x] Agregar `SCRAPFLY_API_KEY` a settings
- [x] Implementar `_scrape_with_scrapfly()` método
- [x] Modificar lógica de decisión en `scrape()`
- [ ] **Configurar API key en `.env`**
- [ ] **Instalar dependencias** (`pip install -r requirements.txt`)
- [ ] **Test scraping de encuentra24**
- [ ] **Verificar logs de Scrapfly**
- [ ] **Monitorear uso de credits**
- [ ] **Deploy con variables de entorno**

---

## 🎉 ¡Listo!

Tu scraper ahora usa Scrapfly automáticamente para bypass de Cloudflare.

**Siguiente paso:** Configura tu API key y prueba scrapear encuentra24.com
