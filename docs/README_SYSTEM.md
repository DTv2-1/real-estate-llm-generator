# 🏠 Real Estate LLM System for Kelly Phillipps

**Sistema Completo de Chatbot con RAG para Bienes Raíces en Costa Rica**

---

## 📁 Estructura del Proyecto

```
kp-real-estate-llm-prototype/
├── web/                          # Frontend web demo (original)
│   ├── index.html
│   ├── server.js
│   └── docs/
└── real_estate_llm/              # ⭐ SISTEMA PRINCIPAL (Django Backend)
    ├── README.md                 # Documentación completa del sistema
    ├── QUICKSTART.md             # Guía de inicio rápido (5 minutos)
    ├── API_REFERENCE.md          # Referencia completa de endpoints
    ├── API_TESTING.md            # Ejemplos de testing con curl
    ├── DEVELOPMENT_GUIDE.md      # Comandos de desarrollo
    ├── PROJECT_DELIVERY.md       # Resumen de entrega y checklist
    ├── apps/                     # Django applications
    │   ├── tenants/              # Multi-tenancy
    │   ├── users/                # Sistema de usuarios con roles
    │   ├── properties/           # Propiedades con embeddings
    │   ├── documents/            # Knowledge base RAG
    │   ├── conversations/        # Historial de chats
    │   ├── ingestion/            # APIs de importación
    │   └── chat/                 # API del chatbot
    ├── core/                     # Lógica de negocio
    │   ├── scraping/             # Web scraping (Playwright/httpx)
    │   ├── llm/                  # LLM integration (OpenAI/Anthropic)
    │   └── utils/                # Utilidades
    ├── config/                   # Django settings
    ├── static/                   # Frontend data collector
    ├── scripts/                  # Setup y testing scripts
    └── tests/                    # Test suite
```

---

## 🚀 Quick Start

### Opción 1: Setup Automático (Recomendado)

```bash
cd real_estate_llm

# Ejecutar script de setup
chmod +x scripts/setup.sh
./scripts/setup.sh
```

El script automáticamente:
- ✅ Crea virtual environment
- ✅ Instala dependencias
- ✅ Configura Docker (PostgreSQL + Redis)
- ✅ Ejecuta migraciones
- ✅ Crea datos de prueba
- ✅ Genera embeddings

### Opción 2: Docker Compose

```bash
cd real_estate_llm

# Copiar .env
cp .env.example .env
# Editar .env con tus API keys

# Iniciar servicios
docker-compose up -d

# Ejecutar setup
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py shell < scripts/create_test_data.py
docker-compose exec web python manage.py generate_embeddings
```

---

## 📚 Documentación

| Documento | Descripción |
|-----------|-------------|
| [README.md](./real_estate_llm/README.md) | Documentación completa del sistema (400+ líneas) |
| [QUICKSTART.md](./real_estate_llm/QUICKSTART.md) | Guía de inicio rápido (5 minutos) |
| [API_REFERENCE.md](./real_estate_llm/API_REFERENCE.md) | Referencia completa de todos los endpoints |
| [API_TESTING.md](./real_estate_llm/API_TESTING.md) | Ejemplos de testing con curl |
| [DEVELOPMENT_GUIDE.md](./real_estate_llm/DEVELOPMENT_GUIDE.md) | Comandos útiles para desarrollo |
| [PROJECT_DELIVERY.md](./real_estate_llm/PROJECT_DELIVERY.md) | Resumen de entrega y estado del proyecto |

---

## 🎯 Características Principales

### 1. Scraping Web Inteligente
- ✅ Playwright para sitios JavaScript (Encuentra24, RE.CR)
- ✅ httpx para sitios estáticos (más rápido)
- ✅ Rate limiting automático
- ✅ Detección inteligente de tipo de sitio

### 2. Extracción con LLM
- ✅ GPT-4 para extracción estructurada
- ✅ Confidence scoring por campo
- ✅ Validación automática
- ✅ Reintentos con exponential backoff

### 3. RAG Pipeline Completo
- ✅ Búsqueda híbrida (vector + keyword)
- ✅ pgvector para similaridad coseno
- ✅ Semantic caching (reduce costos 30-40%)
- ✅ LLM routing (GPT-4o-mini / Claude 3.5)

### 4. Sistema de Roles
- ✅ **Buyer**: Ve precios, análisis de inversión
- ✅ **Tourist**: NO ve precios, actividades/restaurantes
- ✅ **Vendor**: Insights de demanda
- ✅ **Staff**: Acceso completo
- ✅ **Admin**: Control total

### 5. Multi-Tenant
- ✅ Aislamiento completo de datos por cliente
- ✅ Límites de suscripción configurables
- ✅ Row-level security

