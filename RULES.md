# 📋 Reglas de Desarrollo: MaestroCan IA

_Última Actualización: 18 de julio de 2025_

## 🔄 Conciencia del Proyecto y Contexto

### Documentación Obligatoria
- **Siempre lee `PLANNING.md`** al inicio de una nueva conversación para entender la arquitectura, objetivos y restricciones del proyecto.
- **Consulta `TASK.md`** antes de iniciar una nueva tarea. Si la tarea no está listada, añádela con una breve descripción y prioridad.
- **Revisa `README.md`** para entender el estado actual del proyecto y las instrucciones de configuración.

### Contexto del Proyecto
- **Tipo:** Aplicación móvil Flutter para entrenamiento de mascotas con IA conversacional
- **Plataformas:** iOS (12.0+) y Android (API 21+)
- **Arquitectura:** Clean Architecture con separación estricta de capas
- **Stack Principal:** Flutter + Dart, Google Gemini, Firebase Auth, Supabase, shadcn_flutter

## 🧱 Estructura de Código y Modularidad

### Clean Architecture (Obligatorio)
- **Separación estricta de capas:** `presentation` → `domain` → `data` → `core`
- **Regla de dependencias:** Las capas internas NO pueden depender de las externas
- **Interfaces en domain:** Todos los repositorios deben definirse como interfaces en `domain/repositories/`
- **Implementaciones en data:** Las implementaciones van en `data/repositories/`

### Organización por Features
```
lib/presentation/
├── auth/                    # Módulo de autenticación
│   ├── blocs/              # Estados y lógica de presentación
│   ├── screens/            # Pantallas del módulo
│   └── widgets/            # Widgets específicos del módulo
├── chat/                   # Módulo de chat conversacional
├── profile/                # Módulo de perfiles de mascotas
└── shared/                 # Widgets y utilidades compartidas
```

### Límites de Código
- **Archivos:** Máximo 300 líneas por archivo (excepción: archivos generados)
- **Métodos:** Máximo 50 líneas por método
- **Clases:** Máximo 20 métodos públicos por clase
- **Parámetros:** Máximo 5 parámetros por método (usar objetos para más)

### Generación de Código
- **Modelos:** Usar `freezed` + `json_serializable` para todas las entidades y DTOs
- **Base de Datos:** Usar `isar_generator` para modelos de base de datos local
- **Inyección:** Usar `get_it` para todas las dependencias

## 🧪 Pruebas y Fiabilidad

### Cobertura Obligatoria
- **Cobertura mínima:** 80% para todo el código de producción
- **Casos de uso:** 100% de cobertura (son críticos para la lógica de negocio)
- **Repositorios:** 90% de cobertura (manejo de datos crítico)
- **Widgets:** 70% de cobertura (UI menos crítica pero importante)

### Tipos de Pruebas Requeridas
```
test/
├── unit/                   # Pruebas unitarias
│   ├── domain/            # Casos de uso y entidades
│   ├── data/              # Repositorios y fuentes de datos
│   └── core/              # Utilidades y helpers
├── widget/                # Pruebas de widgets
│   └── presentation/      # Pantallas y widgets
└── integration/           # Pruebas de integración
    └── flows/             # Flujos completos de usuario
```

### Casos de Prueba Obligatorios
Para cada funcionalidad nueva:
1. **Happy Path:** Caso de uso exitoso principal
2. **Edge Cases:** Al menos 2 casos límite
3. **Error Cases:** Al menos 2 casos de fallo
4. **Null Safety:** Verificar manejo de valores nulos
5. **Performance:** Para operaciones críticas (IA, DB)

### Comandos de Testing
- `flutter test` - Ejecutar todas las pruebas
- `flutter test --coverage` - Generar reporte de cobertura
- `flutter test test/unit/` - Solo pruebas unitarias
- `flutter test test/widget/` - Solo pruebas de widgets

## ✅ Finalización de Tareas

### Proceso de Completado
1. **Verificar funcionalidad:** La tarea debe funcionar completamente
2. **Ejecutar pruebas:** `flutter test` debe pasar al 100%
3. **Revisar código:** Cumplir con todas las reglas de estilo
4. **Actualizar documentación:** Si la tarea afecta APIs o comportamiento
5. **Marcar en TASK.md:** Cambiar estado a ✅ Completado

