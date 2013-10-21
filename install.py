# -*- coding: utf-8 -*-

"""
Este archivo debe ser ejecutado despues de crear los modelos, crea los grupos
y sus permisos para los managers del chat

>> python manage.py syncdb
>> python install.py
"""

from os import environ
environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.core.files import File
from usuarios.models import AdminComercial
from portal.models import Inmobiliaria
import os
# diccionario de grupos y sus respectivos permisos
groups_permissions = {
    'Informacion':( ({'app_label':'zinnia'},{'model':'category'},
                     {'permissions':(u'All',)}),
                    ({'app_label':'zinnia'},{'model':'entry'},
                     {'permissions':(u'All',)}),
                    ({'app_label':'comments'},{'model':'comment'},
                     {'permissions': (u'Can moderate comments',
                                      u'Can change comment',
                                      u'Can delete comment')}),
                    ({'app_label':'comments'},{'model':'commentflag'},
                     {'permissions': (u'Can add comment flag',
                                      u'Can change comment flag',
                                      u'Can delete comment flag')}),
                    ({'app_label':'common'},{'model':'fuente'},
                     {'permissions': (u'All',)}),
                    ({'app_label':'common'},{'model':'sitiofuente'},
                     {'permissions': (u'All',)}),
                    ({'app_label':'proyectos'},{'model':'avance'},
                     {'permissions':(u'All',)}),                   
                    ),
    'Comercial': ( ({'app_label':'auth'},{'model':'user'},
                    {'permissions': (u'Can add author', 
                                     u'Can change author', 
                                     u'Can delete author')}),
                   ({'app_label':'comments'},{'model':'comment'},
                     {'permissions': (u'Can moderate comments',
                                      u'Can change comment',
                                      u'Can delete comment')}),
                   ({'app_label':'comments'},{'model':'commentflag'},
                    {'permissions': (u'All',)}),                   
                   ({'app_label':'common'},{'model':'tipotelefono'},
                    {'permissions': (u'All',)}),
                   ({'app_label':'common'},{'model':'referencia'},
                    {'permissions': (u'Can change referencia',
                                     u'Can delete referencia')}),
                   ({'app_label':'common'},{'model':'fuente'},
                    {'permissions': (u'All',)}),
                   ({'app_label':'common'},{'model':'sitiofuente'},
                    {'permissions': (u'All',)}),
                   ({'app_label':'portal'},{'model':'faq'},
                    {'permissions': (u'All',)}),
                   ({'app_label':'portal'},{'model':'area'},
                    {'permissions': (u'All',)}),
                   ({'app_label':'portal'},{'model':'inmobiliaria'},
                    {'permissions': (u'Can change Inmobiliaria',)}),
                   ({'app_label':'proyectos'},{'model':'alerta'},
                    {'permissions': (u'All',)}),
                   ({'app_label':'proyectos'},{'model':'avance'},
                    {'permissions': (u'All',)}),
                   ({'app_label':'proyectos'},{'model':'aviso'},
                    {'permissions': (u'All',)}),
                   ({'app_label':'proyectos'},{'model':'etapa'},
                    {'permissions': (u'All',)}),
                   ({'app_label':'proyectos'},{'model':'oferta'},
                    {'permissions': (u'All',)}),
                   ({'app_label':'proyectos'},{'model':'plano'},
                    {'permissions': (u'All',)}),
                   ({'app_label':'proyectos'},{'model':'proyecto'},
                    {'permissions': (u'All',)}),
                   ({'app_label':'proyectos'},{'model':'tipoitem'},
                    {'permissions': (u'All',)}),
                   ({'app_label':'proyectos'},{'model':'tipoitemnombre'},
                    {'permissions': (u'All',)}),
                   # ({'app_label':'sites'},{'model':'site'},
                   #  {'permissions': (u'Can change site',)}),
                   ({'app_label':'usuarios'},{'model':'admincomercial'},
                    {'permissions': (u'All',)}),
                   ({'app_label':'usuarios'},{'model':'adminhelpdesk'},
                    {'permissions': (u'All',)}),
                   ({'app_label':'usuarios'},{'model':'admininformacion'},
                    {'permissions': (u'All',)}),
                   ({'app_label':'usuarios'},{'model':'cliente'},
                    {'permissions': (u'All',)}),
                   ({'app_label':'usuarios'},
                    {'model':'mensajeformulariocontacto'},
                    {'permissions': (u'Can change Mensaje del formulario de \
contacto',)}),
                   ({'app_label':'usuarios'},{'model':'solicitud'},
                    {'permissions': (u'Can change Solicitud',)}),
                   ({'app_label':'usuarios'},{'model':'ventaterreno'},
                    {'permissions': (u'Can change venta terreno',)}),
                   ({'app_label':'zinnia'},{'model':'category'},
                    {'permissions':(u'All',)}),
                   ({'app_label':'zinnia'},{'model':'entry'},
                    {'permissions':(u'All',)}),                   

                   ),
        }

