# -*- coding: utf-8 -*-

from django.contrib import admin, messages
from django.db.models.query_utils import Q
from django.http import HttpResponseRedirect, HttpResponse
from django.conf.urls.defaults import patterns, url
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.db import models, transaction
from forms import AdminClienteForm, AdminAdminComercialForm, AdminRespuestaForm,\
AdminAdminHelpDeskForm, AdminAdminInformacionForm
from proyectos.forms import AdminFonoFormSet, AdminDeleteTelefonoForm
from models import Cliente, AdminComercial, Corredor, AdminInformacion,\
AdminHelpDesk, MensajeFormularioContacto, Solicitud
from proyectos.models import Item
from usuarios.forms import AdminSolicitudForm
from usuarios.models import CambioEstadoItem


class AdminComercialAdmin(admin.ModelAdmin):
    list_display = ('fullName', 'is_active',)
    actions = ('desactivar_administradores', 'activar_administradores')

    def get_actions(self, request):
        """
        funcion that disables some admins actions in this model
        """
        actions = super(self.__class__, self).get_actions(request)
        del actions['delete_selected']
        return actions    

    def desactivar_administradores(self, request, queryset):
        """
        desactiva a los usuarios seleccionados excepto a si mismo
        """
        msg2 = u''
        if queryset.filter(id=request.user.admincomercial.id):
            msg2 = u'Recuerde que no puede desactivar su propia cuenta.'
            messages.warning(request, msg2)
        if queryset.count() > 1:
            msg = u'Los admnistradores comerciales fueron desactivados'
        else:
            if msg2:
                msg=u''
            else:
                msg = u'El administrador comercial fue desactivado'
        for c in queryset.exclude(id=request.user.admincomercial.id):
            c.deactivate_user()
        self.message_user(request, msg)
    desactivar_administradores.short_description = 'Desactivar administradores \
comerciales seleccionados'

    def activar_administradores(self, request, queryset):
        """
        activa a los usuario seleccionados
        """
        if queryset.count() > 1:
            msg = u'Los administradores comerciales fueron activados'
        else:
            msg = u'El administrador comercial fue activado'
        for c in queryset:
            c.activate_user()
        self.message_user(request, msg)
    activar_administradores.short_description = 'Activar administradores \
comerciales seleccionados'

    def get_urls(self):
        urls = super(self.__class__, self).get_urls()
        my_urls = patterns(
            '',
            url(r'^add/$', self.admin_site.admin_view(self.adminComercial_add),
                name='admin_admincomercial_add'),
            url(r'^(?P<admincomercial_id>\d+)/$', 
                self.admin_site.admin_view(self.adminComercial_add),
                name='admin_admincomercial_edit'),
            )
        return my_urls + urls

    def adminComercial_add(self, request, admincomercial_id=''):
        """
        muestra la pagina para agregar o editar un administrador comercial
        """
        created = edit = can_assign_projects = False
        if request.user.is_superuser:
            can_assign_projects = True
        else:
            try:
                can_assign_projects =  request.user.admincomercial.\
asignar_proyectos
            except AdminComercial.DoesNotExist: 
                pass
        if admincomercial_id:
            a=get_object_or_404(AdminComercial, id=admincomercial_id)
            created = edit = True
            form = AdminAdminComercialForm().init(a)
        else:
            form = AdminAdminComercialForm()
        if request.method == 'POST':
            form = AdminAdminComercialForm(request.POST)
            if form.is_valid():
                a=form.save()
                if admincomercial_id:
                    msg = u'Los datos del administrador comercial fueron \
actualizados'
                else:
                    msg = u'El administrador comercial fue agregado con éxito'
                self.message_user(request, msg)
                if '_save' in form.data:
                    return HttpResponseRedirect('../')
                if '_addanother' in form.data:
                    return HttpResponseRedirect(
                        reverse('admin:admin_admincomercial_add'))
                if '_continue' in form.data:
                    created = True
                    admincomercial_id = a.id
                    form = AdminAdminComercialForm().init(a)
        return render_to_response(
            'admin/usuarios/admincomercial/change_form.html',
            {'form':form, 'admincomercial_id':admincomercial_id,
             'can_assign_projects':can_assign_projects,},
            context_instance=RequestContext(request))


