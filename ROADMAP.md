# 🗺️ Roadmap de Implementación - Próximas Tareas

**Fecha de Actualización:** 25 de noviembre de 2025
**Estado Actual:** 87% - Staging Ready
**Objetivo:** 100% Production Ready en 1 semana

---

## 🎯 Sprint 1: Correcciones Críticas (Días 1-2)
**Objetivo:** Resolver blockers para producción

### Prioridad ALTA 🔴

#### 1. Fix Dependencias Faltantes
**Issue:** Tests de voice_translation fallan por `sentencepiece` no instalado

**Archivos afectados:**
- `requirements.txt`
- `tests/test_voice_translation.py`

**Tareas:**
- [ ] Agregar `sentencepiece>=0.1.99` a `requirements.txt`
- [ ] Verificar instalación: `pip install sentencepiece`
- [ ] Correr tests: `pytest tests/test_voice_translation.py -v`
- [ ] Actualizar `QUICKSTART.md` con dependencia nueva

**Tiempo estimado:** 2 horas
**Responsable:** Backend Team

---

#### 2. Corregir Imports en Tests
**Issue:** `test_voice_translation.py` usa imports incorrectos

**Problema actual:**
```python
from video_generator.voice_translation import ...  # ❌ Falla
```

**Solución:**
```python
from src.video_generator.voice_translation import ...  # ✅ Correcto
```

**Tareas:**
- [ ] Refactorizar todos los imports en `tests/test_voice_translation.py`
- [ ] Verificar que TTS y Whisper se mockean correctamente
- [ ] Agregar docstring explicando el mock strategy

**Tiempo estimado:** 3 horas
**Responsable:** QA Team

---

#### 3. Implementar Queue para Webhooks
**Issue:** `webhook_server.py` usa `subprocess.Popen` (no escalable)

**Solución propuesta:**
Opción A (Simple): **RQ (Redis Queue)**
```python
from redis import Redis
from rq import Queue

redis_conn = Redis()
q = Queue(connection=redis_conn)

@app.route('/webhook', methods=['POST'])
def github_webhook():
    # ...
    job = q.enqueue('scripts.run_pipeline.main', repo_url=repo_url)
    return jsonify({"job_id": job.id}), 202
```

Opción B (Producción): **Celery + Redis**
```python
from celery import Celery

celery = Celery('tasks', broker='redis://localhost:6379/0')

@celery.task
def run_pipeline_task(repo_url):
    subprocess.run(['python', 'scripts/run_pipeline.py', '--repo', repo_url])
```

**Tareas:**
- [ ] Decidir entre RQ o Celery
- [ ] Instalar Redis: `docker run -d -p 6379:6379 redis`
- [ ] Refactorizar `webhook_server.py` con queue
- [ ] Agregar endpoint `/jobs/<job_id>` para status
- [ ] Actualizar `DEPLOYMENT.md` con setup de Redis

**Tiempo estimado:** 1 día
**Responsable:** DevOps Team

---

### Prioridad MEDIA 🟡

#### 4. Refactorizar Tests de Image Generator
**Issue:** Mocks fallan porque `FoundryLocalManager` se importa dinámicamente

**Solución:**
```python
# En src/image_gen/image_generator.py
try:
    from foundry_local import FoundryLocalManager
    FOUNDRY_AVAILABLE = True
except ImportError:
    FoundryLocalManager = None
    FOUNDRY_AVAILABLE = False

class ImageGenerator:
    def __init__(self, model_name="nano-banana-2", output_dir="output/images"):
        if not FOUNDRY_AVAILABLE:
            raise ImportError("Install foundry-local-sdk")
        # ...
```

**Tareas:**
- [ ] Refactorizar `image_generator.py` con flag `FOUNDRY_AVAILABLE`
- [ ] Actualizar todos los tests en `test_image_gen.py`
- [ ] Agregar test para caso de ImportError
- [ ] Verificar que 6/6 tests pasen

**Tiempo estimado:** 4 horas
**Responsable:** Backend Team

---

#### 5. Fix Test End-to-End
**Issue:** `test_reel_creation_flow` no valida correctamente la composición

**Problema:**
```python
self.assertTrue(mock_concat.called)  # Falla porque mock está mal configurado
```

**Solución:**
- Usar `vcr.py` para grabar responses reales de APIs
- O refactorizar para validar el output file en lugar de mocks internos

**Tareas:**
- [ ] Analizar por qué `mock_concat` no se llama
- [ ] Decidir estrategia: vcr.py o test sobre archivo real
- [ ] Implementar test mejorado
- [ ] Agregar fixtures para audio/imágenes de test

**Tiempo estimado:** 6 horas
**Responsable:** QA Team

---

## 🚀 Sprint 2: Optimización y Calidad (Días 3-5)

### Prioridad MEDIA 🟡

#### 6. Conectar Dashboard con Firebase
**Issue:** Dashboard muestra placeholder data

**Tareas:**
- [ ] Crear endpoint `/api/status` que consulte Firebase
- [ ] Query a colección `repos` por fecha descendente
- [ ] Agregar campos: `status`, `created_at`, `video_url`, `error`
- [ ] Actualizar `Dashboard.jsx` para mostrar datos reales
- [ ] Agregar auto-refresh cada 10s

**Tiempo estimado:** 1 día
**Responsable:** Frontend + Backend

---

#### 7. Validación End-to-End Manual
**Objetivo:** Probar flujo completo en staging

**Checklist:**
- [ ] Levantar ambiente: `docker-compose up`
- [ ] Trigger webhook con repo de prueba
- [ ] Verificar:
  - [ ] Scanner detecta repo
  - [ ] Blog post se crea en `blog/_posts/`
  - [ ] Imágenes se generan en `blog/assets/images/`
  - [ ] Video se crea en `blog/assets/videos/`
  - [ ] (Opcional) Video se sube a YouTube
