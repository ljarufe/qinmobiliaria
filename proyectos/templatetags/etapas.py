# -*- coding: utf-8 -*-

from django import template
from proyectos.models import Etapa, SubEtapa

#tag {% get_all_subEtapas etapa as subEtapasList %}
def do_getAllSubetapas(parser, token):
    bits = token.split_contents()
    if len(bits) != 4:
       raise template.TemplateSyntaxError("el tag 'get_all_subEtapas' toma \
 exactamente 3 argumentos. ")
    return GetAllSubetapasNode(bits[1], bits[3])
    
class GetAllSubetapasNode(template.Node):
    """
        retorna una lista de todas las subetapas de la etapa
    """    
    def __init__(self, etapa, varname):
        self.etapa = template.Variable(etapa)
        self.varname = varname
        
    def render(self, context):
        try:
            etapa = self.etapa.resolve(context)
        except template.VariableDoesNotExist:
            return ''
        if etapa:
            context[self.varname] = etapa.subetapa_set.all()
        return ''

        
register = template.Library()
register.tag('get_all_subEtapas', do_getAllSubetapas)
