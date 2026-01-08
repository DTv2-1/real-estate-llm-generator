# 🤖 PLAN: Chatbot RAG con Propiedades Reales

**Fecha**: 7 de enero de 2026  
**Objetivo**: Hacer funcionar el chatbot con propiedades reales (local testing + deployment en nube)  
**Duración Estimada**: 4-6 horas  
**Nota**: PostgreSQL ya está en DigitalOcean, backend se desplegará en nube después de testing local

---

## 📊 Estado Actual del Sistema

### ✅ Ya Existe (Implementado):

1. **RAG Pipeline** (`core/llm/rag.py`)
   - Hybrid search (vector + keyword)
   - Semantic caching
   - Role-based filtering
   - LLM routing (GPT-4o-mini / Claude 3.5 Sonnet)

2. **Modelos de Base de Datos**
   - `Property` model con campo `embedding` (pgvector)
   - `Document` model para knowledge base
   - Multi-tenant support

3. **Chat API** (`apps/chat/views.py`)
   - Endpoint POST `/chat`
   - Conversation tracking
   - Message history

4. **Management Command**
   - `generate_embeddings.py` para indexar propiedades

5. **Script de Test Data**
   - `scripts/create_test_data.py` con 3 propiedades mock

### ❌ Lo que Falta:

1. **Propiedades Reales**: Solo hay 3 propiedades mock en DB
2. **Embeddings Generados**: Propiedades no tienen embeddings
3. **Documents para Propiedades**: No hay Documents vinculados a Properties
4. **Frontend del Chatbot**: No hay interface web para probar
5. **Testing del Flujo Completo**: No se ha probado end-to-end

---

## 🎯 PLAN DE IMPLEMENTACIÓN (5 Fases)

---

## **FASE 1: Preparar Base de Datos (DigitalOcean)** ⏱️ 30 minutos

### Objetivo:
Conectar Django local a PostgreSQL en DigitalOcean con estructura correcta

### Pasos:

#### 1.1 Verificar PostgreSQL en DigitalOcean
```bash
# La base de datos PostgreSQL ya está en DigitalOcean con pgvector
# Verificar conexión desde local:
psql "postgresql://user:pass@host:25060/dbname?sslmode=require"

# Verificar extensión pgvector (ya debe estar instalada)
\dx

# Si no existe pgvector (raro, pero por si acaso):
CREATE EXTENSION IF NOT EXISTS vector;
```

#### 1.2 Configurar Django Database Settings
```python
# config/settings/local.py (debe apuntar a DigitalOcean):
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),  # DigitalOcean host
        'PORT': os.getenv('DB_PORT', '25060'),
        'OPTIONS': {
            'sslmode': 'require',  # Importante para DigitalOcean
        }
    }
}
```

#### 1.2b Crear/Verificar .env file
```bash
# .env (raíz del proyecto):
DB_NAME=real_estate_prod
DB_USER=doadmin
DB_PASSWORD=<tu_password>
DB_HOST=<tu_host>.db.ondigitalocean.com
DB_PORT=25060

OPENAI_API_KEY=sk-proj-...
ANTHROPIC_API_KEY=sk-ant-...
```

#### 1.3 Correr Migraciones
```bash
### ✅ Checklist Fase 1:
- [ ] Conexión a PostgreSQL DigitalOcean funcionando
- [ ] .env configurado con credenciales DigitalOcean
- [ ] Extensión pgvector verificada
- [ ] Migraciones aplicadas en DB cloud
- [ ] Superuser creado (o usar existente)

#### 1.4 Crear Superuser
```bash
python manage.py createsuperuser
# Username: admin
# Email: admin@example.com
# Password: admin123
```

### ✅ Checklist Fase 1:
- [ ] PostgreSQL corriendo
- [ ] Extensión pgvector instalada
- [ ] Migraciones aplicadas
- [ ] Superuser creado

---
## **FASE 2: Recolectar Propiedades Reales** ⏱️ 1-2 horas

### Objetivo:
Tener 10-20 propiedades reales de Costa Rica en la base de datos DigitalOcean

### Opción A: Manual via Data Collector (Recomendado para testing)

#### 2.1 Levantar Backend Django Local (conectado a DB cloud)
```bash
# Django local se conecta a PostgreSQL en DigitalOcean
python manage.py runserver
```

#### 2.2 Abrir Data Collector
```
http://localhost:8000/static/data_collector/index.html
```

**Nota**: Los datos se guardarán directamente en PostgreSQL de DigitalOcean, así cuando despliegues el backend, los datos ya estarán ahí.p://localhost:8000/static/data_collector/index.html
```

