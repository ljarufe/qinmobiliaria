# -*- coding: utf-8 -*-

from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.date_based import archive_year
from django.views.generic.date_based import archive_month
from django.views.generic.date_based import archive_day
from common.utils import direct_response, get_paginated
from zinnia.forms import CommentForm
from zinnia.models import Entry
from zinnia.views.decorators import update_queryset

entry_year = update_queryset(archive_year, Entry.published.all)

entry_month = update_queryset(archive_month, Entry.published.all)

entry_day = update_queryset(archive_day, Entry.published.all)


@csrf_exempt
def entry_detail(request, year, month, day, slug):
    """
    Detalle de una entrada del blog
    """
    entry = get_object_or_404(Entry, creation_date__year=year,
                              creation_date__month=month, creation_date__day=day,
                              slug=slug)
    if request.method == "POST":
        form = CommentForm(entry, request.POST)
        if form.is_valid():
            form.save()
            form = CommentForm(entry)
    else:
        form = CommentForm(entry)

    return direct_response(request, "zinnia/portal/entrada.html",
                           {"entry": entry,
                            "entries": Entry.published.exclude(id=entry.id)[:2],
                            "form": form})


def entry_index(request):
    """
    Entradas para la página de inicio
    """
    entries = Entry.published.all()

    return direct_response(request, "zinnia/portal/lista.html",
                           {"entries": get_paginated(request, entries, 5)})


def entry_shortlink(request, object_id):
    """
    Redirect to the 'get_absolute_url' of an Entry,
    accordingly to 'object_id' argument
    """
    entry = get_object_or_404(Entry, pk=object_id)
    return redirect(entry, permanent=True)


def fotos(request, entry_id):
    """
    Devuelve las fotos de una entrada en un slider
    """
    noticia = get_object_or_404(Entry, id=entry_id)
    fotos = noticia.fotos.all()

    return direct_response(request, "zinnia/iframes/slider_fotos.html",
                           {"fotos": fotos,
                            "foto_principal": noticia.image,
                            "nombre_noticia": noticia.title})


def videos(request, entry_id):
    """
    Devuelve los videos de un proyecto en un slider
    """
    videos = get_object_or_404(Entry, id=entry_id).videos.all()

    return direct_response(request, "zinnia/iframes/slider_videos.html",
                           {"videos": videos})