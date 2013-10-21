"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse
from models import TipoTelefono
from proyectos.models import Rubro, Proyecto, Contacto
import random
from datetime import date


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

    # def _create_cliente(self):
    #     from django.contrib.auth.models import User
    #     u=User.objects.create(
    #         username = self._get_random_string(), password = '1')
    #     return Cliente.objects.create(usuario = u)

    def _create_superuser(self):
        from django.contrib.auth.models import User
        u=User.objects.create(
            username = self._get_random_string(), password = '1', is_staff=True,
            is_active=True, is_superuser=True)
        u.set_password('1')
        u.save()
        return u

    def _create_proyecto(self, rubro=None):
        from django.conf import settings
        #import os
        #imagen = os.path.join(settings.STATIC_ROOT, 'probe.jpg')
        proyecto, created = Proyecto.objects.get_or_create(
            nombre = self._get_random_string(), latitud = 1, longitud = 1, 
            #foto_principal = f, 
            rubro=rubro,
            direccion = self._get_random_string(),
            fecha_inicio = date.today(), fecha_fin = date.today()
            )
        
        return proyecto

    def _create_contacto(self, proyecto):
        c = Contacto.objects.create(direccion=self._get_random_string(),
                                    email=self._get_random_string()+'@mail.com',
                                    proyecto=proyecto)
        for i in xrange(5):
            c.telefonos.create(
                numero=self._get_random_string(),
                tipo_telefono=TipoTelefono.objects.create(
                    nombre=self._get_random_string()
                    )
                )
        return c


class TestTipoTelefono(BaseOperation):
    def test_borrar_tipotelefono(self):
        """
        verifica solo se borren lso tipos de telefono que no estan asociados
        a un telefono. Realiza esta verificacion tanto en la accion delete
        del changelits como en el delete_view
        """
        self._create_grupos()
        r=self._create_rubro()
        p=self._create_proyecto(r)
        self._create_contacto(p)
        tt1=TipoTelefono.objects.create(nombre='1')
        tt2=TipoTelefono.objects.create(nombre='1')
        self.assertEqual(TipoTelefono.objects.count(),7,
                         'Not all tipotelefono objects were created')
        
        #crea un usuario 
        u = self._create_superuser()
        #logear usuario
        result = self.client.login(username=u.username,password='1')
        self.assertEqual(result, True, 'Login process Failed')

        #tratando de borrar los objetos tipotelefono asociados al proyecto
        #desde el changelist y desde el delete_view
        for i in xrange(1,6):            
            response = self.client.post(
                reverse('admin:common_tipotelefono_changelist'),
                {'_selected_action':i,
                 'action':'borrar_tipotelefonos',
                 }
                )

            response = self.client.post(
                reverse( 'admin:common_tipotelefono_delete', args=(i,) ))

        #tratando de borrar uno de los objetos tipotelefono no asociados desde
        #el changelist
        response = self.client.post(
            reverse('admin:common_tipotelefono_changelist'),
            {'_selected_action':tt1.id,
             'action':'borrar_tipotelefonos',
             }
            )

        #verificando que solo se borro tt1
        self.assertEqual(TipoTelefono.objects.count(),6,
                         'Wrong tipo item deletion')

        #tratando de borrar uno de los objetos tipotelefono no asociados
        #desde el delete view
        response = self.client.post(
            reverse( 'admin:common_tipotelefono_delete', args=(tt2.id,) ))
        
        #verificando que se borro tt2
        self.assertEqual(TipoTelefono.objects.count(),5,
                         'Wrong tipo item deletion')
