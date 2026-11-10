from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from PIL import Image

from .views import (
    _extraer_metadatos_examen,
    _incrementar_version_examen,
    _normalizar_saltos_examen,
    cargar_practica,
    cargar_teoria,
)


class GuardarExamenTests(TestCase):
    def _iniciar_sesion_formacion(self):
        grupo = Group.objects.create(name='admin')
        usuario = get_user_model().objects.create_user(
            username='formacion-admin',
            password='test-password',
        )
        usuario.groups.add(grupo)
        self.client.force_login(usuario)

    def test_guardar_examen_no_duplica_finales_de_linea(self):
        self._iniciar_sesion_formacion()

        contenido = '1- Pregunta\r\r\nA- Respuesta.*\r\r\n\r\r\n2- Otra pregunta\r\r\n'
        with TemporaryDirectory() as directorio:
            Path(directorio, 'teoria').mkdir()
            with patch('formacion.views.PLANTILLAS_ROOT', directorio):
                with patch(
                    'formacion.views._normalizar_saltos_examen',
                    wraps=_normalizar_saltos_examen,
                ) as normalizar:
                    respuesta = self.client.post(
                        reverse('edicion_plantillas'),
                        {
                            'accion': 'guardar',
                            'nombre_archivo': 'Puesto.txt',
                            'dir_actual': 'teoria',
                            'contenido': contenido,
                        },
                    )
                    normalizar.assert_called_once()

            self.assertEqual(respuesta.status_code, 302)
            guardado = Path(directorio, 'teoria', 'Puesto.txt').read_bytes()

        self.assertTrue(guardado.startswith(b'VERSION: 1.00\nFECHA_GUARDADO: '))
        self.assertTrue(guardado.endswith(b'1- Pregunta\nA- Respuesta.*\n\n2- Otra pregunta'))

    def test_subir_mostrar_y_eliminar_imagen_de_pregunta(self):
        self._iniciar_sesion_formacion()

        contenido = '1- Pregunta uno\nA- Respuesta.*\n\n2- Pregunta dos\nA- Otra respuesta'
        buffer_imagen = BytesIO()
        Image.new('RGB', (1, 1), color='blue').save(buffer_imagen, format='PNG')

        with TemporaryDirectory() as directorio:
            ruta_examen = Path(directorio, 'teoria', 'Puesto.txt')
            ruta_examen.parent.mkdir()
            ruta_examen.write_text(contenido, encoding='utf-8')
            with patch('formacion.views.PLANTILLAS_ROOT', directorio):
                respuesta = self.client.post(
                    reverse('edicion_plantillas'),
                    {
                        'accion': 'subir_imagen',
                        'nombre_archivo': 'Puesto.txt',
                        'dir_actual': 'teoria',
                        'file_rel': 'teoria/Puesto.txt',
                        'numero_pregunta': '2',
                        'contenido': contenido,
                        'imagen': SimpleUploadedFile(
                            'imagen.png',
                            buffer_imagen.getvalue(),
                            content_type='image/png',
                        ),
                    },
                    follow=True,
                )
                self.assertEqual(respuesta.status_code, 200)

                imagenes = list(Path(directorio, 'teoria', 'imagenes', 'Puesto').glob('pregunta-2-*.png'))
                self.assertEqual(
                    len(imagenes),
                    1,
                    [str(mensaje) for mensaje in respuesta.context['messages']],
                )
                imagen_rel = imagenes[0].relative_to(directorio).as_posix()
                imagen_legacy = Path(directorio, 'teoria', 'imagenes', 'Puesto', 'pregunta-1.jpg')
                buffer_legacy = BytesIO()
                Image.new('RGB', (1, 1), color='red').save(buffer_legacy, format='JPEG')
                imagen_legacy.write_bytes(buffer_legacy.getvalue())

                respuesta_editor = self.client.get(
                    reverse('edicion_plantillas'),
                    {'subdir': 'teoria', 'file': 'teoria/Puesto.txt'},
                )
                self.assertEqual(respuesta_editor.status_code, 200)
                self.assertEqual(
                    [imagen['numero'] for imagen in respuesta_editor.context['archivo']['imagenes']],
                    [1, 2],
                )

                respuesta_imagen = self.client.get(
                    reverse('imagen_plantilla', kwargs={'image_rel': imagen_rel})
                )
                self.assertEqual(respuesta_imagen.status_code, 200)
                self.assertEqual(b''.join(respuesta_imagen.streaming_content), buffer_imagen.getvalue())

                def shared_plantillas_path(*partes):
                    return str(Path(directorio, *partes))

                with patch('formacion.views.shared_plantillas_path', side_effect=shared_plantillas_path):
                    preguntas, error, meta = cargar_teoria('Puesto')
                self.assertIsNone(error)
                self.assertEqual(meta['version'], '1.00')
                self.assertIsNotNone(meta['fecha_guardado'])
                self.assertEqual(preguntas[0]['imagenes'][0]['nombre'], 'pregunta-1.jpg')
                self.assertEqual(preguntas[1]['imagenes'][0]['rel'], imagen_rel)

                respuesta_eliminar = self.client.post(
                    reverse('edicion_plantillas'),
                    {
                        'accion': 'eliminar_imagen',
                        'nombre_archivo': 'Puesto.txt',
                        'dir_actual': 'teoria',
                        'file_rel': 'teoria/Puesto.txt',
                        'imagen_rel': imagen_rel,
                        'contenido': contenido,
                    },
                )
                self.assertEqual(respuesta_eliminar.status_code, 302)
                self.assertFalse(imagenes[0].exists())


