# -*- coding: utf-8 -*-

import sha
import random
from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from common.models import TipoTelefono
from portal.models import Inmobiliaria
from proyectos.models import Rubro
from proyectos.tests import BaseOperation
from usuarios.models import Cliente

# TODO: HAY QUE AJUSTAR ESTOS TEST PORQUE LOS 2 ULTIMOS NO CORREN
# class TestUsuariosViews(BaseOperation):
#     """
#     Test para el módulo de usuarios
#     """

#     def _create_inmobiliaria(self):
#         """
#         Crea una inmobiliaria
#         """
#         foto = '%s/public/media/sorl-thumbnail-test_01.jpg' % settings.BASEDIR
#         inmobiliaria = Inmobiliaria(link_facebook=u"", link_twitter=u"",
#                                     logo=foto, logo_watermark=foto)
#         inmobiliaria.save()

#         return inmobiliaria

#     def _create_user(self, username, is_active=True):
#         """
#         Crea un nuevo usuario
#         """
#         user, created = User.objects.get_or_create(username=username,
#                                                    email=username,
#                                                    is_active=is_active)
#         user.set_password('123')
#         user.save()

#         return user

#     def _create_cliente(self, nombre, is_active=True):
#         """
#         Crea un cliente
#         """
#         salt = sha.new(str(random.random())).hexdigest()[:5]
#         key = sha.new(salt+"cadena_texto").hexdigest()
#         cliente = Cliente(usuario=self._create_user(nombre, is_active),
#                           clave_activacion=key)
#         cliente.save()

#         return cliente

#     def _create_tipo_telefono(self, nombre):
#         """
#         Crea un nuevo tipo de telefono
#         """
#         tipo = TipoTelefono(nombre=nombre)
#         tipo.save()

#         return tipo

#     def _create_rubro(self, nombre):
#         """
#         Crea u nuevo rubro
#         """
#         rubro = Rubro(nombre=nombre, descripcion=u"", texto_email=u"")
#         rubro.save()

#         return rubro

#     def test_login(self):
#         """
#         Prueba el correcto funcionamiento del login
#         """
#         user = self._create_user("test@test.com")
#         response = self.client.post("/usuarios/iframes/login/",
#                                     {'email': "test@test.com",
#                                      'contrasena': "123"},
#                                     HTTP_HOST='127.0.0.1:8082')
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(self.client.session.get('_auth_user_id'), user.pk)

#     def test_recuperar_pass(self):
#         """
#         Prueba para el iframe de recuperar password
#         """
#         cliente = self._create_cliente("test@test.com")
#         response = self.client.post("/usuarios/iframes/recuperar_pass/",
#                                     {"email": "test@test.com"},
#                                     HTTP_HOST='127.0.0.1:8082')
#         self.assertEqual(response.status_code, 200)

#     def test_registro_cliente(self):
#         """
#         Prueba el registro de un nuevo cliente
#         """
#         self._create_inmobiliaria()
#         response = self.client.post("/usuarios/registro/",
#                                     {'form-1-id': u'',
#                                      'form-INITIAL_FORMS': u'0',
#                                      'apellido': u'Apellido',
#                                      'form-MAX_NUM_FORMS': u'',
#                                      'recibir_email': u'on',
#                                      'form-0-tipo_telefono': self._create_tipo_telefono("tipo1").id,
#                                      'rubros_interes': [self._create_rubro("rubro1").id],
#                                      'form-TOTAL_FORMS': u'2',
#                                      'form-0-id': u'',
#                                      'form-1-numero': u'111111',
#                                      'form-0-numero': u'222222',
#                                      'nombre': u'Nombre',
#                                      'contrasena': u'a',
#                                      'form-1-tipo_telefono': self._create_tipo_telefono("tipo2").id,
#                                      'email': u'test1@test.com',
#                                      'rastrear_proyectos': u'on'},
#                                      HTTP_HOST='127.0.0.1:8082')
#         self.assertEqual(response.status_code, 200)
#         cliente = Cliente.objects.get(id=1)
#         self.assertEqual(cliente.usuario.username, u'test1@test.com')
#         self.assertEqual(cliente.rastrear_proyectos, True)
#         telefonos = cliente.telefonos.all()
#         self.assertEqual(telefonos[0].numero, u'222222')



