# -*- coding: utf-8 -*-

from django.contrib import admin, messages
from django.http import HttpResponseRedirect, HttpResponse
from django.conf.urls.defaults import patterns, url
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.utils.safestring import SafeUnicode
from models import Rubro, Proyecto, Etapa, SubEtapa, Caracteristica,Plano, \
    Milestone, Avance, Oferta, TipoItem, TipoItemNombre, Item, Beneficio, \
    Desarrollado
from forms import AdminEtapaForm, AdminSubEtapaForm, AdminProyectoForm, \
    AdminUbicacionForm, AdminReferenciaForm, AdminFotoForm, \
    AdminDeleteFotoForm, AdminVideoForm, AdminDeleteVideoForm, \
    AdminCaracteristicaForm, AdminContactoForm, AdminFonoFormSet, \
    DesarrolladoAdminForm, AdminDeleteTelefonoForm, AdminMilestoneForm, \
    AdminAvanceForm, AdminOfertaForm, SendMail1, SendMail2, SendMail3, \
    AdminPlanoForm, AdminItemForm, AdminEditItemForm, AdminBeneficioForm, \
    AdminTipoItemForm
from common.utils import json_response
from common.models import Referencia, Foto, Video
from proyectos.models import Aviso
from usuarios.models import Cliente


class RubroAdmin(admin.ModelAdmin):
    list_display= ('nombre',)
    list_display_links = ('nombre',)
    actions = ['borrar_rubro']

    def delete_model(self, request, obj):
        """
        borra al rubro sí y sólo si no tiene proyectos asociados
        , si es así dis-asocia todos los clientes del rubro antes
        de eliminarlo        
        """
        Rubro().admin_borrar_rubro(Rubro.objects.filter(id=obj.id))

    def get_actions(self, request):
        """
        funcion that disables some admins actions in this model
        """
        actions = super(self.__class__, self).get_actions(request)
        del actions['delete_selected']
        return actions    

    def borrar_rubro(self, request, queryset):
        """
        borra los rubros seleccionados sí y sólo si no tiene proyectos 
        asociados, si es así dis-asocia todos los clientes del rubro antes
        de eliminarlo
        """
        resulting_message =  Rubro().admin_borrar_rubro(queryset)
        self.message_user(request, resulting_message)
    borrar_rubro.short_description = 'Borrar rubros seleccionados'


