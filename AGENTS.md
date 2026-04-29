# AGENTS.md

Guia operativa para agentes que trabajen en este repositorio.
Objetivo: permitir cambios seguros sin romper flujos de negocio, rutas, permisos ni generacion de documentos.

## 1) Mision del proyecto

Aplicacion Django para gestionar:

- Matriz de polivalencia de operarios por puesto/proceso.
- OPIs: alta, validacion por supervisores, firma y generacion de actas.
- Formacion completa por puesto: teoria, practica, producto, firmas y PDF final.
- Auditoria diaria por operario/proceso.
- Notificaciones internas por usuario/grupo.

## 2) Estado tecnico actual (resumen rapido)

- Lenguaje: Python.
- Framework: Django (requirements fija Django==5.2.7).
- DB por entorno: PostgreSQL en servidor/produccion y SQLite ([db.sqlite3](db.sqlite3)) solo en desarrollo local.
- OS objetivo: Windows (hay rutas UNC y LibreOffice en ruta de Windows).
- Templates: Django templates + JS en cliente (sin SPA).
- PDFs: python-docx + LibreOffice (subprocess) + PyPDF2 + FPDF.
- Excel: pandas/openpyxl para cargar y exportar matriz.
- Seguridad login: django-axes + expiracion de contrasena.

Nota: [formaciones/settings.py](formaciones/settings.py) aun contiene cabecera generada de Django 4.2.4, pero dependencias y migraciones activas son 5.2.x.

## 3) Mapa del repo (solo piezas relevantes)

- [manage.py](manage.py): entrypoint Django.
- [requirements.txt](requirements.txt): dependencias reales del proyecto.
- [formaciones/settings.py](formaciones/settings.py): configuracion global.
- [formaciones/urls.py](formaciones/urls.py): rutas raiz (admin, auth, include app).
- [formacion/models.py](formacion/models.py): 7 modelos de negocio.
- [formacion/forms.py](formacion/forms.py): formularios de filtros/alta/edicion.
- [formacion/views.py](formacion/views.py): logica principal (57 funciones + 2 clases).
- [formacion/urls.py](formacion/urls.py): 37 rutas de app.
- [formacion/middleware.py](formacion/middleware.py): expiracion de password.
- [formacion/signals.py](formacion/signals.py): notificacion de bloqueos por axes.
- [formacion/templates](formacion/templates): 22 templates.
- [formacion/templatetags/custom_filters.py](formacion/templatetags/custom_filters.py): filtros de template.
- [media/plantillas](media/plantillas): plantillas .txt/.docx usadas en los flujos.

Directorios que NO deben tocarse manualmente salvo necesidad justificada:

- [staticfiles](staticfiles): output de collectstatic.
- [formacion/__pycache__](formacion/__pycache__) y similares.

## 4) Entorno y comandos confiables

### 4.1 Regla critica de ejecucion

Usar SIEMPRE el Python de la venv local del repo para comandos Django:

```powershell
.\.venv\Scripts\python.exe manage.py check
```

No confiar en `python` a secas: en este equipo puede resolver a otro entorno.

### 4.2 Setup base

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py runserver
```

### 4.3 Validacion minima antes de cerrar cambios

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py test
```

Estado actual observado: `manage.py check` sin issues, `manage.py test` sin tests (0).

## 5) Configuracion critica (no romper)

Archivo clave: [formaciones/settings.py](formaciones/settings.py)

- `INSTALLED_APPS` incluye `axes` y `formacion.apps.FormacionConfig`.
- `MIDDLEWARE` incluye `axes.middleware.AxesMiddleware` y `formacion.middleware.PasswordExpiryMiddleware`.
- `AUTHENTICATION_BACKENDS` incluye AxesStandaloneBackend + ModelBackend.
- `PASSWORD_EXPIRATION_DAYS = 90`.
- `SESSION_COOKIE_AGE = 7200`.
- `CSRF_USE_SESSIONS = True`.
- `LIBREOFFICE_PATH` apunta a `C:\Program Files\LibreOffice\program\soffice.exe`.
- `STATICFILES_STORAGE` usa WhiteNoise con manifest.
- En servidor la app opera con PostgreSQL; SQLite queda solo para entorno local de desarrollo.

### 5.1 Variables de entorno recomendadas para PostgreSQL (servidor)

Para despliegue en servidor, parametrizar al menos:

- DB_ENGINE (valor recomendado: django.db.backends.postgresql)
- DB_NAME
- DB_USER
- DB_PASSWORD
- DB_HOST
- DB_PORT (valor habitual: 5432)

Reglas operativas:

- No guardar credenciales en el repo ni hardcodearlas en settings.
- Mantener SQLite solo para desarrollo local.
- Validar conexion y esquema en servidor con:

```powershell
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py check
```

Riesgos de seguridad ya presentes (no introducir mas):