### Criterios de Definición de "Hecho"
- [ ] Código implementado y funcionando
- [ ] Pruebas escritas y pasando
- [ ] Código formateado con `dart format`
- [ ] Sin warnings en `flutter analyze`
- [ ] Documentación actualizada si es necesario
- [ ] Tarea marcada como completada en TASK.md

### Gestión de Nuevas Tareas
- **Tareas descubiertas:** Añadir a sección "Tareas Descubiertas" en TASK.md
- **Bugs encontrados:** Crear tarea con prioridad ALTA
- **Mejoras identificadas:** Crear tarea con prioridad BAJA o MEDIA
- **Deuda técnica:** Documentar en sección específica

## 📎 Estilo y Convenciones

### Lenguaje y Formato
- **Lenguaje principal:** Dart 3.8.1+
- **Estilo:** Seguir estrictamente [Effective Dart](https://dart.dev/guides/language/effective-dart)
- **Formato:** Ejecutar `dart format .` antes de cada commit
- **Análisis:** Ejecutar `flutter analyze` y resolver todos los warnings

### Convenciones de Nomenclatura
```dart
// Clases: PascalCase
class UserRepository {}
class ChatBloc {}

// Variables y métodos: camelCase
String userName = '';
void sendMessage() {}

// Constantes: camelCase con const
const String apiBaseUrl = '';
const Duration timeoutDuration = Duration(seconds: 30);

// Archivos: snake_case
user_repository.dart
chat_bloc.dart
login_screen.dart

// Directorios: snake_case
auth/screens/
chat/widgets/
shared/utils/
```

### Documentación de Código
```dart
/// Repositorio para gestionar la autenticación de usuarios.
/// 
/// Proporciona métodos para login, registro y gestión de sesiones
/// utilizando Firebase Authentication como proveedor principal.
/// 
/// Ejemplo de uso:
/// ```dart
/// final authRepo = AuthRepository();
/// final user = await authRepo.signIn(email, password);
/// ```
class AuthRepository {
  /// Inicia sesión con email y contraseña.
  /// 
  /// Retorna [User] si el login es exitoso, o lanza [AuthException]
  /// si las credenciales son inválidas.
  Future<User> signIn(String email, String password) async {
    // Implementación...
  }
}
```

### Estructura de Imports
```dart
// 1. Dart core libraries
import 'dart:async';
import 'dart:convert';

// 2. Flutter libraries
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

// 3. Third-party packages
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

// 4. Internal imports (relative)
import '../../../domain/entities/user.dart';
import '../../../core/errors/failures.dart';
import '../../widgets/custom_button.dart';
```

## 🧠 Comportamiento de la IA y Desarrollo

### Principios de Desarrollo
- **Nunca asumas contexto faltante:** Hacer preguntas específicas si algo no está claro
- **No alucinar dependencias:** Usar únicamente paquetes especificados en `pubspec.yaml`
- **Verificar rutas:** Confirmar estructura de archivos antes de referenciar
- **Seguridad first:** Nunca exponer credenciales en código fuente

### Gestión de Dependencias
```yaml
# Solo usar dependencias aprobadas en pubspec.yaml
dependencies:
  flutter_bloc: ^8.1.6        # ✅ Aprobado
  get_it: ^7.7.0              # ✅ Aprobado
  google_generative_ai: ^0.4.1 # ✅ Aprobado
  # provider: ^6.0.0          # ❌ NO usar, usamos bloc
```

### Seguridad y Credenciales
```dart
// ❌ NUNCA hacer esto
const String apiKey = 'sk-1234567890abcdef';

// ✅ Usar variables de entorno
class ApiConfig {
  static String get geminiApiKey => 
    const String.fromEnvironment('GEMINI_API_KEY');
  
  static String get supabaseUrl => 
    const String.fromEnvironment('SUPABASE_URL');
}
```

### Manejo de Errores Específico
```dart
// Para el proyecto MaestroCan IA, usar estos tipos de errores:
abstract class Failure {
  const Failure();
}

class AuthFailure extends Failure {
  final String message;
  const AuthFailure(this.message);
}

class AIFailure extends Failure {
  final String message;
  const AIFailure(this.message);
}

class NetworkFailure extends Failure {
  const NetworkFailure();
}
```

### Logging y Debugging
```dart
// Usar logging estructurado
import 'package:logger/logger.dart';

final logger = Logger();

// En desarrollo
logger.d('Debug: Usuario autenticado');
logger.i('Info: Enviando mensaje al agente IA');
logger.w('Warning: Respuesta de IA tardó más de 5 segundos');
logger.e('Error: Falló la autenticación');
```

## 🚀 Comandos y Herramientas

### Comandos de Desarrollo Diarios
```bash
# Verificación completa antes de commit
flutter analyze                    # Análisis estático
dart format .                     # Formateo de código
flutter test --coverage          # Pruebas con cobertura
flutter build apk --debug        # Build de prueba

# Generación de código
dart run build_runner build      # Generar modelos
dart run build_runner watch      # Generar en modo watch

# Limpieza
flutter clean                    # Limpiar build
flutter pub get                  # Actualizar dependencias
```

### Herramientas Requeridas
- **IDE:** VS Code con extensiones Flutter/Dart
- **Emuladores:** iOS Simulator + Android Emulator
- **Debugging:** Flutter Inspector, Dart DevTools
- **Versionado:** Git con commits descriptivos

## 🎯 Específico para MaestroCan IA

### Prompts del Agente IA
```dart
// Estructura estándar para prompts del agente
class PetTrainingPrompts {
  static const String systemPrompt = '''
  Eres MaestroCan, un experto entrenador de mascotas con 20 años de experiencia.
  Tu objetivo es ayudar a los dueños a entrenar a sus mascotas de manera efectiva y positiva.
  
  Reglas:
  - Siempre usa refuerzo positivo
  - Adapta consejos según raza, edad y temperamento
  - Nunca recomiendes métodos punitivos
  - Si detectas problemas de salud, recomienda veterinario
  ''';
  
  static String buildUserPrompt(String petProfile, String userQuestion) {
    return '''
    Perfil de la mascota: $petProfile
    Pregunta del usuario: $userQuestion
    
    Proporciona una respuesta personalizada, práctica y alentadora.
    ''';
  }
}
```

### Validaciones Específicas
```dart
// Validaciones para perfiles de mascotas
class PetProfileValidators {
  static String? validatePetName(String? name) {
    if (name == null || name.trim().isEmpty) {
      return 'El nombre de la mascota es obligatorio';
    }
    if (name.length < 2) {
      return 'El nombre debe tener al menos 2 caracteres';
    }
    return null;
  }
  
  static String? validatePetAge(int? age) {
    if (age == null || age < 0) {
      return 'La edad debe ser un número positivo';
    }
    if (age > 30) {
      return 'Por favor verifica la edad de tu mascota';
    }
    return null;
  }
}
```

---

## 📋 Checklist de Revisión de Código

Antes de marcar cualquier tarea como completada, verificar:

### Arquitectura ✅
- [ ] Respeta Clean Architecture
- [ ] Dependencias van en la dirección correcta
- [ ] Interfaces definidas en domain
- [ ] Implementaciones en data

### Calidad ✅
- [ ] Código formateado (`dart format`)
- [ ] Sin warnings (`flutter analyze`)
- [ ] Pruebas escritas y pasando
- [ ] Cobertura > 80% para nuevas funciones

### Seguridad ✅
- [ ] No hay credenciales hardcodeadas
- [ ] Validaciones de entrada implementadas
- [ ] Manejo de errores apropiado
- [ ] Datos sensibles encriptados

### UX/UI ✅
- [ ] Responsive design
- [ ] Accesibilidad considerada
- [ ] Loading states implementados
- [ ] Error states manejados

### Documentación ✅
- [ ] Código documentado con ///
- [ ] README actualizado si es necesario
- [ ] TASK.md actualizado
- [ ] APIs documentadas

---

**Recuerda:** Estas reglas son para mantener la calidad y consistencia del proyecto MaestroCan IA. Cualquier excepción debe ser justificada y documentada.