# 📚 Documentación del Proyecto: MaestroCan IA

_Última Actualización: 18 de julio de 2025_

Esta carpeta contiene toda la documentación técnica y de planificación del proyecto **MaestroCan IA**. La documentación está organizada para facilitar el desarrollo, mantenimiento y colaboración en el proyecto.

## 📋 Estructura de Documentación

### Documentos Principales

| Documento | Propósito | Audiencia | Estado |
|-----------|-----------|-----------|---------|
| **[PLANNING.md](PLANNING.md)** | Planificación técnica y arquitectural del proyecto | Desarrolladores, Arquitectos | ✅ Completo |
| **[TASK.md](TASK.md)** | Gestión de tareas y seguimiento de progreso | Equipo de desarrollo | 🔄 Actualizado |
| **[RULES.md](RULES.md)** | Reglas de desarrollo y estándares de código | Desarrolladores | ✅ Completo |
| **[README.md](README.md)** | Información general del proyecto | Todos los stakeholders | ✅ Completo |

### Contenido de Cada Documento

#### 📋 PLANNING.md
- **Visión y propósito** del proyecto
- **Arquitectura técnica** detallada (Clean Architecture)
- **Pila tecnológica** completa con justificaciones
- **Principios y restricciones** de diseño
- **Roadmap detallado** con 6 fases de desarrollo
- **Métricas de éxito** y KPIs
- **Gestión de riesgos** y mitigaciones
- **Recursos necesarios** y estructura del equipo

#### 📋 TASK.md
- **Estado actual** del proyecto (35% completado)
- **Progreso por componente** con métricas específicas
- **Tabla de tareas** de la fase actual con estados
- **Hitos completados** y pendientes
- **Deuda técnica** identificada
- **Tareas descubiertas** durante el desarrollo

#### 📋 RULES.md
- **Reglas de Clean Architecture** específicas
- **Estándares de código** y convenciones
- **Proceso de testing** con cobertura mínima
- **Flujo de finalización** de tareas
- **Comandos y herramientas** de desarrollo
- **Checklist de revisión** de código
- **Reglas específicas** para MaestroCan IA

## 🎯 Cómo Usar Esta Documentación

### Para Desarrolladores Nuevos
1. **Leer PLANNING.md** para entender la visión y arquitectura
2. **Revisar RULES.md** para conocer las reglas de desarrollo
3. **Consultar TASK.md** para ver el estado actual y próximas tareas
4. **Seguir el README.md** principal para configuración inicial

### Para Desarrollo Diario
1. **Consultar TASK.md** antes de iniciar nuevas tareas
2. **Seguir RULES.md** durante el desarrollo
3. **Actualizar TASK.md** al completar tareas
4. **Referenciar PLANNING.md** para decisiones arquitecturales

### Para Revisiones de Código
1. **Verificar cumplimiento** de reglas en RULES.md
2. **Usar checklist** de revisión incluido
3. **Validar arquitectura** según PLANNING.md
4. **Actualizar documentación** si es necesario

## 🔄 Mantenimiento de Documentación

### Responsabilidades
- **Desarrolladores:** Actualizar TASK.md con progreso diario
- **Arquitecto:** Mantener PLANNING.md actualizado con cambios
- **Lead Developer:** Revisar y actualizar RULES.md según necesidades
- **Product Owner:** Validar que la documentación refleje los objetivos

### Frecuencia de Actualización
- **TASK.md:** Diario (al completar/iniciar tareas)
- **PLANNING.md:** Semanal (revisiones de sprint)
- **RULES.md:** Mensual (o cuando se identifiquen nuevas reglas)
- **README.md:** Por release (cambios significativos)

### Versionado
- Cada documento incluye fecha de última actualización
- Cambios significativos se documentan en commits descriptivos
- Revisiones importantes se marcan con tags en Git

## 📊 Métricas de Documentación

### Estado Actual
- **Completitud:** 90% (todos los documentos principales completos)
- **Actualización:** Última semana (documentos sincronizados)
- **Cobertura:** 100% (todos los aspectos del proyecto documentados)
- **Accesibilidad:** Alta (formato Markdown, estructura clara)

### Objetivos
- Mantener documentación actualizada semanalmente
- Asegurar que nuevos desarrolladores puedan onboardearse en < 2 horas
- Documentar todas las decisiones arquitecturales importantes
- Mantener sincronización entre código y documentación

## 🛠️ Herramientas y Formato

### Formato
- **Markdown:** Todos los documentos en formato .md
- **Emojis:** Para mejorar legibilidad y navegación
- **Tablas:** Para información estructurada
- **Código:** Bloques de código con syntax highlighting
- **Diagramas:** ASCII art para diagramas simples

### Herramientas Recomendadas
- **Editor:** VS Code con extensión Markdown Preview
- **Validación:** markdownlint para consistencia
- **Visualización:** GitHub/GitLab para renderizado
- **Colaboración:** Pull requests para cambios importantes

## 🔗 Enlaces Útiles

### Documentación Externa
- [Flutter Documentation](https://docs.flutter.dev/)
- [Dart Language Guide](https://dart.dev/guides)
- [Clean Architecture Guide](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Firebase Documentation](https://firebase.google.com/docs)
- [Supabase Documentation](https://supabase.com/docs)

### Recursos del Proyecto
- [Repositorio Principal](../README.md)
- [Issues y Bugs](https://github.com/tu-usuario/maestrocan/issues)
- [Releases](https://github.com/tu-usuario/maestrocan/releases)
- [Wiki](https://github.com/tu-usuario/maestrocan/wiki)

## 📝 Plantillas

### Template para Nuevas Tareas
```markdown
| ID | Tarea | Prioridad | Estado | Responsable | Estimación |
|----|-------|-----------|---------|-------------|------------|
| FX-XX | Descripción clara y específica | ALTA/MEDIA/BAJA | ⬜ Pendiente | Nombre | X días |
```

### Template para Documentación de APIs
```dart
/// Descripción clara del propósito de la clase/método.
/// 
/// Explicación detallada del comportamiento y casos de uso.
/// 
/// Ejemplo de uso:
/// ```dart
/// final result = await method(parameter);
/// ```
/// 
/// Parámetros:
/// - [parameter]: Descripción del parámetro
/// 
/// Retorna:
/// - [Type]: Descripción del valor de retorno
/// 
/// Lanza:
/// - [ExceptionType]: Cuándo y por qué se lanza
```

---

## 🎯 Próximos Pasos

1. **Completar Fase 1:** Finalizar autenticación y configuración
2. **Iniciar Fase 2:** Comenzar integración del agente IA
3. **Mantener documentación:** Actualizar semanalmente
4. **Revisar métricas:** Evaluar progreso mensualmente

**Nota:** Esta documentación es un documento vivo que evoluciona con el proyecto. Todos los miembros del equipo son responsables de mantenerla actualizada y útil.

---

*Para más información sobre el proyecto, consultar el [README.md principal](../README.md).*