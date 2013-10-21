from django import template
#from django.contrib.auth.models import User

register = template.Library()

#{%  BelongsToGroup user groupname as varname %}
@register.tag(name='BelongsToGroup')
def do_ifBelongsToGroup(parser, token):
    bits = token.split_contents()
    if len(bits) != 5:
       raise template.TemplateSyntaxError("el tag 'BelongsToGroup' toma \
exactamente 4 argumentos ")
    return BelongsToGroupNode(bits[1], bits[2], bits[4])
    
class BelongsToGroupNode(template.Node):
    """
    si el usuario pertenece al grupo groupname o es superuser retorna en 
    varname True, sino retorna en varname False
    """    
    def __init__(self, user, groupname, varname):
        self.user = template.Variable(user)        
        self.groupname = groupname
        self.varname = varname

    def render(self, context):
        try:
            user = self.user.resolve(context)
        except template.VariableDoesNotExist:
            return ''
        if user.is_superuser:
            context[self.varname] = True
        else:
            context[self.varname] = False
            for g in user.groups.all():
                if g.name == self.groupname:
                    context[self.varname] = True
                    break
        return ''





