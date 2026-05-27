# ADR-001: Elección de SQLite como base de datos

## Estado

**Aceptado**

## Fecha

2025-05-20

## Contexto

La API de Gestión de Tareas necesita una base de datos relacional para persistir tareas con sus
atributos (título, descripción, estado y fecha de creación). El proyecto tiene las siguientes
características que condicionan la elección:

- Es una API REST de alcance limitado, con un único recurso principal (`tasks`) y un volumen de
  datos bajo-medio.
- El equipo de desarrollo es reducido y se prioriza la velocidad de puesta en marcha frente a la
  escalabilidad horizontal.
- El despliegue inicial se realiza en un solo servidor, sin necesidad de acceso concurrente desde
  múltiples instancias.
- Se utiliza **SQLAlchemy 2.0** como ORM, que abstrae la capa de acceso a datos y facilita una
  posible migración futura a otro motor relacional.
- Los tests necesitan una base de datos aislada que no interfiera con los datos de producción.

## Decisión

Se elige **SQLite** como motor de base de datos, almacenando los datos en el archivo local
`tareas.db`. La conexión se configura con el parámetro `check_same_thread=False` para permitir
su uso con FastAPI y Uvicorn en un entorno asíncrono con múltiples hilos.

Para los tests, se utiliza una base de datos SQLite independiente (`test_tareas.db`) que se crea y
destruye en cada ejecución, garantizando el aislamiento total respecto a los datos de producción.

## Razones de la decisión

1. **Cero configuración**: SQLite no requiere instalar ni administrar un servidor de base de datos
   externo. Basta con la biblioteca estándar de Python (`sqlite3`) que ya incluye el driver.
2. **Portabilidad**: la base de datos es un único archivo que se puede copiar, respaldar o
   trasladar fácilmente entre entornos.
3. **Arranque inmediato**: no hay pasos de provisioning, creación de usuarios ni asignación de
   permisos. El desarrollador clona el repositorio, instala dependencias y ejecuta la API.
4. **Compatibilidad con SQLAlchemy**: SQLAlchemy soporta SQLite de forma nativa, lo que permite
   definir modelos ORM estándar que son reutilizables si se migra a otro motor.
5. **Ideal para tests**: se pueden crear bases de datos en memoria o temporales de forma
   instantánea, sin infraestructura adicional.
6. **Bajo consumo de recursos**: no hay proceso de servidor ejecutándose en segundo plano,
   reduciendo el uso de memoria y CPU en entornos de desarrollo y CI/CD.

## Alternativas consideradas

### PostgreSQL

**Ventajas:**

- Soporte completo de tipos de datos avanzados (JSON, arrays, rangos, UUID nativo).
- Alta concurrencia: modelo MVCC robusto que gestiona múltiples conexiones simultáneas sin bloqueos
  a nivel de archivo.
- Escalabilidad horizontal mediante réplicas de lectura y particionado de tablas.
- Ecosistema maduro de extensiones (PostGIS, pg_trgm, pgcrypto, etc.).
- Transacciones ACID completas con niveles de aislamiento configurables.

**Inconvenientes:**

- Requiere instalar y mantener un servidor de base de datos independiente.
- Configuración inicial compleja: creación de usuarios, roles, bases de datos y permisos.
- Mayor consumo de recursos (memoria y CPU) incluso en reposo.
- Añade una dependencia externa al entorno de desarrollo, complicando el onboarding de nuevos
  colaboradores.
- Sobredimensionado para el volumen de datos y la concurrencia actuales del proyecto.

### MySQL

**Ventajas:**

- Amplia adopción en la industria y gran cantidad de documentación disponible.
- Buen rendimiento en operaciones de lectura intensiva gracias a sus mecanismos de caché.
- Herramientas de administración gráficas maduras (MySQL Workbench, phpMyAdmin).
- Soporte nativo de replicación maestro-esclavo para alta disponibilidad.

**Inconvenientes:**

- Requiere instalar y administrar un servidor independiente, al igual que PostgreSQL.
- Implementación parcial del estándar SQL (limitaciones históricas en subconsultas, CTEs y
  window functions en versiones anteriores).
- El manejo de encodings y colaciones puede ser problemático si no se configura correctamente
  desde el inicio (por ejemplo, `utf8` vs. `utf8mb4`).
- Licencia dual (GPL / comercial) que puede generar incertidumbre en ciertos contextos de uso.
- No aporta ventajas claras sobre PostgreSQL para este caso de uso y añade las mismas
  complejidades de infraestructura.

## Consecuencias

### Positivas

- **Desarrollo ágil**: cualquier desarrollador puede levantar el proyecto completo en minutos sin
  configurar infraestructura de base de datos.
- **CI/CD simplificado**: el pipeline de integración continua no necesita un servicio de base de
  datos externo; los tests se ejecutan directamente contra SQLite.
- **Costes de infraestructura nulos**: no se requiere un servicio gestionado de base de datos en
  la fase inicial del proyecto.

### Negativas y riesgos a largo plazo

- **Concurrencia limitada**: SQLite utiliza bloqueo a nivel de archivo para las escrituras. Si la
  aplicación escala a múltiples instancias o un volumen alto de escrituras concurrentes, se
  convertirá en un cuello de botella.
- **Sin acceso remoto nativo**: SQLite no expone un protocolo de red; solo la instancia local del
  servidor puede acceder a los datos. Esto impide arquitecturas con múltiples servicios accediendo
  a la misma base de datos.
- **Funcionalidades SQL reducidas**: SQLite no soporta de forma nativa `ALTER TABLE DROP COLUMN`
  (en versiones anteriores a 3.35), tipos de datos estrictos ni procedimientos almacenados.
  Migraciones complejas pueden requerir recrear tablas completas.
- **Migración futura necesaria**: si el proyecto crece en usuarios o complejidad, será necesario
  migrar a PostgreSQL u otro motor cliente-servidor. Gracias a SQLAlchemy, el impacto en el código
  de la aplicación será mínimo (cambio de URL de conexión y ajuste de parámetros específicos del
  driver), pero los datos deberán exportarse e importarse.
- **Sin gestión de usuarios ni permisos**: SQLite no tiene un sistema de autenticación o control de
  acceso integrado. La seguridad depende enteramente de los permisos del sistema de archivos.

### Señales para reconsiderar esta decisión

- El proyecto requiere acceso concurrente desde más de una instancia de la aplicación.
- El volumen de escrituras simultáneas supera lo que SQLite puede gestionar sin degradación.
- Se necesita acceso remoto a la base de datos desde otros servicios o herramientas de análisis.
- Se requieren funcionalidades avanzadas de SQL no soportadas por SQLite (tipos JSON consultables,
  full-text search avanzado, replicación).