class ProyectoAdmin(admin.ModelAdmin):
    date_hierarchy = 'fecha_inicio'
    list_display = ('nombre', 'fecha_inicio', 'relevancia', 'estado', 
                    'departamento', 'provincia')
    list_editable = ('relevancia', 'estado')
    list_filter = ('relevancia','estado', 'provincia__departamento',)
    search_fields = ('nombre',)
    actions = ['actualizar_pdf', 'borrar_pdf', 'borrar_proyectos',]

    form = AdminProyectoForm

    def queryset(self, request):
        """
        solo los super usuarios tienen acceso a todos los proyectos
        los demas usuarios solo tendran acceso a los proyectos donde fueron
        asociados
        """
        qs = super(self.__class__, self).queryset(request)
        if request.user.is_superuser:
            return qs
        return request.user.proyecto_set.all()

    def get_actions(self, request):
        """
        funcion that disables some admins actions in this model
        """
        actions = super(self.__class__, self).get_actions(request)
        del actions['delete_selected']
        return actions    

    def borrar_proyectos(self, request, queryset):
        """
        borra los proyectos seleccionados asi como todos sus objetos relacionados
        """
        for proyecto in queryset:
            proyecto.delete()
        if queryset.count() > 1:
            msg = u'Los proyectos fueron eliminados.'
        else:
            msg = u'El proyecto fue eliminado.'
        self.message_user(request, msg)
    borrar_proyectos.short_description = 'Borrar proyectos seleccionados'

    def actualizar_pdf(self, request, queryset):
        """
        actualiza los pdf's de los proyectos seleccionados
        """
        #queryset[0].create_pdf()
        import threading, time
        for p in queryset:
            p.create_pdf()
            # t=threading.Thread(target=p.create_pdf())
            # t.start()
            # t.join()
            # while(t.is_alive()):
            #   A=1
        if queryset.count() > 1:
            resulting_message =  u'Los pdfs fueron actualizados'
        else:
            resulting_message =  u'El pdf fue actualizado'
        self.message_user(request, resulting_message)
    actualizar_pdf.short_description = 'Actualizar pdfs informativos'

    def borrar_pdf(self, request, queryset):
        """
        Borra los pdfs creados para lso proyectos seleccionados
        """
        for proyecto in queryset:
            proyecto.delete_pdf()
        if queryset.count() > 1:
            resulting_message =  u'Los pdfs fueron borrados'
        else:
            resulting_message =  u'El pdf fue borrado'
        self.message_user(request, resulting_message)
    borrar_pdf.short_description = "Borrar pdfs informativos"

    def get_urls(self):
        urls = super(self.__class__, self).get_urls()
        my_urls = patterns(
            '',
            url(r'^add/$', self.admin_site.admin_view(self.proyecto_add),
                name='admin_proyecto_add'),
            url(r'^location/(?P<proyecto_id>\d+)?$', 
                self.admin_site.admin_view(self.location),
                name='admin_proyecto_location'),
            url(r'^add_fotos/(?P<proyecto_id>\d+)?$', 
                self.admin_site.admin_view(self.add_fotos),
                name='admin_proyecto_add_fotos'),
            url(r'ajax_edit_foto/$', 
                self.admin_site.admin_view(self.ajax_edit_foto),
                name='admin_proyecto_ajax_edit_foto'),
            url(r'^add_videos/(?P<proyecto_id>\d+)?$', 
                self.admin_site.admin_view(self.add_videos),
                name='admin_proyecto_add_videos'),
            url(r'ajax_edit_video/$', 
                self.admin_site.admin_view(self.ajax_edit_video),
                name='admin_proyecto_ajax_edit_video'),
            url(r'^add_caracteristica/(?P<proyecto_id>\d+)?$', 
                self.admin_site.admin_view(self.add_caracteristica),
                name='admin_proyecto_add_caracteristica'),
            url(r'ajax_edit_caracteristica/$', 
                self.admin_site.admin_view(self.ajax_edit_caracteristica),
                name='admin_proyecto_ajax_edit_caracteristica'),
            url(r'ajax_delete_caracteristica/$', 
                self.admin_site.admin_view(self.ajax_delete_caracteristica),
                name='admin_proyecto_ajax_delete_caracteristica'),

            url(r'^add_beneficio/(?P<proyecto_id>\d+)?$', 
                self.admin_site.admin_view(self.add_beneficio),
                name='admin_proyecto_add_beneficio'),
            url(r'ajax_edit_beneficio/$', 
                self.admin_site.admin_view(self.ajax_edit_beneficio),
                name='admin_proyecto_ajax_edit_beneficio'),
            url(r'ajax_delete_beneficio/$', 
                self.admin_site.admin_view(self.ajax_delete_beneficio),
                name='admin_proyecto_ajax_delete_beneficio'),

            url(r'^add_contacto/(?P<proyecto_id>\d+)?$', 
                self.admin_site.admin_view(self.add_contacto),
                name='admin_proyecto_add_contacto'),
            url(r'^(?P<proyecto_id>\d+)/$', 
                self.admin_site.admin_view(self.proyecto_add),
                name='admin_proyecto_edit'),
            url(r'^send_email1/$', 
                self.admin_site.admin_view(self.send_email_to_user),
                name='admin_proyecto_send_mail_to_user'),
            url(r'^send_email2/$', 
                self.admin_site.admin_view(self.send_email_to_portalUser),
                name='admin_proyecto_send_mail_to_portalUser'),
            url(r'^send_email3/$', 
                self.admin_site.admin_view(self.send_email_to_admins),
                name='admin_proyecto_send_mail_to_admins'),
            url(r'^customers_export/(?P<compradores>\d+)/$', 
                self.admin_site.admin_view(self.customers_export),
                name='admin_proyecto_customers_export'),

            )

        return my_urls + urls

    def proyecto_add(self, request, proyecto_id=''):
        """
        muestra la página para agregar o editar un proyecto
        """
        created = edit =False
        if proyecto_id:
            p=get_object_or_404(Proyecto, id=proyecto_id)
            created = edit = True
            form = AdminProyectoForm(instance = p)
        else:
            form = AdminProyectoForm()
        if request.method == 'POST':
            form = AdminProyectoForm(request.POST, request.FILES)
            if form.is_valid():
                p=form.save(request.user)
                if proyecto_id:
                    msg = u'El proyecto fue actualizado'
                else:
                    msg = u'El proyecto fue agregado con éxito'
                self.message_user(request, msg)
                if '_save' in form.data:
                    return HttpResponseRedirect('../')
                if '_addanother' in form.data:
                    return HttpResponseRedirect('')
                if '_continue' in form.data:
                    created = True
                    proyecto_id = p.id
                    form = AdminProyectoForm(instance = p)
        return render_to_response(
            'admin/proyectos/proyecto/change_form.html',
            {'form':form, 'created':created, 'proyecto_id':proyecto_id,
             'edit':edit,},
            context_instance=RequestContext(request))
           
    def location(self, request, proyecto_id=''):
        """
        muestra el mapa y el formulario para la direccion y ubicación del 
        proyecto
        """
        success = successRef = showAddRef = False
        latitud = longitud = latitudRef = longitudRef =''
        formRef = AdminReferenciaForm()
        form = AdminUbicacionForm()
        if proyecto_id:
            p = get_object_or_404(Proyecto, id=proyecto_id)
            if p.latitud and p.longitud:
                showAddRef = True
                form = AdminUbicacionForm(initial={'direccion':p.direccion,
                                                   'latitud':p.latitud,
                                                   'longitud':p.longitud,
                                                   'provincia':p.provincia,
                                                   })                
                latitud = p.latitud
                longitud = p.longitud
        if request.method == 'POST':
            if 'localizacion' in request.POST:
                form = AdminUbicacionForm(request.POST)
                latitud = form.data['latitud']
                longitud = form.data['longitud']
                if form.is_valid():
                    form.save(proyecto_id)
                    success = showAddRef = True
            else:
                formRef = AdminReferenciaForm(request.POST, request.FILES)
                if formRef.is_valid():
                    formRef.save(proyecto_id)
                    successRef = True
                    formRef = AdminReferenciaForm()
                else:
                    latitudRef = formRef.data['latitud']
                    longitudRef = formRef.data['longitud']                    
        return render_to_response(
            'admin/proyectos/proyecto/location.html',
            {'form':form, 'success':success, 'latitud':latitud,
             'longitud':longitud, 'formRef':formRef, 'successRef':successRef,
             'latitudRef':latitudRef, 'longitudRef':longitudRef, 
             'refList':Referencia.objects.iterator(), 'showAddRef':showAddRef},
            context_instance=RequestContext(request))

    def add_fotos(self, request, proyecto_id=''):
        """
        página que muestra la herramienta para subir y editar fotos
        """
        fotosList = ''
        fotosLength = 0
        if proyecto_id:
            print proyecto_id
            p = get_object_or_404(Proyecto, id=proyecto_id)
            fotosList = p.fotos.iterator()
            fotosLength = p.fotos.count()
        add_success = False
        del_success = False
        form = AdminFotoForm()
        delForm = AdminDeleteFotoForm()
        if request.method == 'POST':
            if not 'delete' in request.POST:
                form = AdminFotoForm(request.POST, request.FILES)
                if form.is_valid():
                    form.saveTo(p)
                    add_success = True
                    form = AdminFotoForm()
            else:
                delForm = AdminDeleteFotoForm(request.POST)
                if delForm.is_valid():
                    delForm.save()
                    del_success = True
                    delForm = AdminDeleteFotoForm()   
            fotosList = p.fotos.iterator()
            fotosLength = p.fotos.count()        
        return render_to_response(
            'admin/proyectos/proyecto/add_fotos.html',
            {'form':form, 'add_success':add_success, 'fotosList':fotosList,
             'fotosLength':fotosLength, 'delForm':delForm, 
             'del_success':del_success},
            context_instance=RequestContext(request))

    @csrf_exempt
    def ajax_edit_foto(self, request):
        """
        si el id recibido es correcto devuelve el nombre y descripcion de la 
        foto
        """
        if request.method == 'POST':
            try:
                f = Foto.objects.get(id=request.POST['id'])
                data = {'nombre': f.nombre, 'descripcion': f.descripcion,
                        'id':f.id,}
            except:
                data = {'response' : 'el id no pertenece a ninguna foto'}
            return json_response(data)
        return None

    def add_videos(self, request, proyecto_id=''):
        """
        página que muestra la herramienta para subir y editar videos
        """
        videosList = ''
        videosLength = 0
        if proyecto_id:
            p= get_object_or_404(Proyecto, id=proyecto_id)
            videosList = p.videos.iterator()
            videosLength = p.videos.count()
        add_success = False
        del_success = False
        form = AdminVideoForm()
        delForm = AdminDeleteVideoForm()
        if request.method == 'POST':
            if not 'delete' in request.POST:
                form = AdminVideoForm(request.POST)
                if form.is_valid():
                    form.saveTo(p)
                    add_success = True
                    form = AdminVideoForm()
            else:
                delForm = AdminDeleteVideoForm(request.POST)
                if delForm.is_valid():
                    delForm.save()
                    del_success = True
                    delForm = AdminDeleteVideoForm()   
            videosList = p.videos.iterator()
            videosLength = p.videos.count()        
        return render_to_response(
            'admin/proyectos/proyecto/add_videos.html',
            {'form':form, 'add_success':add_success, 'videosList':videosList,
             'videosLength':videosLength, 'delForm':delForm, 
             'del_success':del_success},
            context_instance=RequestContext(request))

    @csrf_exempt
    def ajax_edit_video(self, request):
        """
        si el id recibido es correcto devuelve el nombre, url y descripcion del 
        video
        """
        if request.method == 'POST':
            try:
                f = Video.objects.get(id=request.POST['id'])
                data = {'nombre': f.nombre, 'url': f.url, 
                        'descripcion': f.descripcion, 'id':f.id,}
            except:
                data = {'response' : u'el id no pertenece a ningún video'}
            return json_response(data)
        return None

    def add_caracteristica(self, request, proyecto_id=''):
        """
        página que muestra la herramienta para crear y editar características
        """
        caractList = ''
        if proyecto_id:
            p= get_object_or_404(Proyecto, id=proyecto_id)
            caractList = p.caracteristica_set.iterator()
        add_success = False
        if request.method == 'POST':
            form = AdminCaracteristicaForm(request.POST)
            if form.is_valid():
                form.save()
                add_success = True
                form = AdminCaracteristicaForm(initial={'proyecto':proyecto_id})
                caractList = p.caracteristica_set.iterator()
        else:
            form = AdminCaracteristicaForm(initial={'proyecto':proyecto_id})
        return render_to_response(
            'admin/proyectos/proyecto/add_caracteristica.html',
            {'form':form, 'add_success':add_success, 'caractList':caractList,},
            context_instance=RequestContext(request))

    @csrf_exempt
    def ajax_edit_caracteristica(self, request):
        """
        si el id recibido es correcto devuelve el nombre, id y descripcion de la
        característica
        """
        if request.method == 'POST':
            try:
                f = Caracteristica.objects.get(id=request.POST['id'])
                data = {'nombre': f.nombre, 'id': f.id, 
                        'descripcion': f.descripcion,}
            except:
                data = {'response' : u'el id no pertenece a ninguna \
característica'}
            return json_response(data)
        return None

    @csrf_exempt
    def ajax_delete_caracteristica(self, request):
        """
        borra una característica con el id recibido
        """
        if request.method == 'POST':
            try:
                c = Caracteristica.objects.get(id=request.POST['id'])
                c.delete()
                data = {'response': u'característica borrada'}
            except:
                data = {'response': u'id erróneo'}
            return json_response(data)
        return None

    def add_beneficio(self, request, proyecto_id=''):
        """
        página que muestra la herramienta para crear y editar beneficios
        """
        caractList = ''
        if proyecto_id:
            p= get_object_or_404(Proyecto, id=proyecto_id)
            caractList = p.beneficio_set.iterator()
        add_success = False
        if request.method == 'POST':
            form = AdminBeneficioForm(request.POST)
            if form.is_valid():
                form.save()
                add_success = True
                form = AdminBeneficioForm(initial={'proyecto':proyecto_id})
                caractList = p.beneficio_set.iterator()
        else:
            form = AdminBeneficioForm(initial={'proyecto':proyecto_id})
        return render_to_response(
            'admin/proyectos/proyecto/add_beneficio.html',
            {'form':form, 'add_success':add_success, 'caractList':caractList,},
            context_instance=RequestContext(request))

    @csrf_exempt
    def ajax_edit_beneficio(self, request):
        """
        si el id recibido es correcto devuelve el id y descripcion del
        beneficio
        """
        if request.method == 'POST':
            try:
                f = Beneficio.objects.get(id=request.POST['id'])
                data = {'id': f.id, 
                        'descripcion': f.descripcion,}
            except:
                data = {'response' : u'error'}
            return json_response(data)
        return None

    @csrf_exempt
    def ajax_delete_beneficio(self, request):
        """
        borra el beneficio correspondiente al id recibido
        """
        if request.method == 'POST':
            try:
                c = Beneficio.objects.get(id=request.POST['id'])
                c.delete()
                data = {'response': u'beneficio borrado'}
            except:
                data = {'response': u'error'}
            return json_response(data)
        return None
                
    def add_contacto(self, request, proyecto_id=''):
        """
        página que muestra la herramienta para crear y editar los datos de 
        contacto
        """
        fonoList = ''
        numFonos = 0
        add_success = showFonoFormSet = addFonoSuccess = delFono = False
        form = AdminContactoForm(initial={'proyecto':proyecto_id})
        formset = AdminFonoFormSet()
        if proyecto_id:
            p= get_object_or_404(Proyecto, id=proyecto_id)
            try :
                fonoList = p.contacto.telefonos.iterator()
                numFonos = p.contacto.telefonos.count()
                form =  AdminContactoForm(
                    initial={'id':p.contacto.id, 'proyecto':proyecto_id,
                             'direccion':p.contacto.direccion,
                             'email':p.contacto.email})
                showFonoFormSet = True
            except ObjectDoesNotExist: 
                fonoList = ''
        if request.method == 'POST':
            if 'save' in request.POST:
                form = AdminContactoForm(request.POST)
                if form.is_valid():
                    form.save()
                    add_success = showFonoFormSet = True
            elif 'delete' in request.POST:
                delForm = AdminDeleteTelefonoForm(request.POST)
                if delForm.is_valid():
                    delForm.save()
                    delFono = True
                    fonoList = p.contacto.telefonos.iterator()
                    numFonos = p.contacto.telefonos.count()
            else:
                formset = AdminFonoFormSet(request.POST)
                if formset.is_valid():
                    formset.save(p.contacto)
                    formset = AdminFonoFormSet()
                    addFonoSuccess = True
                    fonoList = p.contacto.telefonos.iterator()
                    numFonos = p.contacto.telefonos.count()
        return render_to_response(
            'admin/proyectos/proyecto/add_contacto.html',
            {'form':form, 'add_success':add_success, 
             'fonoList':fonoList, 'formset':formset, 
             'addFonoSuccess': addFonoSuccess, 'numFonos':numFonos, 
             'delFono':delFono, 'showFonoFormSet':showFonoFormSet},
            context_instance=RequestContext(request))

    def send_email_to_user(self, request):
        """
        muestra la pagina que envia un correo a uno o varios emails
        """
        form = SendMail1()
        if request.method == 'POST':
            form = SendMail1(request.POST)
            if form.is_valid():
                form.save(request.user)
                self.message_user(request, u'El mensaje fue enviado con éxito')
                if '_save' in form.data:
                    return HttpResponseRedirect('../../../')
                return HttpResponseRedirect('')
        return render_to_response(
            'admin/proyectos/proyecto/send_mail1.html',
            {'form':form},
            context_instance=RequestContext(request))

    def send_email_to_portalUser(self, request):
        """
        envia correos a todos los usuarios del portal asociados a una
        o varias obras determinadas, a uno o varios rubros ó a todos los
        usuarios 
        """
        form = SendMail2()
        if request.method == 'POST':
            form = SendMail2(request.POST)
            if form.is_valid():
                form.save(request.user)
                self.message_user(request, u'El mensaje fue enviado con éxito')
                if '_save' in form.data:
                    return HttpResponseRedirect('../../../')
                return HttpResponseRedirect('')
        return render_to_response(
            'admin/proyectos/proyecto/send_mail2.html',
            {'form':form},
            context_instance=RequestContext(request))

    def send_email_to_admins(self, request):
        """
        envia correos a todos los administradores del portal asociados a una
        o varios proyectos, a todos los administradores o solo a ciertos
        tipos de administrador
        """
        form = SendMail3()
        if request.method == 'POST':
            form = SendMail3(request.POST)
            if form.is_valid():
                form.save(request.user)
                self.message_user(request, u'El mensaje fue enviado con éxito')
                if '_save' in form.data:
                    return HttpResponseRedirect('../../../')
                return HttpResponseRedirect('')
        return render_to_response(
            'admin/proyectos/proyecto/send_mail3.html',
            {'form':form},
            context_instance=RequestContext(request))

    def customers_export(self, request, compradores=0):
        """
        Genera y descarga el backup de clientes en csv
        """
        from django.utils import encoding
        from django.http import HttpResponse
        from django.conf import settings
        import csv, os

        def a(x):
            return encoding.smart_str(x, encoding='ascii', errors='ignore')

        baseName = 'QuimeraInmobiliaria_Clientes.csv'
        path = os.path.join(settings.BASEDIR,'CSV_Files')
        if not os.path.exists(path):
            os.makedirs(path)        
        fullPath = os.path.join(path, baseName)
        writer = csv.writer(open(fullPath, 'wb'))
        data = ['NOMBRES', 'APELLIDOS', 'CORREO', 'DIRECCION', 'RECIBIR CORREOS',
                'DEPARTAMENTO', 'PROVINCIA', 'TELEFONOS']
        writer.writerow(data)
        departamento = 'None'
        telefonos = ''
        queryset = Cliente.objects.all()
        if int(compradores):
            queryset = queryset.filter(item__isnull=False).distinct()
        for c in queryset:
            if c.provincia:
                departamento = c.provincia.departamento
            else:
                departamento = 'None'
            telefonos = ' / '.join('%s(%s)' % (t.numero,t.tipo_telefono.nombre) \
for t in c.telefonos.all())
            data = [a(c.usuario.first_name),a(c.usuario.last_name),
                    a(c.usuario.email),a(c.direccion), a(c.recibir_email),
                    a(departamento),a(c.provincia), a(telefonos)]
            writer.writerow(data)
        del writer
        fsock = open(fullPath, 'r')
        response = HttpResponse(fsock, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; \
filename=QuimeraInmobiliaria_Clientes.csv'
        return response        

# class ContactoAdmin(admin.ModelAdmin):
#     pass


class EtapaAdmin(admin.ModelAdmin):
    list_display= ('titulo', 'porcentaje', 'fecha_inicio', 
                   'fecha_fin','proyecto',)
    list_display_links = ('titulo', 'porcentaje', 'fecha_inicio', 
                   'fecha_fin', 'proyecto',)
    list_filter = ('proyecto',)

    actions = ['borrar_etapa']

    def queryset(self, request):
        """
        solo los super usuarios tienen acceso a todas las etapas de todos los 
        proyectos, los demas usuarios solo tendran acceso a las etapas de los
        proyectos donde estan asociados
        """
        qs = super(self.__class__, self).queryset(request)
        if request.user.is_superuser:
            return qs;
        return qs.filter(proyecto__usuarios__id=request.user.id)

    def get_urls(self):
        urls = super(self.__class__, self).get_urls()
        my_urls = patterns(
            '',
            (r'^add/$', self.admin_site.admin_view(self.etapa_add)),
            url(r'^delete/$', self.admin_site.admin_view(self.etapa_delete),
                name="admin_etapa_delete"),
            (r'^(?P<etapaId>\d+)/$', 
             self.admin_site.admin_view(self.etapa_add)),
            url(r'^add/ajax_list_subetapas/$', 
                self.admin_site.admin_view(self.ajax_list_subetapas),
                name='ajax_list_subetapas'),
            url(r'^add/ajax_edit_subetapa/$',
                self.admin_site.admin_view(self.ajax_edit_subetapa),
                name='ajax_edit_subetapa'),
            url(r'^add/ajax_delete_subetapa/$',
                self.admin_site.admin_view(self.ajax_delete_subetapa),
                name='ajax_delete_subetapa'),
            url(r'^ajax_delete_subetapa_view/$',
                self.admin_site.admin_view(self.ajax_delete_subetapa_view),
                name='ajax_delete_subetapa_view'),
                           )
        return my_urls + urls

    def get_actions(self, request):
        """
        funcion that disables some admins actions in this model
        """
        actions = super(self.__class__, self).get_actions(request)
        del actions['delete_selected']
        return actions    

    def borrar_etapa(self, request, queryset):
        """
        muestra una página para confirmar la eliminación de las subetapas 
        seleccionadas y todos sus objetos relacionados
        """
        return render_to_response(
            'admin/proyectos/etapa/delete_selected_confirmation.html',
            {'etapasList':queryset}, context_instance=RequestContext(request))
    
    def etapa_delete(self, request):
        """
        borra las etapas seleccionadas utilizando el delete de la clase 
        Etapa
        """
        if request.method == 'POST':
            nro = 0
            for key in request.POST.keys():
                try: 
                    int(key)
                    e = get_object_or_404(Etapa, id=request.POST[key])
                    e.delete()
                    nro += 1
                except:
                    key=-1
            resulting_message = u''
            if nro > 1:
                resulting_message = u'Las etapas fueron borradas'
            elif nro == 1:
                resulting_message = u'La etapa fue borrada'
            self.message_user(request, resulting_message)
        return HttpResponseRedirect('../')

    def etapa_add(self, request, etapaId=-1):
        created= False
        etapa_id = '-1'
        if etapaId != -1:
            edit = True
            e = get_object_or_404(Etapa, id = etapaId)
            form = AdminEtapaForm(instance = e, user=request.user)
            etapa_id = etapaId
            created = True
        else:
            edit = False
            form = AdminEtapaForm(user=request.user)
        if request.method == 'POST':
            if 'proyecto' in request.POST:
                form  = AdminEtapaForm(request.POST, user=request.user)
                if form.is_valid():
                    etapa = form.save()
                    self.message_user(request,'La etapa fue agregada con éxito')
                    if '_save' in form.data:
                        return HttpResponseRedirect('../')
                    if '_addanother' in form.data:
                        return HttpResponseRedirect('')
                    if '_continue' in form.data:
                        created = True
                        etapa_id = etapa.id
                        form = AdminEtapaForm(instance = etapa, 
                                              user=request.user)
            else:
                created = True
                formSE = AdminSubEtapaForm(request.POST)
                etapa = get_object_or_404(Etapa, id=formSE.data['etapa'])
                etapa_id = etapa.id
                form = AdminEtapaForm(instance = etapa, user=request.user)
                if formSE.is_valid():
                    formSE.save()
                    self.message_user(request,
                                      'La sub-etapa fue agregada con éxito')
                    # if '_save' in formSE.data:
                    #     return HttpResponseRedirect('../')
                else:
                    return render_to_response(
                        'admin/proyectos/etapa/change_form.html',
                        {'form':form, 'formSE':formSE, 'created':created,
                         'etapa_id':etapa_id, 'edit': edit},
                        context_instance=RequestContext(request))
        formSE = AdminSubEtapaForm(initial = {'etapa':etapa_id})
        return render_to_response('admin/proyectos/etapa/change_form.html',
                                  {'form':form, 'formSE':formSE, 'edit': edit,
                                   'created':created, 'etapa_id': etapa_id,},
                                  context_instance=RequestContext(request))

    # def etapa_add(self, request, etapaId):
    #     created= False
    #     etapa_id = '-1'
    #     form = AdminEtapaForm()
    #     if request.method == 'POST':
    #         if 'proyecto' in request.POST:
    #             form  = AdminEtapaForm(request.POST)
    #             if form.is_valid():
    #                 #ToDo: al poner de nuevo cualquier save se va volver a 
    #                 #crear un objeto, hay q hacer una funcion update 
    #                 #y llamarla cuando etapa_id != ''
    #                 etapa = form.save()
    #                 self.message_user(request,'La etapa fue agregada con éxito')
    #                 if '_save' in form.data:
    #                     return HttpResponseRedirect('../')
    #                 if '_addanother' in form.data:
    #                     return HttpResponseRedirect('')
    #                 if '_continue' in form.data:
    #                     created = True
    #                     etapa_id = etapa.id
    #                     form = AdminEtapaForm(instance = etapa)
    #         else:
    #             created = True
    #             formSE = AdminSubEtapaForm(request.POST)
    #             etapa = get_object_or_404(Etapa, id=formSE.data['etapa'])
    #             etapa_id = etapa.id
    #             form = AdminEtapaForm(instance = etapa)
    #             if formSE.is_valid():
    #                 formSE.save()
    #                 self.message_user(request,
    #                                   'La sub-etapa fue agregada con éxito')
    #                 if '_save' in formSE.data:
    #                     return HttpResponseRedirect('../')
    #             else:
    #                 return render_to_response(
    #                     'admin/proyectos/etapa/change_form.html',
    #                     {'form':form, 'formSE':formSE, 'created':created,
    #                      'etapa_id':etapa_id},
    #                     context_instance=RequestContext(request))
    #     formSE = AdminSubEtapaForm(initial = {'etapa':etapa_id})
    #     return render_to_response('admin/proyectos/etapa/change_form.html',
    #                               {'form':form, 'formSE':formSE, 
    #                                'created':created, 'etapa_id': etapa_id,},
    #                               context_instance=RequestContext(request))


    def ajax_list_subetapas(self, request):
        """
        retorna la lista de subetapas de la etapa
        """
        etapa_id = request.GET['etapa_id']
        html_return = {}
        try:
            etapa = Etapa.objects.get(id=etapa_id)
            querySet = etapa.subetapa_set.all()
            if querySet:
                content = ''
                for se in querySet:
                    content += u"<tr id='%s'><td class='first'>%s</td>\
<td class='second'>%s%s</td><td><a alt='%s' class='changelink ajaxedit'\
 href='#'>Editar</a></td><td><a alt='%s' class='deletelink ajaxdelete' \
href='#'>Borrar</a></td></tr>" % (se.id, se.titulo, se.porcentaje, 
                                  "%", se.id, se.id)
                    html_return['response'] = SafeUnicode(u"<div class='\
subetapas_list'><fieldset class='module'><table class='subetapas_list'>%s\
</table></fieldset></div>" % content)
            else:
                html_return['response'] = u'Aún no hay subetapas creadas'
        except:
            html_return['response'] = u'El id de la etapa es incorrecto'
        return json_response(html_return)

    def ajax_edit_subetapa(self, request):
        """
        retorna los datos de la su-etapa
        """
        if request.method == 'GET':
            try:
                se = SubEtapa.objects.get(id=request.GET['id'])
                fecha_inicio, fecha_fin = None, None
                if se.fecha_inicio:
                    fecha_inicio = se.fecha_inicio .strftime('%d/%m/%y')
                if se.fecha_fin:
                    fecha_fin = se.fecha_fin.strftime('%d/%m/%y')
                data = {'id': se.id, 
                         'titulo': se.titulo, 
                         'fecha_inicio': fecha_inicio, 
                         'fecha_fin': fecha_fin, 
                         'porcentaje': se.porcentaje}
            except:
                data = {'response' : ''}
            return json_response(data)
        return None
        
    def ajax_delete_subetapa(self, request):
        """
        borra una subetapa
        ToDo: falta revisar que se borren correctamente todos los objetos
        en etapa, subetapa, milesteosne, etc
        """
        if request.method == 'GET':
            try:
                se = SubEtapa.objects.get(id=request.GET['id'])
                se.delete()
                data = {'response': 'Subetapa Eliminada',
                        'id': request.GET['id']}
            except:
                data = {'response': 'Id incorrecto'}
            return json_response(data)
        return None

    def ajax_delete_subetapa_view(self, request):
        """
        verifica si hay datos que se van a borrar en cascada y los retorna
        """
        if request.method == 'GET':
            se = SubEtapa.objects.get(id=request.GET['id'])
            # queryset = se.milestone_set.all()
            queryset = se.avance_set.all()
            if queryset:
                related_objects = u'<ul>'
                for a in queryset:
                    related_objects += u'<li>Avance creado el %s' % a.fecha_creacion.strftime('%d/%m/%Y a las %H:%M:%S')
                    fotos = a.fotos.all()
                    if fotos:
                        related_objects += u'<ul><li>Fotos '
                        fotoStr = ''
                        fotoStr += ''.join(
                            u'<li>%s</li>' % f for f in fotos)
                        related_objects  += u'<ul>%s</ul></li></ul>' % fotoStr
                    videos =  a.videos.all()
                    if videos:
                        related_objects += u'<ul><li>Videos '
                        videoStr = u''
                        videoStr += u''.join(
                            u'<li>%s</li>' % f for f in videos)
                        related_objects  += u'<ul>%s</ul></li></ul>' % videoStr
                    milestones = a.milestone_set.all()
                    if milestones:
                        related_objects += u'<ul><li>Milestones '
                        mStr = ''
                        mStr += ''.join(
                            u'<li>%s</li>' % f for f in milestones)
                        related_objects  += u'<ul>%s</ul></li></ul>' % mStr

                    related_objects += u'</li>'
                related_objects += u'</ul>'
                data = {
                    'cascade': '1', 'id': request.GET['id'],
                    'related_objects': u'<p class="jqmConfirmMsg">Si borra \
esta sub-etapa los siguientes objetos relacionados a ella también serán \
eliminados.</p>%s' % related_objects}

            else:
                data = {'cascade': '0', 'id': request.GET['id']}
            return json_response(data)
        return None

    
# class SubEtapaAdmin(admin.ModelAdmin):
#     pass


# class CaracteristicaAdmin(admin.ModelAdmin):
#     pass


class PlanoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'proyecto', 'actualizacion')
    list_display_links = ('titulo', 'proyecto', 'actualizacion')
    list_filter = ('proyecto',)
    actions = ('borrar_planos',)

    def queryset(self, request):
        """
        solo los super usuarios tienen acceso a todos planos de todo los 
        proyectos, los demas usuarios solo tendran acceso a los planos de los
        proyectos donde estan asociados
        """
        qs = super(self.__class__, self).queryset(request)
        if request.user.is_superuser:
            return qs;
        return qs.filter(proyecto__usuarios__id=request.user.id)

    def get_urls(self):
        urls = super(self.__class__, self).get_urls()
        my_urls = patterns(
            '',
            url(r'^add/$', self.admin_site.admin_view(self.plano_add),
                name='admin_plano_add'),
            url(r'^(?P<plano_id>\d+)/$', 
                self.admin_site.admin_view(self.plano_add),
                name='admin_plano_edit'),
            url(r'^edit_map/(?P<plano_id>\d+)?$', 
                self.admin_site.admin_view(self.edit_map),
                name='admin_proyecto_edit_map'),
            url(r'^punto_update/$', 
                self.admin_site.admin_view(self.ajax_update_punto),
                name='admin_plano_update_punto'),
            url(r'^plano_dibujado_update/$', 
                self.admin_site.admin_view(self.ajax_update_plano_dibujado),
                name='admin_plano_update_plano_dibujado'),
            url(r'^redirect_to_plano/(?P<plano_id>\d+)/$', 
                self.admin_site.admin_view(self.redirect_to_plano),
                name='admin_redirect_to_plano'),            
            url(r'^delete_selected/$', 
                self.admin_site.admin_view(self.delete_selected),
                name='admin_plano_delete_selected'),            

            )
        return my_urls + urls

    def get_actions(self, request):
        """
        funcion that disables some admins actions in this model
        """
        actions = super(self.__class__, self).get_actions(request)
        del actions['delete_selected']
        return actions    

    def borrar_planos(self, request, queryset):
        """
        muestra una página para confirmar la eliminación de los planos 
        seleccionados y todos sus objetos relacionados
        """
        return render_to_response(
            'admin/proyectos/plano/delete_selected_confirmation.html',
            {'planosList':queryset}, context_instance=RequestContext(request))
        #self.message_user(request, resulting_message)
    borrar_planos.short_description = 'Borrar planos seleccionados'


    def plano_add(self, request, plano_id=''):
        """
        muestra la vista para agregar o editar un plano
        """
        created = edit =False
        proyecto_id = ''
        if plano_id:
            a=get_object_or_404(Plano, id=plano_id)
            created = edit = True
            form = AdminPlanoForm(instance = a)
            proyecto_id = a.proyecto.id
        else:
            form = AdminPlanoForm()
        if request.method == 'POST':
            form = AdminPlanoForm(request.POST, request.FILES)
            if form.is_valid():
                a=form.save()
                if plano_id:
                    msg = u'El plano fue actualizado'
                else:
                    msg = u'El plano fue agregado con éxito'
                self.message_user(request, msg)
                if '_save' in form.data:
                    return HttpResponseRedirect('../')
                if '_addanother' in form.data:
                    return HttpResponseRedirect('')
                if '_continue' in form.data:
                    created = True
                    plano_id = a.id
                    form = AdminPlanoForm(instance = a)
                    proyecto_id = a.proyecto.id
        return render_to_response(
            'admin/proyectos/plano/change_form.html',
            {'form':form, 'created':created, 'plano_id':plano_id,
             'edit':edit, 'proyecto_id':proyecto_id},
            context_instance=RequestContext(request))
    
    def edit_map(self, request, plano_id=''):
        """
        pagina para la edicion de planos
        """
        plano = success = ''
        coordList = poligons = polColors = itemList = []
        form = AdminItemForm()
        if plano_id:
            plano = get_object_or_404(Plano, id=plano_id)
            form =  AdminItemForm(initial={'plano':plano})
            queryItems = plano.item_set.all()
            poligons = [i.poligono.get_points_list(False,1,1,True,10) for i in \
queryItems]
            polColors = [i.poligono.color_relleno for i in queryItems]
            itemList = [i.id for i in queryItems]
        if request.method == 'POST':
            form = AdminItemForm(request.POST)
            if form.is_valid():
                form.save()
                form = AdminItemForm(initial={'plano':plano})
                success = True                
                queryItems = plano.item_set.all()
                poligons=[i.poligono.get_points_list(False,1,1,True,10) for i \
in queryItems]
                polColors = [i.poligono.color_relleno for i in queryItems]
                itemList = [i.id for i in queryItems]
            else:
                coordList = form.get_list_of_coordinates()
        #print poligons
        return render_to_response(
            'admin/proyectos/plano/edit_map.html',
            {'plano_id':plano_id, 'plano':plano, 'form':form,
             'success':success, 'coordList':coordList, 'poligons':poligons,
             'polColors':polColors, 'itemList':itemList,},
            context_instance=RequestContext(request))

    @csrf_exempt
    def ajax_update_punto(self, request):
        """
        actualiza el punto de un poligono perteneciente al item de un plano
        """
        if request.method == 'POST':
