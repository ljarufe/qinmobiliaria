# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.shortcuts import get_object_or_404
from common.models import Referencia
from common.utils import direct_response, get_paginated, json_response, \
    json_fastsearch, get_object_or_none
from django.views.decorators.csrf import csrf_exempt
from django.http import Http404, HttpResponseRedirect
from datetime import date
from portal.forms import BusquedaForm
from proyectos.models import Rubro, Proyecto, Item, Plano, Desarrollado
from usuarios.models import Cliente
from usuarios.forms import SolicitudForm
from zinnia.models import Entry


@csrf_exempt
def resultados(request, rubro_id=None):
    """
    Resultados de la búsqueda de proyectos
    """
    rubro = get_object_or_none(Rubro, id=rubro_id)
    if request.method == "POST":
        form = BusquedaForm(request.POST)
        if form.is_valid():
            resultado = form.save()
            request.session["resultado"] = resultado
    else:
        form = BusquedaForm()
        if "resultado" in request.session:
            resultado = request.session["resultado"]
        else:
            resultado = Proyecto.accepted.all()
        if rubro:
            resultado = resultado.filter(rubro=rubro)

    return direct_response(request, 'proyectos/resultados.html',
                           {'resultado': get_paginated(request, resultado, 3),
                            'resultados_sp': resultado,
                            'form': form,
                            'cliente': Cliente.get_authenticated(request),
                            'rubros': Rubro.objects.all(),
                            'rubro_activo': rubro,
                            'rango_venta': Proyecto.get_rango_precio(u"V"),
                            'rango_renta': Proyecto.get_rango_precio(u"R"),})


def rubro(request, slug_rubro):
    """
    Perfil de un rubro
    """
    rubro = get_object_or_404(Rubro, slug=slug_rubro)
    proyectos_objects = Proyecto.accepted.filter(rubro=rubro)
    proyectos = get_paginated(request, proyectos_objects, 2)
    noticias_objects = Entry.objects.filter(proyectos__rubro=rubro).distinct()
    noticias = get_paginated(request, noticias_objects, 2)

    return direct_response(request, 'proyectos/rubro.html',
                           {"rubro": rubro,
                            "proyectos": proyectos,
                            "noticias": noticias})


def perfil_proyecto(request, slug_proyecto):
    """
    Perfil de un proyecto

    Ofertas: 1- se elije aleatoriamente una de las ofertas del proyecto con
                fecha_fin posterior a hoy
             2- se elige aleatoriamente uno de los items(con estado disponible)
                pertenecientes al tipo de item en oferta
             3- si puede realizar los pasos anteriores, pone en blanco 
                la oferta y el item
    """
    proyecto = get_object_or_404(Proyecto, ~Q(estado=u'B'), slug=slug_proyecto)
    etapa_actual, subetapa_actual, avance_actual = proyecto.get_etapa_actual()
    relacionados = Proyecto.accepted.filter(rubro=proyecto.rubro).exclude(
        slug=slug_proyecto)
    if proyecto.latitud:
        CLOSE_CONST = 2
        referencias = Referencia.objects.filter(
            latitud__lte=proyecto.latitud+CLOSE_CONST,
            latitud__gte=proyecto.latitud-CLOSE_CONST,
            longitud__lte=proyecto.longitud+CLOSE_CONST,
            longitud__gte=proyecto.longitud-CLOSE_CONST,
        )
    else:
        referencias = None
    # Ofertas
    try:
        oferta = proyecto.oferta_set.filter(
            fecha_fin__gt=date.today(), fecha_inicio__lte=date.today(),
            item__estado=u'D').order_by('?')[0]
        # random_item_id = oferta.tipo_item.item_set.filter(
        #     estado=u'D').order_by('?')[0].id
        random_item_id = oferta.item.id
    except IndexError:
        oferta = ''
        random_item_id = 0
    #items = Item.objects.filter(plano__proyecto=proyecto)

    return direct_response(
        request, 'proyectos/perfil_proyecto.html',
        {"proyecto": proyecto,
         "caracteristicas": proyecto.caracteristica_set.all(),
         "beneficios": proyecto.beneficio_set.all(),
         "referencias": referencias,
         "items_height": Item.objects.filter(plano__proyecto=proyecto).count()*71,
         "cliente": Cliente.get_authenticated(request),
         "etapa_actual": etapa_actual,
         "subetapa_actual": subetapa_actual,
         "avance_actual": avance_actual,
         "relacionados": relacionados,
         'oferta': oferta,
         'random_item_id': random_item_id})


def perfil_desarrollado(request, slug):
    """
    Devuelve el perfil de un proyecto desarrollado
    """
    desarrollado = get_object_or_404(Desarrollado, slug=slug)

    return direct_response(request, "proyectos/perfil_desarrollado.html",
                           {"desarrollado": desarrollado,
                            'desarrollados': Desarrollado.objects.all()})


def items_proyecto(request, proyecto_id):
    """
    Devuelve items paginados de un proyecto
    """
    items = Item.objects.filter(plano__proyecto__id=proyecto_id)

    return direct_response(request, "proyectos/iframes/items_proyecto.html",
                           {"items": get_paginated(request, items, 8)})


