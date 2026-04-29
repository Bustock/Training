# ESTRUCTURA DEL PROYECTO

Este documento describe la estructura real del repo y como se conectan sus partes.
Uso recomendado: leerlo antes de tocar codigo para saber que archivos deben cambiar juntos.

## 1) Arbol principal

```text
Training/
|- manage.py
|- requirements.txt
|- db.sqlite3
|- AGENTS.md
|- docs/
|  |- DOCUMENTACION.md
|  |- ESTRUCTURA_DEL_PROYECTO.md
|  |- ESTRUCTURA_DE_LA_BASE_DE_DATOS.md
|- formaciones/
|  |- settings.py
|  |- urls.py
|  |- asgi.py
|  |- wsgi.py
|- formacion/
|  |- models.py
|  |- views.py
|  |- urls.py
|  |- forms.py
|  |- middleware.py
|  |- signals.py
|  |- apps.py
|  |- cruce_opis.py
|  |- tests.py
|  |- migrations/
|  |- templates/
|  |- templatetags/
|- media/
|  |- plantillas/
|  |- firmas_opis/
|  |- documentos/
|- staticfiles/
```

## 2) Capa por capa

### 2.1 Bootstrap Django

- [manage.py](../manage.py): entrada a comandos `check`, `migrate`, `test`, `runserver`.

### 2.2 Configuracion global

- [formaciones/settings.py](../formaciones/settings.py): apps, middleware, auth, BD, static/media, seguridad.
- [formaciones/urls.py](../formaciones/urls.py): root URLConf (`admin/`, `login/`, `logout/`, include app principal).
- [formaciones/asgi.py](../formaciones/asgi.py) y [formaciones/wsgi.py](../formaciones/wsgi.py): despliegue.

### 2.3 App de negocio (formacion)

- [formacion/models.py](../formacion/models.py): modelo de dominio.
- [formacion/views.py](../formacion/views.py): logica funcional principal.
- [formacion/urls.py](../formacion/urls.py): contratos de navegacion por nombre.
- [formacion/forms.py](../formacion/forms.py): formularios y filtros.
- [formacion/middleware.py](../formacion/middleware.py): expiracion de password.
- [formacion/signals.py](../formacion/signals.py): notificacion de bloqueo de login.
- [formacion/apps.py](../formacion/apps.py): inicializacion de senales (critico).
- [formacion/templatetags/custom_filters.py](../formacion/templatetags/custom_filters.py): filtros de template.

### 2.4 Presentacion

- [formacion/templates](../formacion/templates): UI server-rendered con Django templates.
- [formacion/static](../formacion/static): assets propios de la app.
- [staticfiles](../staticfiles): salida de collectstatic (no editar manualmente).

### 2.5 Documentos y activos runtime

- [media/plantillas](../media/plantillas): base de examenes y DOCX.
- [media/firmas_opis](../media/firmas_opis): firmas/PDFs de OPI.
- [media/documentos](../media/documentos): PDFs de formacion completa.

## 3) Mapa funcional y rutas

Archivo de referencia: [formacion/urls.py](../formacion/urls.py).

### 3.1 Acceso y sesion

- `inicio`
- `registro`
- `logout_message`
- `timeout`
- `password_change`
- `password_change_done`

### 3.2 Matriz de polivalencia

- `actualizar_matriz`
- `editar_matriz`
- `agregar_tecnico`
- `eliminar_tecnico`
- `editar_tecnico`
- `descargar_polivalencia`
- `grafica`

### 3.3 OPI

- `formacion_opis`
- `nueva_opi`
- `guardar_opi`
- `listar_opis`
- `aceptar_opi`
- `rechazar_opi`
- `introducir_fecha`
- `guardar_fecha`
- `introducir_firma`
- `subir_firma`
- `ver_pdf_opi`

### 3.4 Formacion completa