class AdminInformacionAdmin(admin.ModelAdmin):
    list_display = ('fullName', 'is_active',)
    actions = ('desactivar_administradores', 'activar_administradores')

    def get_actions(self, request):
        """
        funcion that disables some admins actions in this model
        """
        actions = super(self.__class__, self).get_actions(request)
        del actions['delete_selected']
        return actions    

    def desactivar_administradores(self, request, queryset):
        """
        desactiva a los usuarios seleccionados
        """
        if queryset.count() > 1:
            msg = u'Los admnistradores de información fueron desactivados'
        else:
            msg = u'El administrador de información fue desactivado'
        for c in queryset:
            c.deactivate_user()
        self.message_user(request, msg)
    desactivar_administradores.short_description = u'Desactivar administradores\
 de información seleccionados'

    def activar_administradores(self, request, queryset):
        """
        activa a los usuarios seleccionados
        """
        if queryset.count() > 1:
            msg = u'Los administradores de información fueron activados'
        else:
            msg = u'El administrador de información fue activado'
        for c in queryset:
            c.activate_user()
        self.message_user(request, msg)
    activar_administradores.short_description = u'Activar administradores \
de información seleccionados'

    def get_urls(self):
        urls = super(self.__class__, self).get_urls()
        my_urls = patterns(
            '',
            url(r'^add/$', self.admin_site.admin_view(self.adminInformacion_add),
                name='admin_admininformacion_add'),
            url(r'^(?P<admininformacion_id>\d+)/$', 
                self.admin_site.admin_view(self.adminInformacion_add),
                name='admin_admininformacion_edit'),
            )
        return my_urls + urls

    def adminInformacion_add(self, request, admininformacion_id=''):
        """
        muestra la pagina para agregar o editar un administrador de Informacion
        """
        created = edit = can_assign_projects = False
        if admininformacion_id:
            a=get_object_or_404(AdminInformacion, id=admininformacion_id)
            created = edit = True
            if request.user.is_superuser:
                can_assign_projects = True
            else:
                if request.user.admincomercial:
                    can_assign_projects =  request.user.admincomercial.\
asignar_proyectos
#                 elif request.user.admininformacion:
#                     can_assign_projects =  request.user.admininformacion.\
# asignar_proyectos                                
            form = AdminAdminInformacionForm().init(a)
        else:
            form = AdminAdminInformacionForm()
        if request.method == 'POST':
            form = AdminAdminInformacionForm(request.POST)
            if form.is_valid():
                a=form.save()
                if admininformacion_id:
                    msg = u'Los datos del administrador de información fueron \
actualizados'
                else:
                    msg = u'El administrador de información fue agregado con éxito'
                self.message_user(request, msg)
                if '_save' in form.data:
                    return HttpResponseRedirect('../')
                if '_addanother' in form.data:
                    return HttpResponseRedirect(
                        reverse('admin:admin_admininformacion_add'))
                if '_continue' in form.data:
                    created = True
                    admininformacion_id = a.id
                    form = AdminAdminInformacionForm().init(a)
        return render_to_response(
            'admin/usuarios/admininformacion/change_form.html',
            {'form':form, 'admininformacion_id':admininformacion_id,
             'can_assign_projects':can_assign_projects},
            context_instance=RequestContext(request))



