# -*- coding: utf-8 -*-

from django import template
from portal.models import Inmobiliaria

register = template.Library()


@register.inclusion_tag('portal/templatetags/fb_link.html')
def fb_link():
    """
    Muestra los links a las cuentas en redes sociales de la inmobiliaria
    """
    try:
        inmobiliaria = Inmobiliaria.objects.latest("id")

        return {'fb_link': inmobiliaria.link_facebook}
    except Inmobiliaria.DoesNotExist:
        return None


@register.inclusion_tag('portal/templatetags/tw_link.html')
def tw_link():
    """
    Muestra los links a las cuentas en redes sociales de la inmobiliaria
    """
    try:
        inmobiliaria = Inmobiliaria.objects.latest("id")

        return {'tw_link': inmobiliaria.link_twitter}
    except Inmobiliaria.DoesNotExist:
        return None


@register.inclusion_tag('portal/templatetags/logo.html')
def logo():
    """
    Muestra el link
    """
    try:
        inmobiliaria = Inmobiliaria.objects.values('logo').latest("id")

        return {'inmobiliaria': inmobiliaria}
    except Inmobiliaria.DoesNotExist:
        return None