- `formacion_completa`
- `completar_teoria`
- `completar_practica`
- `completar_producto`
- `firmar_formacion`
- `guardar_firma`
- `generar_pdf`
- `ver_pdf_form`

### 3.5 Auditoria y utilidades

- `auditoria_diaria`
- `registrar_auditoria`
- `notificaciones`
- `notificacion_leida`
- `edicion_plantillas`

## 4) Flujo de dependencias (resumen)

1. URL name -> vista en [formacion/views.py](../formacion/views.py).
2. Vista -> formulario(s) en [formacion/forms.py](../formacion/forms.py) + modelos en [formacion/models.py](../formacion/models.py).
3. Vista -> template en [formacion/templates](../formacion/templates).
4. Vista -> lectura/escritura de archivos en [media](media).

Si cambias un nodo, revisar siempre los nodos conectados.

## 5) Templates por area funcional

### 5.1 Base y autenticacion

- [formacion/templates/base.html](../formacion/templates/base.html)
- [formacion/templates/registro.html](../formacion/templates/registro.html)
- [formacion/templates/registration/login.html](../formacion/templates/registration/login.html)
- [formacion/templates/registration/password_change_form.html](../formacion/templates/registration/password_change_form.html)
- [formacion/templates/registration/password_change_done.html](../formacion/templates/registration/password_change_done.html)

### 5.2 Matriz

- [formacion/templates/editar_matriz.html](../formacion/templates/editar_matriz.html)
- [formacion/templates/grafica.html](../formacion/templates/grafica.html)

### 5.3 OPI

- [formacion/templates/form_opis.html](../formacion/templates/form_opis.html)
- [formacion/templates/nueva_opi.html](../formacion/templates/nueva_opi.html)
- [formacion/templates/listar_opis.html](../formacion/templates/listar_opis.html)
- [formacion/templates/introducir_fecha.html](../formacion/templates/introducir_fecha.html)
- [formacion/templates/introducir_firma.html](../formacion/templates/introducir_firma.html)

### 5.4 Formacion completa

- [formacion/templates/form_completa.html](../formacion/templates/form_completa.html)
- [formacion/templates/completar_teoria.html](../formacion/templates/completar_teoria.html)
- [formacion/templates/completar_practica.html](../formacion/templates/completar_practica.html)
- [formacion/templates/completar_producto.html](../formacion/templates/completar_producto.html)
- [formacion/templates/firmar_formacion.html](../formacion/templates/firmar_formacion.html)
- [formacion/templates/generando_pdf.html](../formacion/templates/generando_pdf.html)

### 5.5 Auditoria, inicio, notificaciones, edicion de plantillas

- [formacion/templates/auditoria.html](../formacion/templates/auditoria.html)
- [formacion/templates/inicio.html](../formacion/templates/inicio.html)
- [formacion/templates/notificaciones.html](../formacion/templates/notificaciones.html)
- [formacion/templates/edicion_plantillas.html](../formacion/templates/edicion_plantillas.html)

## 6) Puntos estructurales sensibles

- Nombres de rutas (`name=`) usados en templates.
- Doble diccionario de puestos (forms + views).
- Estado global en vistas (`opi_a_mod`, `puesto_info`).
- Dependencias de plantillas y ficheros DOCX/TXT en [media/plantillas](../media/plantillas).
- Timeout por inactividad invocado desde multiples templates.

## 7) Reglas para editar sin romper

1. No cambiar una ruta sin actualizar todas sus llamadas en templates.
2. No renombrar campos de modelo sin migracion y revision de forms/views/templates.
3. No renombrar claves JSON de negocio sin migracion de datos.
4. No introducir cambios en [staticfiles](../staticfiles).
5. Si se toca [formacion/apps.py](../formacion/apps.py), mantener la carga de senales.

## 8) Comandos de comprobacion estructural

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py test
```

Si se tocaron modelos:

```powershell
.\.venv\Scripts\python.exe manage.py makemigrations
.\.venv\Scripts\python.exe manage.py migrate
```

