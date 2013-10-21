# -*- coding: utf-8 -*-

from django import template
from proyectos.models import Aviso

register = template.Library()


@register.inclusion_tag('common/templatetags/pager.html')
def paginator(paginated_list):
    """
    Muestra el paginador estandar para servicios de una lista paginada
    """
    return {'paginated_list': paginated_list}


@register.inclusion_tag('common/templatetags/publicidad.html')
def publicidad():
    """
    Muestra un slider automático de publicidades
    """
    return {'total': Aviso.objects.count()}