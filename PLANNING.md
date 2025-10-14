# 📋 Planificación del Proyecto: MaestroCan IA

_Última Actualización: 18 de julio de 2025_

## 1. Visión y Propósito del Proyecto

**Visión:** Desarrollar una aplicación móvil conversacional e inteligente que actúe como un entrenador personal de mascotas, utilizando IA para ofrecer guía y soporte personalizado en el entrenamiento de diversas habilidades y la resolución de problemas de comportamiento.

**Propósito:** Resolver la necesidad de los dueños de mascotas de tener acceso a un experto en entrenamiento 24/7, proporcionando consejos personalizados, planes de entrenamiento y seguimiento del progreso de manera interactiva y accesible a través de una interfaz conversacional.

**Problema que Resuelve:**
- Falta de acceso inmediato a expertos en entrenamiento de mascotas
- Costos elevados de entrenadores profesionales
- Inconsistencia en métodos de entrenamiento
- Dificultad para mantener rutinas de entrenamiento constantes
- Necesidad de orientación personalizada según la raza, edad y temperamento de la mascota

**Valor Diferencial:**
- Disponibilidad 24/7 sin citas previas
- Consejos personalizados basados en el perfil específico de cada mascota
- Interfaz conversacional natural (voz y texto)
- Seguimiento continuo del progreso
- Costo accesible comparado con entrenadores tradicionales

---

## 2. Arquitectura y Pila Tecnológica

### 2.1 Arquitectura General
**Patrón Arquitectónico:** Clean Architecture (Flutter) con separación clara de responsabilidades en capas:

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Screens   │  │    Blocs    │  │      Widgets        │  │
│  │             │  │             │  │                     │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                     DOMAIN LAYER                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  Entities   │  │ Use Cases   │  │   Repositories      │  │
│  │             │  │             │  │   (Interfaces)      │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                      DATA LAYER                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Models    │  │ Data Sources│  │   Repositories      │  │
│  │             │  │             │  │ (Implementations)   │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                      CORE LAYER                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Utils     │  │   Constants │  │      Errors         │  │
│  │             │  │             │  │                     │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Pila Tecnológica (Stack)

**Frontend & UI:**
- **Lenguaje Principal:** Dart 3.8.1+
- **Framework:** Flutter (multiplataforma iOS/Android)
- **UI Kit:** shadcn_flutter (componentes modernos y consistentes)
- **Gestión de Estado:** flutter_bloc + get_it (inyección de dependencias)
- **Iconografía:** Cupertino Icons

**Backend & Datos:**
- **Base de Datos Principal:** Supabase (PostgreSQL en la nube)
- **Base de Datos Local:** Isar (para cache y datos offline)
- **Autenticación:** Firebase Authentication
- **Almacenamiento de Archivos:** Supabase Storage

**Inteligencia Artificial:**
- **Modelo de Lenguaje:** Google Gemini (generación de respuestas)
- **Orquestación de IA:** langchain_dart (cadenas de procesamiento)
- **Memoria del Agente:** isar_agent_memory (contexto persistente)
- **Speech-to-Text:** Google Gemini STT
- **Text-to-Speech:** Google Gemini TTS

**Desarrollo & Herramientas:**
- **Generación de Código:** Freezed, json_serializable, isar_generator
- **Testing:** flutter_test, mockito
- **Linting:** flutter_lints
- **Build Runner:** build_runner

### 2.3 Estructura de Directorios
```
lib/
├── core/                     # Funcionalidades transversales
│   ├── constants/           # Constantes globales
│   ├── errors/              # Manejo de errores
│   ├── network/             # Configuración de red
│   └── utils/               # Utilidades generales
├── data/                    # Capa de datos
│   ├── datasources/         # Fuentes de datos (API, DB local)
│   ├── models/              # Modelos de datos
│   └── repositories/        # Implementaciones de repositorios
├── domain/                  # Lógica de negocio
│   ├── entities/            # Entidades del dominio
│   ├── repositories/        # Interfaces de repositorios
│   └── usecases/            # Casos de uso
└── presentation/            # Capa de presentación
    ├── auth/                # Módulo de autenticación
    ├── chat/                # Módulo de chat conversacional
    ├── profile/             # Módulo de perfiles de mascotas
    └── shared/              # Widgets compartidos
```

---

## 3. Principios y Restricciones Clave

### 3.1 Principios de Diseño

**Arquitectura:**
- **SOLID Principles:** Aplicación estricta de principios de diseño orientado a objetos
- **Clean Architecture:** Separación clara de responsabilidades en capas
- **Dependency Injection:** Uso de get_it para inversión de dependencias
- **Modularidad:** Código organizado por características (features) y capas

**Experiencia de Usuario:**
- **Mobile-First:** Diseño optimizado para dispositivos móviles (iOS/Android)
- **Conversational UI:** Interfaz centrada en la interacción natural
- **Accessibility:** Cumplimiento de estándares de accesibilidad
- **Offline-First:** Funcionalidad básica disponible sin conexión

