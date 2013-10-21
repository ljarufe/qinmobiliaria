# -*- coding: utf-8 -*-
from common.models import Fuente, SitioFuente

from models import Referencia, TipoTelefono#, Telefono, Foto, Video
from django.contrib import admin, messages
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404

class ReferenciaAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        """
        evita que se puedan agregar elementos a este modelo
        """
        return False

        # def has_change_permission(self, request):
        #     """
        #     evita que se puedan agregar elementos a este modelo
        #     """
        #     return False


# class TelefonoAdmin(admin.ModelAdmin):
#     pass

class TipoTelefonoAdmin(admin.ModelAdmin):
    actions = ('borrar_tipotelefonos',)

    def get_actions(self, request):
        """
        funcion that disables some admins actions in this model
        """
        actions = super(self.__class__, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def borrar_tipotelefonos(self, request, queryset):
        """
        borra los tipos de telefonos seleccionados solo si no estan
        asociados a un telefono
        """
        deleted=''
        nonDeleted=''
        for f in queryset:
            if not f.telefono_set.all():
                f.delete()
                deleted+=f.nombre+', '
            else:
                nonDeleted+=f.nombre+', '
        if deleted:
            deleted = deleted[:-2]
            msg1 = u'Se eliminaron los siguientes tipo de teléfono: %s.' %\
                   deleted
            self.message_user(request, msg1)
        if nonDeleted:
            msg2 = u'Recuerde que sólo se pueden eliminar los tipos de teléfono \
que no estén asociados a ningún número telefónico.'
            messages.warning(request,msg2)
            nonDeleted = nonDeleted[:-2]
            msg3 = u'Los siguientes tipos de teléfono no fueron eliminados: %s.'\
            % nonDeleted
            messages.error(request,msg3)

    borrar_tipotelefonos.short_description = u'Borrar teléfonos seleccionados'

    def delete_view(self, request, object_id, extra_context=None):
        """

        """
        obj = get_object_or_404(TipoTelefono, id=object_id)
        if not obj.telefono_set.all():
            obj.delete()
            msg1 = u'Se eliminó el tipo de teléfono.'
            self.message_user(request, msg1)
            return HttpResponseRedirect(
                reverse('admin:common_tipotelefono_changelist'))
        else:
            msg2 = u'Recuerde que sólo se pueden eliminar los tipos de teléfono \
que no estén asociados a ningún número telefónico.'
            messages.warning(request,msg2)
            msg3 = u'El tipo de teléfono no fue eliminado.'
            messages.error(request,msg3)
            return HttpResponseRedirect(
                reverse('admin:common_tipotelefono_change', args=(object_id,)))


# class FotoAdmin(admin.ModelAdmin):
#     pass

# class VideoAdmin(admin.ModelAdmin):
#     pass

admin.site.register(Referencia, ReferenciaAdmin)
admin.site.register(Fuente)
admin.site.register(SitioFuente)
admin.site.register(TipoTelefono, TipoTelefonoAdmin)
# admin.site.register(Telefono, TelefonoAdmin)
# admin.site.register(Foto, FotoAdmin)
# admin.site.register(Video, VideoAdmin)
