# Instrucciones para Devin — [Nombre del Proyecto / Cliente]

> **Template para proyectos de consultoría.**
> Adapta cada sección reemplazando los marcadores `[...]` con la información del proyecto concreto.

---

## Descripción del proyecto

[Breve descripción del proyecto, su propósito y el cliente al que pertenece.]

## Stack tecnológico

| Capa | Tecnología |
|------|------------|
| [Capa] | [Tecnología y versión] |

## Estructura del proyecto

```
[Incluir árbol de directorios relevante]
```

---

## 1. Archivos protegidos — No modificar sin aprobación explícita

Los siguientes archivos y directorios **nunca** deben ser modificados por Devin sin aprobación
previa del responsable técnico del proyecto. Ante cualquier necesidad de cambio, Devin debe
notificar y esperar confirmación antes de proceder.

### Configuración de producción

- `**/production.*`, `**/prod.*` — Ficheros de configuración de entorno productivo
- `.env.production`, `config/production.yml`, `settings/prod.py`
- Archivos de variables de entorno con valores reales (no plantillas)
- Configuración de bases de datos de producción

### CI/CD

- `.github/workflows/` — Pipelines de GitHub Actions
- `.gitlab-ci.yml` — Pipelines de GitLab CI
- `Jenkinsfile`, `azure-pipelines.yml`
- `Dockerfile` y `docker-compose.yml` de producción
- Configuración de despliegue (`deploy/`, `k8s/`, `.helm/`)

### Infraestructura como código (IaC)

- `terraform/`, `*.tf`, `*.tfvars`
- `cloudformation/`, `*.cfn.yml`
- `pulumi/`, `ansible/`, `cdk/`
- Cualquier archivo bajo carpetas de infraestructura

### Seguridad y políticas

- Políticas de acceso (IAM, RBAC, políticas de red)
- Configuración de certificados y secretos
- Reglas de firewall y security groups
- Archivos `.npmrc`, `.pypirc` con configuración de registros privados

### Otros archivos críticos del cliente

- `[Añadir archivos específicos del proyecto que el cliente considere sensibles]`

> **Protocolo ante necesidad de cambio:**
> 1. Identificar el archivo protegido y el cambio necesario
> 2. Notificar al responsable técnico con: qué cambiar, por qué y el impacto esperado
> 3. Esperar aprobación explícita antes de realizar cualquier modificación
> 4. Documentar la aprobación en la descripción del PR

---

## 2. Gestión de datos sensibles

### Principios generales

- **Nunca** registrar, imprimir o exponer datos sensibles en logs, comentarios o salidas de consola
- **Nunca** incluir datos sensibles en mensajes de commit, descripciones de PR o documentación
- **Nunca** copiar datos sensibles entre entornos (producción → desarrollo)
- Si un archivo contiene datos reales de clientes/usuarios, tratarlo como confidencial

### Qué se considera dato sensible

- Credenciales: contraseñas, tokens, API keys, certificados, claves privadas
- Datos personales: nombres, emails, teléfonos, direcciones, documentos de identidad
- Datos financieros: números de tarjeta, cuentas bancarias, información fiscal
- Datos de negocio: lógica propietaria del cliente, algoritmos confidenciales
- Infraestructura: IPs internas, URLs de servicios internos, topología de red

### Protocolo al encontrar datos sensibles en el código

1. **No copiar** el valor sensible en ningún output ni herramienta
2. **Notificar** al responsable técnico inmediatamente indicando:
   - Archivo y línea donde se encontró
   - Tipo de dato sensible (sin revelar el valor)
   - Riesgo estimado de la exposición
3. **Sugerir** remediación (uso de variables de entorno, secrets manager, etc.)
4. **No realizar commits** que perpetúen la exposición del dato

---

## 3. Protocolo ante credenciales expuestas

Si Devin detecta credenciales expuestas (hardcodeadas en código, en archivos versionados,
en logs o documentación), debe seguir este protocolo **de forma inmediata**:

### Severidad CRÍTICA — Credenciales de producción

1. **DETENER** cualquier otra actividad en curso
2. **Notificar** al responsable técnico con máxima urgencia:
   - Archivo, línea y tipo de credencial (sin incluir el valor)
   - Si el archivo está versionado y posiblemente expuesto en historial de Git
3. **No realizar ningún commit** hasta que se resuelva
4. **Sugerir acciones de remediación**:
   - Rotación inmediata de la credencial
   - Eliminación del archivo del historial (`git filter-branch` o BFG Repo-Cleaner)
   - Migración a un gestor de secretos (AWS Secrets Manager, HashiCorp Vault, etc.)

### Severidad MEDIA — Credenciales de desarrollo/staging

1. **Notificar** al responsable técnico
2. **Proponer** un PR que reemplace la credencial por una referencia a variable de entorno
3. **Documentar** en el PR la ubicación original y la remediación aplicada

### Severidad BAJA — Credenciales de ejemplo o placeholder

1. **Verificar** que efectivamente son valores ficticios (ej. `password123`, `xxx-api-key`)
2. Si son reales disfrazadas de ejemplo, tratar como severidad MEDIA
3. Si son claramente ficticias, continuar con el trabajo normal

---

## 4. Restricciones sobre ramas protegidas

### Ramas donde NUNCA se debe hacer commit directo

- `main` / `master` — Rama principal de producción
- `release/*` — Ramas de release
- `hotfix/*` — Solo mediante PR con aprobación
- `[Añadir ramas protegidas específicas del proyecto]`

### Flujo obligatorio

