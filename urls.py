# -*- coding: utf-8 -*-

from django.contrib.sitemaps import FlatPageSitemap
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.defaults import patterns, include, url
from os.path import dirname
from django.contrib import admin
from sitemap import *
from zinnia.sitemaps import TagSitemap
from zinnia.sitemaps import EntrySitemap
from zinnia.sitemaps import CategorySitemap

sitemaps = {
    'flatpages': FlatPageSitemap,
    'inmobiliarias': InmobiliariaSitemap,
    'rubros': RubroSitemap,
    'proyectos': ProyectoSitemap,
    'tags': TagSitemap,
    'entries': EntrySitemap,
    'categories': CategorySitemap,
}

admin.autodiscover()

basedir = dirname(__file__)
media = '%s/public/media/' % basedir
static = '%s/public/static/' % basedir

urlpatterns = patterns('',
    # Sitemap
    (r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap',
        {'sitemaps': sitemaps}),
    (r'^sitemap-(?P<section>.+)\.xml$', 'django.contrib.sitemaps.views.sitemap',
         {'sitemaps': sitemaps}),
    # Mensajes
    url(r'^comments/', include('django.contrib.comments.urls')),
    url(r'^send_message/$', 'common.chat_server.send_message',
        name="send_message"),
    url(r'^manager_request/$', 'common.chat_server.manager_request',
        name='manager_request'),
    # Admin
    url(r'^admin/', include(admin.site.urls)),
    # Media y static
    (r'^media/(?P<path>.*)$','django.views.static.serve',
         {'document_root': media,'show_indexes': True}),
    (r'^static/(?P<path>.*)$','django.views.static.serve',
         {'document_root': static,'show_indexes': True}),
    # Apps
    (r'^proyectos/', include('proyectos.urls')),
    (r'^usuarios/', include('usuarios.urls')),
    (r'^noticias/', include('zinnia.urls')),
    (r'^tinymce/', include('tinymce.urls')),
    (r'^', include('portal.urls')),
)

urlpatterns += staticfiles_urlpatterns()

urlpatterns+= patterns('django.contrib.flatpages.views',
    url(r'^faqs/$', 'flatpage', {'url': '/faqs/'}, name='faqs'),
)