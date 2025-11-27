# Guía Rápida: Sistema de PRs Automáticos Jules

## ¿Qué hace este sistema?

**Detecta** → **Revisa** → **Integra** PRs de Jules automáticamente

## Instalación Rápida

1. **Los workflows ya están configurados** en `.github/workflows/auto-pr-review.yml`

2. **Instala GitHub CLI** (para continuación de tareas):

   ```powershell
   winget install GitHub.cli
   gh auth login
   ```

## Uso Diario

### 🤖 Cuando Jules crea un PR

**No hagas nada** - El sistema:

1. Ejecuta tests automáticamente
2. Revisa el código
3. Mergea si todo pasa
4. Te notifica si algo falla

### 📋 Para continuar con siguiente fase

```bash
# Ver estado actual
python scripts/jules_continue.py status

# Crear issue para siguiente fase
python scripts/jules_continue.py continue --prompt "Tu descripción de la siguiente fase aquí"
```

## Ejemplo Real

### Tarea: "Implementar sistema de autenticación"

```bash
# Jules crea PR con Fase 1
# → Sistema detecta, revisa y mergea automáticamente ✅

# Tú continúas:
python scripts/jules_continue.py continue --prompt "Fase 2: Añadir tests y documentación de autenticación"

# Jules crea nuevo PR con Fase 2
# → Sistema detecta, revisa y mergea automáticamente ✅

# Continúas de nuevo:
python scripts/jules_continue.py continue --prompt "Fase 3: Integrar con frontend y añadir UI"

# Jules completa con Fase 3
# → Sistema final ✅
```

## ¿Qué pasa si algo falla?

El sistema:

1. ❌ Marca el PR como "Changes Requested"
2. 💬 Publica detalles de los errores
3. ⏸️ Espera correcciones
4. 🔄 Re-revisa cuando Jules haga push

## Comandos Útiles

```bash
# Ver último PR de Jules
python scripts/jules_continue.py status

# Continuar tarea
python scripts/jules_continue.py continue --prompt "Descripción fase"

# Comentar en PR
python scripts/jules_continue.py comment --pr-number 5 --message "Tu mensaje"
```

## ¿Necesitas más información?

Lee la documentación completa: `docs/JULES_PR_AUTOMATION.md`

---

**¡Eso es todo! 🚀 El sistema está listo para usar.**
