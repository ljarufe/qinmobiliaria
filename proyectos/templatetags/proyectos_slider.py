# -*- coding: utf-8 -*-

from django import template
from django.http import Http404
from qinmobiliaria.proyectos.models import Proyecto

register = template.Library()

@register.inclusion_tag('proyectos/templatetags/proyectos_slider.html')
def proyectos_slider():
    """
    Muestra un slider con los proyectos ordenados por su relevancia
    """
    proyectos = Proyecto.accepted.all().order_by('relevancia')
    if proyectos:
        return {"proyecto": proyectos[0]}
    else:
        raise Http404