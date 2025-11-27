# 🔍 Hidden Gems Discovery Strategy

## Objetivo
Encontrar proyectos de alta calidad sin mucha visibilidad pero bien construidos y mantenidos.

## Criterios para "Gemas Escondidas"

### 1. **Actividad y Commits** (Peso: 30%)
- ✅ Mínimo 40 commits recientes (últimos 6 meses)
- ✅ Commits regulares (no abandonado)
- ❌ Sin keywords: "alpha", "test", "wip", "beta", "experimental" en commits recientes
- ✅ Commits con mensajes descriptivos (no solo "fix", "update")

### 2. **Calidad del Código** (Peso: 25%)
- ✅ README bien documentado (>1000 caracteres)
- ✅ Tiene licencia open source
- ✅ Estructura de proyecto clara (src/, tests/, docs/)
- ✅ Tiene tests (presencia de carpeta tests/ o archivos test_*.py)
- ✅ CI/CD configurado (GitHub Actions, Travis, CircleCI)

### 3. **Engagement del Desarrollador** (Peso: 25%)
- ✅ Issues respondidas (<7 días promedio de respuesta)
- ✅ PRs revisados y mergeados regularmente
- ✅ Ratio de issues cerradas vs abiertas >60%
- ✅ PRs de la comunidad aceptados (indica apertura)
- ✅ Últimos 10 issues cerrados (muestra mantenimiento activo)

### 4. **Madurez del Proyecto** (Peso: 20%)
- ✅ Versión estable (v1.0+ o releases regulares)
- ✅ Changelog mantenido
- ✅ Documentación completa
- ✅ Ejemplos de uso incluidos
- ⚠️ Permitir proyectos "feature-complete" sin desarrollo activo reciente

## Rangos de Visibilidad

### Tier 1: Micro Gemas (10-100 stars)
- Proyectos muy nuevos o nicho específico
- Requiere revisión MUY detallada
- Alta probabilidad de false positives

### Tier 2: Gemas Pequeñas (100-500 stars)
- Balance ideal entre calidad y visibilidad
- Foco principal de búsqueda

### Tier 3: Gemas Medianas (500-2000 stars)
- Ya tienen algo de tracción
- Revisión moderada requerida

## Proceso de Revisión Automatizada

### Fase 1: Pre-filtrado (Rust Scanner)
```
Query: stars:10..2000 forks:5..200 pushed:>2024-06-01
```

### Fase 2: Análisis de Commits (Python)
1. Obtener últimos 50 commits
2. Analizar:
   - Frecuencia (commits/semana)
   - Calidad de mensajes
   - Diversidad de autores
   - Keywords negativos

### Fase 3: Análisis de Issues/PRs (Python)
1. Últimas 30 issues:
   - Tiempo de respuesta
   - Ratio cerradas/abiertas
   - Calidad de respuestas
2. Últimos 20 PRs:
   - Tiempo hasta merge/close
   - PRs externos aceptados
   - Code review quality

### Fase 4: Code Review con AI (GitHub Copilot/Gemini)
Para proyectos que pasan Fase 1-3:

**Prompt para AI:**
```
Analiza este repositorio de GitHub: {repo_url}

Evalúa:
1. Arquitectura del código (1-10)
2. Calidad de documentación (1-10)
3. Cobertura de tests (1-10)
4. Buenas prácticas (1-10)
5. Innovación/Utilidad (1-10)

Considera:
- Estructura de carpetas
- Naming conventions
- Comentarios en código
- Manejo de errores
- Seguridad básica

Responde en JSON:
{
  "architecture_score": X,
  "documentation_score": X,
  "testing_score": X,
  "best_practices_score": X,
  "innovation_score": X,
  "overall_score": X,
  "reasoning": "...",
  "recommendation": "APPROVE/REJECT/NEEDS_REVIEW"
}
```

## Herramientas y APIs

