# -*- coding: utf-8 -*-

from common.forms import TelefonoForm
from common.models import Telefono, ViewPort
from common.utils import direct_response, json_response
from django.forms.models import modelformset_factory
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.sites.models import Site
from django.db.models.aggregates import Min
from portal.forms import BusquedaForm, ContactoForm, ChatForm
from portal.models import Inmobiliaria, Area
from proyectos.models import Aviso, Proyecto, Desarrollado
from usuarios.forms import AreaInteresForm
from usuarios.models import AdminHelpDesk


def inicio(request):
    """
    Vista de inicio
    """
    return direct_response(request, 'portal/inicio.html',
                           {'destacados': Proyecto.get_destacados(4),
                            'form': BusquedaForm(),
                            'rango_renta': Proyecto.get_rango_precio(u"R"),
                            'rango_venta': Proyecto.get_rango_precio(u"V"),})

@csrf_exempt
def chat(request):
    """
    Chat con los administradores de servicio
    """
    if request.method == "POST":
        form_chat = ChatForm(request.POST)
        if form_chat.is_valid():

            return direct_response(request, "portal/iframes/chat.html",
                    {'form_chat': form_chat})
    else:
        form_chat = ChatForm()

    return direct_response(request, "portal/iframes/chat.html",
                           {'form_chat': form_chat})


def ayuda_en_linea(request, id_area, usuario):
    """
    Crea un canal de chat con uno de lso administradores y registra a ambos
    usuarios para comenzar el chat
    """
    area = get_object_or_404(Area, id=id_area)

    return direct_response(request, 'portal/ayuda_en_linea.html',
            {'port': 9000,
             'hostname': Site.objects.get_current().name,
             'area': area,
             'manager': AdminHelpDesk.get_area_manager(area),
             'usuario': usuario})


# TODO: Colocar las ayudas en flatpages
def ayuda(request, template):
    """
    Carga una página de ayuda
    """
    return direct_response(request, template)


def nosotros(request):
    """
    Vista informativa con datos de la inmobiliaria
    """
    return direct_response(request, 'portal/nosotros.html',
                           {'desarrollados': Desarrollado.objects.all(),
                            'inmobiliaria': Inmobiliaria.objects.latest("id")})


@csrf_exempt
def contacto(request):
    """
    Formulario de contacto
    """
    AreasFormSet = modelformset_factory(ViewPort, form=AreaInteresForm, extra=0)
    TelefonoFormSet = modelformset_factory(Telefono, form=TelefonoForm)
    if request.method == 'POST' and "contacto_submit" in request.POST:
        form = ContactoForm(request.POST)
        formset_areas = AreasFormSet(request.POST, prefix="area")
        formset_telefonos = TelefonoFormSet(request.POST, prefix="tel")
        if form.is_valid() and formset_telefonos.is_valid() and \
           formset_areas.is_valid():
            form.save(request, formset_telefonos, formset_areas)

            return direct_response(request, 'portal/contacto_exito.html')
    elif request.method == "POST" and "contacto_proyecto_id" in request.POST:
        proyecto = Proyecto.objects.get(id=request.POST["contacto_proyecto_id"])
        form = ContactoForm(initial={'proyecto': proyecto.id,
                                     "rubros_interes": [proyecto.rubro]})
    else:
        form = ContactoForm()
    formset_areas = AreasFormSet(queryset=ViewPort.objects.none(),
                                 prefix="area")
    formset_telefonos = TelefonoFormSet(queryset=Telefono.objects.none(),
        prefix="tel")

    return direct_response(request, 'portal/contacto.html',
                           {'form': form,
                            'formset_telefonos': formset_telefonos,
                            'formset_areas': formset_areas})


def json_get_aviso(request):
    """
    Devuelve un aviso según el indice enviado
    """
    if request.method == 'GET' and "index" in request.GET:
        total = Aviso.objects.all().count()
        min_id = Aviso.objects.aggregate(Min("id"))['id__min']
        if total:
            aviso = Aviso.objects.get(id=(int(request.GET['index'])%total)+min_id)
            data = {
                'url': aviso.proyecto.get_absolute_url(),
                'aviso': aviso.get_archivo_html(),
                'duracion': aviso.duracion,
                'status': True,
            }
            return json_response(data)
        else:
            return json_response({'status': False,})
    else:
        return json_response({})


def google_webmaster_verification(request):
    """
    Vista para verificar la propiedad del dominio de quimerainmobiliaria
    """
    return direct_response(request, "portal/google_verification.html")
