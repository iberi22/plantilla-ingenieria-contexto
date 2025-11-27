# Integración con Grok (xAI) - API Gratuita

## ¿Por qué Grok?

Grok es el modelo de IA de xAI (de Elon Musk) que ofrece:
- ✅ **API Gratuita** con tier generoso
- ✅ **Excelente para análisis de código**
- ✅ **Sin cuotas tan restrictivas como Gemini**
- ✅ **Respuestas rápidas y precisas**

## Cómo Obtener Tu API Key

### Paso 1: Crear Cuenta en xAI
1. Ve a https://x.ai
2. Haz clic en "Get API Key" o "Console"
3. Inicia sesión con tu cuenta de X (Twitter)

### Paso 2: Generar API Key
1. En la consola de xAI: https://console.x.ai
2. Ve a "API Keys"
3. Clic en "Create New Key"
4. Copia tu API key (empieza con `xai-...`)

### Paso 3: Configurar en el Proyecto
1. Abre tu archivo `.env`
2. Agrega la línea:
   ```
   XAI_API_KEY=xai-tu-api-key-aqui
   ```
3. Guarda el archivo

## Modelos Disponibles (Gratis)

- `grok-beta` - Modelo principal, rápido y gratuito
- `grok-vision-beta` - Para análisis visual (futuro)

## Límites del Tier Gratuito

- **Requests**: 60 por minuto (muy generoso)
- **Tokens**: 10,000 por minuto
- **Contexto**: 131,072 tokens (muy grande)

Esto es **mucho más generoso que Gemini free tier**.

## Comparación vs Gemini

| Feature | Grok Free | Gemini Free |
|---------|-----------|-------------|
| Requests/min | 60 | 15 |
| Tokens/min | 10,000 | 1,500 |
| Rate limits | Generosos | Muy restrictivos |
| Quota resets | Cada minuto | Diario |

## Uso en el Proyecto

El script `discover_hidden_gems.py` ahora usa Grok automáticamente:

```bash
# Configurar variables de entorno
$env:GITHUB_TOKEN = "tu-token"
$env:XAI_API_KEY = "xai-tu-key"

# Ejecutar pipeline
python scripts/discover_hidden_gems.py small 3
```

## Archivos Modificados

1. **`src/scanner/grok_reviewer.py`** - Nuevo reviewer con Grok API
2. **`scripts/discover_hidden_gems.py`** - Actualizado para usar Grok
3. Ya no usa `src/scanner/ai_reviewer.py` (Gemini)

## Ventajas de la Implementación

- ✅ Retry automático con exponential backoff
- ✅ Manejo robusto de rate limits
- ✅ Parsing inteligente de JSON responses
- ✅ Fallback a scores por defecto si falla
- ✅ Logging detallado para debugging

## Testing

Para probar la integración:

```bash
# Test simple con 1 repo
python scripts/discover_hidden_gems.py small 1

# Pipeline completo
python scripts/discover_hidden_gems.py small 5
```

## Alternativas (si Grok no funciona)

1. **OpenRouter** - Proxy para múltiples modelos, tiene free tier
2. **Claude via API** - Anthropic tiene tier gratuito limitado
3. **Ollama local** - Gratis pero requiere GPU local
4. **HuggingFace Inference API** - Algunos modelos gratuitos

## Troubleshooting

### Error: "No XAI_API_KEY"
- Verifica que el archivo `.env` tiene la key
- Reinicia el terminal para cargar nuevas variables

### Error: 429 Rate Limit
- Grok tiene 60 req/min, es difícil exceder
- El script ya tiene retry automático

### Error: 401 Unauthorized
- Verifica que tu API key es correcta
- Asegúrate que empieza con `xai-`

## Documentación Oficial

- xAI Console: https://console.x.ai
- API Docs: https://docs.x.ai/api
- Pricing: https://x.ai/pricing (Free tier disponible)