#            try:
            plano = Plano.objects.get(id=request.POST['plano_id'])
            item = plano.item_set.all()[int(request.POST['poligono'])]
            #ToDo: se puede mejorar utilizando el id en lugar de filtrar
            point = item.poligono.punto_set.filter(
                x=float(request.POST['x_old'])).filter(
                y=float(request.POST['y_old'])).get()
            point.x = request.POST['x_new']
            point.y = request.POST['y_new']
            point.save()
            data = {'response': u'ok'}
            # except:
            #     data = {'response' : u'error en los datos enviados'}
            return json_response(data)
        return None

    @csrf_exempt
    def ajax_update_plano_dibujado(self, request):
        """
        actualiza el plano dibujado
        """
        if request.method == 'POST':
            try:
                Plano.objects.get(
                    id=request.POST['plano_id']).create_plano_image()
                data = {'response': u'ok'}
            except:
                data = {'response': u'error'}
            return json_response(data)
        return None

    def redirect_to_plano(self, request, plano_id):
        return HttpResponseRedirect(
            reverse('admin:admin_proyecto_edit_map', args=(int(plano_id),)))

    def delete_selected(self, request):
        """
        borra los planos seleccionados sí y sólo si no tienen items separados
        o vendidos
        """
        deleted=''
        nonDeleted=''
        if request.method == 'POST':
            nro = 0
            for key in request.POST.keys():
                try: 
                    int(key)
                    e = get_object_or_404(Plano, id=request.POST[key])
                    delete = True
                    for item in e.item_set.all():
                        if item.estado != u'D':
                            delete = False
                    if delete == True:
                        e.delete()
                        nro += 1
                        deleted += str(e.titulo) + ', '
                    else:
                        nonDeleted += str(e.titulo) + ', '
                except:
                    key=-1
            resulting_message = u''
            if deleted:
                deleted = deleted[:-2]
                if nro > 1:
                    resulting_message = u'Los siguientes planos fueron \
borrados: ' + deleted
                else:
                    resulting_message = u'El siguiente plano fue \
borrado: ' + deleted
                self.message_user(request, resulting_message)
            if nonDeleted:
                msg1 = u'Recuerde que sólo los planos con items disponibles \
pueden ser eliminados'
                messages.warning(request,msg1)
                msg2 = u'Los siguientes planos no fue borrados: '\
 + nonDeleted[:-2]
                messages.error(request,msg2 )
        return HttpResponseRedirect('../')


