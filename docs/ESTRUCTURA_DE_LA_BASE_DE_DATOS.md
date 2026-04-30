# ESTRUCTURA DE LA BASE DE DATOS

Este documento define el esquema funcional de datos y las reglas para modificarlo sin romper la app.

## 1) Estrategia por entorno

- Servidor/produccion: PostgreSQL.
- Desarrollo local: SQLite ([db.sqlite3](../db.sqlite3)).

Archivo de referencia de configuracion: [formaciones/settings.py](../formaciones/settings.py).

Nota operativa:

- En el estado actual del settings hay un bloque SQLite comentado y un bloque PostgreSQL activo.
- No dejar credenciales hardcodeadas en cambios futuros.

## 2) Tablas de negocio (app formacion)

Los nombres de tabla siguen convencion Django: `formacion_<modelo>`.

### 2.1 formacion_polivalencia (modelo `polivalencia`)

Clave funcional:

- `OPERARIO` (unique).

Campos de nivel (IntegerField, default=0):

- `CONFIRM`
- `OPEN_MAIL`
- `ORDER_ENTRY_SERVICE`
- `ORDER_ENTRY_NEW`
- `DIAG_ITE`
- `DIAG_ITE_SAF`
- `DIAG_SDS`
- `DIAG_SDS_SAF`
- `DIAG_BTE`
- `DIAG_FM_DWA`
- `DIAG_TITANIUM`
- `REPAIR_FM_DWA`
- `REPAIR_CARGADORES`
- `REPAIR_BTE`
- `RSM`
- `MINI_KITTING`
- `KITTING_CUSTOM`
- `KITTING_BTE`
- `DCC`
- `DLP`
- `KIT_PREP_SDS`
- `CLOSING_SDS`
- `KIT_PREP_ITE`
- `CLOSING_ITE`
- `CUT_TRIM`
- `FL`
- `TITANIUM`
- `VISUAL_ITE`
- `VISUAL_SDS`
- `VISUAL_BTE`
- `VISUAL_FM_DWA`
- `PRO_GO_ITE`
- `PRO_GO_SDS`
- `PRO_GO_BTE`
- `PRO_GO_FM_DWA`
- `PACKING_NEW`
- `PACKING_SERVICE`
- `RPM_DESMONTAJE_LIMPIEZA`
- `RPM_DECONTAMINACION`
- `RPM_IRS1_IDENTIFICACION`
- `RPM_LPS2_BLUETOOTH`
- `RPM_VISUAL_SNW2`
- `ACS2`
- `SORTING`
- `REFURBISHING`
- `REPROCESSING_CARGADORES`
- `PACKING_RPM_REFURBISHING`

Auditoria:

- `creado_por` (FK auth_user, SET_NULL)
- `creado_en`
- `modificado_por` (FK auth_user, SET_NULL)
- `modificado_en`

### 2.2 formacion_nuevas_opis (modelo `nuevas_opis`)

Clave funcional:

- `OPI` (unique).

Campos:

- `INFO`
- `SECCION1..SECCION7` (CharField)
- `ok_supervisor` (JSONField)

Auditoria igual que el resto de modelos de negocio.

### 2.3 formacion_opis (modelo `opis`)

Clave funcional:

- `OPI` (unique).

Campos:

- `INFO`
- `SECCION1..SECCION7`
- `formados` (JSONField)
- `firmas` (JSONField)

Auditoria incluida.

### 2.4 formacion_completa (modelo `completa`)

Campos:

- `PUESTO` (CharField)
- `OPERARIO` (CharField)
- `TEORIA` (bool)
- `PRACTICA` (bool)
- `PRODUCTO` (bool)
- `firmas` (JSONField)

Auditoria incluida.

Importante:

- No hay constraint unique para `(OPERARIO, PUESTO)` en modelo actual.
- Varias vistas asumen un unico registro y usan `.get()` o `.first()`.

### 2.5 formacion_auditoria (modelo `auditoria`)

Campos:

- `DIA`
- `SAP`
- `NUM_SERIE`
- `FAMILIA`
- `PROCESO`
- `AUDITOR`
- `OPERARIO`
- `NO_CONFORMIDAD`
- `OBSERVACIONES`

Auditoria incluida.

