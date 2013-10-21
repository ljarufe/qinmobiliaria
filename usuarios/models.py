# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.sites.models import Site
from django.utils.safestring import SafeUnicode
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from datetime import datetime
import random
import sha
from common.models import Provincia, ViewPort
from common.utils import send_html_mail
from django.db.models.query_utils import Q
from portal.models import Area, Inmobiliaria


class AdminComercial(models.Model):
    """
    datos exclusivos de un administrador comercinal
    """
    usuario = models.OneToOneField(User, verbose_name=_(u"usuario"))
    asignar_proyectos = models.BooleanField(_(u'asignar proyectos'),
                                                 default=False)
    # proyectos = models.ManyToManyField('proyectos.Proyecto', 
    #                                    verbose_name=_(u'proyectos'), null=True,
    #                                    blank=True)

    class Meta:
        ordering = ('-id',)
        verbose_name = _(u'Administrador Comercial')
        verbose_name_plural = _(u'Administradores Comerciales')

    def __unicode__(self):
        return u'%s' % self.usuario.get_full_name()

    def fullName(self):
        return u'%s' % self.usuario.get_full_name()
    fullName.short_description = u'Nombres completos'

    def save(self, *args, **kwargs):
        """
        graba al administrador comercial y lo agrega al grupo 'Comercial'
        """
        super(self.__class__, self).save(*args, **kwargs)
        self.usuario.groups.add(Group.objects.get(name='Comercial'))

    def is_active(self):
        if self.usuario.is_active:
            icon = 'yes'
        else:
            icon = 'no'
        return u'<img src="%sadmin/img/admin/icon-%s.gif" \
alt="activo">' % (settings.STATIC_URL,icon)
    is_active.allow_tags = True
    is_active.short_description = u'Activo'

    def deactivate_user(self):
        """
        desactiva el usuario del adminitrador comercial
        """
        u = self.usuario
        u.is_active = False
        return u.save()

    def activate_user(self):
        """
        activa el usuario del administrador comercial
        """
        u = self.usuario
        u.is_active = True
        return u.save()


class AdminInformacion(models.Model):
    """
    datos exclusivos de un administrador de informacion
    """
    usuario = models.OneToOneField(User, verbose_name=_(u"usuario"))
#    asignar_proyectos = models.BooleanField(_(u'asignar proyectos'),
#                                                 default=False)

    class Meta:
        ordering = ('-id',)
        verbose_name = _(u'Administrador de Información')
        verbose_name_plural = _(u'Administradores de Información')

    def __unicode__(self):
        return u'%s' % self.usuario.get_full_name()

    def fullName(self):
        return u'%s' % self.usuario.get_full_name()
    fullName.short_description = u'Nombres completos'

    def save(self, *args, **kwargs):
        """
        graba al administrador de informacion y lo agrega al grupo 'Informacion'
        """
        super(self.__class__, self).save(*args, **kwargs)
        self.usuario.groups.add(Group.objects.get(name='Informacion'))

    def is_active(self):
        if self.usuario.is_active:
            icon = 'yes'
        else:
            icon = 'no'
        return u'<img src="%sadmin/img/admin/icon-%s.gif" \
alt="activo">' % (settings.STATIC_URL,icon)
    is_active.allow_tags = True
    is_active.short_description = u'Activo'

    def deactivate_user(self):
        """
        desactiva el usuario del adminitrador comercial
        """
        u = self.usuario
        u.is_active = False
        return u.save()

    def activate_user(self):
        """
        activa el usuario del administrador comercial
        """
        u = self.usuario
        u.is_active = True
        return u.save()