# class MilestoneAdmin(admin.ModelAdmin):
#     def delete_model(self, request, obj):
#         """
#         llama al delete definido en la clase MilesStone
#         """
#         obj.delete()


class AvanceAdmin(admin.ModelAdmin):
    list_display= ('notas', 'proyecto','etapa','subetapa', 'estado')
    list_display_links = ('notas', 'proyecto','etapa','subetapa','estado')
    list_filter = ('estado', 'proyecto',)
    actions = ['borrar_avance',]

    def queryset(self, request):
        """
        solo los super usuarios tienen acceso a todos acances de todo los 
        proyectos, los demas usuarios solo tendran acceso a los avances de los
        proyectos donde estan asociados
        """
        qs = super(self.__class__, self).queryset(request)
        if request.user.is_superuser:
            return qs;
        return qs.filter(proyecto__usuarios__id=request.user.id)

    def get_urls(self):
        urls = super(self.__class__, self).get_urls()
        my_urls = patterns(
            '',
            url(r'^add/$', self.admin_site.admin_view(self.avance_add),
                name='admin_avance_add'),
            url(r'^get_etapas/$', 
                self.admin_site.admin_view(self.ajax_get_etapas),
                name='admin_avance_ajax_get_etapas'),            
            url(r'^get_subetapas/$', 
                self.admin_site.admin_view(self.ajax_get_subetapas),
                name='admin_avance_ajax_get_subetapas'),            
            url(r'^(?P<avance_id>\d+)/$', 
                self.admin_site.admin_view(self.avance_add),
                name='admin_avance_edit'),
            url(r'^add_fotos/(?P<avance_id>\d+)?$', 
                self.admin_site.admin_view(self.add_fotos),
                name='admin_avance_add_fotos'),
            #no se creó esta vista porque se esta reutilizando 
            #la del proyecto: admin_proyecto_ajax_edit_foto
            # url(r'ajax_edit_foto/$', 
            #     self.admin_site.admin_view(self.ajax_edit_foto),
            #     name='admin_avance_ajax_edit_foto'),
            url(r'^add_videos/(?P<avance_id>\d+)?$', 
                self.admin_site.admin_view(self.add_videos),
                name='admin_avance_add_videos'),
            #no se creó esta vista porque se esta reutilizando 
            #la del proyecto: admin_proyecto_ajax_edit_video
            # url(r'ajax_edit_video/$', 
            #     self.admin_site.admin_view(self.ajax_edit_video),

            #     name='admin_proyecto_ajax_edit_video'),
            url(r'^add_milestones/(?P<avance_id>\d+)?$', 
                self.admin_site.admin_view(self.add_milestones),
                name='admin_avance_add_milestones'),
            url(r'^ajax_edit_milestone/$', 
                self.admin_site.admin_view(self.ajax_edit_milestone),
                name='admin_avance_ajax_edit_milestone'),
            url(r'^ajax_delete_milestone/$', 
                self.admin_site.admin_view(self.ajax_delete_milestone),
                name='admin_avance_ajax_delete_milestone'),
            url(r'^delete_avances/$', 
                self.admin_site.admin_view(self.avances_delete),
                name='admin_avances_delete'),

                           )
        return my_urls + urls

    def get_actions(self, request):
        """
        funcion that disables some admins actions in this model
        """
        actions = super(self.__class__, self).get_actions(request)
        del actions['delete_selected']
        return actions    

    def borrar_avance(self, request, queryset):
        """
        muestra una página para confirmar la eliminación de los avance
        seleccionados y todos sus objetos relacionados
        """
        return render_to_response(
            'admin/proyectos/avance/delete_selected_confirmation.html',
            {'etapasList':queryset}, context_instance=RequestContext(request))
    borrar_avance.short_description = 'Borrar avances seleccionados'
    
    def avances_delete(self, request):
        """
        borra los avances seleccionados utilizando el delete del la clase 
        Avance
        """
        if request.method == 'POST':
            nro = 0
            for key in request.POST.keys():
                try: 
                    int(key)
                    e = get_object_or_404(Avance, id=request.POST[key])
                    e.delete()
                    nro += 1
                except:
                    key=-1
            resulting_message = u''
            if nro > 1:
                resulting_message = u'Los avances fueron borrados'
            elif nro == 1:
                resulting_message = u'El avance fue borrado'
            self.message_user(request, resulting_message)
        return HttpResponseRedirect('../')

    def avance_add(self, request, avance_id=''):
        """
        muestra la pagina para agregar un avances, sus fotos, videos y 
        milestones abarcados por el avance
        """
        created = edit =False
        etapa = subetapa = proyecto_id = ''
        if avance_id:
            a=get_object_or_404(Avance, id=avance_id)
            created = edit = True
            form = AdminAvanceForm(instance = a, user=request.user)
            proyecto_id = a.subetapa.etapa.proyecto.id
            etapa = a.subetapa.etapa.id
            subetapa = a.subetapa.id
        else:
            form = AdminAvanceForm(user=request.user)
        if request.method == 'POST':
            form = AdminAvanceForm(request.POST, user=request.user)
            if form.is_valid():
                a=form.save(request)
                if avance_id:
                    msg = u'El avance fue actualizado'
                else:
                    msg = u'El avance fue agregado con éxito'
                self.message_user(request, msg)
                if '_save' in form.data:
                    return HttpResponseRedirect('../')
                if '_addanother' in form.data:
                    return HttpResponseRedirect('')
                if '_continue' in form.data:
                    created = True
                    avance_id = a.id
                    form = AdminAvanceForm(instance = a, user=request.user)
                    proyecto_id = a.subetapa.etapa.proyecto.id
                    etapa = a.subetapa.etapa.id
                    subetapa = a.subetapa.id
        return render_to_response(
            'admin/proyectos/avance/change_form.html',
            {'form':form, 'created':created, 'avance_id':avance_id,
             'edit':edit, 'etapa':etapa, 'subetapa':subetapa,
             'proyecto_id':proyecto_id},
            context_instance=RequestContext(request))
        
    def ajax_get_etapas(self, request):
        """
        retorna un string con las etapas del proyecto listas para ser mostradas
        en un select
        """
        if request.method == 'GET':
            try:
                selectId = request.GET.get('etapaId')
                p = Proyecto.objects.get(id=request.GET['id'])