class CargaExamenTests(SimpleTestCase):
    def test_cargar_teoria_ignora_lineas_vacias_entre_respuestas(self):
        contenido = (
            b'1- Pregunta de prueba\r\r\n'
            b'A- Primera respuesta.*\r\r\n'
            b'B- Segunda respuesta\r\r\n'
            b'C- Tercera respuesta\r\r\n'
        )
        with TemporaryDirectory() as directorio:
            Path(directorio, 'Puesto.txt').write_bytes(contenido)
            with patch('formacion.views.shared_plantillas_path', return_value=directorio):
                preguntas, error, meta = cargar_teoria('Puesto')

        self.assertIsNone(error)
        self.assertIsNone(meta['version'])
        self.assertEqual(len(preguntas), 1)
        self.assertEqual(
            [opcion['letra'] for opcion in preguntas[0]['opciones']],
            ['A', 'B', 'C'],
        )
        self.assertEqual(preguntas[0]['respuesta_correcta'], 'A')

    def test_cargar_practica_ignora_lineas_vacias_entre_cuestiones(self):
        contenido = b'1- Primera cuestion\r\r\n\r\r\n2- Segunda cuestion\r\r\n'
        with TemporaryDirectory() as directorio:
            Path(directorio, 'Puesto.txt').write_bytes(contenido)
            with patch('formacion.views.shared_plantillas_path', return_value=directorio):
                cuestiones, error, meta = cargar_practica('Puesto')

        self.assertIsNone(error)
        self.assertIsNone(meta['version'])
        self.assertEqual(
            [cuestion['texto'] for cuestion in cuestiones],
            ['Primera cuestion', 'Segunda cuestion'],
        )

    def test_normalizar_saltos_quita_vacios_internos_y_separa_preguntas(self):
        contenido = (
            '1- Pregunta\r\r\n'
            'A- Respuesta\r\r\n'
            'B- Otra respuesta\r\r\n'
            '\r\r\n'
            '2- Siguiente pregunta\r\r\n'
        )

        self.assertEqual(
            _normalizar_saltos_examen(contenido),
            '1- Pregunta\nA- Respuesta\nB- Otra respuesta\n\n2- Siguiente pregunta',
        )


