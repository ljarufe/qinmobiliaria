# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404
from common.utils import direct_response, get_paginated
from zinnia.models import Category


def get_category_or_404(path):
    """
    Retrieve a Category by a path
    """
    path_bits = [p for p in path.split('/') if p]
    return get_object_or_404(Category, slug=path_bits[-1])


def category_detail(request, path, page=None, **kwargs):
    """
    Muestra las entradas relacionadas a una categoría
    """
    categoria = get_category_or_404(path)
    entries = categoria.entries_published()

    return direct_response(request, "zinnia/portal/categoria.html",
                           {"categoria": categoria,
                            "entries": get_paginated(request, entries, 3)})
