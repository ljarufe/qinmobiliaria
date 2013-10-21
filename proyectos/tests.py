# -*- coding: utf-8 -*-
"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.files import File
from django.core.urlresolvers import reverse
from models import Rubro, Proyecto, Etapa, SubEtapa, Avance, Milestone, \
TipoItemNombre, TipoItem, Oferta, Plano, Item, Alerta, Aviso, Contacto, \
Caracteristica, Beneficio
from usuarios.models import Cliente, AdminComercial, CambioEstadoItem, \
Solicitud, MensajeFormularioContacto, Respuesta, AdminHelpDesk
from portal.models import Inmobiliaria, Area
from common.models import Foto, Video, Poligono, Punto, TipoTelefono, Provincia,\
Telefono, Departamento
from datetime import date, datetime
from zinnia.models import Entry
import urls, random, os

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

    def _create_cliente(self, active=False):
        u=User.objects.create(
            username = self._get_random_string(), 
            is_active=active)
        u.set_password('1')
        u.save()
        return Cliente.objects.create(usuario = u)

    def _create_superuser(self):
        from django.contrib.auth.models import User
        u=User.objects.create(
            username = self._get_random_string(), is_staff=True,
            is_active=True, is_superuser=True)
        u.set_password('1')
        u.save()
        return u

    def _create_adminComercial(self):
        from django.contrib.auth.models import User
        u=User.objects.create(
            username = self._get_random_string(), password = '1', is_staff=True,
            is_active=True)
        u.set_password('1')
        u.save()
        return AdminComercial.objects.create(usuario = u)

    def _create_adminHelpDesk(self):
        from django.contrib.auth.models import User
        u=User.objects.create(
            username = self._get_random_string(), password = '1', is_staff=True,
            is_active=True)
        u.set_password('1')
        u.save()
        return AdminHelpDesk.objects.create(usuario = u)


    def _create_proyecto(self, rubro=None):
        from django.conf import settings
        #import os
        #imagen = os.path.join(settings.STATIC_ROOT, 'probe.jpg')
        proyecto, created = Proyecto.objects.get_or_create(
            nombre = self._get_random_string(), latitud = 1, longitud = 1, 
            foto_principal = 'no-image.png', 
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

    def _create_proyecto_videos(self, proyecto, numVideos=5):
        for i in xrange(numVideos):
            proyecto.videos.create(nombre=self._get_random_string())

    def _create_proyecto_fotos(self, proyecto, numFotos=5):
        for i in xrange(numFotos):
            proyecto.fotos.create(nombre=self._get_random_string())    

    def _create_alerta(self,proyecto):
        return Alerta.objects.create(proyecto=proyecto,
                                     tipo='o',
                                     fecha_inicio=datetime.now(),
                                     duracion=random.randint(1,3))

    def _create_aviso(self, proyecto):
        return Aviso.objects.create(proyecto=proyecto,
                                    duracion=random.randint(1,3))

    def _create_caracteristica(self,proyecto):
        return Caracteristica.objects.create(
            nombre=self._get_random_string(),
            descripcion=self._get_random_string(),
            proyecto=proyecto)

    def _create_beneficios(self, proyecto, numben=5):
        for i in xrange(numben):
            proyecto.beneficio_set.create(descripcion=self._get_random_string())
    
    def _create_etapa(self, proyecto, porcentaje=0):
        if not porcentaje:
            porcentaje = random.randint(1,100)
        return Etapa.objects.create(titulo=self._get_random_string(),
                                    proyecto=proyecto,
                                    descripcion=self._get_random_string(),
                                    fecha_inicio = date.today(),
                                    fecha_fin=date.today(),
                                    porcentaje=porcentaje)

    def _create_subetapa(self, etapa, porcentaje=0):
        if not porcentaje:
            porcentaje = random.randint(1,100)
        return SubEtapa.objects.create(titulo=self._get_random_string(),
                                        etapa=etapa,
                                        fecha_inicio=date.today(),
                                        fecha_fin=date.today(),
                                        porcentaje=porcentaje)

    def _create_avance(self, proyecto, subetapa):
        return Avance.objects.create(notas=self._get_random_string(),
                                     estado=u'B',
                                     proyecto=proyecto,
                                     subetapa=subetapa)

    def _create_milestone(self, subetapa, avance, alcanzado=False, porcentaje=0):
        if not porcentaje:
            porcentaje = random.randint(1,100)
        return Milestone.objects.create(titulo=self._get_random_string(),
                                        subetapa=subetapa,
                                        avance=avance,
                                        alcanzado=alcanzado,
                                        fecha_fin=date.today(),
                                        porcentaje=porcentaje)

    def _create_fotos_avance(self, avance, num_fotos):
        for i in xrange(num_fotos):
            avance.fotos.create(nombre=str(i))

    def _create_videos_avance(self, avance, num_videos):
        for i in xrange(num_videos):
            avance.videos.create(nombre=str(i))

    def _create_plano(self, proyecto):
        return Plano.objects.create(titulo=self._get_random_string(),
                                    proyecto=proyecto,
                                    plano='no-image.png',
                                    )

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

    def _create_solicitud(self, item, proyecto, cliente, tipo):
        return Solicitud.objects.create(item=item,
                                        proyecto=proyecto,
                                        cliente=cliente,
                                        tipo=tipo,
                                        )

    def _create_tipoitemnombre(self):
        return TipoItemNombre.objects.create(nombre=self._get_random_string())
    
    def _create_tipoitem(self, tipoitemnombre, proyecto):
        return TipoItem.objects.create(proyecto=proyecto,
                                       nombre=tipoitemnombre,
                                       area=random.randint(1,100),
                                       precio=random.randint(1,100),
                                       foto='no-image.png')

    def _create_oferta(self, proyecto, item):
        return Oferta.objects.create(proyecto=proyecto,
                                     item=item,
                                     fecha_inicio=datetime.now(),
                                     duracion=random.randint(1,5),
                                     tasa_descuento=random.randint(1,99))

    def _create_entries(self, proyecto, num=5):
        for i in xrange(num):
            proyecto.entry_set.create(title=self._get_random_string(),
                                      content=self._get_random_string(),
                                      )

    def _create_mensajeformulariocontacto(self, proyecto, cliente):
        return MensajeFormularioContacto.objects.create(
            proyecto=proyecto,
            cliente=cliente,
            mensaje=self._get_random_string(),
            )

    def _create_respuesta(self, user, mensaje):
        return Respuesta.objects.create(admin=user,
                                        mensaje=mensaje,
                                        respuesta=self._get_random_string())

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

        # Crear los nuevos permisos
        user = ContentType.objects.get(app_label="auth", model='user')
        help_desk_perm, created = Permission.objects.get_or_create(
            name=u'Puede administrar un canal de chat',
            codename='puede_help_desk',
            content_type=user)

        # Crear los grupos iniciales asociado a los permisos creados
        help_desk_managers, created= Group.objects.get_or_create(name='Help Desk')
        help_desk_managers.permissions.add(help_desk_perm)

        return I

    def _create_area(self, i):
        area, created = Area.objects.get_or_create(
            nombre = self._get_random_string(),
            inmobiliaria = i
            )
        return area


class TestProyectosViews(BaseOperation):
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


       views_to_test = (
           ('','resultados'),
           ('%s/' % r.id,'resultados con id'),
           ('rubro/%s/' % r.slug,'rubro'),
           ('venta_terreno/','venta_terreno'),
           ('fotos/%s/' % p.id,'fotos'),
           ('videos/%s/' % p.id,'videos'),
           ('planos/%s/' % plano.id,'planos'),
           ('planos_slider/%s/' % p.id,'planos_slider'),
           #('get_item_data/', 'proyectos_ajax_get_item_data'),
           ('solicitud/%s' % item.id, 'solicitud'),
           ('plano_item/%s' % item.id, 'plano_item'),
           #('solicitud_enviada/%s/' % item.id, 'solicitud_enviada'),
           ('items_proyecto/%s/' % p.id, 'items_proyecto'),
           #('json_suscribir/', 'json_suscribir'),
           #('json_desuscribir/', 'json_desuscribir'),
           #('json_afiliar/', 'json_afiliar'),
           #('json_desafiliar/', 'json_desafiliar'),
           #('json_proyectos_slider/','json_proyectos_slider')
           #('json_fast_proyectos/','json_fast_proyectos'),
           )

       for view in views_to_test:
           response = self.client.get('/proyectos/'+view[0])
           self.assertEqual(response.status_code, 200, str(response.status_code)+view[1])

       response = self.client.get('/proyectos/get_item_data/',
                                  {'item_id': item.id})
       self.assertEqual(response.status_code,200,'proyectos_ajax_get_item_data')
       
       response = self.client.get('/proyectos/solicitud_enviada/%s/' % item.id)
       self.assertEqual(response.status_code, 302, str(response.status_code)+'solicitud_enviada')

       response = self.client.get('/proyectos/json_suscribir/',
                                  {'rubro': r.id})
       self.assertEqual(response.status_code,302,'json_suscribir')

       response = self.client.get('/proyectos/json_desuscribir/',
                                  {'rubro_id': r.id})
       self.assertEqual(response.status_code,302,'json_desuscribir')

       response = self.client.get('/proyectos/json_afiliar/',
                                  {'proyecto': p.id})
       self.assertEqual(response.status_code,302,'json_afiliar')

       response = self.client.get('/proyectos/json_desafiliar/',
                                  {'proyecto_id': p.id})
       self.assertEqual(response.status_code,302,'json_desafiliar')

       response = self.client.get('/proyectos/json_proyectos_slider/',
                                  {'index': random.randint(1,10)})
       self.assertEqual(response.status_code,200,'json_proyectos_slider')

       response = self.client.get('/proyectos/json_fast_proyectos/',
                                  {'substring': ''})
       self.assertEqual(response.status_code,200,'json_fast_proyectos')

       response = self.client.get('/proyectos/json_fast_proyectos/',
                                  {'substring': self._get_random_string()})
       self.assertEqual(response.status_code,200,'json_fast_proyectos')
       

       #trying login required views (now logged in)
       #crea un cliente
       u = self._create_cliente(True)
       #logea al cliente
       result = self.client.login(username=u.usuario.username,password='1')
       self.assertEqual(result, True, 'Login process Failed')

       response = self.client.get('/proyectos/json_suscribir/',
                                  {'rubro': r.id})
       self.assertEqual(response.status_code,200, 'json_suscribir logged')

       response = self.client.get('/proyectos/json_desuscribir/',
                                  {'rubro_id': r.id})
       self.assertEqual(response.status_code,200, 'json_desuscribir logged')

       response = self.client.get('/proyectos/json_afiliar/',
                                  {'proyecto': p.id})
       self.assertEqual(response.status_code,200,'json_afiliar logged')
        
       response = self.client.get('/proyectos/json_desafiliar/',
                                  {'proyecto_id': p.id})
       self.assertEqual(response.status_code,200,'json_desafiliar logged')
        

class TestRubro(BaseOperation):
    def test_borrar_rubro(self):
        """
        Prueba que un rubro se borra correctamente sólo cuando debe borrarse
        """
        #crea un usuario 
        u = self._create_superuser()
        #logear usuario
        result = self.client.login(username=u.username,password='1')
        self.assertEqual(result, True, 'Login process Failed')

        #caso 1: no tiene ningún objeto relacionado (se borra)
        r=self._create_rubro()
        #Rubro().admin_borrar_rubro(Rubro.objects.all())
        response = self.client.post(
            reverse('admin:proyectos_rubro_changelist'),
            {'_selected_action':r.id,
             'action':'borrar_rubro',
             }
            )

        self.assertEqual(Rubro.objects.count(),0)
        #caso 2: cuando tiene clientes relacionados pero no proyectos (se borra)
        for j in xrange(5):
            r=self._create_rubro()
            for i in xrange(10):
                c = self._create_cliente()
                r.cliente_set.add(c)
            response = self.client.post(
                reverse('admin:proyectos_rubro_changelist'),
                {'_selected_action':r.id,
                 'action':'borrar_rubro',
                 }
                )
        # Rubro().admin_borrar_rubro(Rubro.objects.all())
#        self.client.post(reverse('admin:proyectos_rubro_delete', args=(,)))

        self.assertEqual(Rubro.objects.count(),0)
        self.assertEqual(Cliente.objects.count(),50)        
        Cliente.objects.all().delete()
        #caso 3: cuando tiene proyectos y clientes relacionados (no se borra)
        for j in xrange(5):
            r=self._create_rubro()
            for i in xrange(10):
                c = self._create_cliente()
                r.cliente_set.add(c)
                p = self._create_proyecto()
                r.proyecto_set.add(p)
            response = self.client.post(
                reverse('admin:proyectos_rubro_changelist'),
                {'_selected_action':r.id,
                 'action':'borrar_rubro',
                 }
                )

#        Rubro().admin_borrar_rubro(Rubro.objects.all())
        self.assertEqual(Rubro.objects.count(),5)
        self.assertEqual(Cliente.objects.count(),50)        
        self.assertEqual(Proyecto.objects.count(),50)

        
class TestProyecto(BaseOperation):
    def test_recalcular_avance(self):
        """
        Prueba que la funcion recalcular avance funcione correctamente
        """
        r=self._create_rubro()
        p=self._create_proyecto(r)

        ##caso 1: e1-30% [se1-10% se2-15%] avance = 7.5%
        e1 = self._create_etapa(p,30)
        se1 = self._create_subetapa(e1,10)
        se2 = self._create_subetapa(e1,15)
        av1 = self._create_avance(p,se1)
        av2 = self._create_avance(p,se1)
        m1_1 = self._create_milestone(se1, av1, True, 100)
        m2_1 = self._create_milestone(se2, av2, True, 100)
        self.assertEqual(p.avance,7.5)

        #caso 2: caso 1 + e1 [se3-50%] + e2-40% [se1-35% se2-60%] avance = 60.5%
        se3 = self._create_subetapa(e1,50)
        av3 = self._create_avance(p,se3)
        m3_1 = self._create_milestone(se3, av3, True, 100)
        
        e2 = self._create_etapa(p,40)
        
        se2_1 = self._create_subetapa(e2,35)
        av2_1 = self._create_avance(p,se2_1)
        m2_1 = self._create_milestone(se2_1,av2_1, True,100)

        se2_2 = self._create_subetapa(e2,60)
        av2_2 = self._create_avance(p,se2_2)
        m2_2 = self._create_milestone(se2_2,av2_2, True,100)

        self.assertEqual(p.avance, 60.5)

        #caso 3: caso 1 + caso 2 + e1 [se4-25%] + e2 [se3-5%] + 
        #        e3-10% [se1-50% se2-50%] avance = 80
        se4 = self._create_subetapa(e1,25)
        av4 = self._create_avance(p,se4)
        m4_1 = self._create_milestone(se4, av4, True, 100)
        
        se2_3 = self._create_subetapa(e2,5)
        av2_3 = self._create_avance(p,se2_3)
        m2_3 = self._create_milestone(se2_3,av2_3,True,100)

        e3 = self._create_etapa(p,10)
        
        se3_1 = self._create_subetapa(e3,50)
        av3_1 = self._create_avance(p,se3_1)
        m3_1 = self._create_milestone(se3_1,av3_1,True,100)

        se3_2 = self._create_subetapa(e3,50)
        av3_2 = self._create_avance(p,se3_2)
        m3_2 = self._create_milestone(se3_2,av3_2,True,100)
        self.assertEqual(p.avance, 80)

    def test_admin_delete(self):
        """
        verifica que al borrar un proyecto se borren todos sus objetos 
        relacionados
        """
        self._create_grupos()
        r=self._create_rubro()
        p=self._create_proyecto(r)
        for i in xrange(5):
            self._create_caracteristica(p)
            self._create_alerta(p)
            self._create_aviso(p)

        ti_name=self._create_tipoitemnombre()
        ti1=self._create_tipoitem(ti_name,p)
        plano1=self._create_plano(p)
        item1=self._create_item(plano1,ti1)
        oferta1=self._create_oferta(p,ti1)

        #crea un usuario 
        u = self._create_superuser()
        #logear usuario
        result = self.client.login(username=u.username,password='1')
        self.assertEqual(result, True, 'Login process Failed')
        
        #simulando cambios de estados del item 1
        cliente = self._create_cliente()
        response = self.client.post(
            reverse('admin:proyectos_item_change', args=(item1.id,)),
            {'numero':item1.numero,
             'tipo_item':item1.tipo_item.id,
             'estado':'D',
             'detalles':item1.detalles,
             'cliente':cliente.id,
             'id':item1.id,
             'plano':item1.plano.id,
             'poligono':item1.poligono.id}
            )

        #simulando aceptacion de una solicitud
        solicitud = self._create_solicitud(item1, p, cliente, 'S')
        response = self.client.post(
            reverse('admin:usuarios_solicitud_change', args=(solicitud.id,)),
            {'accion':'V', 'mensaje':'qqq', 'item':item1.id,
             '_continue':'Grabar y continuar editando'}
            )
        p.clientes.add(cliente)
        self._create_contacto(p)
        ac=self._create_adminComercial()
        p.usuarios.add(ac.usuario)
        p.provincia=Provincia.objects.order_by('?')[0]
        p.save()
        self._create_proyecto_videos(p)
        self._create_proyecto_fotos(p)
        e1 = self._create_etapa(p, 30)
        se1_1 = self._create_subetapa(e1,100)
        av1_1 = self._create_avance(p,se1_1)
        self._create_videos_avance(av1_1,5)
        self._create_fotos_avance(av1_1,5)
        m1_1_1 = self._create_milestone(se1_1, av1_1, False, 10)
        m1_1_2 = self._create_milestone(se1_1, av1_1, True, 90)
        av1_2 = self._create_avance(p,se1_1)
        self._create_videos_avance(av1_2,5)
        self._create_fotos_avance(av1_2,5)
        m1_2_1 = self._create_milestone(se1_1, av1_2, False, 100)
        e2 = self._create_etapa(p, 30)
        se2_1 = self._create_subetapa(e2,50)        
        av2_1 = self._create_avance(p,se2_1)
        m2_1_1 = self._create_milestone(se2_1, av2_1, True, 100)
        se2_2 = self._create_subetapa(e2,50)
        av2_2 = self._create_avance(p,se2_2)
        e3 = self._create_etapa(p, 40)
        se3_1 = self._create_subetapa(e3,100)        
        
        self._create_beneficios(p)
        self._create_entries(p)
        for i in xrange(5):
            mensaje = self._create_mensajeformulariocontacto(p, cliente)
            self._create_respuesta(ac.usuario,mensaje)
            self._create_respuesta(ac.usuario,mensaje)
        self.assertEqual(MensajeFormularioContacto.objects.count(),5,
                         'The message was not created')
        self.assertEqual(Respuesta.objects.count(),10,
                         'The respuesta was not created')

        #borrando el proyecto p
        #p.delete()
        response = self.client.post(
            reverse('admin:proyectos_proyecto_changelist'),
            {'_selected_action':p.id,
             'action':'borrar_proyectos',
             }
            )
        
        #verificando que se borraron sus objetos relacionados que debian borrarse
        self.assertEqual(Proyecto.objects.count(),0,
                         'The project was not deleted')
        self.assertEqual(TipoItem.objects.count(),0,
                         'The tipoitem object was deleted')
        self.assertEqual(Oferta.objects.count(),0,'The ofertas were not deleted')
        self.assertEqual(Caracteristica.objects.count(),0,
                         'The caracteristicas were not deleted')
        self.assertEqual(Alerta.objects.count(),0,'The alertas were not deleted')
        self.assertEqual(Plano.objects.count(),0,'The plano was not deleted')
        self.assertEqual(Item.objects.count(),0,'Not all items were deleted')
        self.assertEqual(Poligono.objects.count(),0,
                         'Not all poligons were deleted')
        self.assertEqual(Punto.objects.count(),0,'Not all points were deleted')
        self.assertEqual(Solicitud.objects.count(),0,
                         'Not all the solicitudes were deleted')
        self.assertEqual(CambioEstadoItem.objects.count(),0,
                         'Not all cambioestadoitem objects were deleted')
        self.assertEqual(Aviso.objects.count(),0,'The avisos were not deleted')
        self.assertEqual(Contacto.objects.count(),0,
                         'The Contacto was not deleted')
        self.assertEqual(Telefono.objects.count(),0,
                         'Telephones were not deleted')
        self.assertEqual(MensajeFormularioContacto.objects.count(),0,
                         'Messages of the contact form were not deleted')
        self.assertEqual(Respuesta.objects.count(),0, 
                         'Respuestas were not deleted')
        self.assertEqual(Video.objects.count(),0,
                         'Not all the videos were deleted')
        self.assertEqual(Foto.objects.count(),0,'Not all the fotos were deleted')
        self.assertEqual(Avance.objects.count(),0,
                         'Not all the avances were deleted')
        self.assertEqual(Etapa.objects.count(),0,
                         'Not all the etapas were deleted')
        self.assertEqual(SubEtapa.objects.count(),0,
                         'Not all the subetapas were deleted')
        self.assertEqual(Milestone.objects.count(),0,
                         'Not all the milestones were deleted')
        self.assertEqual(Beneficio.objects.count(),0,
                         'Not all the beneficios were deleted')


        #revisando que no se borraron los datos que no debian borrarse
        self.assertEqual(Entry.objects.count(),5,'The entries were deleted')
        self.assertEqual(TipoItemNombre.objects.count(),1,
                         'The tipoitemnombre object was deleted')
        self.assertEqual(User.objects.count(),3,'Some users were deleted')
        self.assertEqual(AdminComercial.objects.count(),1,
                         'The admincomercial user was deleted')
        self.assertEqual(Cliente.objects.count(),1,'The cliente was deleted')
        self.assertEqual(Rubro.objects.count(),1,'The rubro was deleted')
        self.assertEqual(TipoTelefono.objects.count(),5,
                         'TipoTelefono objects were deleted')
        self.assertEqual(Provincia.objects.count(),195, 
                         'Some provincia objects were deleted')
        self.assertEqual(Departamento.objects.count(),25, 
                         'Some departamento objects were deleted')


class TestMilestone(BaseOperation):
    def test_admin_delete(self):
        """
        verifica que al borrar un milestone desde el admin solo se borra el
        milestone dejando intactos a sus objetos relacionados
        """
        self._create_grupos()
        r=self._create_rubro()
        p=self._create_proyecto(r)
        e1=self._create_etapa(p,50)
        se1=self._create_subetapa(e1,100)
        av1=self._create_avance(p,se1)
        m1=self._create_milestone(se1,av1,True,100)
        
        #crea un usuario 

        ac = self._create_adminComercial()
        #print '%s %s' % (ac.usuario.is_active,ac.usuario.is_staff)
        #logear usuario
        response = self.client.post('/admin/',
                                    {'username':ac.usuario.username,
                                     'password':'1',
                                     'this_is_the_login_form':1,
                                     'next':'/admin/',
                                     'submit':'Log in'},)
        self.assertEqual(self.client.session.get('_auth_user_id'), ac.usuario.id,
                         'Login process Failed')

        # result = self.client.login(username=ac.usuario.username,password='1')
        # self.assertEqual(result, True, 'Login process Failed')

        #borrar milestone desde la interface
        response = self.client.post(
            reverse('admin:admin_avance_ajax_delete_milestone'),
            {'id':m1.id})
        #revisar que solo se borro el milestone
        self.assertEqual(Milestone.objects.count(),0,
                         'Unable to delete de milestone')
        self.assertEqual(SubEtapa.objects.count(),1,
                         "It's not supposed that the subetapa was deleted")
        self.assertEqual(Avance.objects.count(),1,
                         "It's not supposed that the Avance was deleted")        


class TestAvance(BaseOperation):
    def test_admin_delete(self):
        """
        verifica que al borrar un avance desde el admin tambien se borren sus 
        videos, fotos y milestones
        verifica que el avance es recalculado luego de borrar todo
        """
        self._create_grupos()
        r=self._create_rubro()
        p=self._create_proyecto(r)
        e1=self._create_etapa(p,100)
        se1=self._create_subetapa(e1,100)
        av1=self._create_avance(p,se1)
        self._create_fotos_avance(av1,5)
        self._create_videos_avance(av1,5)
        av2=self._create_avance(p,se1)
        self._create_fotos_avance(av2,5) 
        self._create_videos_avance(av2,5)       
        m1_1=self._create_milestone(se1,av1,True,10)
        m1_2=self._create_milestone(se1,av1,True,40)
        m2_1=self._create_milestone(se1,av2,True,50)
        
        #crea un usuario 
        ac = self._create_adminComercial()
        #logear usuario
        result = self.client.login(username=ac.usuario.username,password='1')
        self.assertEqual(result, True, 'Login process Failed')
        #revisando avance al 100
        self.assertEqual(Proyecto.objects.get(id=1).avance,100,
                         'Project progress was not recalculated')
        #borrando avance1 desde la interface
        response = self.client.post(
            reverse('admin:admin_avances_delete'),
            {'1':av1.id})
        #revisando que se recalculo el avance
        self.assertEqual(Proyecto.objects.get(id=1).avance,50,
                         'Project progress was not recalculated')
        #revisando que solo se borraron lo objetos que debian borrarse
        self.assertEqual(Etapa.objects.count(),1,
                         'The Etapa was deleted')
        self.assertEqual(SubEtapa.objects.count(),1,
                         'The SubEtapa was deleted')
        self.assertEqual(Avance.objects.count(),1,
                         'The Avance was deleted')
        self.assertEqual(Milestone.objects.count(),1,
                         'The milestones were not deleted')
        self.assertEqual(Foto.objects.count(),5,
                         'The fotos where not deleted')
        self.assertEqual(Video.objects.count(),5,
                         'The videos where not deleted')


class TestSubEtapa(BaseOperation):
    def test_admin_delete(self):
        """
        verifica que al borrar una subetapa desde el admin se borren tambien sus
        avances, fotos, videos y milestones
        verifica tambien que se recalcula el avance luego de borrar todo        
        """
        self._create_grupos()
        r=self._create_rubro()
        p=self._create_proyecto(r)
        e1=self._create_etapa(p,100)
        se1=self._create_subetapa(e1,50)
        se2=self._create_subetapa(e1,50)
        av1=self._create_avance(p,se1)
        self._create_fotos_avance(av1,5)
        self._create_videos_avance(av1,5)
        av2=self._create_avance(p,se1)
        self._create_fotos_avance(av2,5) 
        self._create_videos_avance(av2,5)       
        av2_0=self._create_avance(p,se1)
        av3=self._create_avance(p,se2)
        self._create_fotos_avance(av3,5) 
        self._create_videos_avance(av3,5)       

        m1_1=self._create_milestone(se1,av1,True,10)
        m1_2=self._create_milestone(se1,av1,True,40)
        m2_1=self._create_milestone(se1,av2,True,50)
        m3_1=self._create_milestone(se2,av3,True,100)
        
        #crea un usuario 
        ac = self._create_adminComercial()
        #logear usuario
        result = self.client.login(username=ac.usuario.username,password='1')
        self.assertEqual(result, True, 'Login process Failed')
        #revisando avance al 100
        self.assertEqual(Proyecto.objects.get(id=1).avance,100,
                         'Project progress was not recalculated')
        #borrando subetapa 1 desde el admin
        response = self.client.get(
            reverse('admin:ajax_delete_subetapa'),
            {'id':se1.id})
        #revisando que se recalculo el avance
        self.assertEqual(Proyecto.objects.get(id=1).avance,50,
                         'Project progress was not recalculated')
        #revisando que solo se borraron lo objetos que debian borrarse
        self.assertEqual(Etapa.objects.count(),1,
                         'The Etapa was deleted')
        self.assertEqual(SubEtapa.objects.count(),1,
                         'The SubEtapa was deleted')
        av = Avance.objects.count()
        #print Avance.objects.get(id=3).etapa
        self.assertEqual(av,1, 
                         'Error ocurred when deleting avances: %s=!1' % av)     
        self.assertEqual(Milestone.objects.count(),1,
                         'The milestones were not deleted')
        self.assertEqual(Foto.objects.count(),5,
                         'The fotos where not deleted')
        self.assertEqual(Video.objects.count(),5,
                         'The videos where not deleted')


class TestEtapa(BaseOperation):
    def test_admin_delete(self):
        """
        verifica que al borrar una etapa desde el admin tambien se borren sus 
        objetos relacionados y se recalcule el avance
        """
        self._create_grupos()
        r=self._create_rubro()
        p=self._create_proyecto(r)
        e1=self._create_etapa(p,75)
        se1=self._create_subetapa(e1,100)
        av1=self._create_avance(p,se1)
        self._create_fotos_avance(av1,5)
        self._create_videos_avance(av1,5)
        av2=self._create_avance(p,se1)
        self._create_fotos_avance(av2,5) 
        self._create_videos_avance(av2,5)       
        m1_1=self._create_milestone(se1,av1,True,10)
        m1_2=self._create_milestone(se1,av1,True,40)
        m2_1=self._create_milestone(se1,av2,True,50)
        
        e2=self._create_etapa(p,25)
        se2_1=self._create_subetapa(e2,50)
        se2_2=self._create_subetapa(e2,50)
        av2_1=self._create_avance(p,se2_1)
        self._create_fotos_avance(av2_1,5)
        self._create_videos_avance(av2_1,5)
        av2_2=self._create_avance(p,se2_2)
        self._create_fotos_avance(av2_2,5)
        self._create_videos_avance(av2_2,5)
        m3_1=self._create_milestone(se2_1,av2_1,True,1)
        m3_2=self._create_milestone(se2_1,av2_1,True,2)
        m3_3=self._create_milestone(se2_1,av2_1,True,97)
        m4_1=self._create_milestone(se2_2,av2_2,True,100)

        #crea un usuario 
        ac = self._create_adminComercial()
        #logear usuario
        result = self.client.login(username=ac.usuario.username,password='1')
        self.assertEqual(result, True, 'Login process Failed')
        #revisando avance al 100
        self.assertEqual(Proyecto.objects.get(id=1).avance,100,
                         'Project progress was not recalculated')
        #borrando etapa 1 desde la interface
        response = self.client.post(
            reverse('admin:admin_etapa_delete'),
            {'1':e1.id})
        #revisando que se recalculo el avance
        self.assertEqual(Proyecto.objects.get(id=1).avance,25,
                         'Project progress was not recalculated')
        #revisando que solo se borraron lo objetos que debian borrarse
        self.assertEqual(Etapa.objects.count(),1,
                         'The Etapa was deleted')
        self.assertEqual(SubEtapa.objects.count(),2,
                         'The SubEtapa was deleted')
        self.assertEqual(e2.subetapa_set.count(),2,
                         'Wrong SubEtapas was deleted')
        self.assertEqual(Avance.objects.count(),2,
                         'The Avance was deleted')
        self.assertEqual(se2_1.avance_set.count(),1,
                         'Wrong Avance was deleted')
        self.assertEqual(se2_2.avance_set.count(),1,
                         'Wrong Avance was deleted')
        self.assertEqual(Milestone.objects.count(),4,
                         'The milestones were not deleted')
        self.assertEqual(se2_1.milestone_set.count(),3,
                         'Wrong milestones deleted')
        self.assertEqual(se2_2.milestone_set.count(),1,
                         'Wrong milestones deleted')
        self.assertEqual(Foto.objects.count(),10,
                         'Wrong fotos deletion')
        self.assertEqual(av2_1.fotos.count(),5,
                         'av2_1 fotos where deleted')
        self.assertEqual(av2_2.fotos.count(),5,
                         'av2_2 fotos where deleted')
        self.assertEqual(Video.objects.count(),10,
                         'Wrong videos deletion')
        self.assertEqual(av2_1.videos.count(),5,
                         'av2_1 videos where deleted')
        self.assertEqual(av2_2.videos.count(),5,
                         'av2_2 videos where deleted')


class TestTipoItemNombre(BaseOperation):
    def test_admin_delete(self):
        """
        verifica que solo se borren los nombres de tipo de item que no esten
        asociados a ningun tipo de item
        """
        self._create_grupos()
        r=self._create_rubro()
        p=self._create_proyecto(r)
        ti_name1=self._create_tipoitemnombre()
        ti_name2=self._create_tipoitemnombre()
        ti1=self._create_tipoitem(ti_name1,p)

        #crea un usuario 
        u = self._create_superuser()
        #logear usuario
        result = self.client.login(username=u.username,password='1')
        self.assertEqual(result, True, 'Login process Failed')
        
        #borrando los nombres de tipos 1 y 2 de item desde el changelist
        response = self.client.post(
            reverse('admin:proyectos_tipoitemnombre_changelist'),
            {'_selected_action':'1',
             'action':'borrar_tipositemnombre',
             }
            )
        response = self.client.post(
            reverse('admin:proyectos_tipoitemnombre_changelist'),
            {'_selected_action':'2',
             'action':'borrar_tipositemnombre',
             }
            )

        #verificando que se borraron los objectos adecuados
        self.assertEqual(TipoItemNombre.objects.count(),1,
                         'Error deleting objects tipoitemnombre')
        self.assertEqual(TipoItemNombre.objects.all()[0].id,ti_name1.id,
                         'Wrong tipoitemname deleted')

        #creando nuevos tipos e items
        ti_name3=self._create_tipoitemnombre()
        ti_name4=self._create_tipoitemnombre()
        ti2=self._create_tipoitem(ti_name3,p)

        #tratando de borrar los nombre de tipos 3 y 4 desde el delete del
        #add or edit view
        response = self.client.post(
            reverse( 'admin:proyectos_tipoitemnombre_delete', args=(3,) ))
        response = self.client.post(
            reverse( 'admin:proyectos_tipoitemnombre_delete', args=(4,) ))

        #verificando que se borraron los objectos adecuados
        self.assertEqual(TipoItemNombre.objects.count(),2,
                         'Error deleting objects tipoitemnombre')
        self.assertEqual(TipoItemNombre.objects.all()[1].id,ti_name2.id,
                         'Wrong tipoitemname deleted')

        
class TestTipoItem(BaseOperation):
    def test_admin_delete(self):
        """
        verifica que solo se borren los tipos de item que no esten
        asociados a ningun item, ademas revisa que se eliminen las ofertas
        relacionadas 
        """
        self._create_grupos()
        r=self._create_rubro()
        p=self._create_proyecto(r)
        ti_name1=self._create_tipoitemnombre()
        ti_name2=self._create_tipoitemnombre()
        ti1=self._create_tipoitem(ti_name1,p)
        ti2=self._create_tipoitem(ti_name2,p)        
        oferta1=self._create_oferta(p,ti1)
        oferta2=self._create_oferta(p,ti2)
        plano=self._create_plano(p)
        item1=self._create_item(plano,ti1)

        self.assertEqual(Oferta.objects.count(),2,
                         'Not all the ofertas were created')

        #crea un usuario 
        u = self._create_superuser()
        #logear usuario
        result = self.client.login(username=u.username,password='1')
        self.assertEqual(result, True, 'Login process Failed')
        
        #tratando de borrar ti1 utilizando la accion
        #borrar del changelist del AdminModel
        response = self.client.post(
            reverse('admin:proyectos_tipoitem_changelist'),
            {'_selected_action':'1',
             'action':'borrar_tipoitem',
             }
            )
        self.assertTemplateUsed(
            response, 
            'admin/proyectos/tipoitem/unable_to_delete.html',
            'wrong objects will be deleted')

        #tratando de borrar ti2 utilizando la accion
        #borrar del changelist del AdminModel
        response = self.client.post(
            reverse('admin:proyectos_tipoitem_changelist'),
            {'_selected_action':'2',
             'action':'borrar_tipoitem',
             }
            )
        self.assertTemplateUsed(
            response, 
            'admin/proyectos/tipoitem/confirm_delete.html',
            'wrong objects will be deleted')

        #tratando de borrar los items directamente con la funcion
        #delete_tipositem
        response = self.client.post(
            reverse('admin:admin_tipositem_delete'),
            {'1':ti1.id,'2':ti2.id,})
        self.assertEqual(TipoItem.objects.count(),1,'Wrong tipoitem deletion')
        self.assertEqual(TipoItem.objects.all()[0].id, ti1.id,
                         'The wrong tipoitem object was deleted')
        self.assertEqual(Oferta.objects.count(),1,'Wrong Oferta deletion')
        self.assertEqual(Oferta.objects.all()[0].id,oferta1.id,
                         'The wrong oferta object was deleted')
        self.assertEqual(Plano.objects.count(),1,'Wrong plano deletion')
        self.assertEqual(TipoItemNombre.objects.count(),2,
                         'Wrong tipoitemnombre deletion')
        self.assertEqual(Item.objects.count(),1,'Wrong item deletion')
        self.assertEqual(Proyecto.objects.count(),1,'Wrong project deletion')
              
        
class TestItem(BaseOperation):
    def test_admin_delete(self):
        """
        verifica que al borrar un item se borren correctamente su poligono y sus
        puntos, en caso existan registros de cambio de estado de item tambien
        verifica que se borren, si tiene solicitudes estas tambien deben 
        borrarse
        verifica que solo puedan borrarse los items con estado disponible
        """
        self._create_grupos()
        r=self._create_rubro()
        p=self._create_proyecto(r)
        ti_name=self._create_tipoitemnombre()
        ti=self._create_tipoitem(ti_name,p)
        plano=self._create_plano(p)
        item1=self._create_item(plano,ti)
        item2=self._create_item(plano,ti)
        item3=self._create_item(plano,ti)

        #revisando que los objectos se crearon correctamente
        self.assertEqual(Proyecto.objects.count(),1,'project not created')
        self.assertEqual(Item.objects.count(),3,'Wrong item creation')
        self.assertEqual(plano.item_set.count(),3,'Wrong item creation')
        self.assertEqual(Poligono.objects.count(),3,'Wrong poligono creation')
        points_item1 = item1.poligono.punto_set.count()
        pi1 = False
        if points_item1 >= 3:
            pi1 = True
        self.assertTrue(pi1, 'Wrong points creation')
        points_item2 = item2.poligono.punto_set.count()
        pi2 = False
        if points_item2 >= 3:
            pi2 = True
        self.assertTrue(pi2, 'Wrong points creation')        
        points_item3 = item3.poligono.punto_set.count()
        pi3 = False
        if points_item3 >= 3:
            pi3 = True
        self.assertTrue(pi3, 'Wrong points creation')        

        #crea un usuario 
        u = self._create_superuser()
        #logear usuario
        result = self.client.login(username=u.username,password='1')
        self.assertEqual(result, True, 'Login process Failed')

        #borrando el item1 desde el delete view
        response = self.client.post(
            reverse( 'admin:admin_proyecto_delete_item', args=(1,) )
            )
        #revisando que se borraron los objectos correctos
        self.assertEqual(Item.objects.count(),2,'Wrong item deletion')
        self.assertEqual(plano.item_set.count(),2,'Wrong item deletion')
        self.assertEqual(Poligono.objects.count(),2,'Wrong poligono deletion')
        self.assertEqual(item2.poligono.punto_set.count(),points_item2,
                        'Wrong items deletion')
        self.assertEqual(item3.poligono.punto_set.count(),points_item3,
                        'Wrong items deletion')
        self.assertEqual(Punto.objects.count(),points_item2+points_item3, 
                         'Points from item1 were not deleted')

        #simulando cambios de estados del item 2
        cliente = self._create_cliente()
        response = self.client.post(
            reverse('admin:proyectos_item_change', args=(item2.id,)),
            {'numero':item2.numero,
             'tipo_item':item2.tipo_item.id,
             'estado':'D',
             'detalles':item2.detalles,
             'cliente':cliente.id,
             'id':item2.id,
             'plano':item2.plano.id,
             'poligono':item2.poligono.id}
            )
        self.assertEqual(item2.cambioestadoitem_set.count(),1,
                         'CambioEstadoItem not created')

        response = self.client.post(
            reverse('admin:proyectos_item_change', args=(item2.id,)),
            {'numero':item2.numero,
             'tipo_item':item2.tipo_item.id,
             'estado':'D',
             'detalles':item2.detalles,
             'cliente':cliente.id,
             'id':item2.id,
             'plano':item2.plano.id,
             'poligono':item2.poligono.id}
            )
        self.assertEqual(item2.cambioestadoitem_set.count(),2,
                         'CambioEstadoItem not created')
        
        response = self.client.post(
            reverse('admin:proyectos_item_change', args=(item2.id,)),
            {'numero':item2.numero,
             'tipo_item':item2.tipo_item.id,
             'estado':'S',
             'detalles':item2.detalles,
             'cliente':cliente.id,
             'id':item2.id,
             'plano':item2.plano.id,
             'poligono':item2.poligono.id}
            )
        self.assertEqual(item2.cambioestadoitem_set.count(),3,
                         'CambioEstadoItem not created')
        self.assertEqual(cliente.item_set.count(),1,
                         'The item was not joined with the cliente')

        response = self.client.post(
            reverse('admin:proyectos_item_change', args=(item2.id,)),
            {'numero':item2.numero,
             'tipo_item':item2.tipo_item.id,
             'estado':'V',
             'detalles':item2.detalles,
             'cliente':cliente.id,
             'id':item2.id,
             'plano':item2.plano.id,
             'poligono':item2.poligono.id}
            )
        self.assertEqual(item2.cambioestadoitem_set.count(),4,
                         'CambioEstadoItem not created')
        self.assertEqual(cliente.item_set.count(),1,
                         'The item was not joined with the cliente')


        #tratando de borrar el item2 desde el delete view
        response = self.client.post(
            reverse( 'admin:admin_proyecto_delete_item', args=(item2.id,) )
            )
        #verficando que no se pudo borrar el item por tener estado diferente a
        #disponible
        self.assertEqual(Item.objects.count(),2,
                         'An item with state different to "D" was deleted')

        #cambiando a estado disponible y borrando item2
        response = self.client.post(
            reverse('admin:proyectos_item_change', args=(item2.id,)),
            {'numero':item2.numero,
             'tipo_item':item2.tipo_item.id,
             'estado':'D',
             'detalles':item2.detalles,
             'cliente':cliente.id,
             'id':item2.id,
             'plano':item2.plano.id,
             'poligono':item2.poligono.id}
            )
        self.assertEqual(item2.cambioestadoitem_set.count(),5,
                         'CambioEstadoItem not created')
        response = self.client.post(
            reverse( 'admin:admin_proyecto_delete_item', args=(item2.id,) )
            )

        #revisando que se borraron los objectos correctos
        self.assertEqual(Item.objects.count(),1,'Wrong item deletion')
        self.assertEqual(plano.item_set.count(),1,'Wrong item deletion')
        self.assertEqual(Poligono.objects.count(),1,'Wrong poligono deletion')
        self.assertEqual(item3.poligono.punto_set.count(),points_item3,
                        'Wrong items deletion')
        self.assertEqual(Punto.objects.count(),points_item3, 
                         'Points from item1 were not deleted')
        self.assertEqual(CambioEstadoItem.objects.count(),0,
                         'CambioEstadoItem not created')
        self.assertEqual(Cliente.objects.count(),1,'Wrong cliente deletion')
        self.assertEqual(cliente.item_set.count(),0,
                         'The item is still joined with the cliente')
        
        
        #creado solicitudes en el item3
        self._create_solicitud(item3, p, cliente, 'S')
        self._create_solicitud(item3, p, cliente, 'S')
        self._create_solicitud(item3, p, cliente, 'S')
        
        self.assertEqual(item3.solicitud_set.count(),3,
                         'Not all the solicitudes were created')
        self.assertEqual(Solicitud.objects.count(),3,
                         'Not all the solicitudes were created')

        #simulando el rechazo de una solicitud
        solicitud = self._create_solicitud(item3, p, cliente, 'S')
        response = self.client.post(
            reverse('admin:usuarios_solicitud_change', args=(solicitud.id,)),
            {'accion':'R', 'mensaje':'qqq', 'item':item3.id,
             '_continue':'Grabar y continuar editando'}
            )
        #verificando que todo ocurrio correctamente
        self.assertEqual(Item.objects.count(),1,'The item was deleted!')
        self.assertEqual(CambioEstadoItem.objects.count(),0,'after processing\
 the solicitud the cambioestadoitem was not created')
        self.assertEqual(item3.cambioestadoitem_set.count(),0,'the \
cambioestadoitem object was not joined to the item')
        self.assertEqual(solicitud.cambioestadoitem_set.count(),0,'the\
 cambioestadoitem object was not joined to the solicitud')
#         cei1=CambioEstadoItem.objects.latest('id')
#         self.assertEqual(cei1.admin,u,'the cambioestadoitem object was not \
# joined to the admin who managed it')
#         self.assertEqual(cei1.cliente, cliente, 'the cambioestadoitems object \
# was not joined with the cliente')

        #borrando el item3
        response = self.client.post(
            reverse( 'admin:admin_proyecto_delete_item', args=(item3.id,) )
            )
        #verificando que solo se borraron lo objectos que debian borrarse
        self.assertEqual(Proyecto.objects.count(),1,'wrong project deletion')
        self.assertEqual(Plano.objects.count(),1,'wrong plano deletion')
        self.assertEqual(Cliente.objects.count(),1,'wrong client deletion')
        self.assertEqual(Item.objects.count(),0,'the item was not deleted')
        self.assertEqual(Poligono.objects.count(),0,
                         'the poligono was not deleted')
        self.assertEqual(Punto.objects.count(),0,'the puntos were not deleted')
        self.assertEqual(Solicitud.objects.count(),0,
                         'the solicitudes were not deleted')
        self.assertEqual(CambioEstadoItem.objects.count(),0,
                         'the cambioestadoitem objects were not deleted')
        

class TestPlano(BaseOperation):
    def test_admin_delete(self):
        """
        verifica que al borrar planos desde el changelist del modulo de planos,
        solo se borren aquellos que tiene items con estado disponible, ademas de
        sus objetos relacionados
        """
        self._create_grupos()
        r=self._create_rubro()
        p=self._create_proyecto(r)

        ti_name=self._create_tipoitemnombre()
        ti1=self._create_tipoitem(ti_name,p)
        plano1=self._create_plano(p)
        item1=self._create_item(plano1,ti1)

        #crea un usuario 
        u = self._create_superuser()
        #logear usuario
        result = self.client.login(username=u.username,password='1')
        self.assertEqual(result, True, 'Login process Failed')
        
        #simulando cambios de estados del item 1
        cliente = self._create_cliente()
        response = self.client.post(
            reverse('admin:proyectos_item_change', args=(item1.id,)),
            {'numero':item1.numero,
             'tipo_item':item1.tipo_item.id,
             'estado':'D',
             'detalles':item1.detalles,
             'cliente':cliente.id,
             'id':item1.id,
             'plano':item1.plano.id,
             'poligono':item1.poligono.id}
            )
        self.assertEqual(CambioEstadoItem.objects.count(),1,
                         'CambioEstadoItem was not created')

        #simulando aceptacion de una solicitud
        solicitud = self._create_solicitud(item1, p, cliente, 'S')
        response = self.client.post(
            reverse('admin:usuarios_solicitud_change', args=(solicitud.id,)),
            {'accion':'V', 'mensaje':'qqq', 'item':item1.id,
             '_continue':'Grabar y continuar editando'}
            )
        self.assertEqual(CambioEstadoItem.objects.count(),2,
                         'CambioEstadoItem was not created')
        self.assertEqual(Solicitud.objects.count(),1,
                         'Solicitud of item1 was not created')

        #tratando de borrar el plano 1
        response = self.client.post(reverse('admin:admin_plano_delete_selected'),
                                   {'1':plano1.id})
        #verificando que no se borro plano1 ni sus objetos relacionados
        self.assertEqual(Plano.objects.count(),1,'Plano1 was deleted')
        self.assertEqual(Item.objects.count(),1,'Item1 was deleted')
        self.assertEqual(CambioEstadoItem.objects.count(),2,
                         'CambioEstadoItem objects of item1 were deleted')
        self.assertEqual(Solicitud.objects.count(),1,
                         'Solicitud objects of item1 were deleted')

        #creando un plano2
        plano2=self._create_plano(p)
        item2=self._create_item(plano2,ti1)
        #tratando de borrar el plano 2
        response = self.client.post(reverse('admin:admin_plano_delete_selected'),
                                   {'1':plano2.id})
        #verificando que se borro plano 2 y sus objetos relacionados
        self.assertEqual(Plano.objects.count(),1,'Plano2 was not deleted')
        self.assertEqual(Item.objects.count(),1,'item2 was not deleted')
        self.assertEqual(Poligono.objects.count(),1,
                         'poligono of item 2 was not deleted')
        self.assertEqual(Punto.objects.count(),item1.poligono.punto_set.count(),
                         'The points of item 2 were not deleted')
        #creando un plano3
        plano3=self._create_plano(p)
        item3=self._create_item(plano3,ti1)
        #simulando cambios de estados del item 3
        response = self.client.post(
            reverse('admin:proyectos_item_change', args=(item3.id,)),
            {'numero':item3.numero,
             'tipo_item':item3.tipo_item.id,
             'estado':'S',
             'detalles':item3.detalles,
             'cliente':cliente.id,
             'id':item3.id,
             'plano':item3.plano.id,
             'poligono':item3.poligono.id}
            )
        response = self.client.post(
            reverse('admin:proyectos_item_change', args=(item3.id,)),
            {'numero':item3.numero,
             'tipo_item':item3.tipo_item.id,
             'estado':'V',
             'detalles':item3.detalles,
             'cliente':cliente.id,
             'id':item3.id,
             'plano':item3.plano.id,
             'poligono':item3.poligono.id}
            )
        response = self.client.post(
            reverse('admin:proyectos_item_change', args=(item3.id,)),
            {'numero':item3.numero,
             'tipo_item':item3.tipo_item.id,
             'estado':'D',
             'detalles':item3.detalles,
             'cliente':cliente.id,
             'id':item3.id,
             'plano':item3.plano.id,
             'poligono':item3.poligono.id}
            )
        self.assertEqual(CambioEstadoItem.objects.count(),5,
                         'not all the CambioEstadoItem objects were created')

        #simulando rechazo de una solicitud
        solicitud2 = self._create_solicitud(item3, p, cliente, 'S')
        response = self.client.post(
            reverse('admin:usuarios_solicitud_change', args=(solicitud2.id,)),
            {'accion':'R', 'mensaje':'qqq', 'item':item3.id,
             '_continue':'Grabar y continuar editando'}
            )
        self.assertEqual(Solicitud.objects.count(),2,
                         'Not all the solicitud objects were created')
        self.assertEqual(CambioEstadoItem.objects.count(),5,
                         'an extra CambioEstadoitem object was created')

        #tratando de borrar el plano 3
        response = self.client.post(reverse('admin:admin_plano_delete_selected'),
                                   {'1':plano3.id})

        #verificando que se borro el plano 3 y sus objetos relacionados 
        self.assertEqual(Plano.objects.count(),1,'plano3 was not deleted')
        self.assertEqual(Item.objects.count(),1,'item3 was not deleted')
        self.assertEqual(Poligono.objects.count(),1,
                         'poligono of item 3 was not deleted')
        self.assertEqual(Punto.objects.count(),item1.poligono.punto_set.count(),
                         'The points of item 3 were not deleted')
        self.assertEqual(Solicitud.objects.count(),1,
                         'Solicitud of item3 was not deleted')
        self.assertEqual(CambioEstadoItem.objects.count(),2,
                         'an extra CambioEstadoitem object was created')
        