class AdminHelpDesk(models.Model):
    """
    datos exclusivos de un administrador de Help Desk
    """
    usuario = models.OneToOneField(User, verbose_name=_(u"usuario"))
    auto_asignar_salas = models.BooleanField(_(u'auto asignar salas'),
                                                 default=False)
    areas = models.ManyToManyField(Area, verbose_name=_(u"areas"),
                                   related_name="helpdesk_admins",
                                   blank=True, null=True)
    conectado = models.BooleanField(_(u"Conectado"), default=False, 
                                    editable=False)

    class Meta:
        ordering = ('-id',)
        verbose_name = _(u'Administrador de Help Desk')
        verbose_name_plural = _(u'Administradores de Help Desk')

    def __unicode__(self):
        return u'%s' % self.usuario.get_full_name()

    @staticmethod
    def get_area_manager(area):
        """
        Devuelve un manager de área si hubiera uno en linea
        """
        managers = AdminHelpDesk.objects.filter(areas=area)
        managers = managers.order_by('?')
        if managers:
            return managers[0]
        else:
            return None

    def fullName(self):
        return u'%s' % self.usuario.get_full_name()
    fullName.short_description = u'Nombres completos'

    def save(self, *args, **kwargs):
        """
        graba al administrador de Help Desk y lo agrega al grupo 'Help Desk'
        """
        ######esto ya ese hace en el form del admin######
        #self.usuario.is_staff = True
        #################################################
        super(self.__class__, self).save(*args, **kwargs)
        self.usuario.groups.add(Group.objects.get(name='Help Desk'))

    def is_active(self):
        if self.usuario.is_active:
            icon = 'yes'
        else:
            icon = 'no'
        return u'<img src="%sadmin/img/admin/icon-%s.gif" \
               alt="activo">' % (settings.STATIC_URL,icon)
    is_active.allow_tags = True
    is_active.short_description = u'Activo'

    def deactivate_user(self):
        """
        desactiva el usuario del adminitrador de Help Desk
        """
        u = self.usuario
        u.is_active = False
        return u.save()

    def activate_user(self):
        """
        activa el usuario del administrador de Help Desk
        """
        u = self.usuario
        u.is_active = True
        return u.save()

    def conectar(self):
        """
        Conecta a un admin cuando se une a una sala de chat
        """
        self.conectado = True
        self.save()

    def desconectar(self):
        """
        Conecta a un admin cuando se une a una sala de chat
        """
        self.conectado = False
        self.save()


class Corredor(models.Model):
    """
    Profile de un corredor
    """
    codigo = models.CharField(_(u'Código'), max_length=10, editable=False)
    usuario = models.OneToOneField(User, verbose_name=_(u"usuario"))
    auto_asignar = models.BooleanField(_(u"auto asignar proyectos"),
                                       default=False)

    class Meta:
        ordering = ('-id',)
        verbose_name = _(u"Corredor")
        verbose_name_plural = _(u"Corredores")
        
    def __unicode__(self):
        return u"%s" % self.usuario.get_full_name()

    def generar_codigo(self):
        """
        Todo: hay q implementar esta funcion de manera que genere codigos
        unicos con length == 10. Por ahora solo retorna el id, asi se asegura
        que es unico
        """
        return self.id

    def save(self):
        """
        graba y genera su codigo
        Todo: hay que hacer una funcion que genere los codigos
        """
        super(self.__class__, self).save()
        self.codigo = self.generar_codigo()
        super(self.__class__, self).save()
        

