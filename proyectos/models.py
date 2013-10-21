# -*- coding: utf-8 -*-

from django.db import models
from django.db.models import Sum, Max, Min, Q
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist
from django.core.files import File
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib.sitemaps import ping_google
from django.conf import settings
from common.utils import send_mass_html_mails, highlyRandomName
from sorl.thumbnail.fields import ImageWithThumbnailsField
from datetime import datetime, timedelta
from common.models import Provincia
import Image, ImageDraw
import os
from django.db.models.signals import pre_save
from django.dispatch import receiver
from usuarios.models import Cliente


class Rubro(models.Model):
    """
    Categoría que alberga a varios proyectos
    """
    nombre = models.CharField(_(u"nombre"), max_length=50)
    slug = models.SlugField(
        _(u"URL corta"), max_length=100,
        help_text=_(u"Utilize letras, números y '_' en vez de los espacios, como"
                    u" en la URL corta de sugerencia"),
        default=u'nombre_rubro'
    )
    descripcion = models.TextField(_(u"descripción"))
    texto_email = models.TextField(
        _(u"texto del correo informativo"),
        help_text=_(u'Mensaje a mostrarse en los correos que se envían como '
                    u'primera respuesta  a un usuario que solicita información.')
    )

    def __unicode__(self):
        return u"%s" % self.nombre

    def save(self, *args, **kwargs):
        """
        Hace un ping a google sobre la actualización
        """
        try:
            ping_google()
        except Exception:
            pass

        return super(self.__class__, self).save(*args, **kwargs)

    @models.permalink
    def get_absolute_url(self):
        """
        Devuelve la url del perfil público del rubro
        """
        return 'proyectos.views.rubro', [str(self.slug)]

    def admin_borrar_rubro(self, queryset):
        """
        Borra al rubro sí y sólo si no tiene proyectos asociados,si es así
        dis-asocia todos los clientes del rubro antes de eliminarlo
        """
        non_empty = ""
        deleted = ""
        for rubro in queryset.all():
            if not rubro.proyecto_set.all():
                rubro.cliente_set.clear()
                rubro.delete()
                deleted += " %s," % rubro.nombre
            else:
                non_empty += " %s," % rubro.nombre
        if deleted:
            message_bit = deleted
        else:
            message_bit = " 0"
        message = "RUBROS ELIMINADOS:" + message_bit
        if non_empty:
            message +=  "IMPORTANTE: Borre o cambie el rubro de los siguientes \
                         proyectos antes de intentar borrarlos:" + non_empty
        return message

    class Meta:
        ordering = ("-nombre",)


class ProyectoManager(models.Manager):
    """
    Object manager para obtener todos los proyectos que no estén en el estado de
    borrador
    """
    def get_query_set(self):
        return super(ProyectoManager, self).get_query_set().exclude(estado=u"B")