#                 etapas = ''.join("<option value='%s'>%s</option>" % \
# (e.id,e.titulo) for e in p.etapa_set.all())
                etapas = ''
                for e in p.etapa_set.all():
                    if selectId and int(selectId) == e.id:
                        etapas += "<option selected='selected' value='%s'>%s\
</option>" % (e.id,e.titulo)
                    else:
                        etapas += "<option value='%s'>%s\
</option>" % (e.id,e.titulo)
                data = {'options': "<option value=''>\
---------</option>"+etapas}
            except:
                data = {'response': 'Id incorrecto'}
            return json_response(data)
        return None

    def ajax_get_subetapas(self, request):
        """
        retorna un string con las subetapas de la etapa listas para ser 
        mostradas en un select
        """
        if request.method == 'GET':
            try:
                selectId = request.GET.get('subetapaId')
                p = Etapa.objects.get(id=request.GET['id'])
#                 subetapas = ''.join("<option value='%s'>%s</option>" % \
# (e.id,e.titulo) for e in p.subetapa_set.all())
                subetapas = ''
                for se in p.subetapa_set.all():
                    if selectId and int(selectId) == se.id:
                        subetapas += "<option selected='selected' value='%s'>%s\
</option>" % (se.id,se.titulo)
                    else:
                        subetapas += "<option value='%s'>%s\
</option>" % (se.id,se.titulo)

                data = {'options': "<option selected='selected' value=''>\
---------</option>"+subetapas}
            except:
                data = {'response': 'Id incorrecto'}
            return json_response(data)
        return None

    def add_fotos(self, request, avance_id=''):
        """
        página que muestra la herramienta para subir y editar fotos
        """
        fotosList = ''
        fotosLength = 0
        if avance_id:
            p= get_object_or_404(Avance, id=avance_id)
            fotosList = p.fotos.iterator()
            fotosLength = p.fotos.count()
        add_success = False
        del_success = False
        form = AdminFotoForm()
        delForm = AdminDeleteFotoForm()
        if request.method == 'POST':
            if not 'delete' in request.POST:
                form = AdminFotoForm(request.POST, request.FILES)
                if form.is_valid():
                    form.saveTo(p)
                    add_success = True
                    form = AdminFotoForm()
            else:
                delForm = AdminDeleteFotoForm(request.POST)
                if delForm.is_valid():
                    delForm.save()
                    del_success = True
                    delForm = AdminDeleteFotoForm()   
            fotosList = p.fotos.iterator()
            fotosLength = p.fotos.count()        
        return render_to_response(
            'admin/proyectos/avance/add_fotos.html',
            {'form':form, 'add_success':add_success, 'fotosList':fotosList,
             'fotosLength':fotosLength, 'delForm':delForm, 
             'del_success':del_success},
            context_instance=RequestContext(request))

    def add_videos(self, request, avance_id=''):
        """
        página que muestra la herramienta para subir y editar videos
        """
        videosList = ''
        videosLength = 0
        if avance_id:
            p= get_object_or_404(Avance, id=avance_id)
            videosList = p.videos.iterator()
            videosLength = p.videos.count()
        add_success = False
        del_success = False
        form = AdminVideoForm()
        delForm = AdminDeleteVideoForm()
        if request.method == 'POST':
            if not 'delete' in request.POST:
                form = AdminVideoForm(request.POST)
                if form.is_valid():
                    form.saveTo(p)
                    add_success = True
                    form = AdminVideoForm()
            else:
                delForm = AdminDeleteVideoForm(request.POST)
                if delForm.is_valid():
                    delForm.save()
                    del_success = True
                    delForm = AdminDeleteVideoForm()   
            videosList = p.videos.iterator()
            videosLength = p.videos.count()        
        return render_to_response(
            'admin/proyectos/avance/add_videos.html',
            {'form':form, 'add_success':add_success, 'videosList':videosList,
             'videosLength':videosLength, 'delForm':delForm, 
             'del_success':del_success},
            context_instance=RequestContext(request))

    def add_milestones(self, request, avance_id):
        """
        pagina que muestra la herramienta para agregar editar los milestones
        de un avance
        """
        milestoneList = subetapaId = ''
        if avance_id:
            p= get_object_or_404(Avance, id=avance_id)
            subetapaId = p.subetapa.id
            milestoneList = p.milestone_set.iterator()
        add_success = False
        if request.method == 'POST':
            form = AdminMilestoneForm(request.POST)
            if form.is_valid():
                form.save()
                add_success = True
                form = AdminMilestoneForm(initial={'avance':avance_id,
                                                   'subetapa':subetapaId})
                milestoneList = p.milestone_set.iterator()
        else:
            form = AdminMilestoneForm(initial={'avance':avance_id,
                                               'subetapa':subetapaId})
        return render_to_response(
            'admin/proyectos/avance/add_milestones.html',
            {'form':form, 'add_success':add_success, 
             'milestoneList':milestoneList,},
            context_instance=RequestContext(request))

    @csrf_exempt
    def ajax_edit_milestone(self, request):
        """
        si el id recibido es correcto devuelve el título, id, id_avance,
        id_subetapa, fecha_fin, porcentaje y alcanazado
        característica
        """
        if request.method == 'POST':
            try:
                f = Milestone.objects.get(id=request.POST['id'])
                fecha_fin = None
                if f.fecha_fin:
                    fecha_fin = f.fecha_fin.strftime('%d/%m/%Y')
                data = {'titulo': f.titulo, 'id': f.id, 
                        'id_avance':f.avance.id, 'id_subetapa':f.subetapa.id,
                        'fecha_fin':fecha_fin, 
                        'porcentaje':f.porcentaje, 'alcanzado': f.alcanzado,}
            except:
                data = {'response' : u''}
            return json_response(data)
        return None

    @csrf_exempt
    def ajax_delete_milestone(self, request):
        """
        borra sólo el milestone con el id recibido, dejando intactos a sus
        objetos relacionados
        """
        if request.method == 'POST':
            try:
                c = Milestone.objects.get(id=request.POST['id'])
                c.delete(custom=False)
                data = {'response': u'milestone borrado'}
            except:
                data = {'response': u'id erróneo'}
            return json_response(data)
        return None