- `DEBUG = True`.
- `ALLOWED_HOSTS` abierto con `*`.
- `SECRET_KEY` hardcodeada.

Si se toca seguridad, documentar impacto y validar login/logout/password_change.

## 6) Modelos y contratos de datos

Archivo: [formacion/models.py](formacion/models.py)

### 6.1 Modelos

- `polivalencia`: operario + campos enteros de nivel por puesto/proceso.
- `nuevas_opis`: OPI en revision, con `ok_supervisor` (JSON).
- `opis`: OPI validada, con `formados` y `firmas` (JSON).
- `completa`: estado de formacion por `(OPERARIO, PUESTO)` + `firmas` (JSON).
- `auditoria`: registro diario de auditoria.
- `Notificacion`: notificaciones por grupo o usuario; `leido_por` M2M.
- `PasswordChangeStatus`: fecha ultimo cambio de password por usuario.

### 6.2 Invariantes de datos

- `polivalencia.OPERARIO` es unico.
- `nuevas_opis.OPI` y `opis.OPI` son unicos.
- Niveles de `polivalencia` en practica: 0,1,2,3,4.
- Flujo actual usa `completa` para registrar progreso de teoria/practica/producto y firmas.
- JSON keys de `completa.firmas` se usan en varias vistas/templates (no renombrar sin migracion de datos):
  - `firma_alumno`, `firma_formador`, `firma_supervisor`, `firma_dpto`
  - `dni`, `supervisor`
  - `fecha_teoria`, `porcentaje_teoria`
  - `fecha_practica`, `porcentaje_practica`
  - `fecha_producto`, `porcentaje_producto`
  - `PDF`

### 6.3 Campos de auditoria

Todos los modelos de negocio principales tienen `creado_por/creado_en/modificado_por/modificado_en`.
Mantener coherencia al crear/modificar registros.

## 7) Matriz de niveles de polivalencia (semantica)

Uso observado en templates y vistas:

- 0: sin formacion.
- 1: formado, no puesto habitual.
- 2: formado, puesto habitual.
- 3: experto.
- 4: en formacion.

Regla critica: al actualizar matriz desde Excel, se crean entradas en `completa` para combinaciones con nivel 4 si no existen.

## 8) Permisos, grupos y control de acceso

Grupos de referencia (strings exactos):

- `admin`
- `formacion`
- `supervisores`
- `tecnicos`

Decoradores custom:

- `groups_required(...)` en [formacion/views.py](formacion/views.py).
- `@login_required` en la mayoria de vistas privadas.

`FormacionConfig.ready()` importa señales, no eliminar esa llamada:
[formacion/apps.py](formacion/apps.py).

## 9) Inventario de rutas (contrato de UI)

Archivo: [formacion/urls.py](formacion/urls.py)

Las plantillas usan estos `name` de URL. Renombrarlos rompe navegacion:

- `inicio`
- `registro`
- `logout_message`
- `timeout`
- `formacion_completa`
- `completar_teoria`
- `completar_practica`
- `completar_producto`
- `formacion_opis`
- `actualizar_matriz`
- `editar_matriz`
- `agregar_tecnico`
- `eliminar_tecnico`
- `editar_tecnico`
- `nueva_opi`
- `guardar_opi`
- `listar_opis`
- `aceptar_opi`
- `rechazar_opi`
- `introducir_fecha`
- `guardar_fecha`
- `introducir_firma`
- `firmar_formacion`
- `subir_firma`
- `guardar_firma`
- `generar_pdf`
- `ver_pdf_opi`
- `ver_pdf_form`
- `descargar_polivalencia`
- `notificaciones`
- `notificacion_leida`
- `password_change`
- `password_change_done`
- `grafica`
- `auditoria_diaria`
- `registrar_auditoria`
- `edicion_plantillas`

En [formaciones/urls.py](formaciones/urls.py):

- `admin/`
- include app en raiz
- `login/`
- `logout/`

## 10) Flujos funcionales E2E (resumen operativo)

### 10.1 Matriz de polivalencia

- Vista: `actualizar_matriz`.
- Lee Excel `TPL-708 [4] RCSE Matriz de Polivalencia Operarios produccion.xlsx` en raiz del repo.
- Renombra columnas con `column_mapping`.
- Borra y recrea `polivalencia`.
- Sincroniza/crea entradas en `completa` para niveles 4.

Impacto de cambio: cualquier cambio en nombres de columnas/campos rompe importacion.

### 10.2 OPI

- Alta en `nueva_opi` + `guardar_opi` (tabla `nuevas_opis`).
- Validacion por supervisor en `listar_opis` + `aceptar_opi/rechazar_opi`.
- Promocion a `opis` cuando todas secciones estan gestionadas.
- Fechas por operario en `guardar_fecha` (`opis.formados`).
- Firma en `subir_firma` (canvas base64 -> docx -> pdf) y guardado en `opis.firmas`.