#crea los grupos y les asigna los permisos correspondientes
for g in groups_permissions.iteritems():
    group, created = Group.objects.get_or_create(name=g[0])
    for i in g[1]:
        ct = ContentType.objects.get(app_label=i[0]['app_label'], 
                                     model=i[1]['model'])
        if i[2]['permissions'][0] == u'All':
            a=1
            for permission in ct.permission_set.all():
                group.permissions.add(permission)
        else:
            for permission in i[2]['permissions']:
                group.permissions.add(
                    Permission.objects.get(name=permission, content_type=ct))

# Crear los nuevos permisos
user = ContentType.objects.get(app_label="auth", model='user')
help_desk_perm, created = Permission.objects.get_or_create(
    name=u'Puede administrar un canal de chat',
    codename='puede_help_desk',
    content_type=user)

# Crear los grupos iniciales asociado a los permisos creados
help_desk_managers, created= Group.objects.get_or_create(name='Help Desk')
help_desk_managers.permissions.add(help_desk_perm)

print "Groups and Permissions installed!"


# Crea los datos iniciales de la inmobiliaria
print "Creating initial data"

I, created = Inmobiliaria.objects.get_or_create(nombre="Quimera Inmobiliaria")
logoPath = os.path.join(settings.STATIC_ROOT,
                      'proyectos/img/pdf', 'logo.jpg')
watermarkPath = os.path.join(settings.STATIC_ROOT,
                                'portal/img/inmobiliaria', 'waterMark.png')

#I.save()
I.logo.save("logoquimera.png",File(open(logoPath)))
I.logo_watermark.save("Wlogoquimera.png",File(open(watermarkPath)))
I.save()

# I, created = Inmobiliaria.objects.get_or_create(nombre="Quimera Inmobiliaria")
# I.logo = os.path.join(settings.STATIC_URL,
#                       'common/img', 'Logo QUimera.png')
# I.logo_watermark = os.path.join(settings.STATIC_URL,
#                                 'portal/img/inmobiliaria', 'waterMark.png')
# I.save()


# Crea la cuenta de un Administrador Comercial por defecto
# solo si existe la cuenta que existe es la root de usuario  que se crea al 
# sincronizar la DB
if User.objects.count() == 1:
    # usuario = User.objects.create(username='QIadmin',
    #                              first_name='QIadmin',
    #                              last_name='QIadmin',
    #                              is_active=True,
    #                              is_staff=True,)
    # usuario.set_password('q1720i')
    # usuario.save()
    # ac = AdminComercial.objects.create(usuario=usuario,
    #                                    asignar_proyectos=True)
    usuario1 = User.objects.create(username='QIadmin1',
                                   first_name='QIadmin1',
                                   last_name='QIadmin1',
                                   is_active=True,
                                   is_staff=True,)
    usuario1.set_password('q1720i')
    usuario1.save()
    usuario2 = User.objects.create(username='QIadmin2',
                                   first_name='QIadmin2',
                                   last_name='QIadmin2',
                                   is_active=True,
                                   is_staff=True,)
    usuario2.set_password('q2017i')
    usuario2.save()
    AdminComercial.objects.create(usuario=usuario1,
                                  asignar_proyectos=True)
    AdminComercial.objects.create(usuario=usuario2,
                                  asignar_proyectos=True)

print "Initial data cretated!"
