from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

puestos_dict = {
    'OPERARIO': 'OPERARIO',
    'CONFIRM': 'CONFIRMACIÓN',
    'OPEN_MAIL': 'OPEN MAIL',
    'ORDER_ENTRY_SERVICE': 'ORDER ENTRY SERVICE',
    'ORDER_ENTRY_NEW': 'ORDER ENTRY NEW',
    'DIAG_ITE': 'DIAGNÓSTICO ITE',
    'DIAG_ITE_SAF': 'DIAGNÓSTICO ITE (SAF)',
    'DIAG_SDS': 'DIAGNÓSTICO SDS',
    'DIAG_SDS_SAF': 'DIAGNÓSTICO SDS (SAF)',
    'DIAG_BTE': 'DIAGNÓSTICO BTE',
    'DIAG_FM_DWA': 'DIAGNÓSTICO FM/DWA',
    'DIAG_TITANIUM': 'DIAGNÓSTICO TITANIUM',
    'REPAIR_FM_DWA': 'REPAIR FM/DWA',
    'REPAIR_CARGADORES': 'REPAIR CARGADORES',
    'REPAIR_BTE': 'REPAIR BTE',
    'RSM': 'RSM',
    'MINI_KITTING': 'MINI-KITTING',
    'KITTING_CUSTOM': 'KITTING CUSTOM',
    'KITTING_BTE': 'KITTING BTE',
    'DCC': 'DCC',
    'DLP': 'DLP',
    'KIT_PREP_SDS': 'KIT PREPARATION SDS',
    'CLOSING_SDS': 'CLOSING SDS',
    'KIT_PREP_ITE': 'KIT PREPARATION ITE',
    'CLOSING_ITE': 'CLOSING ITE',
    'CUT_TRIM': 'CUT & TRIM',
    'FL': 'FINISHING & LACQUERING',
    'TITANIUM': 'TITANIUM',
    'VISUAL_ITE': 'VISUAL ITE',
    'VISUAL_SDS': 'VISUAL SDS',
    'VISUAL_BTE': 'VISUAL BTE',
    'VISUAL_FM_DWA': 'VISUAL FM/DWA',
    'PRO_GO_ITE': 'PRO&GO ITE',
    'PRO_GO_SDS': 'PRO&GO SDS',
    'PRO_GO_BTE': 'PRO&GO BTE',
    'PRO_GO_FM_DWA': 'PRO&GO FM/DWA',
    'PACKING_NEW': 'PACKING NEW',
    'PACKING_SERVICE': 'PACKING SERVICE',
    'RPM_DESMONTAJE_LIMPIEZA': 'RPM: DESMONTAJE Y LIMPIEZA',
    'RPM_DECONTAMINACION': 'RPM: DECONTAMINACIÓN',
    'RPM_IRS1_IDENTIFICACION': 'RPM-IRS1: IDENTIFICACIÓN E INICIALIZACIÓN',
    'RPM_LPS2_BLUETOOTH': 'RPM-LPS2: BLUETOOTH',
    'RPM_VISUAL_SNW2': 'RPM-VISUAL Y SNW2',
    'ACS2': 'ACS2',
    'SORTING': 'SORTING',
    'REFURBISHING': 'REFURBISHING',
    'REPROCESSING_CARGADORES': 'REPROCESSING CARGADORES',
    'PACKING_RPM_REFURBISHING': 'PACKING RPM/REFURBISHING'
}


class RegistroForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "password1", "password2"]
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Quitar textos de ayuda
        for fieldname in ["username", "password1", "password2"]:
            self.fields[fieldname].help_text = None