class Proyecto(models.Model):
    """
    Todos los datos para un proyecto inmobiliario
    OJO: para mostrar los proyectos que le corresponde a cada usuario usar
    https://docs.djangoproject.com/en/1.3/ref/contrib/admin/#django.contrib.admin.ModelAdmin.queryset
    """
    def get_proyecto_photo_path(self, filename):
        return u'fotos/%s' % highlyRandomName(filename)

    nombre = models.CharField(_(u"nombre"), max_length=200)
    slug = models.SlugField(
        _(u"URL corta"), max_length=100,
        help_text=_(u"Utilize letras, números y '_' en vez de los espacios, como"
                    u" en la URL corta de sugerencia"),
        default=u'nombre_proyecto'
    )
    rubro = models.ForeignKey(Rubro, verbose_name=_(u"rubro"), null=True)
    foto_principal = ImageWithThumbnailsField(
        verbose_name=_(u'foto de perfil'),
        upload_to=get_proyecto_photo_path,
        generate_on_save=True,
        thumbnail={'size': (100, 100), 'options': ['crop', 'upscale']},
        extra_thumbnails={
            'icon': {'size': (25, 25), 'options': ['crop', 'upscale']},
            'small': {'size': (40, 40), 'options': ['crop', 'upscale']},
            'rubro_preview': {'size': (200, 100), 'options':['crop', 'upscale']},
            'preview': {'size': (120, 110), 'options': ['crop', 'upscale']},
            'big': {'size': (586, 350), 'options': ['crop', 'upscale']},
            'small_slider': {'size': (280, 250), 'options': ['crop', 'upscale']},
            'slider': {'size': (630, 320), 'options': ['crop', 'upscale']},
        }
    )
    foto_inicio = ImageWithThumbnailsField(
        verbose_name=_(u'foto de inicio'),
        upload_to=get_proyecto_photo_path,
        generate_on_save=True,
        thumbnail={'size': (630, 320), 'options': ['crop', 'upscale']},
        null=True, blank=True,
    )
    fecha_inicio = models.DateField(_(u"fecha de inicio"), blank=True,null=True)
    fecha_fin = models.DateField(_(u"fecha de fin"), blank=True, null=True)
    TIPO_CONTRATO_CHOICES = (
        (u"R", _(u"Renta")),
        (u"V", _(u"Venta")),
    )
    tipo_contrato = models.CharField(_(u"tipo de contrato"), max_length=1,
                                     choices=TIPO_CONTRATO_CHOICES,
                                     default=u"V")
    ESTADO_CHOICES = (
        (u"B", _(u"Borrador")),
        (u"A", _(u"Activo")),
        (u"T", _(u"Terminado")),
    )
    estado = models.CharField(_(u"estado"), max_length=1,
                              choices=ESTADO_CHOICES, default=u"B")

    def get_inmobiliaria_path(self, filename):
        return u'inmobiliaria/%s' % highlyRandomName(filename)

    logo = ImageWithThumbnailsField(
        _(u'logo'), null=True, blank=True,
        upload_to=get_inmobiliaria_path,
        generate_on_save=True,
        thumbnail={'size': (100, 100), 'options': ['crop', 'upscale']},
        extra_thumbnails={
            'small': {'size': (25, 25), 'options': ['crop', 'upscale']},
            'icon': {'size': (40, 40), 'options': ['crop', 'upscale']},
            'big': {'size': (400, 400), 'options': ['crop', 'upscale']},
            'preview': {'size': (130, 110), 'options': ['crop', 'upscale']},
            'pdf_size': {'size': (300,90), 'options': ['upscale'], 
                         'quality':100,},
        }
    )
    logo_watermark = ImageWithThumbnailsField(
        _(u'marca de agua'), null=True, blank=True,
        upload_to=get_inmobiliaria_path,
        generate_on_save=True,
        thumbnail={'size': (100, 100), 'options': ['upscale'],
                   'extension': 'PNG'},
        extra_thumbnails={
            #'small': {'size': (25, 25), 'options': ['crop', 'upscale']},
            'big': {'size': (400, 400), 'options': ['upscale'],
                    'extension': 'PNG'},
        }
    )
    area = models.FloatField(_(u"área"), blank=True, null=True)
    area_construida = models.FloatField(_(u"área construída"), blank=True,
                                          null=True)
    RELEVANCIA_CHOICES = (
        (u"5", _(u"Muy importante")),
        (u"4", _(u"Importante")),
        (u"3", _(u"Medianamente importante")),
        (u"2", _(u"Poco importante")),
        (u"1", _(u"Nada importante")),
    )
    relevancia = models.CharField(_(u"relevancia"), max_length=1,
                                  choices=RELEVANCIA_CHOICES, default=u"3")
    introduccion = models.TextField(_(u"introducción"), blank=True, null=True)
    resumen = models.TextField(_(u"resumen"), blank=True, null=True)
    descripcion = models.TextField(_(u"descripción"), blank=True, null=True)
    latitud = models.FloatField(_(u"latitud"), blank=True, null=True)
    longitud = models.FloatField(_(u"longitud"), blank=True, null=True)
    precio_minimo = models.FloatField(_(u"precio mínimo"), blank=True,
                                      null=True)
    precio_maximo  = models.FloatField(_(u"precio máximo"), blank=True,
                                      null=True)
    direccion = models.CharField(_(u"dirección"), max_length=200, blank=True,
                                 null=True)
    provincia = models.ForeignKey(Provincia, null=True, blank=True)
    avance = models.FloatField(_(u"avance"), blank=True, null=True, default=0)
    pdf = models.CharField('pdf url', max_length=120, blank=True, null=True)
    gmaps_image = models.CharField('pdf url', max_length=120, editable=False)
    fotos = models.ManyToManyField('common.Foto', verbose_name=_(u"fotos"),
                                   blank=True, null=True)
    videos = models.ManyToManyField('common.Video', verbose_name=_(u"videos"),
                                    blank=True, null=True)
    web_url = models.URLField(_(u"Sitio web"), blank=True, null=True)
    #clientes afiliados (que siguen) al proyecto
    clientes = models.ManyToManyField('usuarios.Cliente', null=True,
                                      blank=True,
                                      related_name="proyectos",
                                      verbose_name=_(u"clientes"))
    corredores = models.ManyToManyField('usuarios.Corredor',
                                        null=True, blank=True,
                                        verbose_name=_(u"corredores"))
    # usuarios autorizados para acceder al proyecto desde el admin
    usuarios = models.ManyToManyField(User, null=True, blank=True,
                                       verbose_name=_(u'usuarios'))

    # managers
    objects = models.Manager()
    accepted = ProyectoManager()
    
    class Meta:
        ordering = ("-relevancia",)

    @staticmethod
    def get_destacados(num):
        """
        Devuelve 'num' proyectos destacados ordenados por relevancia
        Excluye a los que están con estado borrador
        """
        return Proyecto.accepted.order_by("-relevancia")[:num]

    @staticmethod
    def get_rango_precio(tipo_contrato):
        """
        Devuelve un rango de precios para los proyectos de un determinado tipo
        de contrato
        """
        rango = Proyecto.accepted.filter(tipo_contrato=tipo_contrato).aggregate(
            Max("precio_maximo"),
            Min("precio_minimo")
        )
        return rango

    def __unicode__(self):
        return u"%s" % self.nombre

    def save(self, *args, **kwargs):
        """
        Hace un ping a google sobre la actualización
        """
        try:
            ping_google()
        except Exception:
            pass

        return super(self.__class__, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        como se desactivo el delete en cascada de este modelo en Etapa
        se están borrando manualmente las etapas relacionadas
        
        se personalizo el delete en item
        se personalizo el delete en contacto
        se borran los videos y fotos del proyecto
        """
        for e in self.etapa_set.all():
            e.delete()

        for plano in self.plano_set.iterator():
            plano.delete()
            # for item in plano.item_set.iterator():
            #     item.delete()

        # if self.contacto:
            # self.contacto.delete()
        try: 
            self.contacto.delete()
        except Contacto.DoesNotExist:
            pass

        for foto in self.fotos.iterator():
            foto.delete()
        for video in self.videos.iterator():
            video.delete()

        return super(self.__class__, self).delete(*args, **kwargs)

    @models.permalink
    def get_absolute_url(self):
        """
        Devuelve la url del perfil público del proyecto
        """
        # TODO: Cambiar a la que usa el slug
        return 'proyectos.views.perfil_proyecto', [str(self.slug)]

    def departamento(self):
        return u'%s' % self.provincia.departamento
    departamento.short_description = u'Departamento'

    def get_random_oferta(self):
        """
        Devuelve una oferta al azar del proyecto
        """
        try:
            return Oferta.objects.filter(proyecto=self).order_by("?")[0]
        except IndexError:
            return None

    def get_etapa_actual(self):
        """
        si alguna etapa no tiene fecha las ordena por -id, en caso contrario
        lo hace por fechas
        Devuelve:
        - La etapa actual si existiera, dependiendo de las fechas
        - La subetapa actual
        - El avance actual del último milestone alcanzado
        """
        # fecha_actual = datetime.now()
        # etapas = Etapa.objects.filter(
        #     proyecto=self,
        #     fecha_inicio__lte=fecha_actual,
        #     fecha_fin__gte=fecha_actual
        # ).order_by("-fecha_fin")
        # if etapas:
        #     subetapa, milestone = etapas[0].get_subetapa_actual()
        #     return etapas[0], subetapa, milestone
        # else:
        #     return None, None, None

        fecha_actual = datetime.now()
        queryset = Etapa.objects.filter(proyecto=self)
        unDatedEtapas = queryset.filter( 
            Q(fecha_inicio__isnull=True) | Q(fecha_fin__isnull=True) )
        if unDatedEtapas:
            etapas = queryset.order_by('-id')
        else:
            etapas = queryset.filter(
                fecha_inicio__lte=fecha_actual,
                fecha_fin__gte=fecha_actual
                ).order_by("-fecha_fin")
        if etapas:
            subetapa, milestone = etapas[0].get_subetapa_actual()
            return etapas[0], subetapa, milestone
        else:
            return None, None, None


    def get_esquema_avance(self):
        """
        Devuelve el esquema de avance de un proyecto, etapas, subetapas y
        milestones
        """
        esquema_avance = []
        etapasqueryset = Etapa.objects.filter(proyecto=self)
        milestonesqueryset = None
        nonDatedEtapas = etapasqueryset.filter(
            Q(fecha_inicio__isnull=True) | Q(fecha_fin__isnull=True))
        if nonDatedEtapas:
            etapas = etapasqueryset.order_by('-id')
        else:
            etapas = etapasqueryset.order_by("fecha_inicio")
        for etapa in etapas:
            subetapas = SubEtapa.objects.filter(etapa=etapa)
            esquema_subetapas = []
            for subetapa in subetapas:
                avances = Avance.objects.filter(subetapa=subetapa, estado=u"P")
                esquema_avances = []
                for avance in avances:
                    milestonesqueryset = Milestone.objects.filter(
                        subetapa=subetapa, alcanzado=True, avance=avance
                        )
                    if milestonesqueryset.filter(fecha_fin__isnull=True):
                        milestones = milestonesqueryset.order_by('-id')
                    else:
                        milestones = milestonesqueryset.order_by('-fecha_fin')
                    if milestones:
                        porcentaje = milestones.aggregate(Sum("porcentaje"))["porcentaje__sum"]
                        fecha_ultimo_milestone = milestones[0].fecha_fin
                    else:
                        porcentaje = None
                        fecha_ultimo_milestone = None
                    esquema_avances.append(
                        {"avance": avance,
                         "porcentaje": porcentaje,
                         "fecha_ultimo_milestone": fecha_ultimo_milestone})
                esquema_subetapas.append({"subetapa": subetapa,
                                          "avances": esquema_avances})
            esquema_avance.append({"etapa": etapa,
                                   "subetapas": esquema_subetapas})

        # TODO: Se puede guardar el esquema de avance para optimizar
        return esquema_avance

    def getLatLng(self):
        """
        Devuelve la latitud y longitud de la ubicación
        """
        return "%s,%s" % (self.latitud, self.longitud)

    def send_location_area_mail(self):
        """
        Envía el correo informativo a los clientes que seleccionaron el área de
        interés conteniendo al proyecto
        """
        li = []
        # TODO: Optimizar con una sola consulta
        for cliente in Cliente.objects.all():
            for area in cliente.areas_interes.all():
                if area.high_latitud >= self.latitud and \
                   area.high_longitud >= self.longitud and \
                   area.low_latitud <= self.latitud and \
                   area.low_longitud <= self.longitud:
                    # send_html_mail(
                    #     "info@quimerainmobiliaria.com", u"Nuevo proyecto",
                    #     "nuevo_proyecto.html",
                    #     {"proyecto": self, "cliente": cliente},
                    #     cliente.usuario.email
                    # )
                    li.append(cliente.usuario.email)
                    break
        if li:
            site = Site.objects.get(id=1)
            url_proyecto = 'http://'+site.name+self.get_absolute_url()
            msg = u'&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Se ha creado un nuevo proyecto\
 dentro de tus áreas de interés. Visítalo en <a href="%s">%s</a>' % \
(url_proyecto,url_proyecto)
            send_mass_html_mails(
                settings.DEFAULT_FROM_EMAIL,
                u"Nuevo proyecto",
                'avance.html',
                {'sitio':site, 
                 'STATIC_URL':settings.STATIC_URL, 'msg':msg},
                li,
                )

    def create_update_gmaps_image(self):
        """
        crea o actualiza la imagen de localizacion en google maps junto con
        sus referencias
        """
        from common.models import Referencia
        import urllib

        path = os.path.join(
            settings.MEDIA_ROOT, 'proyectos', str(self.id))
        if not os.path.exists(path):
            os.makedirs(path)
        name = os.path.join(path, 'gmap%s.png' % self.id)

        r = "http://maps.google.com/maps/api/staticmap?center="\
+str(self.latitud)+","+str(self.longitud)+"&zoom=16&size=650x500&sensor=\
false&format=png32&maptype=roadmap&markers=color:red|label:S|"+\
str(self.latitud)+","+str(self.longitud)
        CLOSE_CONST = 0.0068
        referencias = Referencia.objects.filter(
            latitud__lte=self.latitud+CLOSE_CONST,
            latitud__gte=self.latitud-CLOSE_CONST,
            longitud__lte=self.longitud+CLOSE_CONST,
            longitud__gte=self.longitud-CLOSE_CONST,
            )
        for R in referencias:
            r+= '&markers=color:yellow|label:R|%s,%s' % (R.latitud,R.longitud)
        urllib.urlretrieve(r,name)
        self.gmaps_image = os.path.join(settings.MEDIA_URL,
            'proyectos', str(self.id), 'gmap%s.png' % self.id)
        self.save()

    def create_pdf(self, template_path='proyectos/pdf_template.html'):
        """
        crea un pdf con todos los datos del proyecto
        borra el pdf anterior
        """
        import xhtml2pdf.pisa as pisa
        import cStringIO as StringIO
        from django.template.loader import render_to_string
        from portal.models import Inmobiliaria
        from django.shortcuts import get_object_or_404

        #name = self.nombre+datetime.now().strftime('%d-%m-%y_%H:%M%S')+'.pdf'
        baseName = 'QuimeraInmobiliaria'+datetime.now().strftime(
            '%d-%m-%y %H:%M:%S')+'.pdf'

        path = os.path.join(
            settings.MEDIA_ROOT, 'proyectos', str(self.id))
        if not os.path.exists(path):
            os.makedirs(path)
#        name = os.path.join(path, 'QuimeraInmobiliaria%s.pdf' % self.id)
        name = os.path.join(path, baseName)
        myfile = StringIO.StringIO()
        try:
            I = get_object_or_404(Inmobiliaria, id=1)
        except Inmobiliaria.DoesNotExist:
            return u'No se ha creado una imbobiliaria todavía'
        logo_path = ''
        if self.logo:
            logo_path = self.logo._get_extra_thumbnails()['pdf_size'].dest
        logoW_path = ''
        if self.logo_watermark:
            logoW_path = self.logo_watermark._get_extra_thumbnails()['big'].dest
        else:
            logoW_path = I.logo_watermark._get_extra_thumbnails()['big'].dest
        logoI_path = I.logo._get_extra_thumbnails()['pdf_size'].dest

        showContact = False
        try:
            contacto = self.contacto
            if self.contacto.telefonos.count() > 3:
                showContact = True
        except ObjectDoesNotExist:
            contacto = ''
        dict_data = {
            'logo': logo_path,
            'logoW': logoW_path,
            'logoI': logoI_path,
            'contacto': contacto,
            'showContact': showContact,
            'etapasList': self.etapa_set.order_by("id"),
            'fotosList': self.fotos.order_by("id"),
            'caracList': self.caracteristica_set.order_by("id"),
            'benefList': self.beneficio_set.order_by("id"),
            'planosList': self.plano_set.order_by("id"),
            'MEDIA_ROOT': settings.MEDIA_ROOT,
            'STATIC_ROOT': settings.STATIC_ROOT,
            'obj': self,
        }
        file_data = render_to_string(template_path, dict_data)  

        ###################3
        # import codecs
        # FILE = codecs.open('tmp1.html',encoding='utf-8',mode='rb')
        # #FILE.write(file_data)
        # content = FILE.read()
        # FILE.close()
        # file_data = content
        #####################3

        pisa.CreatePDF(file_data, myfile)

        FILE = open(name,"wb")
        FILE.write(myfile.getvalue())
        FILE.close()
        myfile.close()
        # self.pdf = os.path.join(settings.MEDIA_URL,
        #     'proyectos', str(self.id), 'QuimeraInmobiliaria%s.pdf' % self.id)
        old_pdf = self.pdf
        self.pdf = os.path.join(settings.MEDIA_URL,
            'proyectos', str(self.id), baseName)
        if old_pdf:
            os.remove(os.path.join(settings.MEDIA_ROOT, "proyectos", 
                                   str(self.id), os.path.basename(old_pdf)))
        self.save()
        
        return u'pdf creado exitósamente'

    def delete_pdf(self):
        """
        Borra el pdf de un proyecto
        """
        self.pdf = None
        self.save()

    def recalcular_avance(self):
        """
        recalcula el % avanzado considerando los acances realizados del 
        arbol de avance representado por las etapas, subetapas y 
        milestones
        """
        avance_E = avance_SE = avance_M = 0
        for etapa in self.etapa_set.all():
            avance_SE =0
            for subetapa in etapa.subetapa_set.all():
                avance_M = subetapa.milestone_set.filter(alcanzado=True).\
aggregate(s=Sum('porcentaje'))
                if avance_M['s']:
                    avance_SE += subetapa.porcentaje*avance_M['s']
            avance_E += etapa.porcentaje*avance_SE
        self.avance = avance_E/10000
        self.save()
        return self.avance


@receiver(pre_save, sender=Proyecto, dispatch_uid="save_proyecto")
def pre_save_proyecto(sender, **kwargs):
    """
    Cuando un proyecto es creado o su ubicación es modificada se envía
    información a los clientes que hayan citado su área de interés
    conteniendo este. Sólo se consideran los proyectos con estado diferente de 
    Borrador
    Si se cambia de estado borrado tambien se envia la informaición según las 
    áreas de interés
    """
    new = kwargs["instance"]
    if new.id and new.estado != u'B':
        old = Proyecto.objects.get(id=new.id)
        if old.estado == u'B' and new.latitud:
            new.send_location_area_mail()
        elif old.latitud:
            if round(old.latitud,10) != round(new.latitud,10) or \
round(old.longitud,10) != round(new.longitud,10):
                new.send_location_area_mail()
        elif new.latitud:
            new.send_location_area_mail()


class Alerta(models.Model):
    """
    Una alerta se envía a todos los usuarios al ocurrir un evento
    automáticamente y queda activa por un tiempo, tiene un link al lugar exacto
    donde está la información
    """
    TIPO_CHOICES = (
        (u"O", _(u"tiene una nueva oferta")),
        (u"A", _(u"actualizó el avance de obra")),
        (u"N", _(u"ha sido creado")),
        (u"C", _(u"ha sido concluído")),
    )
    tipo = models.CharField(_(u"tipo"), max_length=1, choices=TIPO_CHOICES)
    proyecto = models.ForeignKey(Proyecto, verbose_name=_(u"proyecto"))
    fecha_inicio = models.DateField(_(u"fecha de inicio"), default=datetime.now)
    duracion = models.IntegerField(_(u"duración"))
    link = models.URLField(_(u"enlace"))

    def __unicode__(self):
        return u"%s" % self.tipo


class Plano(models.Model):
    """
    Plano de un nivel o área de un proyecto
    """
    titulo = models.CharField(_(u"título"), max_length=150)
    descripcion = models.TextField(_(u"descripción"), blank=True)
    proyecto = models.ForeignKey(Proyecto, verbose_name=_(u"proyecto"), 
                                 null=True)

    def get_inmobiliaria_planos(self, filename):
        return u'inmobiliaria/planos/%s' % highlyRandomName(filename)

    plano = ImageWithThumbnailsField(
        _(u'plano'),
        #upload_to="inmobiliaria/planos",
        upload_to=get_inmobiliaria_planos,
        generate_on_save=True,
        thumbnail={'size': (100, 100), 'options': ['crop', 'upscale']},
        extra_thumbnails={
            'small': {'size': (25, 25), 'options': ['crop', 'upscale']},
            'pdf_size': {'size': (380, 380), 
                         'options': ['upscale'], 'quality': 100,},
            'big': {'size': (400, 400), 'options': ['crop', 'upscale']},
            # 'slider_size': {'size': (417, 417), 
            #              'options': ['upscale'], 'quality': 100,},
            'slider_size': {'size': (464, 464), 
                         'options': ['upscale'], 'quality': 100,},
            'plano_size': {'size': (800, 800), 
                         'options': ['upscale'], 'quality': 100,},
            'preview_solicitud': {'size': (890, 890), 
                         'options': ['upscale'], 'quality': 100,},

        }
    )

    plano_dibujado = ImageWithThumbnailsField(
        _(u'plano dibujado'),
        #upload_to="inmobiliaria/planos",
        upload_to=get_inmobiliaria_planos,
        generate_on_save=True,
        thumbnail={'size': (100, 100), 'options': ['upscale'], 'quality': 100,},
        extra_thumbnails={
            'small': {'size': (25, 25), 'options': ['upscale'], 
                      'quality': 100,},
            'pdf_size': {'size': (380, 380), 'options': ['upscale'],
                         'quality': 100,},
            'big_pdf_size': {'size': (990, 990), 
                         'options': ['upscale'], 'quality': 100,},            
            'big': {'size': (400, 400), 'options': ['upscale'], 
                    'quality': 100,},
            'plano_size': {'size': (800, 800), 
                         'options': ['upscale'], 'quality': 100,},
        }
    )
    actualizacion = models.DateTimeField(_(u"actualizado el"), auto_now=True,
                                         editable=False)

    class Meta:
        ordering = ('-id',)

    def __unicode__(self):
        return u"%s, %s" % (self.proyecto, self.titulo)

    def delete(self):
        """
        borra el plano y a sus items llamando al delete del item
        """
        for i in self.item_set.iterator():
            i.delete()
        return super(self.__class__, self).delete()

    def hex_to_rgb(self, value):
        value = value.lstrip('#')
        lv = len(value)
        return tuple(int(value[i:i+lv/3], 16) for i in range(0, lv, lv/3))

    def create_plano_image(self):
        """
        crea la imagen del plano dibujado,
        borra todas las imagenes de los planos dibujados anteriores, 
        sube la imagen dibujada al campo plano_dibujado
        """
#        path = self.plano.extra_thumbnails.get('plano_size').dest
        path = self.plano.path
        #new proportions
        wProp = float(self.plano.width)/self.plano.extra_thumbnails\
.get('plano_size').width()
        hProp = float(self.plano.height)/self.plano.extra_thumbnails\
.get('plano_size').height()
        im = Image.open(path)
#        draw = ImageDraw.Draw(im)
        for i in self.item_set.all():
            poly = Image.new('RGBA',(self.plano.width,self.plano.height))
            drw = ImageDraw.Draw(poly) 
            drw.polygon( i.poligono.get_points_list(True, wProp, hProp), 
                         fill=self.hex_to_rgb(i.poligono.color_relleno)+(102,),
                         outline='#333333')
            im.paste(poly,mask=poly)
            del drw
            
            # draw.polygon( i.poligono.get_points_list(True, wProp, hProp), 
            #               fill=i.poligono.color_relleno,
            #               outline='#333333')
#        del draw

        # path2 = os.path.join(settings.MEDIA_ROOT, 'inmobiliaria/planos/',
        #                      'drawn'+os.path.basename(path))

        path2 = os.path.join(settings.MEDIA_ROOT, 'inmobiliaria/planos/',
                             'drawn'+highlyRandomName(os.path.basename(path)))

        im.save(path2,"JPEG")
        #im.save(path2,"PNG")

        #removiendo imagenes dibujadas anteriores
        try:
            self.plano_dibujado.delete()
        except:
            a=1

        #subiendo la imagen al campo correspondiente
        self.plano_dibujado.save(os.path.basename(path2), File(open(path2)))
        self.save()

        #removiendo imagen creada
        os.remove(path2)
            

class Caracteristica(models.Model):
    """
    Característica de un proyecto
    """
    nombre = models.CharField(_(u"nombre"), max_length=150)
    descripcion = models.TextField(_(u"descripción"))
    proyecto = models.ForeignKey(Proyecto, verbose_name=_(u"proyecto"))

    def __unicode__(self):
        return u"%s" % self.nombre

    class Meta:
        ordering = ['-id',]
        verbose_name = _(u"Característica")
        verbose_name_plural = _(u"Características")


class Beneficio(models.Model):
    """
    Beneficio de un proyecto
    """
    descripcion = models.TextField(_(u"descripción"))
    proyecto = models.ForeignKey(Proyecto, verbose_name=_(u"proyecto"))

    def __unicode__(self):
        return u"%s" % self.descripcion

    class Meta:
        ordering = ['-id',]
        verbose_name = _(u"Beneficio")
        verbose_name_plural = _(u"Beneficios")


class TipoItemNombre(models.Model):
    """
    Categorías de los tipos de items
    """
    nombre = models.CharField(_(u"nombre"), max_length=50)

    def __unicode__(self):
        return u"%s" % self.nombre

    class Meta:
        verbose_name = _(u"Nombre del tipo de item")
        verbose_name_plural = _(u"Nombres de los tipo de item")


class TipoItem(models.Model):
    """
    Categoría a la que pertenece un grupo de items
    """
    nombre = models.ForeignKey(TipoItemNombre, verbose_name=_(u"nombre"),
                               null=True)
    area = models.FloatField(_(u"area"))
    proyecto = models.ForeignKey(Proyecto, verbose_name=_(u"proyecto"),
                                 null=True)
    precio = models.FloatField(_(u"precio"), 
                               help_text=_(u'Precio en dólares'),
                               blank=True, null=True)

    def get_inmobiliaria_tipos(self, filename):
        return u'inmobiliaria/tipos/%s' % highlyRandomName(filename)    

    foto = ImageWithThumbnailsField(
        _(u'foto'),
        #upload_to="inmobiliaria/tipos",
        upload_to=get_inmobiliaria_tipos,
        blank=True,
        generate_on_save=True,
        thumbnail={'size': (100, 100), 'options': ['crop', 'upscale']},
        extra_thumbnails={
            'small': {'size': (25, 25), 'options': ['crop', 'upscale']},
            'items': {'size': (50, 50), 'options': ['crop', 'upscale']},
            'big': {'size': (400, 400), 'options': ['crop', 'upscale']},
            'small_upscale': {'size': (100, 100), 'options': ['upscale']},
        }
    )
    detalles = models.TextField(_(u"detalles"), blank=True)

    class Meta:
        verbose_name = _(u"Tipo de item")
        verbose_name_plural = _(u"Tipos de item")

    def __unicode__(self):
        return u"Tipo: %s, Proyecto: %s" % (self.nombre, self.proyecto)


def update_min_max_prices(sender, instance, created, **kwargs):
    """
    luego de grabar un objeto TipoItem, actualiza los precios minimos y maximos
    """
    obj = instance
    proyecto = obj.proyecto
    prices = proyecto.tipoitem_set.aggregate(lowest=Min('precio'),
                                                 highest=Max('precio'))
    proyecto.precio_minimo = prices['lowest']
    proyecto.precio_maximo = prices['highest']
    proyecto.save()
post_save.connect(update_min_max_prices, sender=TipoItem)


class Item(models.Model):
    """
    Unidad de venta o renta de un proyecto
    """
    numero = models.CharField(_(u"número"), max_length=10)
    tipo_item = models.ForeignKey(TipoItem, verbose_name=(u"tipo de item"))
    plano = models.ForeignKey(Plano, verbose_name=_(u"plano"))
    ESTADO_CHOICES = (
        (u"D", _(u"Disponible")),
        (u"S", _(u"Separado")),
        (u"V", _(u"Vendido")),
    )
    estado = models.CharField(_(u"estado"), max_length=1,
                              choices=ESTADO_CHOICES, default=u"D")
    detalles = models.TextField(_(u"detalles"),blank=True)
    poligono = models.ForeignKey('common.Poligono', verbose_name=_(u"polígono"),
                                 blank=True, null=True)
    #cliente que compro el item
    cliente = models.ForeignKey('usuarios.Cliente', verbose_name=_(u"cliente"),
                                blank=True, null=True)

    class Meta:
        ordering = ('-id',)

    def __unicode__(self):
        return u"Nro: %s, %s" % (self.numero, self.tipo_item)

    def save(self, *args, **kwargs):
        """
        si esta actualizando y el estado es Disponible pone el cliente en None

        graba el item y trata de actualizar el color de su poligono a menos que
        reciba update_poligon=False
        """
        if self.id and self.estado == u'D':
            #print 'se esta actualizando'
            self.cliente = None
                
        super( self.__class__, self ).save()
        update_poligon = kwargs.get('update_poligon')
        if not 'update_poligon' in kwargs or update_poligon != False:
            colores_relleno = {u'D':'#009900', u'S':'#FFFF00', u'V':'#FF0000'}
            p = self.poligono
            p.color_relleno = colores_relleno[self.estado]
            p.save()

    def delete(self):
        """
        borra el item y su poligono
        """
        self.poligono.delete()
        super( self.__class__, self ).delete()

    def human_readable_estado(self):
        """
        retorna el estado del item en forma legible para los humanos
        """
        for e in self.ESTADO_CHOICES:
            if e[0] == self.estado:
                return e[1]


class Oferta(models.Model):
    """
    Oferta sobre algún item de un proyecto
    """
    proyecto = models.ForeignKey(Proyecto, verbose_name=(u"proyecto"), 
                                 null=True)
    # tipo_item = models.ForeignKey(TipoItem, verbose_name=(u"tipo de item"),
    #                                null=True)
    item = models.ForeignKey(Item, verbose_name=(u'item'), null=True)
    tasa_descuento = models.IntegerField(_(u"tasa de descuento"))
    fecha_inicio = models.DateField(_(u"fecha de inicio"))
    duracion = models.IntegerField(
        verbose_name=_(u"duración"),
        help_text=_(u"Número de dias de duración de la oferta desde la fecha \
                    de inicio")
    )
    fecha_fin = models.DateField(_(u'fecha fin'), editable=False)
    descripcion = models.TextField(_(u"descripción"))

    def __unicode__(self):
        return u"%s, %s" % (self.proyecto, self.item.numero)

    def new_price(self):
        return u'%s' % (float(self.item.tipo_item.precio) *
            ( 100 - float(self.tasa_descuento) ) / 100)

    def save(self, *args, **kwargs):
        """
        calcula la fecha fin de la oferta y graba la oferta
        """
        self.fecha_fin = self.fecha_inicio + timedelta(days=self.duracion)

        return super(self.__class__, self).save(*args, **kwargs)
    

class Etapa(models.Model):
    """
    Una etapa de un proyecto
    """
    titulo = models.CharField(_(u"título"), max_length=50)
    proyecto = models.ForeignKey(Proyecto, verbose_name=(u"proyecto"),
                                 on_delete=models.SET_NULL, null=True)
    descripcion = models.TextField(_(u"descripción"))
    fecha_inicio = models.DateField(_(u"fecha de inicio"), blank=True, null=True)
    fecha_fin = models.DateField(_(u"fecha de fin"), blank=True, null=True, 
                                 default='')
    porcentaje = models.FloatField(_(u"porcentaje"))

    class Meta:
        ordering = ['-id']

    def __unicode__(self):
        return u"%s" % self.titulo

    def delete(self):
        """
        como se desactivo el delete en cascada de este modelo en sub-etapa      
        se están borrando manualmente las subetapas 
        """
        for se in self.subetapa_set.all():
            se.delete()
        return super(self.__class__, self).delete()

    ############# FALTA REVISAR CUANDO NO HAY FECHAS CREO Q SE VA YODER TODO
    def get_subetapa_actual(self):
        """
        Si no se ingresaron fechas realiza el ordenamiento de las subetapas por 
        '-id'
        Devuelve:
        - La subetapa actual si existiera, dependiendo de las fechas y de
        una etapa
        - Los avances según el último milestone terminado
        """
        # fecha_actual = datetime.now()
        # subetapas = SubEtapa.objects.filter(
        #     etapa=self,
        #     fecha_inicio__lte=fecha_actual,
        #     fecha_fin__gte=fecha_actual
        # ).order_by("-fecha_fin")
        # if not subetapas:
        #     subetapas = SubEtapa.objects.filter(etapa=self).order_by("-id")
        # if subetapas:
        #     return subetapas[0], subetapas[0].get_last_avance()
        # else:
        #     return None, None

        fecha_actual = datetime.now()
        queryset = SubEtapa.objects.filter(etapa=self)
        nonDatedSubetapas = queryset.filter(
            Q(fecha_inicio__isnull=True) | Q(fecha_fin__isnull=True))
        if nonDatedSubetapas:
            subetapas = queryset.order_by("-id")
        else:
            subetapas = queryset.filter(
                fecha_inicio__lte=fecha_actual,
                fecha_fin__gte=fecha_actual
                ).order_by("-fecha_fin")
        if subetapas:
            return subetapas[0], subetapas[0].get_last_avance()
        else:
            return None, None

#ToDo: comente esto xq demora al crear al pdf ralentiza el proceso
#      hay que hacer una funcion update para que actualicen el pdf 
#      de manera manual y cuando lo vean necesario
#      creo  lo mejor seria poner un boton en los forms q diga actualizar pdf
# def update_pdf_etapa(sender, instance, created, **kwargs):
#     """
#     luego de guardar o actualizar una etapa actualiza el pdf del proyecto
#     """
#     etapa = instance
#     etapa.proyecto.create_pdf()
# post_save.connect(update_pdf_etapa, sender=Etapa)


class SubEtapa(models.Model):
    """
    Una subetapa de un proyecto, parte de una etapa
    """
    titulo = models.CharField(_(u"título"), max_length=50)
    etapa = models.ForeignKey(Etapa, verbose_name=_(u"etapa"))
    fecha_inicio = models.DateField(_(u"fecha de inicio"), blank=True, null=True)
    fecha_fin = models.DateField(_(u"fecha de fin"), blank=True, null=True)
    porcentaje = models.FloatField(_(u"porcentaje"))

    class Meta:
        ordering = ['id']

    def __unicode__(self):
        return u"%s" % self.titulo

    def delete(self):
        """
        como se desactivo el delete en cascada de este modelo en MileStone y 
        Avance se están borrando manualmente los milestones relacionados y sus
        avances asi como los avances que no tienen ningun milestone sociados
        """
        for m in self.milestone_set.all():
            m.delete()
        for a in self.avance_set.all():
            a.delete(cascade=False)
        return super(self.__class__, self).delete()

    def get_last_avance(self):
        """
        Si un milestone no tiene fecha realiza el ordenamienot por -id, sino 
        lo hace por -fecha_fin

        Devuelve el avance correspondientes al último milestone alcanzado
        dentro de una subetapa si esta se da, si no se está usando el porcentaje
        de avance se devuelve el último avance
        """
        # milestones = Milestone.objects.filter(
        #     subetapa=self,
        #     alcanzado=True
        # ).order_by("-fecha_fin")
        # if milestones:
        #     return milestones[0].avance
        # else:
        #     return Avance.objects.filter(
        #         subetapa=self, estado=u"P").order_by("-fecha_creacion")[0]

        queryset = Milestone.objects.filter(subetapa=self, alcanzado=True)
        
        nonDatedMilestones = queryset.filter(fecha_fin__isnull=True)
        if nonDatedMilestones:
            milestones = queryset.order_by('-id')
        else:
            milestones = queryset.order_by('-fecha_fin')
        if milestones:
            return milestones[0].avance
        else:
            try:
                return Avance.objects.filter(
                subetapa=self, estado=u"P").order_by("-fecha_creacion")[0]
            except IndexError:
                return None

#ToDo: comente esto xq demora al crear al pdf ralentiza el proceso
#      hay que hacer una funcion update para que actualicen el pdf 
#      de manera manual y cuando lo vean necesario
#      creo  lo mejor seria poner un boton en los forms q diga actualizar pdf
# def update_pdf_subetapa(sender, instance, created, **kwargs):
#     """
#     luego de guardar o actualizar una sub-etapa actualiza el pdf del proyecto
#     """
#     subetapa = instance
#     try:
#         subetapa.etapa.proyecto.create_pdf()
#     except:
#         a=1
#post_save.connect(update_pdf_subetapa, sender=SubEtapa)


class Avance(models.Model):
    """
    Un avance tiene varios milestones asociados
    """
    notas = models.TextField(_(u"notas"))
    ESTADO_CHOICES = (
        (u"B", _(u"borrador")),
        (u"O", _(u"oculto")),
        (u"P", _(u"publicado")),
    )
    estado = models.CharField(_(u"estado"), max_length=1,
                              choices=ESTADO_CHOICES, default=u'B')
    fotos = models.ManyToManyField('common.Foto', verbose_name=_(u"fotos"), 
                                   blank=True, null=True)
    videos = models.ManyToManyField('common.Video', verbose_name=_(u"videos"),
                                    blank=True, null=True)
    proyecto = models.ForeignKey(Proyecto, verbose_name=_(u"proyecto"),
                                 related_name=('proyectos'), null=True)
    subetapa = models.ForeignKey(SubEtapa, verbose_name=_(u"SubEtapa"),
                                 on_delete=models.SET_NULL, null=True)
    fecha_creacion = models.DateTimeField(_(u'fecha de creación'),
                                          auto_now_add=True)
    ultima_modificacion = models.DateTimeField(_(u'última modificación'),
                                               auto_now=True)

    class Meta:
        ordering = ('-id',)

    def __unicode__(self):
        return u"%s - %s - %s" % (self.proyecto, self.subetapa.etapa, 
                                  self.subetapa)

    def etapa(self):
        return u'%s' % self.subetapa.etapa
    etapa.short_description = u'Etapa'

    def delete(self, *args, **kwargs):
        """
        borra los videos y fotos relacionados al avance
        si cascade=True, borra el avance y sus milestones relacionados # 
        si cascade=False, sólo borra el avance y deja intactos a los milestones
                          relacionados
        """
        if not 'cascade' in kwargs:
            kwargs['cascade'] = True
        for f in self.fotos.all():
            f.delete()
        for v in self.videos.all():
            v.delete()
        if kwargs['cascade'] == True:
            for m in self.milestone_set.all():
                m.delete(custom=False)
        kwargs.pop('cascade')
        super(self.__class__, self).delete(*args, **kwargs)

    # def admin_delete(self, queryset):
    #     """
    #     borra el avance y sus milestones relacionados, ademas de sus fotos y 
    #     videos
    #     """
    #     if queryset.count() > 1:
    #         msg = 'Los avances fueron borrados con éxito'
    #     else:
    #         msg =  'El avance fué borrado con éxito'
    #     for a in queryset.all():
    #         a.delete()
    #     return msg


class Milestone(models.Model):
    """
    Hito de una subetapa, al ser alcanzado el porcentaje del proyecto se
    recalcula
    """
    titulo = models.CharField(_(u"título"), max_length=50)
    subetapa = models.ForeignKey(SubEtapa, verbose_name=_(u"subetapa"), 
                                 on_delete=models.SET_NULL, null=True)
    avance = models.ForeignKey(Avance, verbose_name=_(u"avance"), null=True,
                               on_delete=models.SET_NULL)
    alcanzado = models.BooleanField(_(u"alcanzado"), default=False)
    fecha_fin = models.DateField(_(u"fecha de fin"), blank=True, null=True)
    porcentaje = models.FloatField(_(u"porcentaje"))

    class Meta:
        ordering = ['id']

    def __unicode__(self):
        return u"%s" % self.titulo

    def save(self, *args, **kwargs):
        """
        al grabar o actualizar un milestone, si alcanzado es True
        recalcula el avance del proyecto y envia un mail a todos los usuarios
        que siguen el proyecto
        """
        super(self.__class__, self).save(*args, **kwargs)
        if self.alcanzado == True:
            self.subetapa.etapa.proyecto.recalcular_avance()
            site=Site.objects.get(id=1)
            now = datetime.now().strftime('%d-%m-%y %H:%M:%S')
            avance_url = 'http://'+site.name+reverse(
                'etapas_proyecto', 
                args=(self.avance.proyecto.slug,))
            msg = u'&nbsp;&nbsp;&nbsp;&nbsp;El avance del proyecto "%s" para \
hoy %s es del %s. Mira sus avances en <a href="%s">%s</a>' % ( \
self.avance.proyecto.nombre, now, str(self.subetapa.etapa.proyecto.avance)+'%', \
avance_url, avance_url)
            send_mass_html_mails(
                settings.DEFAULT_FROM_EMAIL,
                u"Avance [%s] : Proyecto %s" % (now,self.avance.proyecto.nombre),
                'avance.html',
                {'sitio':site, 'STATIC_URL':settings.STATIC_URL, 'msg':msg},
                [i[0] for i in self.avance.proyecto.clientes.values_list(
                        'usuario__email')],
                )
            
    def delete(self, *args, **kwargs):
        """
        borra el milestone  así como su avance sólo si esta relacionado sólo
        a este milestone y custom = True, si esta condición se cumple cuando 
        se borra el avance también se borran sus videos y fotos relacionados
        sino se cumple la condición, sólo se borra el milestone
        ***Si recibe el parametro delProyecto como verdadero, no llama a la
        funcion recalcular_avance del proyecto porque como se esta borrando
        todo el proyecto ya no interesa recalcular
        """
        if 'custom' not in kwargs:
            kwargs['custom'] = True
        queryset = self.avance.milestone_set
        if kwargs['custom'] == True and queryset.count() == 1:
            self.avance.delete(cascade=False)
        kwargs.pop('custom')
        p=self.subetapa.etapa.proyecto
        if 'delProyecto' not in kwargs:
            recalcular = True            
        elif kwargs['delProyecto'] != True:
            recalcular = True
            kwargs.pop('delProyecto')
        else:
            recalcular = False
            kwargs.pop('delProyecto')
        super(self.__class__, self).delete(*args, **kwargs)
        if recalcular:
            p.recalcular_avance()


class Contacto(models.Model):
    """
    Datos de contacto con una oficina encargada del proyecto
    """
    proyecto = models.OneToOneField(Proyecto, verbose_name=_(u"proyecto"), 
                                    null=True, blank=True)
    direccion = models.CharField(_(u"dirección"), max_length=200)
    email = models.EmailField(_(u"e-mail"))
    telefonos = models.ManyToManyField('common.Telefono',
                                       verbose_name=_(u"teléfonos"))

    def __unicode__(self):
        return u"%s" % self.proyecto

    def delete(self):
        """
        borra el contacto y sus telefonos asociados
        """
        for telefono in self.telefonos.all():
            telefono.delete()
        return super(self.__class__,self).delete()


class Aviso(models.Model):
    """
    Publicidad en banners de imágenes o flash
    """
    proyecto = models.ForeignKey(Proyecto, verbose_name=_(u"proyecto"), 
                                 null=True)
    archivo = models.FileField(_(u"archivo"), upload_to=u"publicidad",
                               help_text=u"El ancho debe ser 270px")
    duracion = models.IntegerField(_(u"duración"),
                                   help_text=_(u"duración en segundos"))

    def __unicode__(self):
        return u"%s" % self.proyecto

    def get_archivo_html(self):
        """
        Devuelve en formato html correspondiente a la extensión del archivo
        la cadena para incluírlo en un template
        """
        ext = str(self.archivo.url).split(".")[1]
        if ext == "swf":
            html = '<object type="application/x-shockwave-flash" data="%s"> \
                    <param name="movie" value="%s" /> \
                    <param name="scale" value="exactfit" /></object>' % \
                    (self.archivo.url, self.archivo.url)
        else:
            html = '<img src="%s" title="%s" width="320px" height="300">' % \
                   (self.archivo.url, self.proyecto)
        
        return html


class Desarrollado(models.Model):
    """
    Proyecto desarrollado con datos limitados
    """
    def get_photo_path(self, filename):
        return u'desarrollados/%s' % highlyRandomName(filename)

    nombre = models.CharField(max_length=150, verbose_name=_(u"nombre"))
    slug = models.SlugField(verbose_name=_(u"slug"))
    descripcion = models.TextField()
    logo = ImageWithThumbnailsField(
        _(u'logo'),
        upload_to=get_photo_path,
        generate_on_save=True,
        thumbnail={'size': (105, 255), 'options': ['crop', 'upscale']},
    )
    principal = ImageWithThumbnailsField(
        _(u'principal'),
        upload_to=get_photo_path,
        generate_on_save=True,
        thumbnail={'size': (590, 260), 'options': ['crop', 'upscale']},
        null=True, blank=True,
    )

    def __unicode__(self):
        return u"%s" % self.nombre

    @models.permalink
    def get_absolute_url(self):
        return 'proyectos.views.perfil_desarrollado', [str(self.slug)]