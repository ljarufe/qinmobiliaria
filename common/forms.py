#-*- coding: utf-8 -*-

from django import forms
from common.models import Telefono, TipoTelefono


class TelefonoForm(forms.ModelForm):
    """
    Formulario de ingreso de un teléfono
    """
    tipo_telefono = forms.ModelChoiceField(queryset=TipoTelefono.objects.all(),
                                           empty_label=None, label=u'Tipo')

    class Meta:
        model = Telefono
