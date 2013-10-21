# -*- coding: utf-8 -*-
from django import template
from proyectos.models import Proyecto, Contacto

register = template.Library()

@register.simple_tag(takes_context=True)
def get_3_telephones(context):
    """
    retorna todos sus telefonos asociados a los contactos del contexto
    """
    contact = context['contacto']
    phoneList = u''

    contactList = contact.telefonos.all()[:3]
    for f in contactList:
        phoneList += f.numero + u'&nbsp;/&nbsp;'
    if phoneList:
        phoneList = phoneList[:-7]
    return phoneList


@register.simple_tag(takes_context=True)
def get_all_telephones(context):
    """
    retorna todos sus telefonos asociados a los contactos del contexto
    """
    contact = context['contacto']
    contactList = contact.telefonos.all()
    phoneList = u''.join(
        u'<li>%s (%s)</li>' % (f.numero,f.tipo_telefono) for f in contactList)
    return u'<ul>%s</ul>' % phoneList

# @register.simple_tag(takes_context=True)
# def get_all_emails(context):
#     """
#     retorna todos los emails de los contactos
#     """
#     contacts = context['contactos']
#     emailList = u''
#     for c in contacts:
#         emailList += c.email + u'&nbsp;&nbsp;'
#     return emailList
