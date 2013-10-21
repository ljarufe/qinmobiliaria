# -*- coding: utf-8 -*-

from django.http import HttpResponse
import stomp
import json
from common.utils import direct_response
from django.contrib.auth.decorators import permission_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.sites.models import Site
from django.shortcuts import get_object_or_404
from usuarios.models import AdminHelpDesk

conn = stomp.Connection()
conn.start()
conn.connect()

@permission_required('auth.puede_help_desk')
def ayuda_clientes(request):
    """
    Ayuda a clientes, el manager esta subscrito a un canal con su nombre de
    usuario donde recibirá requests de los clientes
    """
    conn.subscribe(destination="/%s" % request.user.username, ack="auto")
    manager = get_object_or_404(AdminHelpDesk, usuario=request.user)
    manager.conectar()

    return direct_response(request, 'usuarios/ayuda_cliente.html',
            {'port': 9000,
             'hostname': Site.objects.get_current().name})


@csrf_exempt
def send_message(request):
    """
    Envío de un mensaje
    """
    destination = request.POST.get("destination", "")
    msg = {
        "code": 2,
        "sender": request.POST.get("sender", ""),
        "message": request.POST.get("message", ""),
        "client": destination.split("/")[2],
    }
    json_msg = json.dumps(msg)
    conn.send(json_msg, destination=destination)

    return HttpResponse("ok")


@csrf_exempt
def manager_request(request):
    """
    Un usuario requiere ayuda en linea de una de las áreas
    """
    cliente = request.POST.get("sender", "")
    manager = request.POST.get("manager", "")
    msg = {
        "code": 1,
        "sender": cliente,
        }
    json_msg = json.dumps(msg)
    conn.send(json_msg, destination="/%s" % manager)

    # TODO: si esta suscrito ya, no hay que suscribirlo de nuevo
    conn.subscribe(destination="/%s/%s" % (manager, cliente), ack='auto')

    return HttpResponse("ok")