class Cliente(models.Model):
    """
    Profile de un cliente
    """
    usuario = models.OneToOneField(User, verbose_name=_(u"usuario"))
    telefonos = models.ManyToManyField('common.Telefono',
                                       verbose_name=_(u"telefonos"),
                                       null=True, blank=True)
    direccion = models.CharField(_(u"dirección"), max_length=200, blank=True,
                                 null=True)
    provincia = models.ForeignKey(Provincia, null=True, blank=True)
    recibir_email = models.BooleanField(_(u"recibir e-mails"), default=True)
    rastrear_proyectos = models.BooleanField(_(u"rastrear proyectos"),
                                             default=True)
    areas_interes = models.ManyToManyField(ViewPort,
                                           verbose_name=_(u"Áreas de interés"),
                                           null=True, blank=True)
    rubros = models.ManyToManyField('proyectos.Rubro', 
                                    verbose_name=_(u"rubros"), null=True,
                                    blank=True)
    clave_activacion = models.CharField(max_length=40,
                                        verbose_name=_(u"clave de activación"))

    TIPO_CLIENTE = (('Q', 'Quimera'), ('C', 'Corredores'), ('I', 'Inversores'))
    tipo = models.CharField(_(u'tipo de cliente'), max_length=1, 
                            choices=TIPO_CLIENTE, default='Q')
    #corredor que asocio al usuario
    corredor = models.ForeignKey(Corredor, null=True, blank=True)

    class Meta:
        ordering = ('-id',)

    def __unicode__(self):
        return u"%s" % self.usuario

    def save(self, *args, **kwargs):
        """
        Crea la clave de activación para el cliente
        Si se cambio de tipo de cliente y estaba relacionado a un corredor, se 
        elimina dicha relacion
        """
        salt = sha.new(str(random.random())).hexdigest()[:5]
        self.clave_activacion = sha.new(salt+self.usuario.email).hexdigest()

        if self.tipo != 'C' and self.corredor:
            self.corredor.cliente_set.remove(self)

        return super(Cliente, self).save(*args, **kwargs)

    def departamento(self):
        return u'%s' % self.provincia.departamento
    departamento.short_description = u'Departamento'

    def fullName(self):
        return u'%s' % self.usuario.get_full_name()
    fullName.short_description = u'Nombres completos'

    def is_active(self):
        if self.usuario.is_active:
            icon = 'yes'
        else:
            icon = 'no'
        return u'<img src="%sadmin/img/admin/icon-%s.gif" \
               alt="activo">' % (settings.STATIC_URL,icon)
    is_active.allow_tags = True
    is_active.short_description = u'Activo'

    @staticmethod
    def get_authenticated(request):
        """
        Retorna un cliente si está autenticado, sino retorna None
        """
        if request.user.is_authenticated():
            try:
                cliente = Cliente.objects.get(usuario=request.user)
            except Cliente.DoesNotExist:
                cliente = None
        else:
            cliente = None

        return cliente

    def deactivate_user(self):
        """
        desactiva el usuario del cliente
        """
        u = self.usuario
        u.is_active = False
        return u.save()

    def activate_user(self):
        """
        activa el usuario del cliente
        """
        u = self.usuario
        u.is_active = True
        return u.save()

    def set_password(self, password):
        """
        Cambia el password del usuario asignado al cliente
        """
        self.usuario.set_password(password)
        self.usuario.save()

    def set_telefono(self, telefono):
        """
        Graba un telefono si no esta repetido
        """
        if not telefono in self.telefonos.all():
            self.telefonos.add(telefono)

# class Separacion(models.Model):
#     """
#     Solicitud para separar un item de un proyecto
#     """
#     cliente = models.ForeignKey(Cliente, verbose_name=_(u"cliente"))
#     item = models.ForeignKey('proyectos.Item', verbose_name=_(u"item"))
#     fecha = models.DateField(_(u"fecha"), default=datetime.now)
#     mensaje = models.TextField(_(u"mensaje"))
#     admin = models.ForeignKey(User, verbose_name=_(u"administrador"))
#     ESTADO_CHOICES = (
#         (u"E", _(u"Espera")),
#         (u"A", _(u"Aceptado")),
#         (u"R", _(u"Rechazado")),
#     )
#     estado = models.CharField(_(u"estado"), max_length=1,
#                               choices=ESTADO_CHOICES)

#     def __unicode__(self):
#         return u"%s - %s" % (self.cliente, self.item)

#     # def save(self, *args, **kwargs):
#     #     """
#     #     Cambia el estado del item asociado
#     #     """
#         #antes estaba asi S y V no son estados de Separacion sino de item
#         # if self.estado == u"S" or self.estado == u"V":
#         #     self.item.estado = self.estado
#         # super(Separacion, self).save(*args, **kwargs)
        

#     class Meta:
#         verbose_name = _(u"Separación")
#         verbose_name_plural = _(u"Separaciones")


