# -*- coding: utf-8 -*-

import os
import random
from django.conf import settings
from django.core.mail import EmailMultiAlternatives, send_mass_mail
from django.core import mail
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext, Context
from django.utils import simplejson, encoding
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from random import Random
import string


def direct_response(request, *args, **kwargs):
    """
    Forma resumida de render_to_response, enviando context_instance al template
    """
    kwargs['context_instance'] = RequestContext(request)
    return render_to_response(*args, **kwargs)


def json_response(data):
    """
    Devuelve una respuesta json con la información de data
    """
    return HttpResponse(simplejson.dumps(data), mimetype='application/json')


def send_html_mail(from_email, subject, templateName, data, to_, text_content='',
                   files=None, path='email_templates/'):
    """
    Envia un correo con un template en html, data es un diccionario y files una
    lista de archivos adjuntos
    """
    ############### hack para que envie el mail con un nombre ############
    try:
        from_email = "%s <%s>" % (settings.SENDER_NAME, from_email)
    except AttributeError:
        pass
    ######################################################################
    context = Context(data)
    html_content = mark_safe(render_to_string(
        '%s%s' % (path, templateName), context))
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to_])
    msg.attach_alternative(html_content, "text/html")
    if files:
        for afile in files:
            msg.attach_file(afile)
    else:
        pass
    msg.send()

#    try:
#        context = Context(data)
#        html_content = mark_safe(render_to_string(
#            '%s%s' % (path, templateName), context))
#        msg = EmailMultiAlternatives(subject, text_content, from_email, [to_])
#        msg.attach_alternative(html_content, "text/html")
#        msg.send()
#    except:
#        a=1

def send_mass_html_mails(from_email, subject, templateName, data, receivers,
                         text_content='', files=None, path='email_templates/'):
    """
    Envía eficientemente varios correos con un template en html, data es un 
    diccionario y files una lista de archivos adjuntos
    """
    ############### hack para que envie el mail con un nombre ############
    try:
        from_email = "%s <%s>" % (settings.SENDER_NAME, from_email)
    except AttributeError:
        pass
    ######################################################################
    context = Context(data)
    html_content = mark_safe(render_to_string(
        '%s%s' % (path, templateName), context))
    li = []
    for to_ in receivers:
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to_])
        msg.attach_alternative(html_content, "text/html")
        if files:
            for afile in files:
                msg.attach_file(afile)
        else:
            pass
        li.append(msg)

    if receivers:
        connection = mail.get_connection()
        connection.send_messages(li)

def send_mass_text_mails(datatuple, sitio, static_url, templateName, 
                         path='email_templates/'):
    """
    envia masivamente correos abriendo una sola conexión en el servidor de 
    correos
    datatuple = ((subject, message, from_email, recipient_list),
    (subject, message, from_email, recipient_list),
    )
    NOTA: lo malo es que solo envia texto plano
    """
    data ={ 'sitio':sitio,
            'STATIC_URL':static_url,}
    for i in datatuple:
        data['msg'] = i[1]
        i[1] = mark_safe(render_to_string('%s%s' % (path, templateName), data))
    send_mass_mail(datatuple, fail_silently=False)


def get_paginated(request, object_list, num_items):
    """
    Devuelve una lista paginada de una lista de objetos y el
    número de objetos por página
    """
    paginator = Paginator(object_list, num_items)

    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    try:
        lista_paginada = paginator.page(page)
    except (EmptyPage, InvalidPage):
        lista_paginada = paginator.page(paginator.num_pages)

    return lista_paginada


def make_password(length=8):
    """
    Devuelve una cadena aleatoria de tamaño length
    """
    return ''.join(Random().sample(string.letters+string.digits, length))


def convert_unicode_to_string(x):
   """
   >>> convert_unicode_to_string(u'ni\xf1era')
   'niera'
   """
   return encoding.smart_str(x, encoding='ascii', errors='ignore')


def json_fastsearch(queryset, search_field, substring, fields):
    """
    Realiza una fastsearch dentro de una tabla retornando un diccionario json
    con los atributos seleccionados enviando los nombres correctos en forma de
    diccionario con el siguiente formato
    {"id": "id",
    "name": "nombre",
    "description": "descripcion",
    "image": "foto"}
    """
    filter = "%s__icontains" % search_field
    match_list = queryset.filter(**{filter: substring})
    json_dict = []
    for object in match_list:
        json_dict.append(
                {"id": getattr(object, fields["id"]),
                 "name": getattr(object, fields["name"]),
                 "subtitle": getattr(object, fields["subtitle"]).nombre,
                 "description": getattr(object, fields["description"]),
                 "image": getattr(object, fields["image"]).extra_thumbnails.get('small').absolute_url,
                 # TODO: Para athumbs
                 #"image": getattr(object, fields["image"]).generate_url("icon")
                 })

    return json_response(json_dict)


def get_object_or_none(Model, *args, **kwargs):
    """
    Retorna el objeto o None en caso de que no exista este
    """
    try:
        Model.objects.get(*args, **kwargs)
        return Model.objects.get(*args, **kwargs)
    except Model.DoesNotExist:
        return None


def highlyRandomName(filename, longitud=20):
    """
    retorna un nombre aleatorio de longitud igual a 'longitud',
    manteniendo la extension de la imagen
    """
    lista_letras_numeros = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
    name = "".join([random.choice(lista_letras_numeros) for i in xrange(longitud)])
    root, ext = os.path.splitext(filename)

    return name + ext