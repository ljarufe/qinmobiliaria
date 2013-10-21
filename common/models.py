# -*- coding: utf-8 -*-

import json
from random import randint
from urllib import urlopen
from django.db import models
from django.utils.translation import ugettext_lazy as _
from common.utils import highlyRandomName
from sorl.thumbnail.fields import ImageWithThumbnailsField


class Departamento(models.Model):
    nombre = models.CharField(max_length=128)

    def __unicode__(self):
        return u'%s' % self.nombre

    class Meta:
        ordering = ['nombre',]


class Provincia(models.Model):
    nombre = models.CharField(max_length=128)
    departamento = models.ForeignKey(Departamento)

    def __unicode__(self):
        return u'%s' % self.nombre

    class Meta:
        ordering = ['nombre',]


class ThumbBase(models.Model):
    """
    Base para incluir una ImageWithThumbField
    """
    height = models.IntegerField(null=True)
    width = models.IntegerField(null=True)

    class Meta:
        abstract = True


class TipoTelefono(models.Model):
    """
    Operador de un número de teléfono
    """
    nombre = models.CharField(_(u"nombre"), max_length=20)

    def __unicode__(self):
        return u"%s" % self.nombre

    class Meta:
        verbose_name = _(u"Tipo de teléfono")
        verbose_name_plural = _(u"Tipos de teléfono")


class Telefono(models.Model):
    """
    Un número de teléfono
    """
    numero = models.CharField(_(u"teléfono"), max_length=15)
    tipo_telefono = models.ForeignKey(TipoTelefono,
                                      verbose_name=_(u"Tipo"),)

    def __unicode__(self):
        return u"%s" % self.numero

    class Meta:
        verbose_name = _(u"Teléfono")
        verbose_name_plural = _(u"Teléfonos")


class ViewPort(models.Model):
    """
    Dos puntos de coordenadas que representan un rectángulo
    En caso de la áreas de interés sólo deben enviar un mail
    cuando se crea un nuevo proyecto y éste cae dentro de las 
    áreas de interés de ciertos usuarios. A esos usuarios se les debe enviar 
    un mail avisándoles que se creó un nuevo proyecto dentro de sus áreas de 
    inteŕes.
    """
    nombre = models.CharField(_(u"nombre"), max_length=50)
    high_latitud = models.FloatField(_(u"latitud superior"))
    high_longitud = models.FloatField(_(u"longitud superior"))
    low_latitud = models.FloatField(_(u"latitud inferior"))
    low_longitud = models.FloatField(_(u"longitud inferior"))

    def __unicode__(self):
        return u"%s" % self.nombre


class Referencia(models.Model):
    """
    Un punto de interés en la tierra ubicado con sus coordenadas
    """
    nombre = models.CharField(_(u"nombre"), max_length=100)
    descripcion = models.TextField(_(u"descripción"), blank=True, null=True)

    def get_icono_photo_path(self, filename):
        return u'referencias/iconos/%s' % highlyRandomName(filename)

    icono = ImageWithThumbnailsField(
        _(u'icono'),
        #upload_to="referencias/iconos",
        upload_to=get_icono_photo_path,
        generate_on_save=True,
        thumbnail={'size': (25, 25), 'options': ['upscale'],
                   'extension': 'PNG'},
        extra_thumbnails={
            'gmap' : {'size': (57, 57), 'options': ['upscale'],
                      'extension': 'PNG'},
        }
    )
    latitud = models.FloatField(_(u"latitud"))
    longitud = models.FloatField(_(u"longitud"))

    def __unicode__(self):
        return u"%s" % self.nombre

    def getLatLng(self):
        """
        Devuelve la latitud y longitud de la ubicación
        """
        return "%s,%s" % (self.latitud, self.longitud)


class Foto(models.Model):
    """
    Una foto
    """
    nombre = models.CharField(_(u"nombre"), max_length=100)

    def get_photo_path(self, filename):
        return u'fotos/%s' % highlyRandomName(filename)

    imagen = ImageWithThumbnailsField(
        _(u'imágen'),
        upload_to=get_photo_path,
        generate_on_save=True,
        thumbnail={'size': (100, 100), 'options': ['crop', 'upscale']},
        extra_thumbnails={
            'small': {'size': (25, 25), 'options': ['crop', 'upscale']},
            'preview': {'size': (310, 280), 'options': ['crop', 'upscale']},
            'news': {'size': (426, 295), 'options': ['crop', 'upscale']},
            'pdf_size': {'size': (380, 380), 'options': ['crop', 'upscale']},
            'big': {'size': (586, 350), 'options': ['crop', 'upscale']},
        }
    )
    descripcion = models.TextField(_(u"descripción"), blank=True, null=True)

    class Meta:
        ordering = ['-id']

    def __unicode__(self):
        return u"%s" % self.nombre