- [ ] Documentar cualquier error encontrado
- [ ] Crear issues para bugs críticos

**Tiempo estimado:** 1 día
**Responsable:** QA Lead

---

#### 8. Implementar Retry Logic
**Issue:** Pipeline falla silenciosamente si API da error temporal

**Solución:**
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def generate_with_retry(prompt):
    return gemini_api.generate(prompt)
```

**Tareas:**
- [ ] Agregar `tenacity` a `requirements.txt`
- [ ] Implementar retry en:
  - [ ] `scriptwriter.py` (Gemini API)
  - [ ] `image_generator.py` (Foundry API)
  - [ ] `youtube_api_client.py` (ya tiene, verificar)
  - [ ] `github_scanner.py` (GitHub API)
- [ ] Agregar logging de reintentos
- [ ] Tests de retry logic

**Tiempo estimado:** 1 día
**Responsable:** Backend Team

---

### Prioridad BAJA 🟢

#### 9. Agregar Monitoring con Prometheus
**Objetivo:** Métricas de performance y errores

**Tareas:**
- [ ] Instalar `prometheus-flask-exporter`
- [ ] Agregar métricas custom:
  - `pipeline_runs_total`
  - `pipeline_duration_seconds`
  - `pipeline_errors_total`
  - `github_api_calls_total`
- [ ] Setup Prometheus + Grafana con Docker
- [ ] Crear dashboard básico

**Tiempo estimado:** 2 días
**Responsable:** DevOps Team

---

#### 10. Security Hardening
**Issues:**
- Secrets en código (algunos)
- CORS sin configurar
- Rate limiting ausente

**Tareas:**
- [ ] Audit de secrets: grep -r "API_KEY" src/
- [ ] Mover todos los secrets a `.env`
- [ ] Implementar CORS en Flask:
  ```python
  from flask_cors import CORS
  CORS(app, origins=["https://yourdomain.com"])
  ```
- [ ] Agregar rate limiting:
  ```python
  from flask_limiter import Limiter
  limiter = Limiter(app, key_func=lambda: request.remote_addr)
  ```
- [ ] Security scan: `bandit -r src/`

**Tiempo estimado:** 1 día
**Responsable:** Security Team

---

## 📦 Sprint 3: Deploy a Producción (Días 6-7)

### Prioridad ALTA 🔴

#### 11. Setup Staging Environment
**Infraestructura:**
- [ ] Deploy en Render/Railway/Fly.io
- [ ] Configurar variables de entorno
- [ ] Setup Redis managed instance
- [ ] Configurar dominio: `staging.yourdomain.com`
- [ ] SSL certificate (Let's Encrypt)

**Tiempo estimado:** 1 día
**Responsable:** DevOps

---

#### 12. CI/CD para Deploy Automático
**Issue:** Workflow `deploy.yml` no existe

**Tareas:**
- [ ] Crear `.github/workflows/deploy.yml`:
  ```yaml
  on:
    push:
      branches: [main]
  jobs:
    deploy:
      - name: Deploy to Staging
        run: ./scripts/deploy.sh staging
  ```
- [ ] Script `deploy.sh` con soporte para `staging` y `production`
- [ ] Healthcheck endpoint: `/health`
- [ ] Rollback strategy si deploy falla

**Tiempo estimado:** 1 día
**Responsable:** DevOps

---

#### 13. Documentación de Deploy
**Actualizar archivos:**
- [ ] `DEPLOYMENT.md`: Agregar sección "Production Deployment"
- [ ] `README.md`: Agregar badge de CI/CD status
- [ ] Crear `RUNBOOK.md` con:
  - Troubleshooting común
  - Comandos de mantenimiento
  - Escalado de workers
  - Backup/restore procedures

**Tiempo estimado:** 4 horas
**Responsable:** Tech Writer

---

## 🎉 Post-Deploy: Mantenimiento

### Tareas Continuas
- [ ] Monitoring dashboard review (diario)
- [ ] Review de logs de errores (diario)
- [ ] Performance optimization (semanal)
- [ ] Security patches (mensual)
- [ ] Dependency updates (mensual)

### Métricas de Éxito
- ✅ Uptime > 99.5%
- ✅ P95 latency < 5s para pipeline completo
- ✅ Error rate < 1%
- ✅ Test coverage > 85%

---

## 📊 Resumen de Tiempo Estimado

| Sprint | Tareas | Días | Prioridad |
|--------|--------|------|-----------|
| Sprint 1 | 1-5 | 2 días | 🔴 Crítico |
| Sprint 2 | 6-10 | 3 días | 🟡 Importante |
| Sprint 3 | 11-13 | 2 días | 🔴 Crítico |
| **Total** | **13 tareas** | **7 días** | **Production Ready** |

---

## 🔄 Proceso de Review

### Daily Standup
- ¿Qué hice ayer?
- ¿Qué haré hoy?
- ¿Hay blockers?

### Sprint Review (Cada 2-3 días)
- Demo de features completadas
- Review de tests
- Actualización de documentación

### Retrospectiva (Al final)
- ¿Qué funcionó bien?
- ¿Qué mejorar?
- Action items para siguiente fase

---

## 📞 Contactos y Responsables

| Área | Responsable | Contacto |
|------|-------------|----------|
| Backend | TBD | backend@team.com |
| Frontend | TBD | frontend@team.com |
| DevOps | TBD | devops@team.com |
| QA | TBD | qa@team.com |
| Product | TBD | product@team.com |

---

**Última Actualización:** 25 de noviembre de 2025
**Próxima Revisión:** 2 de diciembre de 2025
**Status:** 🟡 In Progress
