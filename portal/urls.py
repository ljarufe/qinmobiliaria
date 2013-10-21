# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('portal.views',
                       url(r'^$',
                           'inicio',
                           name='inicio'),
                       url(r'^contacto/$',
                           'contacto',
                           name='contacto'),
                       url(r'^nosotros/$',
                           'nosotros',
                           name='nosotros'),
                       url(r'^ayuda_en_linea/(?P<id_area>\d+)/(?P<usuario>[\w.@+-]+)/$',
                           'ayuda_en_linea',
                           name='ayuda_en_linea'),
                       url(r'^ayuda_ubicacion/$',
                           "ayuda",
                           {"template": "portal/ayuda_ubicacion.html"},
                           name="ayuda_ubicacion"),
                       url(r'^ayuda_areas/$',
                           "ayuda",
                           {"template": "portal/ayuda_areas.html"},
                           name="ayuda_areas"),
                       url(r'^ayuda_suscripcion/$',
                           "ayuda",
                           {"template": "portal/ayuda_suscripcion.html"},
                           name="ayuda_suscripcion"),
                       url(r'^ayuda_separar/$',
                           "ayuda",
                           {"template": "portal/ayuda_separar.html"},
                           name="ayuda_separar"),
                       url(r'^iframes/chat/$',
                           'chat',
                           name='chat'),
                       url(r'^json_get_aviso/$',
                           'json_get_aviso',
                           name='json_get_aviso'),
                       # Google webmaster
                       url(r'^google4ee0c872608a0b7d.html/$',
                           'google_webmaster_verification', )
)

urlpatterns += patterns('proyectos.views',
                        url(r'^(?P<slug_proyecto>[\w]+)/etapas/$',
                            'etapas_proyecto',
                            name='etapas_proyecto'),
                        url(r'^(?P<slug_proyecto>[\w]+)/?$',
                            'perfil_proyecto',
                            name='perfil_proyecto')
)