**Calidad de Código:**
- **Test-Driven Development:** Cobertura mínima del 80% en pruebas
- **Code Review:** Revisión obligatoria de código antes de merge
- **Documentation:** Documentación completa de APIs y componentes
- **Performance:** Tiempo de respuesta < 2 segundos para interacciones críticas

### 3.2 Restricciones Técnicas

**Plataformas:**
- **iOS:** Versión mínima 12.0
- **Android:** API Level 21 (Android 5.0) mínimo
- **Orientación:** Portrait principalmente, landscape opcional

**Rendimiento:**
- **Tamaño de App:** < 50MB inicial, < 100MB con datos
- **Memoria RAM:** Funcionamiento óptimo con 2GB RAM
- **Batería:** Optimización para uso prolongado
- **Red:** Funcionalidad offline para características básicas

**Seguridad:**
- **Encriptación:** Datos sensibles encriptados en tránsito y reposo
- **Autenticación:** Multi-factor authentication opcional
- **Privacidad:** Cumplimiento GDPR y políticas de privacidad
- **API Keys:** Gestión segura de credenciales

### 3.3 Restricciones de Negocio

**Funcionales:**
- **Idiomas:** Español como idioma principal, inglés como secundario
- **Tipos de Mascotas:** Enfoque inicial en perros, expansión futura a gatos
- **Edad de Usuarios:** 13+ años (términos de servicio)
- **Conectividad:** Funciones de IA requieren conexión a internet

**Regulatorias:**
- **Stores:** Cumplimiento de políticas de App Store y Google Play
- **Datos:** Protección de datos personales según legislación local
- **Contenido:** Moderación de contenido generado por IA
- **Responsabilidad:** Disclaimers sobre consejos veterinarios

---

## 4. Hitos Principales (Roadmap)

### 4.1 Fase 1: Configuración y Autenticación (Actual - Semanas 1-2)
**Estado:** 🟡 En Progreso (30% completado)

**Objetivos:**
- Establecer la base técnica del proyecto
- Configurar todas las dependencias necesarias
- Implementar sistema de autenticación robusto
- Crear estructura de Clean Architecture

**Entregables:**
- [✅] Proyecto Flutter inicializado con dependencias
- [✅] Estructura de directorios de Clean Architecture
- [✅] Pantalla de login básica implementada
- [🔄] Resolución de conflictos de dependencias (isar_flutter_libs)
- [⏳] Sistema completo de autenticación Firebase
- [⏳] Configuración inicial de Supabase
- [⏳] Pantallas de registro y recuperación de contraseña
- [⏳] Validación y testing de flujos de autenticación

### 4.2 Fase 2: Agente Conversacional Básico (Semanas 3-5)
**Estado:** ⏳ Pendiente

**Objetivos:**
- Integrar Google Gemini como motor de IA
- Implementar interfaz de chat funcional
- Configurar memoria persistente del agente
- Habilitar comunicación por voz

**Entregables:**
- Integración completa de Google Gemini API
- Implementación de langchain_dart para orquestación
- Configuración de isar_agent_memory
- Interfaz de chat con mensajes de texto
- Funcionalidad básica de STT (Speech-to-Text)
- Funcionalidad básica de TTS (Text-to-Speech)
- Sistema de prompts base para entrenamiento de mascotas
- Testing de respuestas del agente

### 4.3 Fase 3: Perfiles de Mascota y Personalización (Semanas 6-8)
**Estado:** ⏳ Pendiente

**Objetivos:**
- Crear sistema de gestión de perfiles de mascotas
- Personalizar respuestas según características de la mascota
- Implementar almacenamiento en Supabase
- Desarrollar onboarding de mascotas

**Entregables:**
- Modelo de datos para perfiles de mascotas
- Pantallas de creación/edición de perfiles
- Integración con Supabase para persistencia
- Sistema de personalización de respuestas IA
- Onboarding guiado para nuevas mascotas
- Galería de fotos de mascotas
- Configuración de preferencias de entrenamiento
- Sincronización offline/online de datos

### 4.4 Fase 4: Funcionalidades Avanzadas de Entrenamiento (Semanas 9-12)
**Estado:** ⏳ Pendiente

**Objetivos:**
- Desarrollar planes de entrenamiento personalizados
- Implementar seguimiento de progreso
- Crear biblioteca de ejercicios y técnicas
- Añadir funciones de recordatorios y rutinas

**Entregables:**
- Generador de planes de entrenamiento IA
- Sistema de seguimiento de progreso
- Biblioteca de ejercicios categorizados
- Calendario de entrenamientos
- Sistema de recordatorios push
- Métricas y analytics de progreso
- Funciones de compartir logros
- Integración con wearables (futuro)

### 4.5 Fase 5: Funcionalidades Premium y Monetización (Semanas 13-15)
**Estado:** ⏳ Pendiente

