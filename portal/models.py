# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.flatpages.models import FlatPage
from django.contrib.sites.models import Site
from common.utils import highlyRandomName
from django.contrib.sitemaps import ping_google
from sorl.thumbnail.fields import ImageWithThumbnailsField


class Faq(models.Model):
    """
    Pregunta y su respuesta, para las preguntas frecuentes o FAQ
    """
    pregunta = models.CharField(_(u"pregunta"), max_length=300)
    respuesta = models.TextField(_(u"respuesta"))

    class Meta:
        verbose_name = _(u"FAQ")
        ordering = ('-id',)

    def __unicode__(self):
        return u"%s" % self.pregunta

    def create_update_flatPage(self):
        """
        crea o actualiza el flatpage '/faqs/'
        """
        c = '<ol>%s</ol>' % ''.join('<li><h2>%s</h2><p>%s</p></li>' % (
                f.pregunta,f.respuesta) for f in Faq.objects.order_by('id'))
        #ToDo: hay que cambiar el template_name al verdadero template que se 
        #va usar
        #cuadno se sepa que preguntas frecuentes habran crearle sus fixtures
        obj, created = FlatPage.objects.get_or_create(
            url='/faqs/', title='Preguntas Frecuentes',
            template_name='flatpages/default.html',)
        obj.content = c
        obj.sites.add(Site.objects.get(id=1))
        obj.save()

    def save(self, *args, **kwargs):
        """
        ademas de guardar el objecto, crea o actualiza el flatpage /faqs/ de
        preguntas frecuentes
        """
        super(self.__class__, self).save()
        Faq().create_update_flatPage()
        try:
            ping_google()
        except Exception:
            pass

    def delete(self, *args, **kwargs):
        """
        ademas de eliminar el objeto, actualiza el flatpage '/faqs/' de 
        preguntas frecuentes
        """
        super(self.__class__, self).delete()
        Faq().create_update_flatPage()        


class Inmobiliaria(models.Model):
    """
    Datos de la inmobiliaria
    """
    nombre = models.CharField(_('nombre'), max_length=150, unique=True)
    link_facebook = models.URLField(verify_exists=True)
    link_twitter = models.URLField(verify_exists=True)

    def get_inmobiliaria_path(self, filename):
        return u'inmobiliaria/%s' % highlyRandomName(filename)

    logo = ImageWithThumbnailsField(
        _(u'logo'),
        upload_to=get_inmobiliaria_path,
        generate_on_save=True,
        thumbnail={'size': (100, 100), 'options': ['crop', 'upscale']},
        extra_thumbnails={
            'small': {'size': (25, 25), 'options': ['crop', 'upscale']},
            'big': {'size': (400, 400), 'options': ['crop', 'upscale']},
            #'pdf_size' : {'size': (454, 262), 'options': ['upscale']},
            'pdf_size': {'size': (300,90), 'options': ['upscale'], 
                         'quality':100,},
        }
    )
    logo_watermark = ImageWithThumbnailsField(
        _(u'marca de agua'),
        upload_to=get_inmobiliaria_path,
        generate_on_save=True,
        thumbnail={'size': (100, 100), 'options': ['upscale'], 
                   'extension':'PNG'},
        extra_thumbnails={
            #'small': {'size': (25, 25), 'options': ['crop', 'upscale']},
            'big': {'size': (400, 400), 'options': ['upscale'],
                    'extension': 'PNG'},
        }
    )
    introduccion = models.TextField(_(u"introducción"), blank=True, null=True)
    mision = models.TextField(_(u"misión"), blank=True, null=True)
    vision = models.TextField(_(u"visión"), blank=True, null=True)
    historia = models.TextField(_(u"historia"), blank=True, null=True)
    desarrollados = models.TextField(_(u"proyectos desarrollados"), blank=True,
                                     null=True)

    class Meta:
        verbose_name = _(u"Inmobiliaria")
        verbose_name_plural = _(u"Inmobiliarias")

    def __unicode__(self):
        return "%s" % self.nombre

    def save(self, *args, **kwargs):
        """
        Guarda una sola instancia de la inmobiliaria
        """
        try:
            Inmobiliaria.objects.latest("id").delete()
        except Inmobiliaria.DoesNotExist:
            pass
        try:
            ping_google()
        except Exception:
            pass

        return super(Inmobiliaria, self).save(*args, **kwargs)

    @models.permalink
    def get_absolute_url(self):
        """
        Devuelve la url del perfil público de la inmobiliaria
        """
        return 'portal.views.nosotros', ()


class Area(models.Model):
    """
    Datos de un área de servicio de la inmobiliaria
    """
    nombre = models.CharField(_(u"nombre"), max_length=150)
    descripcion = models.TextField(_(u"descripción"), blank=True, null=True)
    inmobiliaria = models.ForeignKey(Inmobiliaria,
                                     verbose_name=_(u'Inmobiliaria'))

    def __unicode__(self):
        return u"%s (%s)" % (self.nombre, self.descripcion)