class AvisoAdmin(admin.ModelAdmin):
    list_display = ('proyecto', 'duracion',)
    list_display_links = ('proyecto', 'duracion',)
    list_filter= ('proyecto',)

    def queryset(self, request):
        """
        solo los super usuarios tienen acceso a todos avisos de todo los 
        proyectos, los demas usuarios solo tendran acceso a los avisos de los
        proyectos donde estan asociados
        """
        qs = super(self.__class__, self).queryset(request)
        if request.user.is_superuser:
            return qs;
        return qs.filter(proyecto__usuarios__id=request.user.id)


class OfertaAdmin(admin.ModelAdmin):
    list_display= ('item', 'fecha_inicio','fecha_fin',)
    list_display_links = ('item', 'fecha_inicio','fecha_fin',)
    list_filter = ('proyecto', 'item__tipo_item__nombre__nombre')
    
    def queryset(self, request):
        """
        solo los super usuarios tienen acceso a todas las ofertas de todos los 
        proyectos, los demas usuarios solo tendran acceso a las ofertas de los
        proyectos donde estan asociados
        """
        qs = super(self.__class__, self).queryset(request)
        if request.user.is_superuser:
            return qs;
        return qs.filter(proyecto__usuarios__id=request.user.id)

    def get_urls(self):
        urls = super(self.__class__, self).get_urls()
        my_urls = patterns(
            '',
            url(r'^add/$', self.admin_site.admin_view(self.oferta_add),
                name='admin_oferta_add'),
            url(r'^(?P<oferta_id>\d+)/$', 
                self.admin_site.admin_view(self.oferta_add),
                name='admin_oferta_edit'),
            url(r'^get_item/$', 
                self.admin_site.admin_view(self.ajax_item),
                name='admin_proyecto_ajax_get_item'),

            )
        return my_urls + urls
    
    def oferta_add(self, request, oferta_id=''):
        """
        muestra la pagina para agregar o editar una oferta
        """
        created = edit =False
        #tipotemId = proyecto_id = ''
        itemId = proyecto_id = ''
        if oferta_id:
            a=get_object_or_404(Oferta, id=oferta_id)
            form = AdminOfertaForm(instance=a)
            edit = True
            #tipoItemId = a.tipo_item.id
            itemId = a.item.id
            proyecto_id = a.proyecto.id
        else:
            form = AdminOfertaForm()
        if request.method == 'POST':
            form = AdminOfertaForm(request.POST)
            if form.is_valid():
                a=form.save()
                if oferta_id:
                    msg = u'Los datos de la oferta fueron actualizados'
                else:
                    msg = u'La oferta fue agregada con éxito'
                self.message_user(request, msg)
                if '_save' in form.data:
                    return HttpResponseRedirect('../')
                if '_addanother' in form.data:
                    return HttpResponseRedirect('')
                if '_continue' in form.data:
                    oferta_id = a.id
                    #tipoItemId = a.tipo_item.id
                    itemId = a.item.id
                    proyecto_id = a.proyecto.id
                    form = AdminOfertaForm(instance=a)
            elif not edit:
                form.data = form.data.copy()
                del form.data['proyecto']
        return render_to_response(
            'admin/proyectos/oferta/change_form.html',
            {'form':form, 'edit':edit, 
             #'tipoItemId':tipoItemId, 
             'itemId':itemId, 
             'proyecto_id':proyecto_id},
            context_instance=RequestContext(request))

    def ajax_item(self, request):
        """
        retorna un string con los items del proyecto listos para ser mostradas
        en un select
        """
        if request.method == 'GET':
            try:
                selectId = request.GET.get('itemId')
                p = Proyecto.objects.get(id=request.GET['id'])
                items = ''
                #for e in p.tipoitem_set.all():
                for e in Item.objects.filter(plano__proyecto=p.id):
                    if selectId and int(selectId) == e.id:
                        items += "<option selected='selected' value='%s'>%s\
</option>" % (e.id,e.numero)
                    else:
                        items += "<option value='%s'>%s\
</option>" % (e.id,e.numero)
                data = {'options': "<option value=''>\
---------</option>"+items}
            except:
                data = {'response': ''}
            return json_response(data)
        return None

class ItemAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'estado',)
    actions = ('delete_items_selected', )

    def get_urls(self):
        urls = super(self.__class__, self).get_urls()
        my_urls = patterns(
            '',
            url(r'^(?P<item_id>\d+)/delete_item/$', 
                self.admin_site.admin_view(self.delete_item),
                name='admin_proyecto_delete_item'),
            url(r'^delete_items/$', 
                self.admin_site.admin_view(self.delete_items),
                name='admin_proyecto_delete_items'),
            url(r'^ajax_seach_clientes/$', 
                self.admin_site.admin_view(self.ajax_search_clientes),
                name='admin_proyecto_ajax_search_clientes'),

            )
        return my_urls + urls

    def get_actions(self, request):
        """
        funcion that disables some admins actions in this model
        """
        actions = super(self.__class__, self).get_actions(request)
        del actions['delete_selected']
        return actions    

    def delete_item(self, request, item_id):
        """
        si el item tiene estado disponible redirecciona para que se borre
        sino muestra un mensaje indicando que solo se pueden borrar los 
        items con estado disponible
        """
        item = get_object_or_404(Item, id=item_id)
        is_popup = False
        if '_popup' in request.GET:
            is_popup = True
        if item.estado == u'D':
            if request.method == 'POST':
                item.delete()
                if is_popup:
                    return HttpResponse('<script type="text/javascript">\
window.opener.location.href = window.opener.location.href; window.close();\
</script>')
                msg = u'El item fue borrado.'
                self.message_user(request, msg)
                return HttpResponseRedirect(
                    reverse('admin:proyectos_item_changelist'))
            else:
                return render_to_response(
                    'admin/proyectos/item/confirm_delete_item.html',
                    {'is_popup':is_popup,},
                    context_instance=RequestContext(request))  
        msg = u'Sólo pueden borrar los items con estado disponible.'
        self.message_user(request, msg)
        if is_popup:
            return HttpResponseRedirect('../?_popup=1')
        return HttpResponseRedirect('../')

    def save_model(self, request, obj, form, change):
        obj.save()

    def delete_model(self, request, obj):
        """
        borra el item solo si este tiene estado disponible
        """
        if obj.estado == u'D':
            super(self.__class__,self).delete_model(request, obj)
        else:
            msg = u'Verifique que todos los items seleccionados tienen estado \
disponible. '
            self.message_user(request, msg)        

    def delete_items_selected(self, request, queryset):
        """
        verifica si todos los items seleccionados tiene estado disponible, 
        si se cumple esto redirecciona a la pagina de confirmacion
        en caso contrario redirecciona al changelist de los items junto con un
        mensaje indicando que todos los items a borrar deben estar en estado
        disponible
        """
        for obj in queryset:
            if obj.estado != u'D':
                msg = u'Verifique que todos los items seleccionados tienen \
estado disponible.'
                self.message_user(request, msg)
                return HttpResponseRedirect(
                    reverse('admin:proyectos_item_changelist'))
        return render_to_response(
            'admin/proyectos/item/confirm_delete.html',
            {'queryset': queryset, 'numItems': queryset.count()},
            context_instance=RequestContext(request))            
    delete_items_selected.short_description = u'Eliminar items seleccionados'

    def delete_items(self, request):
        """
        borra los items seleccionados
        """
        if request.method == 'POST':
            nro = 0
            for key in request.POST.keys():
                try: 
                    int(key)
                    e = get_object_or_404(Item, id=request.POST[key])
                    e.delete()
                    nro += 1
                except:
                    key=-1
            resulting_message = u''
            if nro > 1:
                resulting_message = u'Los items fueron borrados'
            elif nro == 1:
                resulting_message = u'El item fue borrado'
            self.message_user(request, resulting_message)
        if '_popin' in request.GET:
            return HttpResponse('<script type="text/javascript">\
window.opener.location.href = window.opener.location.href; window.close();\
</script>')
        return HttpResponseRedirect('../')

    def add_view(self, request, form_url='', extra_context=None):
        """
        redirecciona al changelist de planos, ya que en cada change_view de los
        planos se encuentra la herramienta para agregar items dibujando sus 
        regiones
        """
        msg = u'Para agregar items, utilice la herramienta que esta en la \
página de edición de planos. Seleccione uno de los planos a continuación y\
 agrege items dibujando en sus regiones.'
        self.message_user(request, msg)
        return HttpResponseRedirect(
            reverse('admin:proyectos_plano_changelist'))

    def change_view(self, request, object_id, extra_context=None):
        """
        gestiona la edicion de items, si encuentra popup en la url 
        luego de realizar las gestiones correspondientes cierra la ventana
        """
        item = get_object_or_404(Item, id=object_id)
        cliente_name = item.cliente
        #print item
        form = AdminEditItemForm(instance=item)
        is_popup = False
        if '_popup' in request.GET:
            is_popup = True
        if request.method == 'POST':
            form = AdminEditItemForm(request.POST)
            form.set_user_id(unicode(request.user.id))
            if form.is_valid():
                form.save()
                if '_popup' in request.GET:
                    return HttpResponse('<script type="text/javascript">\
window.opener.location.href = window.opener.location.href; window.close();\
</script>')
                msg = u'El item fue actualizado correctamente'
                self.message_user(request, msg)
                return HttpResponseRedirect('../')
        return render_to_response(
            'admin/proyectos/item/change_form.html',
            {'form':form, 'is_popup':is_popup, 'cliente_name':cliente_name,},
            context_instance=RequestContext(request))