class AdminHelpDeskAdmin(admin.ModelAdmin):
    list_display = ('fullName', 'is_active',)
    actions = ('desactivar_administradores', 'activar_administradores')

    def get_actions(self, request):
        """
        funcion that disables some admins actions in this model
        """
        actions = super(self.__class__, self).get_actions(request)
        del actions['delete_selected']
        return actions    

    def desactivar_administradores(self, request, queryset):
        """
        desactiva a los usuarios seleccionados
        """
        if queryset.count() > 1:
            msg = u'Los admnistradores de Help Desk fueron desactivados'
        else:
            msg = u'El administrador de Help Desk fue desactivado'
        for c in queryset:
            c.deactivate_user()
        self.message_user(request, msg)
    desactivar_administradores.short_description = u'Desactivar administradores\
 de Help Desk seleccionados'

    def activar_administradores(self, request, queryset):
        """
        activa a los usuarios seleccionados
        """
        if queryset.count() > 1:
            msg = u'Los administradores de Help Desk fueron activados'
        else:
            msg = u'El administrador de Help Desk fue activado'
        for c in queryset:
            c.activate_user()
        self.message_user(request, msg)
    activar_administradores.short_description = u'Activar administradores \
de Help Desk seleccionados'

    def get_urls(self):
        urls = super(self.__class__, self).get_urls()
        my_urls = patterns(
            '',
            url(r'^add/$', self.admin_site.admin_view(self.adminHelpDesk_add),
                name='admin_adminhelpdesk_add'),
            url(r'^(?P<adminhelpdesk_id>\d+)/$', 
                self.admin_site.admin_view(self.adminHelpDesk_add),
                name='admin_adminhelpdesk_edit'),
            )
        return my_urls + urls

    def adminHelpDesk_add(self, request, adminhelpdesk_id=''):
        """
        muestra la pagina para agregar o editar un administrador help desk
        """
        created = edit =False
        if adminhelpdesk_id:
            a=get_object_or_404(AdminHelpDesk, id=adminhelpdesk_id)
            created = edit = True
            form = AdminAdminHelpDeskForm().init(a)
        else:
            form = AdminAdminHelpDeskForm()
        if request.method == 'POST':
            form = AdminAdminHelpDeskForm(request.POST)
            if form.is_valid():
                a=form.save()
                if adminhelpdesk_id:
                    msg = u'Los datos del administrador Help Desk fueron \
actualizados'
                else:
                    msg = u'El administrador Help Desk fue agregado con éxito'
                self.message_user(request, msg)
                if '_save' in form.data:
                    return HttpResponseRedirect('../')
                if '_addanother' in form.data:
                    return HttpResponseRedirect(
                        reverse('admin:admin_adminhelpdesk_add'))
                if '_continue' in form.data:
                    created = True
                    adminhelpdesk_id = a.id
                    form = AdminAdminComercialForm().init(a)
        return render_to_response(
            'admin/usuarios/adminhelpdesk/change_form.html',
            {'form':form, 'adminhelpdesk_id':adminhelpdesk_id,},
            context_instance=RequestContext(request))


class ClienteAdmin(admin.ModelAdmin):
    list_display = ('fullName', 'is_active','tipo', 'departamento', 
                    'provincia', 'corredor')
    search_fields = ('^usuario__first_name', '^usuario__last_name',)
    list_editable = ('tipo',)
    list_filter = ('usuario__is_active','tipo','provincia__departamento')
    actions = ('desactivar_clientes', 'activar_clientes',)

    def get_actions(self, request):
        """
        funcion that disables some admins actions in this model
        """
        actions = super(self.__class__, self).get_actions(request)
        del actions['delete_selected']
        return actions    

    def desactivar_clientes(self, request, queryset):
        """
        desactiva a los usuario seleccionados
        """
        if queryset.count() > 1:
            msg = u'Los clientes fueron desactivados'
        else:
            msg = u'El cliente fue desactivado'
        for c in queryset:
            c.deactivate_user()
        self.message_user(request, msg)
    desactivar_clientes.short_description = 'Desactivar clientes seleccionados'

    def activar_clientes(self, request, queryset):
        """
        desactiva a los usuario seleccionados
        """
        if queryset.count() > 1:
            msg = u'Los clientes fueron activados'
        else:
            msg = u'El cliente fue activado'
        for c in queryset:
            c.activate_user()
        self.message_user(request, msg)
    activar_clientes.short_description = 'Activar clientes seleccionados'

    def get_urls(self):
        urls = super(self.__class__, self).get_urls()
        my_urls = patterns(
            '',
            url(r'^add/$', self.admin_site.admin_view(self.cliente_add),
                name='admin_cliente_add'),
            url(r'^(?P<cliente_id>\d+)/$', 
                self.admin_site.admin_view(self.cliente_add),
                name='admin_cliente_edit'),
            url(r'^add_fonos/(?P<cliente_id>\d+)/$',
                self.admin_site.admin_view(self.add_telefonos),
                name='admin_cliente_add_telefonos'),
            )
        return my_urls + urls

    def cliente_add(self, request, cliente_id=''):
        """
        muestra la pagina para agregar o editar un cliente
        """
        created = edit =False
        if '_popup' in request.GET:
            is_popup = True
        else:
            is_popup = False
        if cliente_id:
            a=get_object_or_404(Cliente, id=cliente_id)
            created = edit = True
            form = AdminClienteForm().init(a)
        else:
            form = AdminClienteForm()
        if request.method == 'POST':
            form = AdminClienteForm(request.POST)
            if form.is_valid():
                a=form.save()
                if '_popup' in request.GET:
                    return HttpResponse('<script type="text/javascript">\
window.opener.location.href = window.opener.location.href; window.close();\
</script>')
                if cliente_id:
                    msg = u'Los datos del cliente fueron actualizados'
                else:
                    msg = u'El cliente fue agregado con éxito'
                self.message_user(request, msg)
                if '_save' in form.data:
                    return HttpResponseRedirect('../')
                if '_addanother' in form.data:
                    return HttpResponseRedirect('')
                if '_continue' in form.data:
                    created = True
                    cliente_id = a.id
                    form = AdminClienteForm().init(a)
        return render_to_response(
            'admin/usuarios/cliente/change_form.html',
            {'form':form, 'created':created, 'cliente_id':cliente_id,
             'edit':edit, 'is_popup':is_popup},
            context_instance=RequestContext(request))

    def add_telefonos(self, request, cliente_id=''):
        """
        página que muestra la herramienta para editar los teléfonos de contacto
        """
        fonoList = ''
        numFonos = 0
        addFonoSuccess = delFono = False
        formset = AdminFonoFormSet()
        if cliente_id:
            p= get_object_or_404(Cliente, id=cliente_id)
            fonoList = p.telefonos.iterator()
            numFonos = p.telefonos.count()
        if request.method == 'POST':
            if 'save' in request.POST:
                formset = AdminFonoFormSet(request.POST)
                if formset.is_valid():
                    formset.save(p)
                    formset = AdminFonoFormSet()
                    addFonoSuccess = True
                    fonoList = p.telefonos.iterator()
                    numFonos = p.telefonos.count()
            else:
                delForm = AdminDeleteTelefonoForm(request.POST)
                if delForm.is_valid():
                    delForm.save()
                    delFono = True
                    fonoList = p.telefonos.iterator()
                    numFonos = p.telefonos.count()
        return render_to_response(
            'admin/usuarios/cliente/add_telefono.html',
            {'fonoList':fonoList, 'formset':formset, 
             'addFonoSuccess': addFonoSuccess, 'numFonos':numFonos, 
             'delFono':delFono,},
            context_instance=RequestContext(request))


