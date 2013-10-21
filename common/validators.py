# -*- coding: utf-8 -*-

from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
import re


def validate_name(name):
    """
    Función de validación para cadenas con caracteres alfabéticos
    """
    if not re.match(u"[a-zA-Z\á\é\í\ó\ú\ñ]+[\s]?([a-zA-Z\á\é\í\ó\ú\ñ]*[\s]*)*$",
                    name):
        raise ValidationError(u'%s contiene caracteres no permitidos.' % name)


def validate_phone(phone):
    """
    Función de validación para telefonos
    """
    if len(phone) < 6:
        raise ValidationError(u'El número debe contener al menos 6 dígitos.')
    if not re.match(u'^[\s\d-]+$', phone):
        raise ValidationError(u'%s tiene caracteres no permitidos.' % phone)


def validate_ruc(ruc):
    """
    El RUC debe tener 11 dígitos
    """
    if not ruc.isdigit():
        raise ValidationError(u'El RUC debe contener solamente números.')
    if len(ruc) != 11:
        raise ValidationError(u'El ruc debe tener 11 digitos.')


def validate_user(user):
    """
    Verifica que no exista otro usuario con el mismo nombre
    """
    try:
        User.objects.get(username=user)
        raise ValidationError(u'Este e-mail ya esta siendo utilizado por otro \
                                usuario.')
    except User.DoesNotExist:
        pass


def validate_email(user):
    """
    Verifica si el correo electrónico ya está siendo utilizado por otro usuario
    """
    try:
        User.objects.get(email=user)
        raise ValidationError(u'Este e-mail ya esta siendo utilizado por otro \
                                usuario.')
    except User.DoesNotExist:
        pass