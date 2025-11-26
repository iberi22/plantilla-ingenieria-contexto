# 🚀 Quick Start Guide - Blog & Webhook Setup

**Para poner en marcha el blog y webhook rápidamente**

---

## 📝 Blog (Astro)

### Desarrollar localmente
```bash
cd website
npm install
npm run dev
```
**URL:** http://localhost:4321/bestof-opensorce/

### Crear nuevo post
```bash
# Crear archivo en website/src/content/blog/
# Formato: YYYY-MM-DD-slug.md

# Ejemplo: website/src/content/blog/2025-11-26-my-post.md
---
title: "Mi Post"
date: 2025-11-26
description: "Descripción breve"
tags: [tag1, tag2]
---

## Contenido aquí...
```

### Desplegar
```bash
git add .
git commit -m "feat: Add new blog post"
git push
# GitHub Actions despliega automáticamente
```

---

## 🔗 Webhook (Privado → Público)

### Opción A: Desarrollo Local (5 minutos)

**1. Iniciar servidor webhook:**
```bash
cd bestof-pipeline  # Repo privado
python api/webhook_server.py
```

**2. Exponer con ngrok:**
```bash
# Instalar: https://ngrok.com/download
ngrok http 5001
# Copia la URL HTTPS (ej: https://abc123.ngrok.io)
```

**3. Configurar webhook en GitHub:**
- Ir a: https://github.com/iberi22/bestof-opensorce/settings/hooks
- Click "Add webhook"
- **Payload URL:** `https://abc123.ngrok.io/webhook`
- **Content type:** `application/json`
- **Secret:** Generar con: `openssl rand -hex 32`
- **Events:** Pushes ✅
- Click "Add webhook"

**4. Variables de entorno (.env en repo privado):**
```bash
GITHUB_WEBHOOK_SECRET=tu-secret-generado
GOOGLE_API_KEY=tu-api-key-gemini
GITHUB_TOKEN=tu-pat-token
```

---

### Opción B: Producción (Render.com)

**1. Crear cuenta en Render.com**

**2. Nuevo Web Service:**
- Conectar repo privado: `bestof-pipeline`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn api.webhook_server:app --bind 0.0.0.0:$PORT`

**3. Variables de entorno en Render:**
```
GITHUB_WEBHOOK_SECRET=tu-secret
GOOGLE_API_KEY=tu-gemini-key
GITHUB_TOKEN=tu-pat-token
```

**4. Deploy → Copia la URL del servicio**

**5. Configurar webhook en GitHub:**
- URL: `https://tu-servicio.onrender.com/webhook`
- Secret: El mismo de arriba
- Events: Pushes ✅

---

## 🧪 Probar Todo

**1. Test webhook manualmente:**
```bash
curl -X POST https://tu-webhook-url.com/webhook \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: ping" \
  -d '{"zen": "test"}'

# Respuesta esperada: {"message": "Pong!"}
```

**2. Test automático (push al repo público):**
```bash
cd bestof-opensorce  # Repo público
echo "test" > test.txt
git add test.txt
git commit -m "test: Trigger webhook"
git push
```

**3. Verificar:**
- Ver entrega en GitHub: Settings → Webhooks → Recent Deliveries
- Ver logs del webhook server
- Verificar que se generó contenido

---

## 📊 Flujo Completo

```
1. Investigation Pipeline (cada 4h)
   ↓
2. Actualiza investigations/ en repo público
   ↓
3. Commit → Trigger webhook
   ↓
4. Webhook server (repo privado) recibe POST
   ↓
5. Genera blog posts con Gemini AI
   ↓
6. Commit de vuelta a repo público
   ↓
7. GitHub Actions deploys a GitHub Pages
```

---

## 🔑 Secrets Necesarios

### Repo Público (bestof-opensorce)
- `GH_PAT` - Para disparar workflows en repo privado
  - Crear en: https://github.com/settings/tokens
  - Permisos: `repo`, `workflow`

### Repo Privado (bestof-pipeline)
- `GITHUB_WEBHOOK_SECRET` - Verificar webhooks
  - Generar: `openssl rand -hex 32`
- `GOOGLE_API_KEY` - Gemini AI
  - Obtener: https://makersuite.google.com/app/apikey
- `GH_PAT` - Commit a repo público
  - Mismo token de arriba

---

## 📁 Scripts Útiles

### Migrar investigations a blog posts
```bash
python scripts/migrate_investigations_to_blog.py
```

### Ver status del webhook
```bash
curl https://tu-webhook-url.com/health
```

### Ver jobs en cola
```bash
curl https://tu-webhook-url.com/jobs
```

---

## 🐛 Troubleshooting

### Webhook no responde
```bash
# 1. Verificar que el servidor está corriendo
curl https://tu-webhook-url.com/health

# 2. Verificar en GitHub: Settings → Webhooks → Recent Deliveries
# 3. Ver detalles del error
```

### Blog no se despliega
```bash
# Ver workflow en GitHub
https://github.com/iberi22/bestof-opensorce/actions

# Build local para ver errores
cd website
npm run build
```

### Webhook signature inválida
```bash
# Verificar que el secret coincide:
# - GitHub webhook settings
# - Variable de entorno del servidor
```

---

## 📚 Documentación Completa

- **Webhook:** `docs/WEBHOOK_SETUP_GUIDE.md`
- **Blog:** `docs/BLOG_CONFIGURATION.md`
- **Arquitectura:** `TWO_REPO_ARCHITECTURE.md`
- **Resumen:** `docs/IMPLEMENTATION_SUMMARY.md`

---

## ✅ Checklist

**Blog:**
- [ ] Dev server funciona (`npm run dev`)
- [ ] Puede crear posts manualmente
- [ ] GitHub Pages despliega automáticamente

**Webhook:**
- [ ] Servidor webhook desplegado
- [ ] GitHub webhook configurado
- [ ] Secrets configurados
- [ ] Test ping funciona
- [ ] Test push funciona
- [ ] Content generation funciona

---

**¿Dudas?** Revisa la documentación completa o contacta al mantenedor del repo.

**Last Updated:** 2025-11-26