# class CorredorAdmin(admin.ModelAdmin):
#     pass


class MensajeFormularioContactoAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'proyecto', 'fecha', 'respondido',)
    list_display_links = ('cliente', 'proyecto', 'fecha', 'respondido',)
    list_filter = ('cliente', 'proyecto',)
    actions = ['mark_as_answered',]

    def queryset(self, request):
        """
        solo los super usuarios tienen acceso a todos mensajes del formulario 
        de contacto de todo los proyectos, los demas usuarios solo tendran
        acceso a los mensajes del formulario de contacto de los
        proyectos donde estan asociados ó aquellos que no están relacionados 
        a ningún rubro
        """
        qs = super(self.__class__, self).queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(Q(proyecto__usuarios__id=request.user.id) | \
Q(proyecto__isnull=True))

    def get_actions(self, request):
        """
        funcion that disables some admins actions in this model
        """
        actions = super(self.__class__, self).get_actions(request)
        del actions['delete_selected']
        return actions    

    def mark_as_answered(self, request, queryset):
        """
        marks as answered all the messages selected only if they haven't been 
        answered
        """
        for m in queryset:
            m.mark_as_answered(request.user)
        if queryset.count() > 1:
            resulting_message =  u'Los mensajes fueron marcados como respondidos'
        else:
            resulting_message = u'El mensaje fue marcado como respondido.'
        self.message_user(request, resulting_message)
    mark_as_answered.short_description = u'Marcar como respondidos'

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

    # def has_delete_permission(self, request, obj=''):
    #     """
    #     evita que se puedan borrar objectos desde el edit o add view
    #     """
    #     return False

    def change_view(self, request, object_id, extra_context=None):
        """
        pagina que muestra el mensaje enviado, las respuestas enviadas y un 
        formulario para enviar mas respuestas
        """
        message = get_object_or_404( MensajeFormularioContacto, id = object_id )
        rptas = message.respuesta_set.all()
        form = AdminRespuestaForm()
        if request.method == 'POST':
            form = AdminRespuestaForm(request.POST)
            if form.is_valid():
                form.save(request.user, object_id)
                self.message_user(request, u'El mensaje fue enviado con éxito')
                return HttpResponseRedirect(reverse(
                        'admin:usuarios_mensajeformulariocontacto_changelist'))
        return render_to_response(
            'admin/usuarios/mensajeformulariocontacto/change_form.html',
            {'message':message, 'rptas':rptas, 'form':form},
            context_instance=RequestContext(request))


