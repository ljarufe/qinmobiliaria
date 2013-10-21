# -*- coding: utf-8 -*-

from django.contrib import admin
from models import Inmobiliaria, Faq
from portal.forms import InmobiliariaForm
from portal.models import Area


class InmobiliariaAdmin(admin.ModelAdmin):
    """
    Admin para el modelo de la inmobiliaria
    """
    form = InmobiliariaForm

    def has_add_permission(self, request):
        """
        evita que se puedan agregar elementos a este modelo
        """
        return False

    def has_delete_permission(self, request, obj=''):
        """
        evita que se puedan borrar objectos desde el edit o add view
        """
        return False

    def get_actions(self, request):
        """
        function that disables some admins actions in this model
        """
        actions = super(self.__class__, self).get_actions(request)
        del actions['delete_selected']

        return actions
    

class FaqAdmin(admin.ModelAdmin):
    actions = ('borrar_faqs',)

    def delete_model(self, request, obj):
        """
        borra la pregunta usando el delete de su modelo
        """
        obj.delete()

    def get_actions(self, request):
        """
        funcion that disables some admins actions in this model
        """
        actions = super(self.__class__, self).get_actions(request)
        del actions['delete_selected']

        return actions    

    def borrar_faqs(self, request, queryset):
        """
        borra los rubros seleccionados sí y sólo si no tiene proyectos 
        asociados, si es así dis-asocia todos los clientes del rubro antes
        de eliminarlo
        """
        if queryset.count() > 1:
            msg = u'Las preguntas fueron borradas'
        else:
            msg = u'La pregunta fue borrada'
        for f in queryset:
            f.delete()
        self.message_user(request, msg)
    borrar_faqs.short_description = 'Borrar preguntas seleccionadas'


admin.site.register(Inmobiliaria, InmobiliariaAdmin)
admin.site.register(Faq, FaqAdmin)
admin.site.register(Area)