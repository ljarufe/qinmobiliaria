# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.forms.models import modelformset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from common.forms import TelefonoForm
from common.models import Telefono, ViewPort
from common.utils import direct_response, json_response, get_paginated
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib.sites.models import Site
from proyectos.models import Rubro
from usuarios.forms import LoginForm, RegistroClienteForm, EditarClienteForm, \
    InteresesClienteForm, AreaInteresForm, CambiarPasswordForm
from usuarios.models import Cliente, Solicitud
from zinnia.models import Entry


@csrf_exempt
def registro(request):
    """
    Registro de un usuario
    """
    AreasFormSet = modelformset_factory(ViewPort, form=AreaInteresForm, extra=0)
    TelefonoFormSet = modelformset_factory(Telefono, form=TelefonoForm)
    if request.method == 'POST' and "registro_submit" in request.POST:
        form = RegistroClienteForm(request.POST)
        formset_areas = AreasFormSet(request.POST, prefix="area")
        formset_telefonos = TelefonoFormSet(request.POST, prefix="tel")
        if form.is_valid() and formset_telefonos.is_valid() and \
           formset_areas.is_valid():
            form.save(formset_telefonos, formset_areas)

            return direct_response(request, 'usuarios/confirmacion.html')
    elif request.method == "POST" and "registro_rubro_id" in request.POST:
        rubro = Rubro.objects.get(id=request.POST["registro_rubro_id"])
        form = RegistroClienteForm(initial={"rubros_interes": [rubro]})
    else:
        form = RegistroClienteForm()
    formset_areas = AreasFormSet(queryset=ViewPort.objects.none(),
        prefix="area")
    formset_telefonos = TelefonoFormSet(queryset=Telefono.objects.none(),
                                        prefix="tel")

    return direct_response(request, 'usuarios/registro.html',
                           {'form': form,
                            'formset_telefonos': formset_telefonos,
                            'formset_areas': formset_areas})


def registro_corredor(request):
    """
    Registro de un corredor o agente
    """
    return direct_response(request, 'usuarios/registro_corredor.html')


@login_required
def perfil_privado_usuario(request):
    """
    Perfil privado de un usuario
    """
    cliente = get_object_or_404(Cliente, usuario=request.user)
    noticias = Entry.published.all()

    return direct_response(request, 'usuarios/perfil_privado_usuario.html',
                           {'noticias': get_paginated(request, noticias, 2)})


@login_required
@csrf_exempt
def usuario_editar(request):
    """
    Edita los datos básicos de un usuario
    """
    TelefonoFormSet = modelformset_factory(Telefono)
    if request.method == 'POST':
        form = EditarClienteForm(request.POST)
        formset = TelefonoFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            form.save(request.user, formset)
    else:
        cliente = get_object_or_404(Cliente, usuario=request.user)
        form = EditarClienteForm(
            initial={
                'nombre': request.user.first_name,
                'apellido': request.user.last_name,
                'email': request.user.email,
                'direccion': cliente.direccion,
                'provincia': cliente.provincia,
            }
        )
        formset = TelefonoFormSet(queryset=cliente.telefonos.all())

    return direct_response(request, 'usuarios/iframes/usuario_editar.html',
            {'form': form,
             'formset': formset})


@login_required
@csrf_exempt
def usuario_intereses(request):
    """
    Edita los intereses de un usuario
    """
    AreasFormSet = modelformset_factory(ViewPort, form=AreaInteresForm, extra=0)
    cliente = get_object_or_404(Cliente, usuario=request.user)
    areas = cliente.areas_interes.all()
    if request.method == "POST":
        form = InteresesClienteForm(request.POST)
        formset = AreasFormSet(request.POST, queryset=areas)
        if form.is_valid() and formset.is_valid():
            form.save(cliente, formset)
            formset = AreasFormSet(queryset=cliente.areas_interes.all())
    else:
        form = InteresesClienteForm(
            initial={
                'recibir_email': cliente.recibir_email,
                'rastrear_proyectos': cliente.rastrear_proyectos,
            }
        )
        formset = AreasFormSet(queryset=cliente.areas_interes.all())

    return direct_response(request, "usuarios/iframes/usuario_intereses.html",
                           {"form": form,
                            "formset": formset,
                            "areas": areas,
                            "rubros": cliente.rubros.all()})


@login_required
def usuario_subscripciones(request):
    """
    Edita las subscripciones a proyectos del usuario
    """
    cliente = get_object_or_404(Cliente, usuario=request.user)
    afiliaciones = cliente.proyectos.all()

    return direct_response(request, 'usuarios/iframes/usuario_subscripciones.html',
            {'afiliaciones': get_paginated(request, afiliaciones, 3)})


