# -*- coding: utf-8  -*-
"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.core.files import File
from proyectos.models import Rubro, Proyecto, Oferta, Plano, TipoItemNombre, \
TipoItem, Item
from portal.models import Inmobiliaria, Area
from common.models import Poligono
import urls, random, os
from datetime import date, datetime

class BaseOperation(TestCase):
    def _get_random_string(self, length=5):
        import string
        return ''.join(random.choice(string.letters) for i in xrange(length))

    def _create_grupos(self):
        for g in ['Informacion','Comercial','Help Desk']:
            Group.objects.get_or_create(name=g)        

    def _create_rubro(self):
        return Rubro.objects.create(nombre = self._get_random_string(),
                                    descripcion = self._get_random_string(1),
                                    texto_email = self._get_random_string(1)) 
    def _create_inmobiliaria(self):
        I, created = Inmobiliaria.objects.get_or_create(
            nombre="Quimera Inmobiliaria")
        logoPath = os.path.join(settings.STATIC_ROOT,
                                'proyectos/img/pdf', 'logo.jpg')
        watermarkPath = os.path.join(settings.STATIC_ROOT,
                                     'portal/img/inmobiliaria', 'waterMark.png')
        I.logo.save("logoquimera.png",File(open(logoPath)))
        I.logo_watermark.save("Wlogoquimera.png",File(open(watermarkPath)))
        I.save()
        return I

    def _create_proyecto(self, rubro=None):
        proyecto, created = Proyecto.objects.get_or_create(
            nombre = self._get_random_string(), latitud = 1, longitud = 1, 
            rubro=rubro,
            direccion = self._get_random_string(),
            fecha_inicio = date.today(), fecha_fin = date.today(),
            )
        return proyecto

    def _create_plano(self, proyecto):
        return Plano.objects.create(titulo=self._get_random_string(),
                                    proyecto=proyecto)

    def _create_tipoitemnombre(self):
        return TipoItemNombre.objects.create(nombre=self._get_random_string())
    
    def _create_tipoitem(self, tipoitemnombre, proyecto):
        return TipoItem.objects.create(proyecto=proyecto,
                                       nombre=tipoitemnombre,
                                       area=random.randint(1,100),
                                       precio=random.randint(1,100))

    def _create_poligono(self):
        poligono = Poligono.objects.create( nombre=self._get_random_string() )
        for i in xrange(random.randint(3,10)):
            poligono.punto_set.create( x=i, y=i)
        return poligono

    def _create_item(self, plano, tipoitem):
        return Item.objects.create(
            numero=random.randint(1,50),
            plano=plano,
            tipo_item=tipoitem,
            poligono=self._create_poligono()
            )

    def _create_area(self, i):
        area, created = Area.objects.get_or_create(
            nombre = self._get_random_string(),
            inmobiliaria = i
            )
        return area

    def _create_oferta(self, proyecto, item):
        return Oferta.objects.create(proyecto=proyecto,
                                     item=item,
                                     fecha_inicio=datetime.now(),
                                     duracion=random.randint(1,5),
                                     tasa_descuento=random.randint(1,99))


class TestPortalViews(BaseOperation):
   def test_allViews(self):
       """
       Prueba que se carguen correctamente todas las vistas de esta aplicación
       (no verifica su funcionamiento)
       """       
       i = self._create_inmobiliaria()
       r = self._create_rubro()
       p = self._create_proyecto(r)
       username = self._get_random_string()
       area = self._create_area(i)

       views_to_test = (
           ('', 'inicio'),
           ('/contacto/%s/%s/' % (r.id,p.id), 'contacto con parametros'),
           ('/contacto/', 'contacto'),
           ('/nosotros/', 'nosotros'),
           ('/ayuda_en_linea/%s/%s/' % (area.id, username), 'ayuda_en_linea'),
           ('/ayuda_ubicacion/', 'ayuda ubicacion'),
           ('/ayuda_areas/', 'ayuda areas'),
           ('/ayuda_suscripcion/','ayuda subscripcion'),
           ('/ayuda_separar/','ayuda separar'),
           ('/iframes/chat/','chat'),
           ('/json_get_aviso/','json_get_aviso'),
           ('/google4ee0c872608a0b7d.html/', 'google_webmaster_verification'),
           ('/%s/etapas/' % p.slug, 'etapas_proyecto',)
           # ('/%s' % p.slug, 'perfil_proyecto'),           
           )   

       for view in views_to_test:
           response = self.client.get(view[0])
           self.assertEqual(response.status_code, 200, view[1])

       #probando el proyecto con estado borrador
       perfil_proyecto = ('/%s' % p.slug, 'perfil_proyecto',)
       response = self.client.get(perfil_proyecto[0])
       self.assertEqual(response.status_code, 302, 
                        u'estado borrador ' + perfil_proyecto[1])
           
       #probando el proyecto con estado activo
       p.estado = u'A'
       p.save()
       response = self.client.get(perfil_proyecto[0])
       self.assertEqual(response.status_code, 200, 
                        u'estado activo' + perfil_proyecto[1])
       
       #aumentandole una oferta y resumen
       tin = self._create_tipoitemnombre()
       ti = self._create_tipoitem(tin,p)
       plano = self._create_plano(p)
       item = self._create_item(plano, ti)
       of = self._create_oferta(p,item)
       p.resumen=u'litte summary jiji'
       p.save()
       response = self.client.get(perfil_proyecto[0])
       self.assertEqual(response.status_code, 200, 
                        u'oferta y resumen' + perfil_proyecto[1])


