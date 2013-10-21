# -*- coding: utf-8 -*-

from django import template
import re

register = template.Library()

def trunc_char(value, arg):
    """
    Trunca una cadena a un cierto número de caracteres, no corta la última
    palabra, toma el espacio anterior a esta y coloca '...' al final de la
    cadena considerando estos 3 puntos en el valor máximo de caracteres.
    """
    if not value:
        return u''

    arg = int(arg) - 3
    if arg > len(value):
        return value

    for i in range(0, arg):
        if re.match(value[arg - i], ' '):
            arg -= i
            break

    return u"%s..." % value[:arg]

register.filter('trunc_char', trunc_char)