def etapas_proyecto(request, slug_proyecto):
    """
    Etapas de un proyecto
    """
    proyecto = get_object_or_404(Proyecto, slug=slug_proyecto)

    return direct_response(request, 'proyectos/esquema_etapas.html',
                           {"proyecto": proyecto,
                            "esquema_avance": proyecto.get_esquema_avance()})


def fotos(request, proyecto_id):
    """
    Devuelve las fotos de un proyecto en un slider
    """
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    fotos = proyecto.fotos.all()

    return direct_response(request, "proyectos/iframes/slider_fotos.html",
                           {"fotos": fotos,
                            "foto_principal": proyecto.foto_principal,
                            "nombre_proyecto": proyecto.nombre,
                            "proyecto_id": proyecto_id})


def videos(request, proyecto_id):
    """
    Devuelve los videos de un proyecto en un slider
    """
    videos = get_object_or_404(Proyecto, id=proyecto_id).videos.all()

    return direct_response(request, "proyectos/iframes/slider_videos.html",
            {"videos": videos})


def planos(request, plano_id):
    """
    devuelve los planos interactivos
    """
    plano = get_object_or_404(Plano, id=plano_id)
    queryItems = plano.item_set.all()
    poligons = [i.poligono.get_points_list(True) for i in queryItems]
    polColors = [i.poligono.color_relleno for i in queryItems]
    itemList = [i.id for i in queryItems]
    thumb = plano.plano.extra_thumbnails['plano_size']
    thumb2 = plano.plano.extra_thumbnails['slider_size']

    return direct_response(request, "proyectos/iframes/planos.html",
            {"plano": plano, 'poligons': poligons, 'polColors': polColors,
             'itemList': itemList,'thumb':thumb,'thumb2': thumb2,
             'proyecto': plano.proyecto.id,})


def planos_slider(request, proyecto_id):
    """
    devuelve un slider vertical de los planos que al hacerles click 
    actualizan los planos vivos que se muestran
    """
    planos = get_object_or_404(Proyecto, id=proyecto_id).plano_set.all()

    return direct_response(request, "proyectos/iframes/slider_planos.html",
            {"planos": planos,})
    

def ajax_get_item_data(request):
    """
    retorna el tipo de item y el path a su imagen, el area, el nro de item
    ,estado y su precio
    """
    if request.method == 'GET':
        try:
            item = get_object_or_404(Item, id=request.GET['item_id'])
            data = {'tipo': item.tipo_item.nombre.nombre,
                    'img_path': item.tipo_item.foto.extra_thumbnails\
                        .get('small_upscale').absolute_url,
                    'area': item.tipo_item.area,
                    'nro': item.numero,
                    'estado': item.estado,
                    'precio': item.tipo_item.precio,
                    'response': 'ok',
                    }
        except:
            data = {'response' : 'error'}
        return json_response(data)
    return None


def solicitud(request, item_id):
    """
    muestra la pagina con el formulario para separar item

    verifica que el item existe y esta disponible, antes de realizar cualquier
    procesamiento

    Ofertas:
    Verifica si esta en oferta el item filtrando sus ofertas con fecha_fin
    mayor a hoy, y filtrando las ofertas con fecha_inicio mayor o igual a hoy.
    Dato que las ofertas de un tipo de item con pueden superponerse con las 
    de inicio y fin, de obtenerse un resultado este sera unico
    
    """
    item = get_object_or_404(Item, id=item_id)
    proyecto = item.plano.proyecto
    if item.estado != u'D':
        return HttpResponseRedirect(item.plano.proyecto.get_absolute_url())
    img_path = item.tipo_item.foto.extra_thumbnails\
        .get('small_upscale').absolute_url
    poligon = item.poligono.get_points_list(True)
    try:
        oferta = item.oferta_set.filter(
            fecha_fin__gt=date.today(), fecha_inicio__lte=date.today(),
            item__estado=u'D')[0]
    except:
        oferta = ''
    form = SolicitudForm()
    if request.user.is_anonymous():
        return direct_response(request, "proyectos/solicitud.html",
                               {'form':form, 'anonimo':True, 'item':item,
                                'img_path':img_path, 'poligon':poligon,
                                'proyecto':proyecto, 'oferta':oferta,})
    if request.method == 'POST':
        cliente = get_object_or_404(Cliente, usuario=request.user)
        postRequest = request.POST.copy()
        postRequest['cliente'], postRequest['item'] = cliente.id, item.id
        form = SolicitudForm(postRequest)
        if form.is_valid():
            form.save(cliente, item)
            return HttpResponseRedirect(
                reverse('proyectos_solicitud_enviada', args=[item_id]) )
    return direct_response(request, "proyectos/solicitud.html",
                               {'form':form, 'anonimo':False, 'item':item,
                                'img_path':img_path, 'poligon':poligon,
                                'proyecto':proyecto, 'oferta':oferta,})