#     def response_change(self, request, obj):
#         """
#         si _popup=1 fue puesto en la url entonces actualiza al padre y cierra
#         al popin
#         """
#         if '_popup' in request.GET:
#             return HttpResponse('<script type="text/javascript">window.opener\
# .location.href = window.opener.location.href; window.close();</script>')
#         return super(self.__class__,self).response_change(request, obj)
            
    def ajax_search_clientes(self, request):
        """
        retorna los usuario que coincidan con el patron de busqueda
        """
        if request.method == 'GET':
            try:
                patron = request.GET['patron']
                queryset = Cliente.objects.filter( 
                    Q(usuario__first_name__icontains=patron) | \
Q(usuario__last_name__icontains=patron) 
                    )
                lista = "".join("<li class='result' name='%s'>%s</li>" % \
(c.id,c.fullName()) for c in queryset)
                if not lista:
                    lista = "<li>No hay resultados</li>"
                data = {'lista':lista}
            except:
                data = {'response' : 'error'}
            return json_response(data)
        return None
            

class TipoItemAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'area', 'precio', 'proyecto',)
    list_display_links = ('nombre', 'area', 'precio', 'proyecto',)
    list_filter = ('proyecto', 'nombre',)
    actions = ['borrar_tipoitem',]
    form = AdminTipoItemForm

    def queryset(self, request):
        """
        solo los super usuarios tienen acceso a todos acances de todo los 
        proyectos, los demas usuarios solo tendran acceso a los avances de los
        proyectos donde estan asociados
        """
        qs = super(self.__class__, self).queryset(request)
        if request.user.is_superuser:
            return qs;
        return qs.filter(proyecto__usuarios__id=request.user.id)

    def get_urls(self):
        urls = super(self.__class__, self).get_urls()
        my_urls = patterns(
            '',
            url(r'^delete_tipositem/$', 
                self.admin_site.admin_view(self.delete_tipositem),
                name='admin_tipositem_delete'),

                           )
        return my_urls + urls

    def delete_view(self, request, object_id, extra_context=None):
        """
        vista que redirecciona el delete del add or edit view a la vista
        borrar_tipoitem
        """
        return self.borrar_tipoitem(
            request, TipoItem.objects.filter(id=object_id))

    def get_actions(self, request):
        """
        funcion that disables some admins actions in this model
        """
        actions = super(self.__class__, self).get_actions(request)
        del actions['delete_selected']
        return actions    

    def borrar_tipoitem(self, request, queryset):
        """
        borra los tipos de item seleccionados sí y sólo si no estan asociados
        a items, sino retorna una pagina mostrando los items relacionados
        """
        related_items = []
        related_ofertas = []
        toDelete=True
        for ti in queryset:
            item_set = ti.item_set.all()
            if item_set:
                related_items.append( ( ti , item_set ) )
                toDelete=False
            oferta_set = ti.oferta_set.all()
            #if oferta_set:
            related_ofertas.append( ( ti, oferta_set ) )
        if toDelete:
            return render_to_response(
                'admin/proyectos/tipoitem/confirm_delete.html',
                {'related_ofertas': related_ofertas,
                 'numRelOfer': len(related_ofertas)},
                context_instance=RequestContext(request))            
        else:
            return render_to_response(
                'admin/proyectos/tipoitem/unable_to_delete.html',
                {'related_items':related_items,
                 'numRelItems': len(related_items)},
                context_instance=RequestContext(request))

    borrar_tipoitem.short_description = 'Borrar tipos de items seleccionados'

    def delete_tipositem(self, request):
        """
        borra los tipos de items seleccionados
        """
        if request.method == 'POST':
            nro = 0
            for key in request.POST.keys():
                try: 
                    int(key)
                    e = get_object_or_404(TipoItem, id=request.POST[key])
                    #verificando una vez mas que no esta asociado a ningun item
                    if not e.item_set.all():
                        e.delete()
                        nro += 1
                except:
                    key=-1
            resulting_message = u''
            if nro > 1:
                resulting_message = u'Los tipos de items fueron borrados'
            elif nro == 1:
                resulting_message = u'El tipo de item fue borrado'
            self.message_user(request, resulting_message)
        return HttpResponseRedirect('../')


class TipoItemNombreAdmin(admin.ModelAdmin):
    actions = ['borrar_tipositemnombre']

    # def has_delete_permission(self, request, obj=''):
    #     """
    #     evita que se puedan borrar objecto desde el edit o add view
    #     """
    #     return False

    def delete_view(self, request, object_id, extra_context=None):
        """
        vista que redirecciona el delete del add or edit view a la vista
        borrar_tipoitem
        borra el tipo de item sí y sólo si no esta asociado a items,
        sino retorna una pagina mostrando los items relacionados
        """
        obj=get_object_or_404(TipoItemNombre, id=object_id)
        if not obj.tipoitem_set.all():
            obj.delete()
            msg2 = u'El nombre de tipo de item fue eliminado'
            self.message_user(request, msg2)
        else: 
            msg0 = u'Sólo se pueden borrar los nombres de tipo de\
 item que no estan asociados a ningún tipo de item.'
            messages.warning(request,msg0)
            msg1 = u'El nombre de tipo de item no fue borrado'
            messages.error(request,msg1)
        return HttpResponseRedirect(reverse(
                'admin:proyectos_tipoitemnombre_changelist'))

    def get_actions(self, request):
        """
        funcion that disables some admins actions in this model
        """
        actions = super(self.__class__, self).get_actions(request)
        del actions['delete_selected']
        return actions    

    # def get_urls(self):
    #     urls = super(self.__class__, self).get_urls()
    #     my_urls = patterns(
    #         '',
    #         url(r'^delete_tipositemnombre/$', 
    #             self.admin_site.admin_view(self.borrar_tipositemnombre),
    #             name='admin_tipositemnombre_delete'),

    #                        )
    #     return my_urls + urls

    def borrar_tipositemnombre(self, request, queryset):
        """
        borra los nombres de tipo de item seleccionados sí y sólo si no
        estan asociados a ningun tipo de item
        """
        nonDeleted = u''
        Deleted=u''
        for t in queryset:
            if not t.tipoitem_set.all():
                t.delete()
                Deleted+=t.nombre+', '
            else: 
                nonDeleted+=t.nombre+', '
        if nonDeleted:
            msg0 = u'Sólo se pueden borrar los nombres de tipo de item que no \
estan asociados a ningún tipo de item.'
            messages.warning(request,msg0)
            nonDeleted = nonDeleted[:-2]
            msg1 = u'Los siguientes nombres de tipo de item no fueron borrados:\
 ' + nonDeleted
            messages.error(request,msg1)
        if Deleted:
            Deleted = Deleted[:-2]
            msg2 = u'Los siguienes nombres de tipo de item fueron eliminados: \
' + Deleted
            self.message_user(request, msg2)
    borrar_tipositemnombre.short_description = 'Borrar nombres de tipo de item \
seleccionados'


class DesarrolladoAdmin(admin.ModelAdmin):
    form = DesarrolladoAdminForm


admin.site.register(Rubro, RubroAdmin)
admin.site.register(Proyecto, ProyectoAdmin)
admin.site.register(Etapa, EtapaAdmin,)
admin.site.register(Plano, PlanoAdmin)
admin.site.register(Avance, AvanceAdmin)
admin.site.register(Aviso, AvisoAdmin)
admin.site.register(Oferta, OfertaAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(TipoItem, TipoItemAdmin)
admin.site.register(TipoItemNombre, TipoItemNombreAdmin)
admin.site.register(Desarrollado, DesarrolladoAdmin)