class TestUsuariosViews(BaseOperation):
   def test_allViews(self):
       """
       Prueba que se carguen correctamente todas las vistas de esta aplicación
       (no verifica su funcionamiento)
       """
       i = self._create_inmobiliaria()
       r = self._create_rubro()
       p = self._create_proyecto(r)
       plano = self._create_plano(p)
       p.estado = u'A'
       p.save()
       username = self._get_random_string()
       area = self._create_area(i)

       tin = self._create_tipoitemnombre()
       ti = self._create_tipoitem(tin,p)
       item = self._create_item(plano, ti)

       #crea un cliente
       u = self._create_cliente(True)

       salt = sha.new(str(random.random())).hexdigest()[:5]
       self.clave_activacion = sha.new(salt+u.usuario.email).hexdigest()
       u.save()
       key = u.clave_activacion

       data_register = {'username':self._get_random_string(),
                        'email':'xuxuca@mail.com',
                        'first_name': 'xuxuca',
                        'last_name': 'xuxuca',
                        'id':'',}

       s = self._create_solicitud(item, p, u, 'S')
       cancelar = {'id_solicitud': s.id}

       hd = self._create_adminHelpDesk()

       #not login required views
       views_to_test = (
           ('registro_corredor/', {}, 'registro_corredor', 200),
           ('registro/%s/' % r.id, {}, 'registro con rubro', 200),
           ('registro/', {}, 'registro sin rubro' ,200),
           ('iframes/login/', {}, 'login', 200),
           ('iframes/recuperar_pass/', {}, 'recuperar_pass', 200),
           ('channel/', {}, 'fb_channel', 200),
           ('json_registro/', data_register, 'json_registro', 200),
           ('cambio_password/%s/%s/' % (key,'12345'), {}, 'cambio_password', 302),
           ('verificar/%s/' % key, {}, 'verificar', 302),
           )

       for view in views_to_test:
           response = self.client.get('/usuarios/'+view[0], view[1])
           self.assertEqual(response.status_code, view[3], 
                            str(response.status_code)+view[2])

       self.client.logout()

       #login required views
       views_to_test = (
           ('', {}, 'perfil_privado_usuario', 200),
           ('iframes/editar_usuario/', {}, 'usuario_editar', 200),
           ('iframes/cambiar_password/', {}, 'usuario_cambiar_password', 200),
           ('iframes/editar_intereses/', {}, 'usuario_intereses', 200),
           ('iframes/editar_subscripciones/', {}, 'usuario_subscripciones', 200),
           ('iframes/editar_separados/', {}, 'usuario_separados', 200),
           ('json_cancelar_solicitud/', cancelar, 'json_cancelar_solicitud', 200),
           ('logout/', {}, 'logout', 302),
           )

       for view in views_to_test:
           response = self.client.get('/usuarios/'+view[0], view[1])
           self.assertEqual(response.status_code, 302, 
                            str(response.status_code)+view[2])

       #trying login required views but now logged in
       #logea al cliente
       result = self.client.login(username=u.usuario.username,password='12345')
       self.assertEqual(result, True, 'Login process Failed')

       for view in views_to_test:
           response = self.client.get('/usuarios/'+view[0], view[1])
           self.assertEqual(response.status_code, view[3], 
                            str(response.status_code)+view[2])
       

       #trying help desk view
       
       # 1 - with no AdminHelpDesk Account
       response  = self.client.get('/usuarios/ayuda_clientes/')
       self.assertEqual(response.status_code, 302, 
                        str(response.status_code)+' ayuda clientes')
       # 2 - with AdminHelpDesk Account 
       self.client.logout()
       self.client.login(username = hd.usuario.username,password='1')
       self.assertEqual(result, True, 'Login process Failed')