class Video(models.Model):
    """
    URL de un video
    """
    nombre = models.CharField(_(u"nombre"), max_length=100)
    url = models.URLField(verify_exists=True, help_text='Debe colocar la URL' \
        'que YouTube le da al hacer click en Compartir debajo del video')
    descripcion = models.TextField(_(u"descripción"), blank=True, null=True)

    class Meta:
        ordering = ['-id',]

    def __unicode__(self):
        return u"%s" % self.nombre

    def get_html(self, width=466, height=350):
        """
        Devuelve el código html para una url en youtube
        """
        # TODO: Colocar esto en el save de video y guardar la src en otro nuevo campo, el dominio para sacar fotos
        url = str(self.url).split("/")
        src = ""
        if url[2].find("youtu") != -1:
            src = "http://www.youtube.com/embed/%s?rel=0&modestbranding=1" % url[3]
        elif url[2].find("vimeo") != -1:
            src = "http://player.vimeo.com/video/%s?title=0&amp;byline=0&amp;portrait=0" % url[3]

        return '<iframe width="%s" height="%s" ' \
               'src="%s" '\
               'frameborder="0" webkitAllowFullScreen mozallowfullscreen allowFullScreen></iframe>' % \
               (width, height, src)

    def get_html_news(self):
        """
        Devuelve el código html para una url en youtube
        """
        return self.get_html(343, 295)

    def get_html_small(self):
        """
        Devuelve el código html para una url en youtube
        """
        return self.get_html(280, 200)

    def get_html_preview(self):
        #TODO: Crear un templatetag para evitar hacer tantas funciones
        """
        Devuelve el código html para una url en youtube
        """
        return self.get_html(310, 280)

    def get_thumbnail(self):
        """
        Devuelve un thumbnail al azar desde youtube
        """
        url = str(self.url).split("/")
        if url[2].find("youtu") != -1:
            random = randint(1, 3)

            return '<img src="http://img.youtube.com/vi/%s/%s.jpg">' % \
                   (url[3], random)
        elif url[2].find("vimeo") != -1:
            data = urlopen('http://vimeo.com/api/v2/video/%s.json' % url[3]).read()

            return '<img src="%s">' % json.loads(data)[0]["thumbnail_small"]


class Poligono(models.Model):
    """
    Conjunto de puntos que forman un polígono
    """
    nombre = models.CharField(_(u"nombre"), max_length=50)
    color_borde = models.CharField(_(u"color de borde"), max_length=7,
                                   editable = False)
    color_relleno = models.CharField(_(u"color de relleno"), max_length=7, 
                                     editable = False, default='#FFFFFF')
    class Meta:
        ordering = ('-id',)

    def __unicode__(self):
        return u"%s" % self.nombre

    def get_points_list(self, integer=False, xFactor=1, yFactor=1, 
                        stringPresicion=False, numDecimals=2):
        """
        retorna una lista con los puntos de conforman el poligono
        si integer = True, las coordenadas son enteras
        sino, las coordenas son flotantes
        multiplica las coordenadas por los factores
        si stringPresicion = True, retorna la lista de puntos pero en 
        formato string y con un numero de decimales igual a numDecimals
        """
        return [p.coordinates(integer,xFactor,yFactor,stringPresicion,
                              numDecimals) for p in self.punto_set.all()]


class Punto(models.Model):
    """
    Tupla (x,y)
    """
    x = models.FloatField()
    y = models.FloatField()
    poligono = models.ForeignKey(Poligono)

    class Meta:
        ordering = ('-id',)

    def __unicode__(self):
        return u"%s (%s, %s)" % (self.poligono, self.x, self.y)

    def stringWithDecimalPresicion(self, numDecimals, xFactor=1, yFactor=1):
        """
        retorna el string de las coordenas con el numero de decimales igual a 
        numDecimals, sin redondear
        """
        decimals = numDecimals+10;
        base = pow(10,decimals)
        format  = '%.'+str(decimals)+'f'
        return format % (float(int(self.x*xFactor*base))/base),\
format % (float(int(self.y*yFactor*base))/base)

    def coordinates(self, integer=False, xFactor=1, yFactor=1,
                    stringPresicion=False, numDecimals=2):
        """
        si integer = True, retorna las coordenadas en enteros, esto es de uso 
        exclusivo de la herramienta para dibujar en los planos
        si integer = False, retorna las coordenadas flotantes
        multiplica las coordenadas por los factores
        si stringPresicion = True, retorna las coordenadas pero en 
        formato string y con un numero de decimales igual a numDecimals
        """
        if integer:
            return int(self.x*xFactor), int(self.y*yFactor)
        if stringPresicion:
            #return self.stringWithDecimalPresicion(numDecimals,xFactor,yFactor)
            return (self.x*xFactor).__repr__(), (self.y*yFactor).__repr__()
        return self.x*xFactor, self.y*yFactor


class SitioFuente(models.Model):
    """
    URL, logo y nombre de una fuente de información
    """
    def get_photo_path(self, filename):
        return u'fotos/%s' % highlyRandomName(filename)

    titulo = models.CharField(_(u"Título"), max_length=50)
    url = models.URLField(_(u"Web"), blank=True, null=True)
    logo = ImageWithThumbnailsField(
        _(u'Logo'),
        upload_to=get_photo_path,
        generate_on_save=True,
        thumbnail={'size': (17, 17), 'options': ['upscale']},
    )

    def __unicode__(self):
        return u"%s" % self.titulo

    def get_logo(self):
        """
        Devuelve el logo como un link a la fuente
        """
        return u"<a href='%s' title='%s' target='_blank'>%s</a>" % \
               (self.url, self.titulo, self.logo.thumbnail_tag)


class Fuente(models.Model):
    """
    URL específica con un texto descriptivo dentro del Sitio Fuente
    """
    sitio_fuente = models.ForeignKey(SitioFuente,
                                     verbose_name= _(u"Sitio Fuente"))
    descripcion = models.CharField(_(u"Descripción"), max_length=250)
    url = models.URLField(_(u"Web"), blank=True, null=True)

    def __unicode__(self):
        return u"%s: %s" % (self.sitio_fuente, self.descripcion)

    def get_cita(self):
        """
        Retorna la cita que se pondrá al final del artículo
        """
        if self.url:
            return u"Fuente: <a href='%s'  target='_blank'>%s, %s</a> %s" % \
                   (self.url, self.sitio_fuente, self.descripcion,
                    self.sitio_fuente.get_logo())
        else:
            return u"Fuente: %s, %s %s" % (self.sitio_fuente, self.descripcion,
                                           self.sitio_fuente.get_logo())