**Objetivos:**
- Implementar modelo de suscripción
- Desarrollar funciones premium
- Crear sistema de consultas con expertos
- Añadir contenido multimedia avanzado

**Entregables:**
- Sistema de suscripciones in-app
- Funciones premium (planes avanzados, consultas ilimitadas)
- Videollamadas con entrenadores certificados
- Biblioteca de videos educativos
- Comunidad de usuarios
- Sistema de gamificación
- Certificaciones de entrenamiento

### 4.6 Fase 6: Pulido y Despliegue (Semanas 16-18)
**Estado:** ⏳ Pendiente

**Objetivos:**
- Optimizar rendimiento y UX
- Realizar testing exhaustivo
- Preparar para lanzamiento en stores
- Implementar analytics y monitoreo

**Entregables:**
- Optimización de rendimiento
- Testing completo (unit, widget, integration)
- Preparación para App Store y Google Play
- Configuración de analytics (Firebase Analytics)
- Sistema de crash reporting
- Documentación de usuario
- Material de marketing
- Plan de lanzamiento y distribución

### 4.7 Cronograma Visual

```
Semanas:  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18
Fase 1:   ████████
Fase 2:         ██████████
Fase 3:                   ██████████
Fase 4:                            ████████████
Fase 5:                                     ██████████
Fase 6:                                           ██████████

Hitos:    🏁     🏁        🏁        🏁           🏁        🏁
         Auth   Chat    Profiles  Training    Premium   Launch
```

### 4.8 Criterios de Éxito por Fase

**Fase 1:** Sistema de autenticación funcional al 100%
**Fase 2:** Agente IA responde coherentemente a preguntas básicas
**Fase 3:** Personalización efectiva basada en perfil de mascota
**Fase 4:** Planes de entrenamiento generados automáticamente
**Fase 5:** Modelo de negocio implementado y funcional
**Fase 6:** App publicada en stores con rating > 4.0

---

## 5. Métricas de Éxito y KPIs

### 5.1 Métricas Técnicas
- **Tiempo de Respuesta:** < 2 segundos para consultas IA
- **Disponibilidad:** 99.5% uptime
- **Cobertura de Tests:** > 80%
- **Crash Rate:** < 0.1%
- **Tamaño de App:** < 50MB inicial

### 5.2 Métricas de Usuario
- **Retención:** > 60% a 7 días, > 30% a 30 días
- **Engagement:** > 3 sesiones por semana por usuario activo
- **Satisfacción:** Rating > 4.0 en stores
- **Conversión:** > 15% de usuarios gratuitos a premium

### 5.3 Métricas de Negocio
- **Usuarios Activos:** 10,000 MAU en 6 meses
- **Revenue:** $50,000 ARR en primer año
- **Costo de Adquisición:** < $10 CAC
- **Lifetime Value:** > $100 LTV

---

## 6. Riesgos y Mitigaciones

### 6.1 Riesgos Técnicos
| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|-------------|---------|------------|
| Problemas con APIs de IA | Media | Alto | Implementar fallbacks y cache |
| Rendimiento en dispositivos antiguos | Alta | Medio | Testing extensivo y optimización |
| Conflictos de dependencias | Media | Medio | Versionado estricto y testing |

### 6.2 Riesgos de Negocio
| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|-------------|---------|------------|
| Competencia directa | Alta | Alto | Diferenciación por personalización |
| Cambios en políticas de stores | Baja | Alto | Cumplimiento estricto de guidelines |
| Problemas legales/responsabilidad | Baja | Alto | Disclaimers claros y términos de uso |

---

## 7. Recursos y Equipo

### 7.1 Roles Necesarios
- **Desarrollador Flutter Senior** (1) - Arquitectura y desarrollo principal
- **Especialista en IA/ML** (0.5) - Integración y optimización de modelos
- **Diseñador UX/UI** (0.5) - Diseño de interfaces y experiencia
- **QA Engineer** (0.5) - Testing y aseguramiento de calidad

### 7.2 Herramientas y Servicios
- **Desarrollo:** VS Code, Android Studio, Xcode
- **Versionado:** Git + GitHub
- **CI/CD:** GitHub Actions
- **Monitoreo:** Firebase Crashlytics, Analytics
- **Comunicación:** Slack, Notion

---

## 8. Conclusiones y Próximos Pasos

**MaestroCan IA** representa una oportunidad significativa en el mercado de aplicaciones para mascotas, combinando tecnologías de IA avanzadas con una experiencia de usuario intuitiva. El enfoque en Clean Architecture y las mejores prácticas de desarrollo aseguran un producto escalable y mantenible.

**Próximos Pasos Inmediatos:**
1. Completar resolución de dependencias (isar_flutter_libs)
2. Finalizar implementación de autenticación Firebase
3. Configurar entorno de desarrollo y testing
4. Iniciar Fase 2 con integración de Google Gemini

**Fecha de Revisión:** Cada viernes para evaluar progreso y ajustar roadmap según necesidades.