# TODO: Optimizar
@login_required
def usuario_separados(request):
    """
    Edita los lotes separados por el cliente
    """
    cliente = get_object_or_404(Cliente, usuario=request.user)
    solicitudes = Solicitud.objects.filter(
        cliente=cliente, tipo=u"S").order_by("proyecto")
    esquema = list(solicitudes.values("proyecto").order_by("proyecto").distinct())
    solicitudes = list(solicitudes)
    for item in esquema:
        solicitudes_item = []
        for solicitud in solicitudes:
            if solicitud.proyecto.id == item["proyecto"]:
                solicitud.cancelando = Solicitud.objects.filter(
                    cliente=cliente, item=solicitud.item, tipo=u"C", estado=u"E").exists()
                solicitudes_item.append(solicitud)
        item["solicitudes"] = solicitudes_item
        item["proyecto"] = solicitudes_item[0].proyecto

    return direct_response(request, 'usuarios/iframes/usuario_separados.html',
            {'esquema': esquema})


@csrf_exempt
def simple_form(request, Form, template):
    """
    Manejador de formularios simples
    """
    if request.method == 'POST':
        form = Form(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = Form()

    return direct_response(request, template, {'form': form})


@csrf_exempt
def log_in(request):
    """
    Manejador de formularios simples
    """
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            form.save(request)
    else:
        form = LoginForm()

    return direct_response(request, 'usuarios/iframes/login.html',
                           {'form': form,
                            'fb_api_id': settings.FACEBOOK_API_ID,
                            'hostname': Site.objects.get_current().name})


@login_required
def log_out(request):
    """
    logout
    """
    logout(request)

    return HttpResponseRedirect(reverse('inicio'))


def verificar(request, clave_activacion):
    """
    Coloca un usuario como activo después de acceder mediante la url con la
    clave de activación, esto se da a traves del mail de confirmación enviado al
    usuario
    """
    cliente = get_object_or_404(Cliente, clave_activacion=clave_activacion)
    cliente.usuario.is_active = True
    cliente.usuario.save()

    return HttpResponseRedirect(reverse('inicio') + "?uc_verified=true")


def cambio_password(request, clave_activacion, password):
    """
    Cambio de contraseña validada por el usuario mediante su mail al recuperar
    contraseña desde la página
    """
    cliente = Cliente.objects.get(clave_activacion=clave_activacion)
    cliente.set_password(password)

    return HttpResponseRedirect(reverse('inicio'))


@login_required
@csrf_exempt
def usuario_cambiar_password(request):
    """
    Cambio de contraseña mediante el formulario de edición de usuario
    """
    if request.method == "POST":
        form = CambiarPasswordForm(request.POST, username=request.user.username)
        if form.is_valid():
            form.save(request)
    else:
        form = CambiarPasswordForm()

    return direct_response(request, "usuarios/iframes/cambiar_password.html",
                           {"form": form})


def fb_channel(request):
    """
    Template para fijar la fecha de caducidad de las cookies utilizadas por fbsdk
    Debe tener una fecha de expiración muy alta
    """

    return direct_response(request, "usuarios/fb_channel.html")


def json_registro(request):
    """
    Registra un usuario a traves de la data envíada por ajax, por ejemplo desde
    el login por fb
    """
    if request.method == 'GET':
        if "username" in request.GET and \
           User.objects.filter(username=request.GET["username"]).exists():
            user = authenticate(username=request.GET["username"], password="fb")
            data = {"exists": True}
        elif "id" in request.GET and \
            User.objects.filter(username=request.GET["id"]).exists():
            user = authenticate(username=request.GET["id"], password="fb")
            data = {"exists": True}
        else:
            if 'username' in request.GET:
                user = User.objects.create_user(request.GET["username"],
                                                request.GET["email"], "fb")
            else:
                if "id" not in request.GET:
                    return json_response({})
                user = User.objects.create_user(request.GET["id"],
                                                request.GET["email"], "fb")
            user.is_active = False
            user.first_name = request.GET["first_name"]
            user.last_name = request.GET["last_name"]
            user.save()
            cliente = Cliente(usuario=user)
            cliente.save()
            data = {"exists": False}
            user = authenticate(username=user.username, password="fb")
        login(request, user)

        return json_response(data)
    else:
        return json_response({})


@login_required
def json_cancelar_solicitud(request):
    """
    Un usuario cancela su solicitud de separación de un item
    """
    if request.method == "GET":
        if 'id_solicitud' in request.GET:
            cliente = Cliente.objects.get(usuario=request.user)
            solicitud = get_object_or_404(
                Solicitud, cliente=cliente, id=request.GET["id_solicitud"])
            if solicitud.estado == u"E":
                solicitud.estado = u"C"
                solicitud.save()
                message = u"Su solicitud ha sido cancelada"
                cancelado = True
            else:
                solicitud_c = Solicitud(tipo=u"C", cliente=cliente,
                                        item=solicitud.item,
                                        proyecto=solicitud.proyecto)
                solicitud_c.save()
                message = u"Se ha enviado una solicitúd de cancelación, será " \
                          u"informado por medio de un e-mail"
                cancelado = False

            return json_response({"cancel_response": message,
                                  "status": True,
                                  "cancelado": cancelado})
        else:
            return json_response({})
    else:
        return json_response({})
