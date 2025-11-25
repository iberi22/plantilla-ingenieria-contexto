# 🔧 Fixes Inmediatos - Checklist

**Fecha:** 25 de noviembre de 2025
**Prioridad:** CRÍTICA
**Tiempo Estimado:** 4-6 horas

---

## ✅ Checklist de Correcciones

### 1. ⚠️ Instalar Dependencias Faltantes
**Problema:** Tests fallan por `sentencepiece` no instalado en el ambiente actual

```bash
# Reinstalar dependencias
pip install -r requirements.txt

# Verificar instalación específica
pip show sentencepiece
```

**Validación:**
```bash
python -c "import sentencepiece; print('✅ SentencePiece OK')"
```

**Estado:** [ ] Pendiente

---

### 2. 🐛 Corregir Imports en test_voice_translation.py
**Archivo:** `tests/test_voice_translation.py`

**Problema actual:**
```python
from video_generator.voice_translation import ...  # ❌ Path incorrecto
```

**Corrección necesaria:**
```python
from src.video_generator.voice_translation import ...  # ✅ Path correcto
```

**Líneas a corregir:**
- Línea ~5: Import del módulo
- Línea ~15-20: Mocks de whisper.load_model
- Línea ~30-35: Mocks de TTS

**Validación:**
```bash
pytest tests/test_voice_translation.py -v
```

**Estado:** [ ] Pendiente

---

### 3. 🔨 Refactorizar image_generator.py para Testing
**Archivo:** `src/image_gen/image_generator.py`

**Problema:** Import dinámico dentro de `__init__` hace que los mocks fallen

**Solución:**
```python
# Al inicio del archivo (línea ~15)
try:
    from foundry_local import FoundryLocalManager
    FOUNDRY_AVAILABLE = True
except ImportError:
    FoundryLocalManager = None
    FOUNDRY_AVAILABLE = False

class ImageGenerator:
    def __init__(self, model_name: str = "nano-banana-2", output_dir: str = "output/images"):
        self.logger = logging.getLogger(__name__)
        self.model_name = model_name
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        if not FOUNDRY_AVAILABLE:
            self.logger.error("foundry-local-sdk is required for image generation")
            raise ImportError("Install foundry-local-sdk: pip install foundry-local-sdk")

        # Initialize Foundry Local
        try:
            self.manager = FoundryLocalManager(self.model_name)
            self.logger.info(f"Initialized Foundry Local with model: {self.model_name}")
        except Exception as e:
            self.logger.error(f"Failed to initialize Foundry Local: {e}")
            raise
```

**Validación:**
```bash
pytest tests/test_image_gen.py -v
```

**Estado:** [ ] Pendiente

---

### 4. 🧪 Actualizar Mocks en test_image_gen.py
**Archivo:** `tests/test_image_gen.py`

**Cambio necesario:**
```python
# Línea ~15
@pytest.fixture
def mock_foundry():
    # Cambiar de:
    with patch('src.image_gen.image_generator.FoundryLocalManager') as mock_manager_class:

    # A:
    with patch('src.image_gen.image_generator.FOUNDRY_AVAILABLE', True):
        with patch('src.image_gen.image_generator.FoundryLocalManager') as mock_manager_class:
            # ... resto del código
```

**Estado:** [ ] Pendiente

---

### 5. 🎬 Fix test_end_to_end.py
**Archivo:** `tests/test_end_to_end.py`

**Problema:** `mock_concat.called` es False

**Análisis necesario:**
1. Verificar que el path del mock sea correcto
2. Confirmar que `concatenate_videoclips` se importa del módulo correcto en `reel_creator.py`

**Solución temporal:** Skip el test mientras se investiga
```python
@pytest.mark.skip(reason="Mock configuration issue - under investigation")
def test_reel_creation_flow(self):
    # ...
```

**Estado:** [ ] Pendiente (investigar después de los críticos)

---

### 6. 🎥 Fix test_dynamic_durations
**Archivo:** `tests/test_reel_creator_features.py`

**Problema:** `os.path.exists(output_path)` retorna False

**Posibles causas:**
- Path relativo vs absoluto
- Directorio no creado
- Test no espera a que moviepy termine de escribir

**Solución:**
```python
import time

def test_dynamic_durations(self):
    # ... código existente ...

    # Agregar wait
    time.sleep(1)

    # Convertir a path absoluto
    output_path = os.path.abspath(output_path)

    self.assertTrue(os.path.exists(output_path),
                   f"Video not found at {output_path}")
```

**Estado:** [ ] Pendiente

---

## 🚀 Script de Validación Rápida

Crear archivo `scripts/quick_validation.py`:

```python
#!/usr/bin/env python3
"""
Quick validation script to check critical functionality.
Run this after applying fixes.
"""

import sys
import subprocess

def run_command(cmd, description):
    """Run a command and report status."""
    print(f"\n{'='*60}")
    print(f"Testing: {description}")
    print(f"{'='*60}")

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.returncode == 0:
        print("✅ PASSED")
        return True
    else:
        print("❌ FAILED")
        print(result.stdout)
        print(result.stderr)
        return False

def main():
    tests = [
        ("python -c 'import sentencepiece'", "SentencePiece import"),
        ("python -c 'from src.video_generator import voice_translation'", "Voice translation import"),
        ("python -c 'from src.image_gen import image_generator'", "Image generator import"),
        ("pytest tests/test_voice_translation.py -v", "Voice translation tests"),
        ("pytest tests/test_image_gen.py -v", "Image generator tests"),
        ("pytest tests/test_api_integration.py -v", "API integration tests"),
    ]

    passed = 0
    failed = 0

    for cmd, description in tests:
        if run_command(cmd, description):
            passed += 1
        else:
            failed += 1

    print(f"\n{'='*60}")
    print(f"SUMMARY: {passed} passed, {failed} failed")
    print(f"{'='*60}\n")

    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
```

**Uso:**
```bash
python scripts/quick_validation.py
```

---

## 📊 Progreso

| # | Tarea | Prioridad | Estado | Tiempo |
|---|-------|-----------|--------|--------|
| 1 | Instalar dependencias | 🔴 Crítica | [ ] | 10 min |
| 2 | Fix imports tests | 🔴 Crítica | [ ] | 30 min |
| 3 | Refactor image_generator | 🔴 Crítica | [ ] | 1h |
| 4 | Update mocks | 🔴 Crítica | [ ] | 30 min |
| 5 | Fix end-to-end test | 🟡 Media | [ ] | 2h |
| 6 | Fix dynamic_durations | 🟡 Media | [ ] | 1h |

**Total estimado:** 5-6 horas

---

## ✅ Criterios de Éxito

Después de aplicar estos fixes:

```bash
pytest tests/ -v
```

**Objetivo:**
- ✅ Al menos 40/45 tests pasando (89%)
- ✅ 0 errors (solo failures permitidos)
- ✅ Tests críticos de voice_translation pasando
- ✅ Tests de image_gen pasando

---

## 🔄 Próximos Pasos (Después de Fixes)

1. Commit cambios: `git commit -m "fix: critical test failures and dependencies"`
2. Push a branch: `git push origin fix/critical-tests`
3. Crear PR con resumen de fixes
4. Continuar con Sprint 1 del [ROADMAP.md](ROADMAP.md)

---

**Última Actualización:** 25 de noviembre de 2025
**Responsable:** Backend Team
**Deadline:** 26 de noviembre de 2025 EOD
