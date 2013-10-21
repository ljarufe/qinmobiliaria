# -*- coding: utf-8 -*-

from django import template

register = template.Library()


@register.inclusion_tag('proyectos/templatetags/oferta.html')
def get_random_oferta(proyecto):
    """
    Devuelve la lista de rubros
    """
    return {'oferta': proyecto.get_random_oferta()}