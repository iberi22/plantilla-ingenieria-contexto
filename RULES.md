# 📋 Reglas de Desarrollo: Open Source Video Generator

_Última Actualización: 23 de noviembre de 2025_

### 🔄 Project Awareness & Context

- **Always read `PLANNING.md`** at the start of a new conversation to understand the project's architecture, goals, style, and constraints.
- **Check `TASK.md`** before starting a new task. If the task isn’t listed, add it with a brief description and today's date.
- **Use consistent naming conventions, file structure, and architecture patterns** as described in `PLANNING.md`.

### 🧱 Code Structure & Modularity

- **Never create a file longer than 800 lines of code.** If a file approaches this limit, refactor by splitting it into modules or helper files.
- **Organize code into clearly separated modules**, grouped by feature or responsibility (Scanner, Agents, Engine, Uploader).
- **Use clear, consistent imports** (prefer relative imports within packages).

## 🧱 Estándares de Código

### Python

- **Estilo:** Adherencia estricta a **PEP 8**.
- **Tipado:** Uso obligatorio de **Type Hints** en firmas de funciones y métodos.
- **Docstrings:** Formato Google Style para todas las clases y funciones públicas.
- **Imports:** Organizados: Estándar -> Terceros -> Locales.

```python
# Ejemplo de firma correcta
def generate_script(self, repo_data: Dict[str, Any]) -> Optional[Dict[str, str]]:
    """Genera un guion de video basado en datos del repositorio.

    Args:
        repo_data: Diccionario con metadatos del repo.

    Returns:
        Dict con el guion estructurado o None si falla.
    """
    ...
```

### Manejo de Errores y Logging

- **No usar `print`:** Usar siempre el módulo `logging`.
- **Excepciones:** Capturar excepciones específicas, nunca `except Exception:` vacío sin re-raise o log detallado.
- **Fail-fast:** Si falta una configuración crítica (ej. API Key), fallar inmediatamente al inicio.

## 🤖 Reglas de IA (LLMs)

### Hibridez Obligatoria

Todo componente de IA debe soportar dos modos:

1. **Cloud (Gemini):** Para ejecución en CI/CD (GitHub Actions). Requiere `GOOGLE_API_KEY`.
2. **Local (Foundry):** Para desarrollo local sin costos. Requiere `foundry-local-sdk`.

### Ingeniería de Prompts

- Los prompts deben solicitar salidas estructuradas (JSON) para facilitar el parsing.
- Incluir instrucciones de "Persona" (ej. "Actúa como un Ingeniero DevOps Senior").

## 🧪 Testing & Reliability

- **Always create Pytest unit tests for new features** (functions, classes, routes, etc).
- **Tests should live in a `/tests` folder** mirroring the main app structure.
- **Mocking:** NUNCA llamar a APIs reales (GitHub, YouTube, Gemini) en los tests automáticos. Usar `unittest.mock` o `pytest-mock`.

## 🚀 DevOps y CI/CD

### GitHub Actions

- **Idempotencia:** Los workflows deben poder correr múltiples veces sin efectos adversos.
- **Headless:** Todo código de UI (Playwright) debe soportar ejecución `--headless`.
- **Secretos:** Las credenciales se leen EXCLUSIVAMENTE de variables de entorno.

### Docker

- El contenedor debe incluir todas las dependencias de sistema (FFmpeg, Browsers) para garantizar consistencia.

## 🔒 Seguridad

- **.gitignore:** Verificar siempre que `output/`, `.env` y `__pycache__` estén ignorados.
- **Sanitización:** Limpiar nombres de archivos generados para evitar inyecciones de comandos.

### 🧠 AI Behavior Rules

- **Never assume missing context. Ask questions if uncertain.**
- **Never hallucinate libraries or functions** – only use known, verified Python packages.
- **Always confirm file paths and module names** exist before referencing them in code or tests.