class Solicitud(models.Model):
    """
    Solicitúd para separar un item o cancelar su separacion
    """
    fecha_emision = models.DateField(_(u"fecha de emisión"),
                                     default=datetime.now, editable=False)
    fecha_cierre = models.DateField(_(u"fecha de cierre"), blank=True,
                                    null=True, editable=False)
    ESTADO_CHOICES = (
        (u"E", _(u"Espera")),
        (u"T", _(u"Trámite")),
        (u"A", _(u"Aceptado")),
        (u"R", _(u"Rechazado")),
        (u"C", _(u"Cancelado")),
    )
    estado = models.CharField(_(u"estado"),max_length=1,choices=ESTADO_CHOICES,
                              default=u'E')
    TIPO_CHOICES = (
        (u'S', _(u'Separación')),
        (u'C', _(u'Cancelación')),
    )
    tipo = models.CharField( _(u'tipo'), max_length=1, choices=TIPO_CHOICES,
                             default=u'S')
    mensaje = models.TextField(_(u"mensaje"))
    admin = models.ForeignKey(User, verbose_name=_(u"administrador"), 
                              blank=True, null=True)
    cliente = models.ForeignKey(Cliente, verbose_name=_(u"cliente"))
    item = models.ForeignKey('proyectos.Item', verbose_name=_(u"item"))
    proyecto = models.ForeignKey('proyectos.Proyecto', 
                                 verbose_name=_(u'proyecto'), blank=True, 
                                 null=True)

    class Meta:
        ordering = ('-id',)
        verbose_name = _(u"Solicitud")
        verbose_name_plural = _(u"Solicitudes")

    def __unicode__(self):
        return u"%s - %s, Tipo %s: %s" % (self.item.numero, self.proyecto.nombre,
                                     self.get_tipo_display(),
                                     self.get_estado_display(),)

    def save(self, *args, **kwargs):
        """
        Al aceptar una solicitud para cancelar la separación se debe eliminar
        la separación, este mismo objeto y colocar el item relacionado como
        disponible

        Al aceptar una solicitud para cancelar la separación se debe quitar
        la relacion entre el cliente y el item, ademas de poner el item como
        disponiuble
        """
        super( self.__class__, self ).save(*args, **kwargs)
        
        # if self.estado == u"A":
        #     self.solicitud.item.estado == u"D"
        #     self.solicitud.delete()
        #     self.delete()

    def tramitar(self, request):
        """
        Separar un item
        """
        self.estado = u"T"
        self.item.estado = u"S"
        self.item.cliente = self.cliente
        cambio_estado = CambioEstadoItem(estado=u"S", admin=request.user,
            item=self.item, solicitud=self, cliente=self.cliente)
        send_html_mail(settings.DEFAULT_FROM_EMAIL,
                       u"Solicitud de separación en trámite",
                       "separado.html",
                       {"solicitud": self, 'sitio':Site.objects.get(id=1),
                        'STATIC_URL':settings.STATIC_URL,
                        'inmobiliaria':Inmobiliaria.objects.get(id=1)},
                       self.cliente.usuario.email)
        cambio_estado.save()
        self.admin = request.user
        self.item.save()
        self.save()

    def tramitado(self, request):
        """
        Vender un item
        """
        self.estado = u"A"
        if self.tipo == u"S":
            self.item.estado = u"V"
            self.item.cliente = self.cliente
            cambio_estado = CambioEstadoItem(estado=u"V", admin=request.user,
                item=self.item, solicitud=self, cliente=self.cliente)
            send_html_mail(settings.DEFAULT_FROM_EMAIL,
                           u"Solicitud de separación tramitada con éxito",
                           "vendido.html",
                           {"solicitud": self, 'sitio':Site.objects.get(id=1), 
                            'STATIC_URL':settings.STATIC_URL,
                            'inmobiliaria':Inmobiliaria.objects.get(id=1)},
                           self.cliente.usuario.email)
        else:
            self.item.estado = u"D"
            self.item.cliente = None
            cambio_estado = CambioEstadoItem(estado=u"D", admin=request.user,
                item=self.item, solicitud=self, cliente=self.cliente)
            solicitud = Solicitud.objects.get(
                Q(estado=u"T")|Q(estado=u"A"),
                cliente=self.cliente, item=self.item, tipo=u"S")
            solicitud.estado = u"C"
            solicitud.save()
            send_html_mail(settings.DEFAULT_FROM_EMAIL,
                           u"Solicitud de cancelación tramitada con éxito",
                           "cancelado.html",
                           {"solicitud": self, 'sitio':Site.objects.get(id=1), 
                            'STATIC_URL':settings.STATIC_URL,
                            'inmobiliaria':Inmobiliaria.objects.get(id=1)},
                           self.cliente.usuario.email)
        cambio_estado.save()
        self.admin = request.user
        self.item.save()
        self.save()

    def rechazar(self, request):
        """
        Rechaza una solicitud de separación
        """
        if self.estado == u"T":
            self.item.estado = u"D"
            self.item.cliente = None
            self.item.save()
            cambio_estado = CambioEstadoItem(estado=u"D", admin=request.user,
                item=self.item, solicitud=self, cliente=self.cliente)
            cambio_estado.save()
        self.estado = u"R"
        self.admin = request.user
        send_html_mail(settings.DEFAULT_FROM_EMAIL,
                       u"Solicitud rechazada",
                       "rechazado.html",
                       {"solicitud": self, 'sitio':Site.objects.get(id=1), 
                        'STATIC_URL':settings.STATIC_URL,
                        'inmobiliaria':Inmobiliaria.objects.get(id=1)},
                       self.cliente.usuario.email)
        self.save()

    def item_numero(self):
        return u'%s' % self.item.numero
    item_numero.short_description = u'número de item'

    def tipo_item(self):
        return u'%s' % self.item.tipo_item.nombre
    tipo_item.short_description = u'tipo de item'

    def plano(self):
        return u'%s' % self.item.plano.titulo
    plano.short_description = u'plano'


