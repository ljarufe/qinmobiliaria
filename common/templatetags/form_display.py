# -*- coding: utf-8 -*-

from django import template
from django.utils.translation import ugettext_lazy as _

register = template.Library()

@register.inclusion_tag('common/templatetags/display_as_table.html')
def display_as_table(form):
    """
    Muestra los campos del formulario en forma de lista
    """
    return {'form': form}