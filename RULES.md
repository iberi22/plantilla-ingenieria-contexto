### 🔄 Conciencia del Proyecto y Contexto

- **Siempre lee `PLANNING.md`** al inicio de una nueva conversación para entender la arquitectura, objetivos y restricciones del proyecto.
- **Consulta `TASK.md`** antes de iniciar una nueva tarea. Si la tarea no está listada, añádela con una breve descripción.

### 🧱 Estructura de Código y Modularidad

- **Nunca crees archivos de más de 500 líneas.** Si un archivo se acerca a este límite, proponme refactorizarlo en módulos más pequeños.
- **Organiza el código en módulos claramente separados**, agrupados por funcionalidad.

### 🧪 Pruebas y Fiabilidad

- **Siempre crea pruebas unitarias (Pytest) para cada nueva funcionalidad** (funciones, clases, endpoints).
- Las pruebas deben residir en una carpeta `/tests` que refleje la estructura de la aplicación principal.
- Incluye como mínimo: 1 prueba para el caso de uso esperado, 1 para un caso límite (edge case) y 1 para un caso de fallo.

### ✅ Finalización de Tareas

- **Marca las tareas como completadas en `TASK.md`** inmediatamente después de terminarlas.
- **Añade nuevas subtareas o TODOs descubiertos** durante el desarrollo a `TASK.md` en la sección "Tareas Descubiertas".

### 📎 Estilo y Convenciones

- **Lenguaje principal:** [Ej: Python].
- **Sigue las convenciones de estilo** [Ej: PEP8] y formatea el código con [Ej: `black`].
- **Usa docstrings para cada función** siguiendo el estilo [Ej: Google].

### 🧠 Comportamiento de la IA

- **Nunca asumas contexto faltante.** Haz preguntas si algo no está claro.
- **Nunca alucines librerías o funciones.** Usa únicamente paquetes conocidos y verificados.
- **Confirma siempre las rutas de archivos y los nombres de los módulos** antes de referenciarlos en el código o en las pruebas.
