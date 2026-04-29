# DOCUMENTACION

Este documento es la referencia principal para trabajar en la app sin romper flujos existentes.
Se complementa con:

- [ESTRUCTURA_DEL_PROYECTO.md](ESTRUCTURA_DEL_PROYECTO.md)
- [ESTRUCTURA_DE_LA_BASE_DE_DATOS.md](ESTRUCTURA_DE_LA_BASE_DE_DATOS.md)
- [AGENTS.md](../AGENTS.md)

## 1) Objetivo del sistema

Aplicacion Django para:

- Matriz de polivalencia por operario/puesto.
- Ciclo completo de OPI (alta, validacion, firma y consulta PDF).
- Formacion completa (teoria, practica, producto, firmas, PDF final).
- Auditoria diaria.
- Notificaciones internas por grupo/usuario.

## 2) Regla de oro para hacer cambios

Antes de tocar codigo, identificar:

1. Que flujo funcional se modifica.
2. Que contratos dependen de ese flujo (rutas, campos POST, JSON, rutas de archivos).
3. Que archivos deben cambiar juntos.
4. Que pruebas minimas validan que no hubo regresion.

Si no se cumple ese analisis, no empezar a editar.

## 3) Entornos y base de datos

Politica de entorno:

- Servidor/produccion: PostgreSQL.
- Desarrollo local: SQLite ([db.sqlite3](../db.sqlite3)).

Estado actual observado en [formaciones/settings.py](../formaciones/settings.py):

- Hay bloque SQLite comentado.
- Hay bloque PostgreSQL activo.

Recomendacion operativa:

- No hardcodear credenciales en cambios futuros.
- Parametrizar con variables de entorno (ver [AGENTS.md](../AGENTS.md)).

## 4) Metodo de cambio seguro (paso a paso)

### Paso 1: Trazar impacto

Segun el tipo de cambio, revisar archivos relacionados en bloque:

- Modelo: [formacion/models.py](../formacion/models.py), migraciones, forms, views, templates.
- Ruta vista: [formacion/urls.py](../formacion/urls.py) y templates que llaman `{% url %}`.
- Flujo de PDF/firma: [formacion/views.py](../formacion/views.py) + plantillas en [media/plantillas](../media/plantillas).
- Seguridad/login: [formaciones/settings.py](../formaciones/settings.py), [formacion/middleware.py](../formacion/middleware.py), [formacion/signals.py](../formacion/signals.py).

### Paso 2: Cambios minimos y enfocados

- Evitar refactor masivo junto con cambio funcional.
- No renombrar claves JSON ni nombres de rutas sin migracion/sincronizacion total.
- No ampliar uso de estado global en vistas.

### Paso 3: Validacion tecnica minima

Usar siempre el Python de la venv del repo:

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py test
```

Si se tocaron modelos:

```powershell
.\.venv\Scripts\python.exe manage.py makemigrations
.\.venv\Scripts\python.exe manage.py migrate
```

### Paso 4: Validacion funcional minima

Recorrer al menos:

1. login -> inicio
2. matriz (editar)
3. opis (alta/listado/acciones)
4. formacion completa
5. auditoria

Si el cambio toca PDF/firma:

1. completar ciclo de firma
2. generar PDF
3. abrir `ver_pdf_opi` y/o `ver_pdf_form`

## 5) Matriz de impacto por tipo de cambio

### 5.1 Nuevo puesto/campo en matriz

Cambiar juntos:

1. [formacion/models.py](../formacion/models.py) (campo nuevo).
2. migracion en [formacion/migrations](../formacion/migrations).
3. `column_mapping` en [formacion/views.py](../formacion/views.py).
4. `puestos_dict` en [formacion/forms.py](../formacion/forms.py).
5. `puestos_dict` en [formacion/views.py](../formacion/views.py).
6. plantillas de examen en [media/plantillas/teoria](../media/plantillas/teoria) y/o [media/plantillas/practica](../media/plantillas/practica).

### 5.2 Cambio de URL o nombre de vista

Cambiar juntos:

1. [formacion/urls.py](../formacion/urls.py).
2. templates que hagan `{% url %}`.
3. acciones hardcodeadas `action="/ruta"` en templates.

### 5.3 Cambio en firmas o PDFs

Cambiar juntos:

1. vistas en [formacion/views.py](../formacion/views.py).
2. plantillas de UI de firma.
3. plantillas DOCX en [media/plantillas](../media/plantillas).
4. contratos JSON (`firmas`, `formados`) sin romper claves existentes.

### 5.4 Cambio de permisos o login

Cambiar juntos:

1. decoradores de grupo/login en [formacion/views.py](../formacion/views.py).
2. middleware en [formacion/middleware.py](../formacion/middleware.py).
3. senales de bloqueo en [formacion/signals.py](../formacion/signals.py).
4. parametros de seguridad en [formaciones/settings.py](../formaciones/settings.py).

## 6) Contratos que NO se deben romper

- Nombres de grupos: `admin`, `formacion`, `supervisores`, `tecnicos`.
- Nombres de rutas usados en templates.
- Claves JSON de `completa.firmas`.
- Campos POST esperados por las vistas.
- Rutas de archivos de plantillas y salidas PDF.
- Inicializacion de senales en [formacion/apps.py](../formacion/apps.py).

## 7) Riesgos conocidos

- Estado global en vistas (`opi_a_mod`, `puesto_info`) puede mezclar contexto entre usuarios.
- Suite de tests funcionales vacia (no hay red de seguridad automatica).
- [formacion/migrations](../formacion/migrations) esta ignorado en [.gitignore](../.gitignore) y puede ocultar migraciones nuevas.

## 8) Definicion de cambio listo (DoD)

Un cambio se considera listo solo si:

1. Se aplico analisis de impacto.
2. Se modificaron todos los archivos acoplados por contrato.
3. `manage.py check` pasa.
4. Flujo funcional afectado se probo de punta a punta.
5. Se documento en PR que se cambio, por que y como se valido.