#### 2.3 Ingresar Propiedades Manualmente
Buscar URLs reales de:
- https://www.encuentra24.com/costa-rica-en/bienes-raices-venta
- https://www.coldwellbankercostarica.com/property/search
- https://crrealestate.com/property-search/

**Propiedades sugeridas para diversidad:**
1. Villa de playa en Tamarindo ($400K+)
2. Casa en Manuel Antonio ($300K-400K)
3. Condo en San José ($150K-250K)
4. Lote en Nosara ($100K-200K)
5. Casa de montaña en Atenas ($200K-300K)
6. Apartamento en Jacó ($150K-200K)
7. Propiedad comercial en Liberia ($500K+)
8. Casa de retiro en Uvita ($250K-350K)
9. Villa moderna en Guanacaste ($600K+)
10. Condo frente al mar en Puntarenas ($180K-280K)

#### Proceso por cada propiedad:
1. Copiar URL de la propiedad
2. Pegar en Data Collector
3. Click "Extract & Save"
4. Verificar que se guardó correctamente

### Opción B: Usar Script Python para Bulk Import

**Si tienes tiempo, puedes crear un CSV con propiedades y usar script:**

```python
# scripts/import_properties_csv.py (crear nuevo)

import csv
from apps.properties.models import Property
from apps.tenants.models import Tenant

def import_from_csv(csv_file):
    tenant = Tenant.objects.first()
    
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            Property.objects.create(
                tenant=tenant,
                property_name=row['name'],
                price_usd=row['price'],
                bedrooms=row['bedrooms'],
                bathrooms=row['bathrooms'],
                location=row['location'],
                description=row['description'],
                # ... más campos
            )
```

### ✅ Checklist Fase 2:
- [ ] Backend Django corriendo
- [ ] Data Collector accesible
- [ ] 10-20 propiedades reales ingresadas
- [ ] Propiedades verificadas en Django Admin

---

## **FASE 3: Generar Embeddings e Indexar** ⏱️ 30 minutos

### Objetivo:
Todas las propiedades tienen embeddings y están en vector store

### 3.1 Verificar Variables de Entorno
```bash
# .env file (verificar):
OPENAI_API_KEY=sk-proj-...
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

### 3.2 Generar `content_for_search` para Properties

Primero verificar que el modelo Property tenga el método:

```python
# apps/properties/models.py (debe existir):

def generate_search_content(self):
    """Generate searchable text content for this property."""
    
    parts = []
    
    # Basic info
    parts.append(f"Property: {self.property_name}")
    parts.append(f"Price: ${self.price_usd:,.0f} USD")
    parts.append(f"Location: {self.location}")
    parts.append(f"Type: {self.get_property_type_display()}")
    
    # Rooms
    if self.bedrooms:
        parts.append(f"{self.bedrooms} bedrooms")
    if self.bathrooms:
        parts.append(f"{self.bathrooms} bathrooms")
    
    # Size
    if self.square_meters:
        parts.append(f"{self.square_meters} m²")
    
    # Description
    if self.description:
        parts.append(f"Description: {self.description}")
    
    # Amenities
    if self.amenities:
        parts.append(f"Amenities: {', '.join(self.amenities)}")
    
    return "\n".join(parts)