1. **Siempre** crear una rama de trabajo desde la rama base correspondiente
2. **Siempre** abrir un Pull Request para integrar cambios
3. **Nunca** usar `--force-push` en ramas compartidas o protegidas
4. **Nunca** hacer merge directo sin revisión en ramas protegidas
5. **Nunca** eliminar ramas protegidas

### Política de aprobaciones

- PRs a `main`/`master` requieren **al menos 1 aprobación** del equipo del cliente
- PRs que modifiquen archivos protegidos (sección 1) requieren **aprobación explícita del lead**
- No realizar merge si hay conversaciones sin resolver en el PR

---

## 5. Naming de ramas y commits

### Nomenclatura de ramas

Formato: `tipo/ID-descripcion-breve`

| Tipo | Uso |
|------|-----|
| `feat/` | Nueva funcionalidad |
| `fix/` | Corrección de bug |
| `refactor/` | Refactorización sin cambio funcional |
| `docs/` | Cambios en documentación |
| `test/` | Adición o mejora de tests |
| `chore/` | Tareas de mantenimiento |
| `hotfix/` | Corrección urgente para producción |

Ejemplos:
```
feat/JIRA-123-add-user-authentication
fix/JIRA-456-null-pointer-in-payment
refactor/JIRA-789-extract-validation-service
```

Reglas:
- Usar **kebab-case** (minúsculas separadas por guión)
- Incluir el **ID del ticket** cuando exista (JIRA, Azure DevOps, etc.)
- Descripción corta pero descriptiva (máx. 50 caracteres)
- Prefijo `devin/` opcional para identificar ramas creadas por Devin:
  `devin/feat/JIRA-123-add-user-authentication`

### Nomenclatura de commits

Formato: `tipo(alcance): descripción breve`

```
feat(auth): add JWT token validation middleware
fix(payments): handle null amount in refund calculation
docs(api): update endpoint documentation for /users
test(orders): add integration tests for order cancellation
```

Reglas:
- **tipo**: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `perf`, `ci`
- **alcance** (opcional): módulo o componente afectado
- **descripción**: imperativo, minúsculas, sin punto final, máx. 72 caracteres
- Un commit por **cambio lógico** — no agrupar cambios no relacionados
- Mensajes en **inglés** (o según convención del proyecto: `[idioma]`)

---

## 6. Descripción obligatoria en Pull Requests

Todo PR creado por Devin **debe** incluir las siguientes secciones:

### Template de PR

```markdown
## Resumen

[Qué cambió y por qué — descripción concisa del objetivo del PR]

## Contexto

- Ticket/Issue: [Link al ticket o "N/A"]
- Solicitud original: [Resumen de lo que se pidió a Devin]

## Cambios realizados

- [Lista de cambios principales, agrupados por componente]

## Archivos modificados relevantes

| Archivo | Tipo de cambio |
|---------|---------------|
| `path/to/file` | [Nuevo / Modificado / Eliminado] |

## Impacto y riesgos

- [ ] No modifica archivos protegidos
- [ ] No introduce dependencias nuevas / Introduce: [lista]
- [ ] No afecta a otros servicios / Afecta: [lista]
- [ ] Backward compatible / Breaking change: [descripción]

## Testing

- [ ] Tests unitarios añadidos/actualizados
- [ ] Tests de integración (si aplica)
- Cómo probar manualmente:
  ```
  [Comandos o pasos para verificar el cambio]
  ```

## Checklist de consultoría

- [ ] Código no contiene datos sensibles hardcodeados
- [ ] No se modificaron archivos protegidos sin aprobación
- [ ] Nomenclatura de rama y commits sigue la convención
- [ ] Documentación actualizada (si aplica)
- [ ] Cambios limitados al alcance solicitado — sin modificaciones fuera de scope
```

### Reglas adicionales para PRs

- **Scope mínimo**: Cada PR debe contener únicamente los cambios necesarios para la tarea
  asignada. No incluir refactorizaciones, mejoras o cambios "de paso" sin aprobación.
- **Sin archivos generados**: No incluir en el PR archivos compilados, caches, logs o bases
  de datos locales.
- **Trazabilidad**: Siempre referenciar el ticket o la solicitud que origina el cambio.
- **Screenshots/evidencia**: Incluir capturas de pantalla cuando el cambio afecte UI.

---

## 7. Reglas generales de conducta en proyectos de cliente

### Lo que Devin SIEMPRE debe hacer

- Preguntar antes de actuar en caso de ambigüedad
- Mantener el principio de mínimo privilegio en cada acción
- Documentar cualquier decisión técnica no trivial
- Respetar las convenciones existentes del proyecto antes de proponer nuevas

### Lo que Devin NUNCA debe hacer

- Modificar código fuera del alcance solicitado
- Instalar dependencias sin justificación y aprobación
- Acceder o manipular datos de producción
- Eliminar código sin entender su propósito (puede ser requerimiento del cliente)
- Compartir información del proyecto en herramientas externas
- Hacer suposiciones sobre la arquitectura sin validar con el equipo

---

## Adaptación del template

Para usar este template en un nuevo proyecto:

1. Reemplazar todos los marcadores `[...]` con información específica del proyecto
2. Revisar la sección de archivos protegidos y añadir los propios del cliente
3. Ajustar la nomenclatura de ramas si el cliente usa otro sistema de tickets
4. Definir el idioma de commits según acuerdo con el equipo
5. Añadir secciones específicas del stack tecnológico del proyecto
6. Validar con el lead técnico y el cliente antes de implementar
