# -*- coding: utf-8 -*-

from django import template

register = template.Library()

#{% concatenate id "opciones" as varname %}
@register.tag(name='concatenate')
def do_concatenate(parser, token):
    bits = token.split_contents()
    if len(bits) != 5:
        raise template.TemplateSyntaxError("el tag 'concatenate' toma \
            exactamente 2 argumentos ")
    return ConcatenateNode(bits[1], bits[2], bits[4])

class ConcatenateNode(template.Node):
    """
    Concatena la variable id con el resto de opciones para watermark
    """
    def __init__(self, id, opciones, varname):
        self.id = template.Variable(id)
        self.opciones = opciones
        self.varname = varname

    def render(self, context):
        try:
            id = self.id.resolve(context)
        except template.VariableDoesNotExist:
            return ""
        context[self.varname] = "%s,%s" % (id, self.opciones[1:len(self.opciones)-1])
        return ""
