from django.db import models
from django.contrib.auth.models import Group, User
from django.utils import timezone

# Create your models here.
class polivalencia(models.Model):
    OPERARIO = models.CharField(max_length=100, unique=True)
    CONFIRM = models.IntegerField(default=0)
    OPEN_MAIL = models.IntegerField(default=0)
    ORDER_ENTRY_SERVICE = models.IntegerField(default=0)
    ORDER_ENTRY_NEW = models.IntegerField(default=0)
    DIAG_ITE = models.IntegerField(default=0)
    DIAG_ITE_SAF = models.IntegerField(default=0)
    DIAG_SDS = models.IntegerField(default=0)
    DIAG_SDS_SAF = models.IntegerField(default=0)
    DIAG_BTE = models.IntegerField(default=0)
    DIAG_FM_DWA = models.IntegerField(default=0)
    DIAG_TITANIUM = models.IntegerField(default=0)
    REPAIR_FM_DWA = models.IntegerField(default=0)
    REPAIR_CARGADORES = models.IntegerField(default=0)
    REPAIR_BTE = models.IntegerField(default=0)
    RSM = models.IntegerField(default=0)
    MINI_KITTING = models.IntegerField(default=0)
    KITTING_CUSTOM = models.IntegerField(default=0)
    KITTING_BTE = models.IntegerField(default=0)
    DCC = models.IntegerField(default=0)
    DLP = models.IntegerField(default=0)
    KIT_PREP_SDS = models.IntegerField(default=0)
    CLOSING_SDS = models.IntegerField(default=0)
    KIT_PREP_ITE = models.IntegerField(default=0)
    CLOSING_ITE = models.IntegerField(default=0)
    CUT_TRIM = models.IntegerField(default=0)
    FL = models.IntegerField(default=0)
    TITANIUM = models.IntegerField(default=0)
    VISUAL_ITE = models.IntegerField(default=0)
    VISUAL_SDS = models.IntegerField(default=0)
    VISUAL_BTE = models.IntegerField(default=0)
    VISUAL_FM_DWA = models.IntegerField(default=0)
    PRO_GO_ITE = models.IntegerField(default=0)
    PRO_GO_SDS = models.IntegerField(default=0)
    PRO_GO_BTE = models.IntegerField(default=0)
    PRO_GO_FM_DWA = models.IntegerField(default=0)
    PACKING_NEW = models.IntegerField(default=0)
    PACKING_SERVICE = models.IntegerField(default=0)
    RPM_DESMONTAJE_LIMPIEZA = models.IntegerField(default=0)
    RPM_DECONTAMINACION = models.IntegerField(default=0)
    RPM_IRS1_IDENTIFICACION = models.IntegerField(default=0)
    RPM_LPS2_BLUETOOTH = models.IntegerField(default=0)
    RPM_VISUAL_SNW2 = models.IntegerField(default=0)
    ACS2 = models.IntegerField(default=0)
    SORTING = models.IntegerField(default=0)
    REFURBISHING = models.IntegerField(default=0)
    REPROCESSING_CARGADORES = models.IntegerField(default=0)
    PACKING_RPM_REFURBISHING = models.IntegerField(default=0)
    
    # Campos de auditoría
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='polivalencia_creadas')
    creado_en = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    modificado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='polivalencia_modificadas')
    modificado_en = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.OPERARIO
    

class nuevas_opis(models.Model):
    OPI = models.CharField(max_length=100, unique=True)
    INFO = models.CharField(max_length=800)
    SECCION1 = models.CharField(max_length=25)
    SECCION2 = models.CharField(max_length=25)
    SECCION3 = models.CharField(max_length=25)
    SECCION4 = models.CharField(max_length=25)
    SECCION5 = models.CharField(max_length=25)
    SECCION6 = models.CharField(max_length=25)
    SECCION7 = models.CharField(max_length=25)
    ok_supervisor = models.JSONField(default=dict)
    
    # Campos de auditoría
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='nuevas_opis_creadas')
    creado_en = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    modificado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='nuevas_opis_modificadas')
    modificado_en = models.DateTimeField(auto_now=True, null=True, blank=True)


class opis(models.Model):
    OPI = models.CharField(max_length=100, unique=True)
    INFO = models.CharField(max_length=800)
    SECCION1 = models.CharField(max_length=25)
    SECCION2 = models.CharField(max_length=25)
    SECCION3 = models.CharField(max_length=25)
    SECCION4 = models.CharField(max_length=25)
    SECCION5 = models.CharField(max_length=25)
    SECCION6 = models.CharField(max_length=25)
    SECCION7 = models.CharField(max_length=25)
    formados = models.JSONField(default=dict)
    firmas = models.JSONField(default=dict)
    
    # Campos de auditoría
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='opis_creadas')
    creado_en = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    modificado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='opis_modificadas')
    modificado_en = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.OPI
    
class completa(models.Model):
    PUESTO = models.CharField(max_length=100)
    OPERARIO = models.CharField(max_length=100)
    TEORIA = models.BooleanField(default=False)
    PRACTICA = models.BooleanField(default=False)
    PRODUCTO = models.BooleanField(default=False)
    firmas = models.JSONField(default=dict)
    
    # Campos de auditoría
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='formaciones_completas_creadas')
    creado_en = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    modificado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='formaciones_completas_modificadas')
    modificado_en = models.DateTimeField(auto_now=True, null=True, blank=True)

class auditoria(models.Model):
    DIA = models.DateField()
    SAP = models.CharField(max_length=100)
    NUM_SERIE = models.CharField(max_length=100)
    FAMILIA = models.CharField(max_length=100)
    PROCESO = models.CharField(max_length=100)
    AUDITOR = models.CharField(max_length=100)
    OPERARIO = models.CharField(max_length=100)
    NO_CONFORMIDAD = models.BooleanField(default=False)
    OBSERVACIONES = models.TextField(blank=True, null=True)
    
    # Campos de auditoría
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='auditorias_creadas')
    creado_en = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    modificado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='auditorias_modificadas')
    modificado_en = models.DateTimeField(auto_now=True, null=True, blank=True)


class Notificacion(models.Model):
    grupo = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    mensaje = models.TextField()
    creado_en = models.DateTimeField(auto_now_add=True)
    creado_por = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notificaciones_creadas', null=True, blank=True)
    leido_por = models.ManyToManyField(User, related_name='notificaciones_leidas', blank=True)

    def __str__(self):
        destino = self.grupo.name if self.grupo else (self.usuario.username if self.usuario else "General")
        return f"Para {destino}: {self.mensaje[:30]}"


class PasswordChangeStatus(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='password_status')
    last_password_change = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - {self.last_password_change}"