### 1. GitHub API
- Rate limit: 5000 requests/hour (authenticated)
- Endpoints necesarios:
  - `/repos/{owner}/{repo}/commits`
  - `/repos/{owner}/{repo}/issues`
  - `/repos/{owner}/{repo}/pulls`
  - `/repos/{owner}/{repo}/contents`

### 2. AI Models (Free/Low-cost)
- **Opción 1**: Google Gemini 1.5 Flash (ya tenemos)
  - Rate limit: 15 requests/min
  - Cost: Free tier disponible

- **Opción 2**: GitHub Copilot API (si disponible)
  - Integrado con GitHub

- **Opción 3**: Anthropic Claude (Haiku)
  - Más barato para análisis
  - Bueno para code review

### 3. Fallback: Análisis Heurístico
Si APIs no disponibles:
- Regex patterns para detectar código de calidad
- Métricas estáticas (LOC, complejidad ciclomática)
- File structure analysis

## Scoring System

```python
total_score = (
    commit_activity_score * 0.30 +
    code_quality_score * 0.25 +
    developer_engagement_score * 0.25 +
    project_maturity_score * 0.20
)

if total_score >= 75:
    priority = "HIGH"  # Crear blog post inmediatamente
elif total_score >= 60:
    priority = "MEDIUM"  # Queue para revisión
else:
    priority = "LOW"  # Descartar
```

## Implementación

### Archivos a Crear:
1. `rust-scanner/src/hidden_gems.rs` - Scanner específico para gemas
2. `src/scanner/gem_analyzer.py` - Análisis profundo
3. `src/scanner/ai_reviewer.py` - Integración con AI
4. `scripts/scan_hidden_gems.py` - Script principal
5. `.github/workflows/hidden_gems_pipeline.yml` - Automation

### Flujo de Trabajo:
```
[Rust Scanner] -> [Gem Analyzer] -> [AI Reviewer] -> [Blog Generator]
     (Fast)         (Deep Analysis)   (Quality Check)   (Content)

     ~10s              ~30s              ~20s/repo        ~15s
```

## Prevención de False Positives

### Red Flags (Auto-reject):
- ❌ Sin commits en >6 meses
- ❌ >70% issues sin respuesta
- ❌ README <200 caracteres
- ❌ Sin licencia
- ❌ Todo el código en un solo archivo >1000 LOC
- ❌ Commits solo de un autor sin PRs externos
- ❌ Issues/PRs spam o abuse

### Yellow Flags (Revisión manual):
- ⚠️ Solo 1-2 contribuidores
- ⚠️ Sin releases oficiales
- ⚠️ Tests faltantes pero código limpio
- ⚠️ Documentación solo en idioma no-inglés

## Métricas de Éxito

### KPIs del Sistema:
- **Precision**: >80% de gemas encontradas son relevantes
- **Recall**: Encontrar al menos 5 gemas/día
- **False Positive Rate**: <20%
- **Processing Time**: <2 min/repositorio completo

### Dashboard Metrics:
- Total repos escaneados
- Gemas descubiertas
- Score promedio
- Categorías más comunes
- Lenguajes predominantes

## Next Steps

1. ✅ Crear scanner Rust para hidden gems
2. ✅ Implementar gem_analyzer.py con análisis detallado
3. ✅ Integrar AI reviewer (Gemini Flash)
4. ✅ Crear workflow automatizado
5. ✅ Testing con repos conocidos de calidad baja visibilidad
6. ✅ Ajustar thresholds basado en resultados
7. ✅ Documentar y deployar

## Ejemplos de "Hidden Gems" Reales

- **typicode/lowdb** (~20k stars ahora, era gema con 500)
- **sindresorhus/ky** (HTTP client, mejor que fetch)
- **lukeed/uvu** (Test runner ultrarrápido)
- **antfu/ni** (Package manager wrapper)

Estos proyectos tenían:
- ✅ Excelente código
- ✅ Gran documentación
- ✅ Mantenimiento activo
- ❌ Poca visibilidad inicial