### 2.6 formacion_notificacion (modelo `Notificacion`)

Campos:

- `grupo` (FK auth_group, nullable, CASCADE)
- `usuario` (FK auth_user, nullable, CASCADE)
- `mensaje`
- `creado_en`
- `creado_por` (FK auth_user, nullable, CASCADE)

Relacion M2M:

- `leido_por` con auth_user (tabla intermedia generada por Django).

### 2.7 formacion_passwordchangestatus (modelo `PasswordChangeStatus`)

Campos:

- `user` (OneToOne con auth_user)
- `last_password_change`

## 3) Tablas del ecosistema Django

Tambien forman parte operativa de la app:

- `auth_user`, `auth_group`, `auth_permission`, tablas M2M auth.
- `django_admin_log`.
- `django_content_type`.
- `django_migrations`.
- `django_session`.
- tablas de `axes` para control de intentos de login.

## 4) Relaciones clave

- `polivalencia` -> `auth_user` (auditoria por FK nullable).
- `nuevas_opis` -> `auth_user` (auditoria).
- `opis` -> `auth_user` (auditoria).
- `completa` -> `auth_user` (auditoria).
- `auditoria` -> `auth_user` (auditoria).
- `Notificacion.grupo` -> `auth_group`.
- `Notificacion.usuario` -> `auth_user`.
- `Notificacion.leido_por` <-> `auth_user` (M2M).
- `PasswordChangeStatus.user` <-> `auth_user` (1:1).

## 5) Contratos JSON (criticos)

### 5.1 completa.firmas

Claves usadas por vistas/templates/documentos:

- `firma_alumno`
- `firma_formador`
- `firma_supervisor`
- `firma_dpto`
- `dni`
- `supervisor`
- `fecha_teoria`, `porcentaje_teoria`
- `fecha_practica`, `porcentaje_practica`
- `fecha_producto`, `porcentaje_producto`
- `PDF`

No renombrar estas claves sin migracion de datos y ajuste total de vistas/templates.

### 5.2 opis.formados

- Estructura esperada: `{ "OPERARIO": "YYYY-MM-DD" }`.

### 5.3 opis.firmas

- Estructura esperada: `{ "OPERARIO": "ruta_archivo" }`.

### 5.4 nuevas_opis.ok_supervisor

- Estructura esperada: `{ "SECCIONX": "ok|ko" }`.

## 6) Invariantes de negocio

- `polivalencia.OPERARIO` unico.
- `OPI` unica en `nuevas_opis` y `opis`.
- Semantica de niveles en matriz:
  - 0 sin formacion
  - 1 en formacion
  - 2 formado
  - 3 experto
- Al actualizar matriz, para nivel 1 se crea entrada en `completa` si no existe.

## 7) Riesgos de datos a vigilar

- Posibles duplicados `(OPERARIO, PUESTO)` en `completa` por falta de unique constraint.
- Uso de estado global en vistas puede afectar consistencia de escrituras.
- Campos JSON sin esquema rigido: cambios de clave rompen runtime facilmente.
- Si no se aplican migraciones, el codigo y la BD pueden quedar desalineados.

## 8) Regla especial de migraciones

En [.gitignore](../.gitignore) existe:

- `formacion/migrations/*`

Impacto:

- Migraciones nuevas pueden no quedar en commit automaticamente.
- Si hay migracion nueva, revisar `git status` y considerar `git add -f`.

## 9) Como cambiar el esquema sin romper

Proceso recomendado:

1. Definir cambio de modelo y su impacto en forms/views/templates.
2. Crear migracion.
3. Aplicar migracion local.
4. Ajustar codigo consumidor (filtros, serializers manuales, templates, JSON).
5. Ejecutar checks y smoke tests funcionales.

Comandos:

```powershell
.\.venv\Scripts\python.exe manage.py makemigrations
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py test
```

## 10) Checklist rapido de validacion de datos

Antes de cerrar cambio con impacto en BD:

1. El modelo nuevo coincide con migraciones.
2. No se rompieron claves JSON existentes.
3. Flujo OPI y flujo formacion completa siguen guardando y leyendo datos.
4. Se generan PDFs y se pueden abrir.
5. Se valida login, password_change y notificaciones.

