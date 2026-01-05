# 🏠 Real Estate LLM - React Version

Mucho más simple y flexible que Streamlit. React + Node.js.

## 🚀 Inicio Rápido

### 1. Instalar dependencias

```bash
cd web
npm install
```

### 2. Iniciar el backend

```bash
npm start
```

El servidor corre en `http://localhost:3001`

### 3. Abrir el frontend

Abre `index.html` en tu navegador, o usa:

```bash
open index.html
```

## ✨ Características

- ✅ **React puro** - Sin compilación, sin complejidad
- ✅ **Backend simple** - Express + OpenAI
- ✅ **Sin keys duplicadas** - React maneja el estado correctamente
- ✅ **Diseño moderno** - Gradientes, animaciones, responsive
- ✅ **21 escenarios** - Organizados por categoría
- ✅ **Click para cargar** - Un botón, todos los campos llenos
- ✅ **Métricas en tiempo real** - Palabras, tiempo, ahorro

## 📁 Estructura

```
web/
├── index.html       # Frontend React (abre en navegador)
├── server.js        # Backend Node.js + OpenAI
├── package.json     # Dependencias
└── README.md        # Este archivo
```

## 🔑 API Key

Usa el mismo `.env` que ya tienes en la raíz del proyecto:

```
OPENAI_API_KEY=sk-proj-...
```

## 💡 Ventajas vs Streamlit

| Feature | Streamlit | React |
|---------|-----------|-------|
| **Keys duplicadas** | ❌ Problema común | ✅ Sin problemas |
| **Personalización** | ❌ Limitado | ✅ Total libertad |
| **Performance** | ⚠️ Lento | ✅ Rápido |
| **Deploy** | ⚠️ Complejo | ✅ Simple |
| **Debugging** | ❌ Difícil | ✅ DevTools |

## 📝 Uso

1. **Selecciona un escenario** del sidebar (click en cualquier botón)
2. **Todos los campos se llenan automáticamente**
3. **Click en "🚀 Generate Response"**
4. **Espera 3-5 segundos**
5. **Copia la respuesta** y personaliza

## 🛠️ Desarrollo

### Hot reload (auto-restart en cambios)

```bash
npm install -g nodemon
npm run dev
```

### Logs en terminal

Todos los logs del backend aparecen en la terminal donde ejecutas `npm start`.

## 🌐 Deploy (Opcional)

### Vercel (Frontend)

```bash
vercel deploy index.html
```

### Railway (Backend)

```bash
railway init
railway up
```

O simplemente corre local - funciona perfecto.

---

**¡Listo para usar! Sin complicaciones de Streamlit.** 🚀
