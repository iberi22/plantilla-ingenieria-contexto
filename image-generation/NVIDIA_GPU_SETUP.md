# Configuración de GPU NVIDIA en Docker (Windows/WSL2)

El error que obtuviste indica que Docker no encuentra el adaptador de GPU en WSL2. Aquí está la solución:

## Pasos para habilitar GPU en Docker Desktop (Windows)

1. **Actualizar Docker Desktop:**
   - Asegúrate de tener Docker Desktop 4.20+ instalado.
   - Ve a Settings → Resources → WSL Integration → Habilita tu distribución de WSL.

2. **Instalar el driver NVIDIA para WSL2:**
   - Descarga el driver desde: https://developer.nvidia.com/cuda/wsl
   - **Importante:** NO instales el CUDA Toolkit dentro de WSL, solo el driver de Windows.

3. **Verificar que WSL detecta la GPU:**
   ```bash
   wsl nvidia-smi
   ```
   Deberías ver tu GPU listada.

4. **Usar el `docker-compose.yml` original:**
   Una vez configurado, usa:
   ```bash
   docker-compose up -d
   ```

## Alternativa Rápida: Usar CPU (Ya configurado)

Si solo necesitas generar pocas imágenes de prueba, puedes usar la versión CPU:

```bash
docker-compose -f docker-compose-cpu.yml up -d
```

**Nota:** La generación con CPU será **mucho más lenta** (5-10 minutos por imagen vs 10-30 segundos con GPU).

## Alternativa Recomendada: API Externa

Para producción, te recomiendo usar una API externa como **Replicate** con Flux Schnell:
- Costo: ~$0.003 USD por imagen
- Velocidad: 5-10 segundos
- Sin complicaciones de infraestructura

Código de ejemplo:
```python
import replicate
import os

os.environ["REPLICATE_API_TOKEN"] = "tu-token-aqui"

output = replicate.run(
    "black-forest-labs/flux-schnell",
    input={
        "prompt": "Modern tech blog header image, minimalist, dark theme",
        "num_outputs": 1,
        "aspect_ratio": "16:9"
    }
)
print(output[0])  # URL de la imagen generada
```