def plano_item(request, item_id):
    """
    muestra la pagina con el item dibujado en su plano correspondiente

    Ofertas:
    Verifica que no este en oferta el item filtrando sus ofertas con fecha_fin
    mayor a hoy, y filtrando las ofertas con fecha_inicio mayor o igual a hoy.
    Dato que las ofertas de un tipo de item con pueden superponerse con las 
    de inicio y fin, de obtenerse un resultado este sera unico
    
    """
    item = get_object_or_404(Item, id=item_id)
    proyecto = item.plano.proyecto
    img_path = item.tipo_item.foto.extra_thumbnails\
        .get('small_upscale').absolute_url
    poligon = item.poligono.get_points_list(True)
    color = item.poligono.color_relleno
    #polColors = [i.poligono.color_relleno for i in queryItems]
    try:
        oferta = item.tipo_item.oferta_set.filter(
            fecha_fin__gt=date.today() ).filter(
            fecha_inicio__gte=date.today() )[0]
    except:
        oferta = ''
#    if request.user.is_anonymous():
    return direct_response(request, "proyectos/plano_item.html",
                           {'item':item,
                            'img_path':img_path, 'poligon':poligon,
                            'color':color, 'proyecto':proyecto, 
                            'oferta':oferta,})


@login_required    
def solicitud_enviada(request, item_id):
    """
    pagina que se muestra luego que se envia con exito una solicitud
    """
    item = get_object_or_404(Item, id=item_id)
    if item.estado  != u'D':
        return HttpResponseRedirect(item.plano.proyecto.get_absolute_url())
    return direct_response(request, "proyectos/solicitud_enviada.html",
                           {'item':item,
                            'img_path':item.tipo_item.foto.extra_thumbnails\
                                .get('small_upscale').absolute_url,
                            'poligon':item.poligono.get_points_list(True),
                            'proyecto':item.plano.proyecto,})
    

def venta_terreno(request):
    """
    Formulario para que un usuario ofrezca su terreno
    """
    return direct_response(request, 'proyectos/venta_terreno.html')


@login_required
def json_suscribir(request):
    """
    Suscribe un cliente a un rubro mediante ajax
    """
    if request.method == 'GET':
        if 'rubro' in request.GET:
            rubro = get_object_or_404(Rubro, id=request.GET['rubro'])
            cliente = get_object_or_404(Cliente, usuario=request.user)
            cliente.rubros.add(rubro)
            data = {"status": True}

            return json_response(data)
        else:
            return json_response({})
    else:
        return json_response({})


@login_required
def json_desuscribir(request):
    """
    Quita la suscripcion a un rubro de un cliente
    """
    if request.method == 'GET':
        if 'id_rubro' in request.GET:
            rubro = get_object_or_404(Rubro, id=request.GET['id_rubro'])
            cliente = get_object_or_404(Cliente, usuario=request.user)
            cliente.rubros.remove(rubro)
            data = {"status": True}

            return json_response(data)
        else:
            return json_response({})
    else:
        return json_response({})


@login_required
def json_afiliar(request):
    """
    Afilia a un cliente a un proyecto en específico
    """
    if request.method == 'GET':
        if 'proyecto' in request.GET:
            proyecto = get_object_or_404(Proyecto, id=request.GET['proyecto'])
            cliente = get_object_or_404(Cliente, usuario=request.user)
            proyecto.clientes.add(cliente)
            data = {"status": True}

            return json_response(data)
        else:
            return json_response({})
    else:
        return json_response({})


@login_required
def json_desafiliar(request):
    """
    Desafilia a un cliente de un proyecto en específico
    """
    if request.method == 'GET':
        if 'id_proyecto' in request.GET:
            proyecto = get_object_or_404(Proyecto, id=request.GET['id_proyecto'])
            cliente = get_object_or_404(Cliente, usuario=request.user)
            proyecto.clientes.remove(cliente)
            data = {"status": True}

            return json_response(data)
        else:
            return json_response({})
    else:
        return json_response({})


def json_proyectos_slider(request):
    """
    Devuelve un proyecto según el índice enviado
    """
    if request.method == 'GET':
        if 'proyectos' in request.session:
            proyectos = request.session['proyectos']
        else:
            proyectos = Proyecto.accepted.all().order_by('relevancia')
            request.session['proyectos'] = proyectos
        if proyectos:
            proyecto = proyectos[int(request.GET['index']) % proyectos.count()]
            data = {
                'nombre': proyecto.nombre,
                'rubro': proyecto.rubro.nombre,
                'url': proyecto.get_absolute_url(),
                'imagen': '%s' % proyecto.foto_principal.extra_thumbnails.get("small_slider").absolute_url,
            }

            return json_response(data)
        else:
            raise Http404
    else:
        return json_response({})


def json_fast_proyectos(request):
    """
    Búsqueda de una subcadena de texto dentro de los nombres de proyectos
    """
    if request.method == 'GET':
        proyectos = Proyecto.accepted.all()

        return json_fastsearch(proyectos, 'nombre', request.GET['substring'],
                               {"id": "slug",
                                "name": "nombre",
                                "subtitle": "rubro",
                                "description": "resumen",
                                "image": "foto_principal"})
    else:
        return json_response({})
