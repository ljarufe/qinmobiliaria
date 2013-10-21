# -*- coding: utf-8 -*-

from django import template
from zinnia.models import Entry

register = template.Library()

@register.inclusion_tag('portal/templatetags/noticias_footer.html')
def noticias():
    """
    Muestra las 4 entradas mas recientes del blog de noticias
    """
    return {'noticias': Entry.published.all().order_by("-creation_date")[:4]}