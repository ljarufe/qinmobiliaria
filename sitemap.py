# -*- coding: utf-8 -*-

from django.contrib.sitemaps import Sitemap
from portal.models import Faq, Inmobiliaria
from proyectos.models import Rubro, Proyecto, Oferta, Avance


class FaqSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return Faq.objects.all()


class InmobiliariaSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.1

    def items(self):
        return Inmobiliaria.objects.all()


class RubroSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Rubro.objects.all()


class ProyectoSitemap(Sitemap):
    changefreq = "always"
    priority = 1.0

    def items(self):
        return Proyecto.accepted.all()

    def lastmod(self, obj):
        return obj.fecha_inicio