# formulario de operarios para OPIS
class OperarioForm(forms.Form):
    OPERARIO = forms.ChoiceField(choices=[], required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        operarios_choices = [(operario.OPERARIO, operario.OPERARIO) for operario in polivalencia.objects.all()]
        self.fields['OPERARIO'].choices = [('', 'Seleccione operario')] + operarios_choices


# formulario de operarios para formacion completa
class OperarioComp(forms.Form):
    OPERARIO = forms.ChoiceField(choices=[], required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        operarios_filtrados = []
        campos_excluidos = ('OPERARIO', 'id', 'creado_por', 'creado_en', 'modificado_por', 'modificado_en')
        for operario in polivalencia.objects.all():
            for field in operario._meta.fields:
                if field.name not in campos_excluidos:
                    valor = getattr(operario, field.name)
                    if valor == 4:
                        operarios_filtrados.append((operario.OPERARIO, operario.OPERARIO))
                        break

        self.fields['OPERARIO'].choices = [('', 'Seleccione operario')] + operarios_filtrados

# formulario de puestos para OPIS
class PuestoForm(forms.Form):
    global puestos_dict
    PUESTO = forms.ChoiceField(choices=[], required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        seccion_choices = []
        for field in polivalencia._meta.fields:
            if field.name not in ['id', 'OPERARIO'] and field.name in puestos_dict:
                seccion_choices.append((field.name, puestos_dict[field.name]))

        self.fields['PUESTO'].choices = [('', 'Seleccione sección')] + seccion_choices
        
#formulario de puestos para formacion completa
class PuestoComp(forms.Form):
    global puestos_dict
    PUESTO = forms.ChoiceField(choices=[], required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        campos_validos = []
        campos_excluidos = ('id', 'OPERARIO', 'creado_por', 'creado_en', 'modificado_por', 'modificado_en')
        for field in polivalencia._meta.fields:
            if field.name not in campos_excluidos:
                if polivalencia.objects.filter(**{field.name: 4}).exists():
                    if field.name in puestos_dict:
                        campos_validos.append((field.name, puestos_dict[field.name]))

        self.fields['PUESTO'].choices = [('', 'Seleccione sección')] + campos_validos

class SeccionForm(forms.Form):
    SECCION1 = forms.ChoiceField(choices=[], required=False)
    SECCION2 = forms.ChoiceField(choices=[], required=False)
    SECCION3 = forms.ChoiceField(choices=[], required=False)
    SECCION4 = forms.ChoiceField(choices=[], required=False)
    SECCION5 = forms.ChoiceField(choices=[], required=False)
    SECCION6 = forms.ChoiceField(choices=[], required=False)
    SECCION7 = forms.ChoiceField(choices=[], required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        seccion_choices = [
            (field.name, puestos_dict.get(field.name, field.name))
            for field in polivalencia._meta.fields
            if field.name not in ['id', 'OPERARIO']
        ]
        for i in range(1, 8):
            self.fields[f'SECCION{i}'].choices = [('', 'Seleccione sección')] + seccion_choices

class OpiForm(forms.Form):
    opi = forms.ChoiceField(choices=[], required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        opis_choices = [(opi.OPI, opi.OPI) for opi in opis.objects.all()]
        self.fields['opi'].choices = [('', 'Seleccione una OPI')] + opis_choices

class CompletaForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.operario = kwargs.pop('operario', None)
        self.puesto = kwargs.pop('puesto', None)
        super().__init__(*args, **kwargs)

        # Si se proporcionan operario y puesto, buscar los datos en el modelo
        if self.operario and self.puesto:
            # Usar filter().first() para manejar duplicados
            registro = completa.objects.filter(PUESTO=self.puesto, OPERARIO=self.operario).first()
            if registro:
                self.initial['TEORIA'] = registro.TEORIA
                self.initial['PRACTICA'] = registro.PRACTICA
                self.initial['PRODUCTO'] = registro.PRODUCTO

class PolivalenciaForm(forms.ModelForm):
    class Meta:
        model = polivalencia
        fields = '__all__'  # o lista específica si quieres restringir campos


class EliminarForm(forms.Form):
    ELIMINAR = forms.ChoiceField(choices=[], required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        operarios_choices = [(operario.OPERARIO, operario.OPERARIO) for operario in polivalencia.objects.all()]
        self.fields['ELIMINAR'].choices = [('', 'Seleccione operario')] + operarios_choices