### 10.3 Formacion completa

- `formacion_completa` selecciona operario/puesto.
- `completar_teoria`: requiere >=80% acierto.
- `completar_practica`: requiere >=80% respuestas "Si".
- `completar_producto`: requiere 100% "No" en no conformidad.
- `firmar_formacion` + `guardar_firma`: 4 firmas.
- `generar_pdf`: compone documentos con plantillas docx + merge de PDFs.

### 10.4 Auditoria diaria

- `auditoria_diaria`: filtro por operario + historial ultimos 90 dias.
- `registrar_auditoria`: alta de auditoria con NO_CONFORMIDAD y observaciones.

### 10.5 Notificaciones

- `notificaciones` lista no leidas por grupo/usuario.
- `notificacion_leida` marca lectura.
- Señal de Axes crea notificaciones a superusuarios al bloquear login.

## 11) Contratos frontend-backend sensibles (NO renombrar sin sincronizar)

### 11.1 Campos POST usados en vistas

- `guardar_opi`: `tipo`, `ID`, `version`, `INFO`, `SECCION1..SECCION7`.
- `guardar_fecha`: `operario`, `fecha`.
- `subir_firma`: `operario`, `imagen`, `dni`, `supervisor`.
- `guardar_firma`: `operario`, `puesto`, `tipo_firma`, `imagen`, opcional `dni/supervisor`.
- `completar_teoria`: `operario_nombre`, `puesto_seleccionado`, `respuesta_{indice}`.
- `completar_practica`: `operario_nombre`, `puesto_seleccionado`, `respuesta_{indice}`.
- `completar_producto`: arrays `estado_pieza[]`, `no_conformidad[]`, `descripcion_no_conformidad[]`, `tipo_no_conformidad[]`.
- `registrar_auditoria`: `SAP`, `NUM_SERIE`, `FAMILIA`, `PUESTO`, `AUDITOR`, `OPERARIO`, `NO_CONFORMIDAD`, `OBSERVACIONES`.
- `edicion_plantillas`: `accion` (`guardar|crear|eliminar`), `nombre_archivo`, `contenido`, `dir_actual`, `file_rel`.

### 11.2 Dependencia JS de timeout

Muchos templates llaman `timeout` por inactividad (fetch + redirect).
No eliminar la ruta ni romper su semantica sin actualizar todos los templates.

## 12) Contratos de archivos y rutas de almacenamiento

Archivo clave: [formacion/views.py](formacion/views.py)

Se usa:

- `BASE_URL = getattr(settings, 'TRAINING_SHARED_ROOT', r"\\es01sw31\APP Training Tool")`
- Helpers: `shared_path`, `shared_media_path`, `shared_plantillas_path`.

Por tanto, la app no asume solo [media](media) local; puede apuntar a share de red.

### 12.1 Entradas esperadas

- `media/plantillas/teoria/{PUESTO}.txt`
- `media/plantillas/practica/{PUESTO}.txt`
- `media/plantillas/validaciones/Validacion Initial Training fase 1.docx`
- `media/plantillas/validaciones/Validacion Initial Training fase 2.docx`
- `media/plantillas/validaciones/Validacion Initial Training fase 3.docx`
- `media/plantillas/validaciones/Validacion final.docx`
- `media/plantillas/plantilla_opis.docx`
- `media/plantillas/acta_formacion.docx`

### 12.2 Salidas generadas

- `media/firmas_opis/{OPI}/...pdf`
- `media/form_completa/teoria_ok/{operario}/{puesto}.pdf`
- `media/form_completa/practica_ok/{operario}/{puesto}.pdf`
- `media/form_completa/producto_ok/{operario}/{puesto}.pdf`
- `media/form_completa/firmas/{operario}/{puesto}/*.png`
- `media/documentos/{operario}/{puesto_traducido}/{puesto_traducido}_formacion_completa.pdf`

## 13) Riesgos y deuda tecnica ya detectados

### 13.1 Riesgos de concurrencia/estado global

En [formacion/views.py](formacion/views.py):

- `opi_a_mod` global.
- `puesto_info` global.

Esto puede mezclar estado entre usuarios concurrentes. No ampliar este patron.
Si se refactoriza, preferir session/request o persistencia explicita en DB.

### 13.2 Riesgos funcionales puntuales

- `ver_pdf_opi` usa `opi_a_mod` global al construir path de PDF.
- `subir_firma` guarda en `opi.firmas[operario]` la ruta `.docx` (`output_path`) aunque luego convierte a PDF.
- `generar_pdf` no esta decorada con login/group; depende de contexto/template.
- Formularios en templates mezclan `action="/ruta"` hardcodeado y `{% url %}`.

### 13.3 Riesgos de mantenimiento

