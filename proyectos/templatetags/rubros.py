# -*- coding: utf-8 -*-

from django import template
from qinmobiliaria.proyectos.models import Rubro, Proyecto

register = template.Library()


@register.inclusion_tag('proyectos/templatetags/lista_rubros.html', takes_context=True)
def lista_rubros(context):
    """
    Devuelve la lista de rubros
    """
    menu = []
    rubros = Rubro.objects.all()
    for rubro in rubros:
        proyectos = Proyecto.accepted.filter(rubro=rubro)
        if proyectos:
            menu.append({'rubro': rubro, 'proyectos': proyectos})

    return {'menu': menu, "context": context}