class VersionadoExamenTests(TestCase):
    def _iniciar_sesion_formacion(self):
        grupo = Group.objects.create(name='admin')
        usuario = get_user_model().objects.create_user(
            username='formacion-admin',
            password='test-password',
        )
        usuario.groups.add(grupo)
        self.client.force_login(usuario)

    def test_extraer_metadatos_examen(self):
        contenido = 'VERSION: 1.05\nFECHA_GUARDADO: 09/11/2026 10:00\n\n1- Pregunta\nA- Respuesta.*'
        version, fecha, cuerpo = _extraer_metadatos_examen(contenido)
        self.assertEqual(version, '1.05')
        self.assertEqual(fecha, '09/11/2026 10:00')
        self.assertEqual(cuerpo, '1- Pregunta\nA- Respuesta.*')

    def test_extraer_metadatos_examen_sin_cabecera(self):
        version, fecha, cuerpo = _extraer_metadatos_examen('1- Pregunta\nA- Respuesta.*')
        self.assertIsNone(version)
        self.assertIsNone(fecha)
        self.assertEqual(cuerpo, '1- Pregunta\nA- Respuesta.*')

    def test_incrementar_version_examen(self):
        self.assertEqual(_incrementar_version_examen('1.00'), '1.05')
        self.assertEqual(_incrementar_version_examen('1.05'), '1.10')
        self.assertEqual(_incrementar_version_examen(None), '1.00')
        self.assertEqual(_incrementar_version_examen('abc'), '1.00')

    def test_crear_examen_asigna_version_inicial(self):
        self._iniciar_sesion_formacion()
        with TemporaryDirectory() as directorio:
            Path(directorio, 'teoria').mkdir()
            with patch('formacion.views.PLANTILLAS_ROOT', directorio):
                respuesta = self.client.post(
                    reverse('edicion_plantillas'),
                    {
                        'accion': 'crear',
                        'nombre_archivo': 'Nuevo.txt',
                        'dir_actual': 'teoria',
                        'contenido': '1- Pregunta\nA- Respuesta.*',
                    },
                )
                self.assertEqual(respuesta.status_code, 302)
                guardado = Path(directorio, 'teoria', 'Nuevo.txt').read_text(encoding='utf-8')
        self.assertTrue(guardado.startswith('VERSION: 1.00\nFECHA_GUARDADO: '))

    def test_guardar_examen_incrementa_version_solo_si_se_pide(self):
        self._iniciar_sesion_formacion()
        with TemporaryDirectory() as directorio:
            ruta = Path(directorio, 'teoria')
            ruta.mkdir()
            Path(ruta, 'Puesto.txt').write_text(
                'VERSION: 1.00\nFECHA_GUARDADO: 01/01/2026 09:00\n\n1- Pregunta\nA- Respuesta.*',
                encoding='utf-8',
            )
            with patch('formacion.views.PLANTILLAS_ROOT', directorio):
                # Sin incremento: mantiene versión
                self.client.post(
                    reverse('edicion_plantillas'),
                    {
                        'accion': 'guardar',
                        'nombre_archivo': 'Puesto.txt',
                        'dir_actual': 'teoria',
                        'contenido': '1- Pregunta\nA- Respuesta.*',
                        'incrementar_version': '0',
                    },
                )
                guardado = Path(ruta, 'Puesto.txt').read_text(encoding='utf-8')
                self.assertTrue(guardado.startswith('VERSION: 1.00\n'))

                # Con incremento: sube a 1.05
                self.client.post(
                    reverse('edicion_plantillas'),
                    {
                        'accion': 'guardar',
                        'nombre_archivo': 'Puesto.txt',
                        'dir_actual': 'teoria',
                        'contenido': '1- Pregunta\nA- Respuesta.*',
                        'incrementar_version': '1',
                    },
                )
                guardado = Path(ruta, 'Puesto.txt').read_text(encoding='utf-8')
                self.assertTrue(guardado.startswith('VERSION: 1.05\n'))