class CambioEstadoItem(models.Model):
    """
    Historial de los estados de un item
    """
    fecha = models.DateTimeField(default=datetime.now())
    ESTADO_CHOICES = (
        (u"D", _(u"Disponible")),
        (u"S", _(u"Separado")),
        (u"V", _(u"Vendido")),
    )
    estado = models.CharField(_(u"estado"), max_length=1,
                              choices=ESTADO_CHOICES, default=u"D")
    admin = models.ForeignKey(User, 
                              verbose_name=_(u"administrador responsable"))
    item = models.ForeignKey('proyectos.Item',
                             verbose_name=_(u"item implicado"))
    #solicitud que genero el cambio un cambio de estado
    solicitud = models.ForeignKey(Solicitud, blank=True, null=True,
                                  verbose_name=_(u"solicitud"))
    cliente = models.ForeignKey(Cliente, blank=True, null=True, 
                                verbose_name=_(u'cliente'))

    class Meta:
        ordering = ('-id',)

    def __unicode__(self):
        return u"%s, %s" % (self.item, self.estado)
    
# class SolicitudCancelarSeparacion(models.Model):
#     """
#     Solicitúd para cancelar la separación de un proyecto
#     """
#     solicitud = models.ForeignKey(Separacion,
#                                   verbose_name=_(u"solicitud para separar"))
#     fecha_emision = models.DateField(_(u"fecha de emisión"), default=datetime.now)
#     fecha_cierre = models.DateField(_(u"fecha de cierre"))
#     ESTADO_CHOICES = (
#         (u"E", _(u"Espera")),
#         (u"T", _(u"Trámite")),
#         (u"A", _(u"Aceptado")),
#         (u"R", _(u"Rechazado")),
#     )
#     estado = models.CharField(_(u"estado"), max_length=1,
#                               choices=ESTADO_CHOICES)