```

### 3.3 Correr Management Command
```bash
# Generar embeddings para todas las propiedades
python manage.py generate_embeddings --properties

# Output esperado:
# Generating property embeddings...
# Properties: 100%|██████████| 15/15 [00:45<00:00,  3.05s/it]
# ✓ Generated embeddings for 15 properties
```

### 3.4 Crear Documents Vinculados a Properties

**IMPORTANTE**: El RAG busca en la tabla `Document`, no directamente en `Property`.

Necesitamos crear Documents que apunten a Properties:

```bash
# Crear management command nuevo:
python manage.py create_property_documents
```

Este comando debe:
1. Para cada Property
2. Crear un Document con:
   - `content` = Property.content_for_search
   - `embedding` = Property.embedding
   - `content_type` = 'property'
   - `metadata` = {property_id, url, etc}
   - `user_roles` = Property.user_roles

### 3.5 Verificar en Django Admin

```bash
# Abrir admin
http://localhost:8000/admin/

# Verificar:
1. Properties tienen `embedding` != NULL
2. Documents existen con content_type='property'
3. Documents tienen embeddings
```

### ✅ Checklist Fase 3:
- [ ] Variable OPENAI_API_KEY configurada
- [ ] Embeddings generados (Property.embedding != NULL)
- [ ] Documents creados para cada Property
- [ ] Verificado en Django Admin

---

## **FASE 4: Crear Frontend Simple del Chatbot** ⏱️ 1-2 horas

### Objetivo:
Interface web para probar el chatbot en navegador

### 4.1 Crear HTML del Chatbot

Archivo: `web/chat.html` (crear nuevo)

```html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kelly Properties - Chatbot</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        
        .chat-container {
            width: 90%;
            max-width: 800px;
            height: 80vh;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        .chat-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
        }
        
        .chat-messages {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        
        .message {
            display: flex;
            gap: 10px;
            max-width: 80%;
        }
        
        .message.user {
            align-self: flex-end;
            flex-direction: row-reverse;
        }
        
        .message-avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: #667eea;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            flex-shrink: 0;
        }
        
        .message-content {
            padding: 12px 16px;
            border-radius: 18px;
            line-height: 1.5;
        }
        
        .message.user .message-content {
            background: #667eea;
            color: white;
        }
        
        .message.assistant .message-content {
            background: #f1f3f5;
            color: #333;
        }
        
        .chat-input-container {
            padding: 20px;
            border-top: 1px solid #e1e8ed;
            display: flex;
            gap: 10px;
        }
        
        .chat-input {
            flex: 1;
            padding: 12px 16px;
            border: 2px solid #e1e8ed;
            border-radius: 25px;
            font-size: 14px;
            outline: none;
        }
        
        .chat-input:focus {
            border-color: #667eea;
        }
        
        .send-button {
            padding: 12px 24px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-weight: 600;
            transition: transform 0.2s;
        }
        
        .send-button:hover {
            transform: scale(1.05);
        }
        
        .send-button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .loading {
            display: flex;
            gap: 5px;
            padding: 10px;
        }
        
        .loading span {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #667eea;
            animation: bounce 1.4s infinite ease-in-out both;
        }
        
        .loading span:nth-child(1) { animation-delay: -0.32s; }
        .loading span:nth-child(2) { animation-delay: -0.16s; }
        
        @keyframes bounce {
            0%, 80%, 100% { transform: scale(0); }
            40% { transform: scale(1); }
        }
        
        .sources {
            margin-top: 10px;
            padding-top: 10px;
            border-top: 1px solid #e1e8ed;
            font-size: 12px;
            color: #666;
        }
        
        .source-item {
            margin-top: 5px;
            padding: 5px;
            background: #f8f9fa;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <h1>🏡 Kelly Properties Assistant</h1>
            <p>Pregúntame sobre propiedades en Costa Rica</p>
        </div>
        
        <div class="chat-messages" id="messages">
            <div class="message assistant">
                <div class="message-avatar">K</div>
                <div class="message-content">
                    ¡Hola! Soy tu asistente de propiedades. Puedo ayudarte a encontrar 
                    la casa perfecta en Costa Rica. ¿Qué estás buscando?
                </div>
            </div>
        </div>
        
        <div class="chat-input-container">
            <input 
                type="text" 
                class="chat-input" 
                id="messageInput" 
                placeholder="Escribe tu pregunta aquí..."
                onkeypress="handleKeyPress(event)"
            >
            <button class="send-button" id="sendButton" onclick="sendMessage()">
                Enviar
            </button>
        </div>
    </div>
    
    <script>
        let conversationId = null;
        
        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        }
        
        async function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            
            if (!message) return;
            
            // Add user message to UI
            addMessage('user', message);
            input.value = '';
            
            // Disable input while processing
            const sendButton = document.getElementById('sendButton');
            sendButton.disabled = true;
            input.disabled = true;
            
            // Show loading
            const loadingId = addLoading();
            
            try {
                const response = await fetch('http://localhost:8000/api/v1/chat/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer YOUR_TOKEN_HERE'  // TODO: Implement auth
                    },
                    body: JSON.stringify({
                        message: message,
                        conversation_id: conversationId
                    })
                });
                
                const data = await response.json();
                
                // Save conversation ID
                if (data.conversation_id) {
                    conversationId = data.conversation_id;
                }
                
                // Remove loading
                removeLoading(loadingId);
                
                // Add assistant response
                addMessage('assistant', data.response, data.sources);
                
            } catch (error) {
                console.error('Error:', error);
                removeLoading(loadingId);
                addMessage('assistant', 'Lo siento, hubo un error. Por favor intenta de nuevo.');
            }
            
            // Re-enable input
            sendButton.disabled = false;
            input.disabled = false;
            input.focus();
        }
        
        function addMessage(role, content, sources = null) {
            const messagesDiv = document.getElementById('messages');
            
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${role}`;
            
            const avatar = document.createElement('div');
            avatar.className = 'message-avatar';
            avatar.textContent = role === 'user' ? 'U' : 'K';
            
            const contentDiv = document.createElement('div');
            contentDiv.className = 'message-content';
            contentDiv.textContent = content;
            
            // Add sources if available
            if (sources && sources.length > 0) {
                const sourcesDiv = document.createElement('div');
                sourcesDiv.className = 'sources';
                sourcesDiv.innerHTML = '<strong>Fuentes:</strong>';
                
                sources.forEach(source => {
                    const sourceItem = document.createElement('div');
                    sourceItem.className = 'source-item';
                    sourceItem.textContent = `📄 ${source.content_type} (relevancia: ${source.relevance_score})`;
                    sourcesDiv.appendChild(sourceItem);
                });
                
                contentDiv.appendChild(sourcesDiv);
            }
            
            messageDiv.appendChild(avatar);
            messageDiv.appendChild(contentDiv);
            messagesDiv.appendChild(messageDiv);
            
            // Scroll to bottom
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
        
        function addLoading() {
            const messagesDiv = document.getElementById('messages');
            
            const loadingDiv = document.createElement('div');
            loadingDiv.className = 'message assistant';
            loadingDiv.id = 'loading-' + Date.now();
            
            const avatar = document.createElement('div');
            avatar.className = 'message-avatar';
            avatar.textContent = 'K';
            
            const contentDiv = document.createElement('div');
            contentDiv.className = 'message-content';
            
            const loadingAnim = document.createElement('div');
            loadingAnim.className = 'loading';
            loadingAnim.innerHTML = '<span></span><span></span><span></span>';
            
            contentDiv.appendChild(loadingAnim);
            loadingDiv.appendChild(avatar);
            loadingDiv.appendChild(contentDiv);
            messagesDiv.appendChild(loadingDiv);
            
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
            
            return loadingDiv.id;
        }
        
        function removeLoading(loadingId) {
            const loadingDiv = document.getElementById(loadingId);
            if (loadingDiv) {
                loadingDiv.remove();
            }
        }
    </script>
</body>
</html>
```

### 4.2 Configurar CORS en Django

```python
# config/settings/local.py (agregar):

CORS_ALLOWED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]

CORS_ALLOW_CREDENTIALS = True
```

### 4.3 Crear Token de Autenticación Temporal

Para simplificar testing, deshabilitar auth temporalmente:

```python
# apps/chat/views.py (modificar):

class ChatView(APIView):
    # permission_classes = [IsAuthenticated]  # Comentar temporalmente
    permission_classes = []  # Permitir acceso sin auth para testing
```

### ✅ Checklist Fase 4:
- [ ] HTML del chatbot creado
- [ ] CORS configurado
- [ ] Auth deshabilitado temporalmente
- [ ] Chatbot accesible en navegador

---

## **FASE 5: Testing y Validación** ⏱️ 1 hora

### Objetivo:
Probar que todo el flujo funciona end-to-end

### 5.1 Test Cases Básicos

```
1. Query Simple:
   Pregunta: "¿Propiedades en Tamarindo?"
   Esperado: Lista de propiedades en esa ubicación

2. Query con Filtros:
   Pregunta: "Casas con 3 cuartos bajo $300K"
   Esperado: Propiedades que cumplan criterios

3. Query sobre Propiedad Específica:
   Pregunta: "¿Villa Mar tiene piscina?"
   Esperado: Información específica de esa propiedad

4. Query de Información General:
   Pregunta: "¿Cómo es el proceso de compra en Costa Rica?"
   Esperado: Respuesta general (si hay documento sobre esto)

5. Query Multi-Turn:
   Pregunta 1: "¿Propiedades de playa?"
   Respuesta: [Lista de propiedades]
   Pregunta 2: "¿Cuál es la más barata?"
   Esperado: Referencia a la conversación anterior
```

### 5.2 Verificar Logs

```bash
# Terminal donde corre Django
# Debes ver:
[INFO] Processing query for user anonymous
[INFO] Vector search found 5 documents
[INFO] Keyword search found 3 documents
[INFO] Using simple_llm (GPT-4o-mini) for query
```

### 5.3 Métricas a Observar

```
1. Latencia:
   - Primera query: ~2-3 segundos (sin cache)
   - Queries subsecuentes: ~1-2 segundos (con cache)

2. Relevancia:
   - Sources relevance_score > 0.7 = bueno
   - Sources relevance_score < 0.5 = revisar embeddings

3. Costos:
   - Embedding generation: ~$0.02 por 100 propiedades
   - Query (GPT-4o-mini): ~$0.001 por query
   - Query (Claude): ~$0.01 por query compleja
```

### 5.4 Troubleshooting Común

#### Problema: "No documents found"
```bash
# Verificar que Documents existen:
python manage.py shell
>>> from apps.documents.models import Document
>>> Document.objects.count()
# Debe ser > 0

# Verificar embeddings:
>>> Document.objects.filter(embedding__isnull=False).count()
# Debe ser igual al total
```

#### Problema: "Responses are generic"
```bash
# Verificar que el RAG encuentra documentos relevantes:
# Ver logs de Django

# Si relevance_score < 0.5:
# 1. Regenerar embeddings
# 2. Verificar que content_for_search tenga información rica
```

#### Problema: "CORS error"
```bash
# Verificar settings:
CORS_ALLOWED_ORIGINS en local.py

# Verificar middleware:
'corsheaders.middleware.CorsMiddleware' en MIDDLEWARE
```

### ✅ Checklist Fase 5:
- [ ] 5 test cases ejecutados
- [ ] Respuestas son relevantes
- [ ] Sources incluyen propiedades correctas
- [ ] Latencia < 3 segundos
- [ ] No hay errores en logs
## 📈 PRÓXIMOS PASOS (Post-Testing)

### Deployment en Nube:
1. **Desplegar Backend Django a DigitalOcean**
   ```bash
   git push origin main
   # DigitalOcean App Platform autodeploys desde GitHub
   ```

2. **Desplegar Frontend Chatbot**
   - Opción A: Static site en DigitalOcean
   - Opción B: Vercel/Netlify (gratis)
   - Actualizar API URL de `localhost:8000` a `https://tu-app.ondigitalocean.app`

3. **Variables de Entorno en DigitalOcean**
   - OPENAI_API_KEY
   - ANTHROPIC_API_KEY
   - DB_* (ya configuradas)

### Mejoras Corto Plazo:
1. **Re-habilitar Autenticación** en ChatView
2. **Agregar más propiedades** (objetivo: 50+ propiedades)
3. **Crear Documents de contexto**:
   - Proceso de compra en Costa Rica
   - Información legal
   - Guías de ubicaciones
4. **Implementar feedback loop**: Botón "👍 👎" en respuestas

### Integración con Apify:
4. **Implementar feedback loop**: Botón "👍 👎" en respuestas

### Integración con Apify:
1. Modificar `views_apify_sync.py` para que después de guardar Property:
   ```python
   # Generar embedding automáticamente
   embedding = embeddings.embed_query(property.content_for_search)
   property.embedding = embedding
## 🎯 RESUMEN EJECUTIVO

### Tiempo Total: 4-6 horas (testing local) + 30 min (deployment)
- Fase 1: 30 min (Conectar a DB DigitalOcean)
- Fase 2: 1-2 hrs (Ingresar propiedades)
- Fase 3: 30 min (Generar embeddings)
- Fase 4: 1-2 hrs (Frontend chatbot)
- Fase 5: 1 hr (Testing local)
- **Deployment**: 30 min (Push a DigitalOcean)

### Resultado Final:
✅ Chatbot funcional con propiedades reales de Costa Rica  
✅ Interface web para testing local  
✅ RAG pipeline operativo  
✅ **Datos en PostgreSQL cloud** (persistentes)  
✅ **Listo para deployment** (solo push a GitHub)  
✅ Base para integración con Apify  

### Métricas de Éxito:
- 10-20 propiedades indexadas en DB cloud
- Tiempo de respuesta < 3 seg
- Relevance score > 0.7
- 5 test cases pasados
## 🚀 ¿Listo para Empezar?

**Siguiente acción inmediata**: Ejecutar Fase 1 (Conectar a DB DigitalOcean)

```bash
# Comando para verificar que todo esté listo:
psql --version && python --version && which python

# Verificar conexión a DigitalOcean:
psql "postgresql://user:pass@host:25060/dbname?sslmode=require"
```

### Ventajas de este Enfoque:

✅ **Testing local** con datos reales en cloud  
✅ **Datos persisten** (no se pierden al redesplegar)  
✅ **Deployment simple**: Solo `git push` y DigitalOcean redeploy automático  
✅ **Mismo DB** para desarrollo y producción (menos bugs)  
✅ **Embeddings generados una vez**, disponibles inmediatamente en producción  

¿Empezamos con la Fase 1?ropiedades reales de Costa Rica  
✅ Interface web para testing  
✅ RAG pipeline operativo  
✅ Base para integración con Apify  

### Métricas de Éxito:
- 10-20 propiedades indexadas
- Tiempo de respuesta < 3 seg
- Relevance score > 0.7
- 5 test cases pasados

---

## 🚀 ¿Listo para Empezar?

**Siguiente acción inmediata**: Ejecutar Fase 1 (Setup DB)

```bash
# Comando para verificar que todo esté listo:
psql --version && python --version && which python
```

¿Empezamos con la Fase 1?