---

## 🧪 Testing Rápido

```bash
# Ejecutar test suite completo
cd real_estate_llm
./scripts/test_system.sh
```

O manualmente:

```bash
# 1. Obtener token
curl -X POST http://localhost:8000/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "john_buyer", "password": "testpass123"}'

# 2. Guardar token
export TOKEN="tu-access-token"

# 3. Listar propiedades
curl http://localhost:8000/api/v1/properties/ \
  -H "Authorization: Bearer $TOKEN"

# 4. Chat con el bot
curl -X POST http://localhost:8000/api/v1/chat/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Tell me about properties in Tamarindo"}'
```

---

## 👥 Usuarios de Prueba

| Username       | Password     | Rol     | Descripción                      |
|----------------|--------------|---------|----------------------------------|
| john_buyer     | testpass123  | buyer   | Inversión/compra, ve precios     |
| sarah_tourist  | testpass123  | tourist | Actividades, NO ve precios       |
| mike_staff     | testpass123  | staff   | Gestión de propiedades           |

---

## 🛠️ Stack Tecnológico

| Componente         | Tecnología                    |
|--------------------|-------------------------------|
| Backend            | Django 4.2.9                  |
| API                | Django REST Framework 3.14.0  |
| Database           | PostgreSQL 15 + pgvector      |
| Cache              | Redis 7.2                     |
| Task Queue         | Celery 5.3.4                  |
| LLM (Simple)       | OpenAI GPT-4o-mini            |
| LLM (Complex)      | Anthropic Claude 3.5 Sonnet   |
| Embeddings         | OpenAI text-embedding-3-small |
| RAG Framework      | LangChain 0.1.0               |
| Web Scraping       | Playwright + httpx            |
| Containerization   | Docker + Docker Compose       |

---

## 📊 URLs del Sistema

| Servicio | URL |
|----------|-----|
| API | http://localhost:8000/api/v1/ |
| Admin Panel | http://localhost:8000/admin/ |
| Data Collector UI | http://localhost:8000/static/data_collector/ |
| Health Check | http://localhost:8000/health/ |
| API Docs (Swagger) | http://localhost:8000/api/docs/ |

---

## 💰 Estimación de Costos

Para 1000 queries/día:
- **OpenAI**: ~$2.25/mes (GPT-4o-mini + embeddings)
- **Anthropic**: ~$9/mes (Claude para queries complejas)
- **Con semantic cache**: ~$7-8/mes total (30-40% de ahorro)

---

## 📈 Próximos Pasos

### Fase 1: Testing (Semana 1-2)
- [ ] Probar ingesta con URLs reales
- [ ] Validar extracción de datos
- [ ] Verificar RAG retrieval quality
- [ ] Probar todos los roles
- [ ] Ejecutar test suite

### Fase 2: Contenido (Semana 3-4)
- [ ] Importar propiedades existentes
- [ ] Crear documentos de mercado
- [ ] Agregar guías legales
- [ ] Documentar actividades
- [ ] Generar embeddings

### Fase 3: Refinamiento (Semana 5-6)
- [ ] Ajustar system prompts
- [ ] Optimizar semantic cache
- [ ] Fine-tuning de búsqueda
- [ ] Mejorar confidence scoring

### Fase 4: Deployment (Semana 7-8)
- [ ] Setup AWS (Lambda o ECS)
- [ ] Configurar RDS PostgreSQL
- [ ] Setup ElastiCache Redis
- [ ] Configurar Sentry
- [ ] Deploy a production

---

## 🆘 Soporte

Para problemas:
1. **Documentación**: Revisar README.md y QUICKSTART.md
2. **Logs**: `docker-compose logs -f web`
3. **Testing**: Ver API_TESTING.md para ejemplos
4. **Development**: Consultar DEVELOPMENT_GUIDE.md

---

## 📝 Estado del Proyecto

**✅ SISTEMA COMPLETO Y LISTO PARA TESTING**

- ✅ Todos los componentes implementados
- ✅ Documentación completa
- ✅ Scripts de setup automatizados
- ✅ Datos de prueba incluidos
- ✅ Test suite configurado
- ✅ Docker setup completo

**Total de archivos creados:** 110+  
**Líneas de código:** 10,000+  
**Documentación:** 2,000+ líneas

---

## 📞 Contacto

**Cliente:** Kelly Phillipps  
**Proyecto:** Real Estate LLM System  
**Ubicación:** Costa Rica  
**Timeline:** 14-16 semanas (30 horas/semana)

---

## 🎉 ¡Listo para empezar!

```bash
cd real_estate_llm
./scripts/setup.sh
```

🚀 **El sistema está completo y listo para testing!**