class SolicitudAdmin(admin.ModelAdmin):
    """
    Clase para el admin de Solicitud de separación de un item
    """
    form = AdminSolicitudForm
    list_display = ('proyecto', 'item_numero', 'cliente', 'tipo_item', 'tipo',
                    'estado','fecha_emision', 'fecha_cierre')
    list_display_links = ('proyecto', 'item_numero', 'cliente', 'tipo_item',
                          'tipo', 'estado', 'fecha_emision', 'fecha_cierre')
    list_filter = ('tipo', 'estado', 'proyecto',)
    readonly_fields = ("cliente", "tipo", "proyecto", "plano", "tipo_item",
                       "item_numero")
    ordering = ["-id"]

    @transaction.commit_manually
    def save_model(self, request, obj, form, change):
        """
        La acción define el estado del item y de la solicitud
        """
        item = form.cleaned_data["item"]
        if form.cleaned_data["accion"] == u"R":
            obj.rechazar(request)
        else:
            if obj.tipo == u"S":
                if form.cleaned_data["accion"] == u"S":
                    obj.tramitar(request)
                elif form.cleaned_data["accion"] == u"V":
                    obj.tramitado(request)
                solicitudes = Solicitud.objects.filter(
                    Q(estado=u"E")|Q(estado=u"T"), item=item).exclude(id=obj.id)
                for solicitud in solicitudes:
                    solicitud.rechazar(request)
            else:
                obj.tramitado(request)
        solicitud_db = Solicitud.objects.get(id=obj.id)
        item_db = Item.objects.get(id=item.id)
        if obj.estado == solicitud_db.estado and item.estado == item_db.estado:
            transaction.commit()
        else:
            transaction.rollback()
            messages.error(request, u"Otro administrador ha cambiado el estado \
                de la solicitud en este momento, sus cambios se descartaron")

    def changelist_view(self, request, extra_context=None):
        """
        Manda por defecto la vista aplicando el filtro para mostrar las
        solicitudes en espera
        """
        if not request.GET.has_key('estado__exact'):
            q = request.GET.copy()
            q['estado__exact'] = u'E'
            q['tipo__exact'] = u'S'
            request.GET = q
            request.META['QUERY_STRING'] = request.GET.urlencode()

        return super(self.__class__, self).changelist_view(request,
            extra_context=extra_context)

    def queryset(self, request):
        """
        solo los super usuarios tienen acceso a todos mensajes del formulario 
        de contacto de todo los proyectos, los demas usuarios solo tendran
        acceso a los mensajes del formulario de contacto de los
        proyectos donde estan asociados
        """
        qs = super(self.__class__, self).queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(proyecto__usuarios__id=request.user.id)

    def get_actions(self, request):
        """
        funcion that disables some admins actions in this model
        """
        actions = super(self.__class__, self).get_actions(request)
        del actions['delete_selected']
        return actions    

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


class CambioEstadoItemAdmin(admin.ModelAdmin):
    """
    Clase para el admin de cambio de estado de un Item
    """
    list_display = ('item', 'estado', 'cliente', 'fecha',)
    list_filter = ('estado', 'item',)
    ordering = ["-fecha"]
    readonly_fields = ("fecha", "estado", "admin", "item", "solicitud",
                       "cliente",)

    def get_actions(self, request):
        """
        funcion that disables some admins actions in this model
        """
        actions = super(self.__class__, self).get_actions(request)
        del actions['delete_selected']
        return actions    

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

    def has_delete_permission(self, request, obj=''):
        """
        evita que se puedan borrar objectos desde el edit o add view
        """
        return False



admin.site.register(AdminComercial, AdminComercialAdmin)
admin.site.register(AdminInformacion, AdminInformacionAdmin)
admin.site.register(AdminHelpDesk, AdminHelpDeskAdmin)
admin.site.register(Cliente, ClienteAdmin)
# admin.site.register(Corredor, CorredorAdmin)
admin.site.register(MensajeFormularioContacto, MensajeFormularioContactoAdmin)
admin.site.register(Solicitud, SolicitudAdmin)
admin.site.register(CambioEstadoItem, CambioEstadoItemAdmin)