- Doble diccionario de puestos: uno en [formacion/forms.py](formacion/forms.py) y otro en [formacion/views.py](formacion/views.py).
- [formacion/cruce_opis.py](formacion/cruce_opis.py) no tiene usos activos detectados y su contenido esta inconsistente.
- No hay tests funcionales automatizados (suite vacia).

## 14) Playbooks de cambio seguro por area

### 14.1 Si agregas un nuevo campo de puesto en polivalencia

Debes tocar TODO lo siguiente:

1. Modelo `polivalencia` en [formacion/models.py](formacion/models.py).
2. Migracion nueva.
3. `column_mapping` en `actualizar_matriz` ([formacion/views.py](formacion/views.py)).
4. `puestos_dict` en [formacion/forms.py](formacion/forms.py).
5. `puestos_dict` en [formacion/views.py](formacion/views.py).
6. Plantillas de examen en [media/plantillas/teoria](media/plantillas/teoria) y/o [media/plantillas/practica](media/plantillas/practica) si aplica.
7. Validar filtros de UI en `editar_matriz`, `formacion_opis`, `formacion_completa`, `auditoria_diaria`.

### 14.2 Si cambias rutas/nombres de vistas

1. Actualizar [formacion/urls.py](formacion/urls.py).
2. Actualizar TODAS las referencias `{% url ... %}` en templates.
3. Revisar acciones hardcodeadas `/ruta` en templates.
4. Probar navegacion completa por rol.

### 14.3 Si cambias flujo de firmas o PDFs

1. Sincronizar templates `introducir_firma`, `firmar_formacion`, `generando_pdf`.
2. Mantener claves JSON usadas por documentos.
3. Verificar conversion LibreOffice y merge PyPDF2.
4. Validar existencia de plantillas docx requeridas.

### 14.4 Si cambias seguridad/login

1. Revisar middleware de password expiry.
2. Revisar Axes + señales de notificacion.
3. Probar login, bloqueo por intentos, password_change, logout_message.

## 15) Regla especial de migraciones (muy importante)

Archivo [.gitignore](.gitignore) contiene:

- `formacion/migrations/*`

Esto implica que nuevas migraciones pueden quedar fuera del commit por defecto.

Si el cambio requiere migracion, comprobar explicitamente `git status` y usar `git add -f` para la migracion nueva, o ajustar `.gitignore` segun politica del repo.

## 16) Checklist obligatorio antes de cerrar cualquier tarea

### 16.1 Tecnico

1. Ejecutar:

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py test
```

2. Si tocaste modelos:

```powershell
.\.venv\Scripts\python.exe manage.py makemigrations
.\.venv\Scripts\python.exe manage.py migrate
```

3. Si tocaste rutas/templates:

- Navegar al menos: login -> inicio -> matriz -> opis -> formacion completa -> auditoria.

4. Si tocaste PDFs:

- Probar un ciclo completo hasta `ver_pdf_form` y `ver_pdf_opi`.

### 16.2 Funcional por rol

Probar minimo con usuarios de grupos:

- `admin`
- `formacion`
- `supervisores`
- `tecnicos`

## 17) Que NO hacer

- No renombrar campos JSON usados en plantillas/docx sin migracion de datos.
- No cambiar nombres de grupos (`admin`, `formacion`, `supervisores`, `tecnicos`).
- No borrar `ready()` en [formacion/apps.py](formacion/apps.py).
- No asumir que rutas de archivos son solo locales; hay fallback a red UNC.
- No editar [staticfiles](staticfiles) manualmente para cambios de app.
- No introducir mas estado global en vistas.

## 18) Troubleshooting rapido

### Error: ModuleNotFoundError (ej. pandas)

Causa comun: se ejecuto Django con otro Python.

Solucion:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py check
```

### Error: no se encuentra archivo de teoria/practica

Verificar existencia de `{PUESTO}.txt` en:

- [media/plantillas/teoria](media/plantillas/teoria)
- [media/plantillas/practica](media/plantillas/practica)

### Error en conversion docx -> pdf

Verificar:

- `LIBREOFFICE_PATH` en [formaciones/settings.py](formaciones/settings.py).
- Permisos de escritura en rutas de salida.
- Disponibilidad de plantillas docx.

## 19) Convenciones para agentes futuros

- Cambios pequenos y focalizados.
- No mezclar refactor masivo con bugfix funcional en un mismo commit.
- Documentar en PR/descripcion:
  - que se cambio
  - por que
  - que rutas/modelos/templates se impactan
  - como se valido

Si una mejora estructural (ej. eliminar globals) es grande, dividir en fases:

1. Estabilizar tests/smoke checks.
2. Refactor incremental.
3. Endurecer seguridad.

---

Este archivo es la referencia operativa para trabajar sin romper nada.
Si el codigo evoluciona, actualizar este documento en el mismo PR del cambio.