#     def save(self, *args, **kwargs):
#         """
#         Al aceptar una solicitud para cancelar la separación se debe eliminar
#         la separación, este mismo objeto y colocar el item relacionado como
#         disponible
#         """
#         if self.estado == u"A":
#             self.solicitud.item.estado == u"D"
#             self.solicitud.delete()
#             self.delete()

#     def __unicode__(self):
#         return u"%s" % self.solicitud


class MensajeFormularioContacto(models.Model):
    """
    El mensaje enviado en el formulario de contacto por un cliente
    """
    cliente = models.ForeignKey(Cliente, verbose_name=_(u"cliente"), null=True)
    mensaje = models.TextField(_(u"mensaje"))
    fecha = models.DateField(_(u"fecha"), default=datetime.now)
    proyecto = models.ForeignKey('proyectos.Proyecto', 
                                 verbose_name=_(u"proyecto"), 
                                 null=True, blank=True)

    class Meta:
        ordering = ('-id',)
        verbose_name = _(u"Mensaje del formulario de contacto")
        verbose_name_plural = _(u"Mensajes del formulario de contacto")

    def __unicode__(self):
        return u"%s" % self.cliente

    def respondido(self):
        if self.respuesta_set.all():
            icon = 'yes'
        else:
            icon = 'no'
        return SafeUnicode(u'<img src="%sadmin/img/admin/icon-%s.gif" \
alt="activo">' % (settings.STATIC_URL,icon))
    respondido.allow_tags = True
    respondido.short_description = u'Respondido'

    def mark_as_answered(self, admin_user):
        """
        verifica que el mensaje no ha sido respondido
        asigna una respuesta automatica inicando que el mensaje fue respondido
        fuera de la interface administrativa
        Si logra marcar el mensaje como respondido retorna true, sino retorna 
        False
        """
        if not self.respuesta_set.all():
            self.respuesta_set.create(
                admin=admin_user,
                mensaje=self,
                respuesta = u'Mensaje respondido fuera de la interface \
administrativa.')
            return True
        return False


class Respuesta(models.Model):
    """
    Respuesta de un administrador al formulario de contacto
    """
    admin = models.ForeignKey(User, verbose_name=_(u"admin"))
    mensaje = models.ForeignKey(MensajeFormularioContacto,
                                verbose_name=_(u"mensaje"))
    respuesta = models.TextField(_(u"respuesta"))
    fecha = models.DateField(_(u"fecha"), default=datetime.now)

    class Meta:
        ordering = ('-id',)

    def __unicode__(self):
        return u"%s <- %s" % (self.mensaje.cliente, self.respuesta)


class VentaTerreno(models.Model):
    """
    Datos sobre la venta de un terreno por un cliente
    """
    TIPO_VENTA_CHOICES = (
        (u"V", _(u"Venta")),
        (u"S", _(u"Sociedad")),
    )
    tipo_venta = models.CharField(_(u"tipo de venta"), max_length=1,
                                  choices=TIPO_VENTA_CHOICES, default=u"V")
    precio = models.CharField(u"precio", max_length=12)
    MONEDA_CHOICES = (
        (u"S", _(u"Soles")),
        (u"D", _(u"Dolares")),
        (u"E", _(u"Euros")),
    )
    moneda = models.CharField(_(u"moneda"), max_length=1,
                              choices=MONEDA_CHOICES, default=u"S")
    area = models.FloatField(_(u"area"))
    UNIDAD_AREA_CHOICES = (
        (u"M", _(u"M2")),
        (u"H", _(u"Hectareas")),
    )
    unidad_area = models.CharField(_(u"moneda"), max_length=1,
                              choices=MONEDA_CHOICES, default=u"M")
    mensaje = models.TextField(_(u"mensaje"))
    cliente = models.ForeignKey(Cliente, verbose_name=_(u"cliente"))
    poligono = models.ForeignKey('common.Poligono', verbose_name=_(u"polígono"))

    def __unicode__(self):
        return u"%s, %s a %s" % (self.cliente, self.area, self.precio)
