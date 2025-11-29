# Generación de Imágenes para el Blog

Esta carpeta contiene scripts para generar imágenes automáticamente para los posts del blog.

## 🆓 Opción 1: Hugging Face (GRATIS)

La opción completamente gratuita usando Hugging Face Inference API.

**Ventajas:**
* **Costo: $0** (completamente gratis)
* Sin límite de imágenes (con rate limits razonables)
* No requiere GPU local ni Docker

**Desventajas:**
* Más lento (20-60 segundos por imagen)
* Puede tardar si el modelo no está cargado

### Configuración (Opción Gratis)

1. **Obtener Token de Hugging Face:**
   * Ve a: <https://huggingface.co/settings/tokens>
   * Crea una cuenta (es gratis)
   * Genera un token (Read access es suficiente)

2. **Configurar el Token:**

   ```powershell
   $env:HUGGINGFACE_TOKEN='tu-token-aqui'
   ```

3. **Generar imágenes:**

   ```powershell
   python image-generation/generate_blog_images_free.py
   ```

---

## ⚡ Opción 2: Replicate API (Económico, Más Rápido)

La forma más rápida con costo mínimo usando Flux.1 [schnell].

**Ventajas:**

* Costo: **~$0.003 USD por imagen** (1000 imágenes = $3 USD)
* Velocidad: 5-10 segundos por imagen
* Mayor calidad que SDXL

### Configuración

1. **Obtener API Token:**
   * Ve a: <https://replicate.com/account/api-tokens>
   * Crea una cuenta (tienen créditos gratis al inicio)
   * Copia tu token

2. **Configurar el Token:**

   ```powershell
   $env:REPLICATE_API_TOKEN='tu-token-aqui'
   ```

3. **Instalar dependencias:**

   ```powershell
   pip install requests
   ```

4. **Generar imágenes para todos los posts:**

   ```powershell
   python image-generation/generate_blog_images.py
   ```

   Esto escaneará todos los posts en `website/src/content/blog/` y generará imágenes en `website/public/images/blog/`.

### Uso Avanzado

```powershell
# Regenerar todas las imágenes (incluso las existentes)
python image-generation/generate_blog_images.py --force
```

---

## 🐳 Opción 3: Docker + GPU (Avanzado)

Si prefieres generar localmente y tienes GPU NVIDIA, revisa `NVIDIA_GPU_SETUP.md` para la configuración completa.

**Nota:** Requiere configuración adicional en Windows/WSL2 y es más lento en CPU.
