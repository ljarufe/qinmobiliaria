#-*- coding: utf-8 -*-

from datetime import datetime
import re
from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from tinymce.widgets import TinyMCE
from portal.models import Area, Inmobiliaria
from proyectos.models import Rubro, Proyecto
from usuarios.models import Cliente, MensajeFormularioContacto
from common.utils import send_html_mail
from common.validators import validate_name


class InmobiliariaForm(forms.ModelForm):
    """
    Formulario para el admin de la inmobiliaria
    """
    introduccion = forms.CharField(
        widget=TinyMCE(attrs={'cols': 100, 'rows': 20}), required=False)
    mision = forms.CharField(
        widget=TinyMCE(attrs={'cols': 100, 'rows': 20}), required=False)
    vision = forms.CharField(
        widget=TinyMCE(attrs={'cols': 100, 'rows': 20}), required=False)
    historia = forms.CharField(
        widget=TinyMCE(attrs={'cols': 100, 'rows': 20}), required=False)
    desarrollados = forms.CharField(
        widget=TinyMCE(attrs={'cols': 100, 'rows': 20}), required=False)

    class Meta:
        model = Inmobiliaria


class HorizRadioRenderer(forms.RadioSelect.renderer):
    """
    This overrides widget method to put radio buttons horizontally
    instead of vertically.
    """
    def render(self):
        """
        Outputs radios
        """
        return mark_safe(u'\n'.join([u'%s\n' % w for w in self]))


class BusquedaForm(forms.Form):
    """
    Formulario para la búsqueda de proyectos
    """
    nombre = forms.CharField(label=_(u"Nombre"), required=False,
                             help_text=u"Este campo no es necesario")
    ubicacion = forms.CharField(label=_(u"Ubicación"), required=False)
    rubro = forms.ModelChoiceField(
        queryset=Rubro.objects.all(),
        label=_(u"Rubro"),
        required=False,
        empty_label=u"Todos los rubros",
    )
    TIPO_CONTRATO_CHOICES = (
        (u"R", _(u"Renta")),
        (u"V", _(u"Venta")),
        (u"T", _(u"Todo")),
    )
    tipo = forms.ChoiceField(
        widget=forms.RadioSelect(renderer=HorizRadioRenderer,),
        choices=TIPO_CONTRATO_CHOICES,
        required=False, initial=u"T", label=_(u"Tipo"))
    max_precio = forms.CharField(widget=forms.HiddenInput, required=False)
    min_precio = forms.CharField(widget=forms.HiddenInput, required=False)
    location = forms.CharField(widget=forms.HiddenInput, required=False)
    hi_lat = forms.CharField(widget=forms.HiddenInput, required=False)
    hi_lon = forms.CharField(widget=forms.HiddenInput, required=False)
    lo_lat = forms.CharField(widget=forms.HiddenInput, required=False)
    lo_lon = forms.CharField(widget=forms.HiddenInput, required=False)
    
    def save(self):
        """
        Devuelve una queryset de los proyectos filtrando los resultados según el
        formulario de búsqueda
        """
        resultado = Proyecto.accepted.all()
        if self.cleaned_data['rubro']:
            resultado = resultado.filter(rubro=self.cleaned_data['rubro'])
        if self.cleaned_data['tipo'] and self.cleaned_data['tipo'] != u"T":
            resultado = resultado.filter(tipo_contrato=self.cleaned_data['tipo'])
        if self.cleaned_data['max_precio']:
            resultado = resultado.filter(
                precio_maximo__lte=self.cleaned_data['max_precio'],
                precio_minimo__gte=self.cleaned_data['min_precio']
            )
        if self.cleaned_data['hi_lat']:
            resultado = resultado.filter(
                latitud__lte=self.cleaned_data['hi_lat'],
                latitud__gte=self.cleaned_data['lo_lat'],
                longitud__lte=self.cleaned_data['hi_lon'],
                longitud__gte=self.cleaned_data['lo_lon'],
            )

        return resultado


class ContactoForm(forms.Form):
    """
    Formulario de registro para un cliente
    """
    nombre = forms.CharField(label=_(u"Nombre"), validators=[validate_name])
    apellido = forms.CharField(label=_(u"Apellido"),
                               validators=[validate_name])
    email = forms.EmailField(label=_(u"e-mail"))
    mensaje = forms.CharField(label=_(u"Mensaje"), widget=forms.Textarea)
    rubros_interes = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        queryset=Rubro.objects.all(),
        label=_(u"Rubros de interés"),
        required=False
    )
    proyecto = forms.ModelChoiceField(queryset=Proyecto.objects.all(), 
                                      required=False, widget=forms.HiddenInput)
    recibir_email = forms.BooleanField(label=_(u"Recibir e-mails"),
                                       required=False)
    rastrear_proyectos = forms.BooleanField(label=_(u"Rastrear proyectos"),
                                            required=False)

    def save(self, request, formset_telefonos, formset_areas):
        """
        Guarda al nuevo cliente con sus preferencias y crea un usuario
        ademas envia los mails que correspondan al usuario y a los 
        administradores correspondientes
        """
        # TODO: No está mandando todos los mails, se debe mandar un solo mail al registrrse
        newcli = False
        if request.user.is_authenticated():
            cliente = Cliente.objects.get(usuario=request.user)
        else:
            try:
                cliente = Cliente.objects.get(usuario__username=self.cleaned_data['email'])
            except Cliente.DoesNotExist:
                newcli = True
                usuario = User.objects.create_user(
                    username=self.cleaned_data['email'],
                    email=self.cleaned_data['email'],
                    password="contacto"
                )
                usuario.first_name = self.cleaned_data['nombre']
                usuario.last_name = self.cleaned_data['apellido']
                usuario.is_active = False
                usuario.save()
                cliente = Cliente(usuario=usuario)
                cliente.save()

        cliente.recibir_email = self.cleaned_data['recibir_email']
        cliente.rastrear_proyectos = self.cleaned_data['rastrear_proyectos']
        for rubro in self.cleaned_data['rubros_interes']:
            cliente.rubros.add(rubro)
        for form_telefono in formset_telefonos.forms:
            telefono = form_telefono.save()
            cliente.set_telefono(telefono)
#        proyectos = []
        for form_area in formset_areas.forms:
            area_interes = form_area.save()
            # proyectos += Proyecto.accepted.filter(
            #     latitud__lte=area_interes.high_latitud,
            #     latitud__gte=area_interes.low_latitud,
            #     longitud__lte=area_interes.high_longitud,
            #     longitud__gte=area_interes.low_longitud,
            # )
            cliente.areas_interes.add(area_interes)
        cliente.save()

        #si es un nuevo cliente envia el mail para confirmar el registro y 
        #envia los mails de bienvenida de cada rubro que selecciono el usuario
        if newcli:
            send_html_mail(settings.DEFAULT_FROM_EMAIL,
                           u"Registro en Quimera Inmobiliaria",
                           "confirmar_registro_contacto.html",
                           {"cliente": cliente,
                            "sitio": Site.objects.get_current(),
                            "STATIC_URL": settings.STATIC_URL,
                            "inmobiliaria":Inmobiliaria.objects.get(id=1)
                            },
                           cliente.usuario.email)

            for rubro in cliente.rubros.all():
                #se envia un correo de bienvenida por rubro
                send_html_mail(settings.DEFAULT_FROM_EMAIL,
                               u"Bienvenido al rubro '%s' de Quimera \
Inmobiliaria" % rubro,
                               "contacto_cliente_rubro.html",
                               {"rubro": rubro,
                                "sitio": Site.objects.get_current(),
                                "STATIC_URL": settings.STATIC_URL,
                                "inmobiliaria":Inmobiliaria.objects.get(id=1)
                                },
                               cliente.usuario.email)

        #mail de mensaje recibido
        send_html_mail(settings.DEFAULT_FROM_EMAIL,
                       u"Mensaje Recibido",
                       "contacto_cliente.html",
                       {"sitio": Site.objects.get_current(),
                        "STATIC_URL": settings.STATIC_URL,
                        "inmobiliaria":Inmobiliaria.objects.get(id=1)
                        },
                       cliente.usuario.email)        
        
        project_message = self.cleaned_data.get("proyecto")
        mensaje = MensajeFormularioContacto(
            cliente = cliente,
            mensaje = self.cleaned_data["mensaje"],
            fecha = datetime.now(),
            proyecto = project_message)
        mensaje.save()

        #se envia un correo a los administradores comerciales del proyecto
        #si no hay admin comerciales asociados al proyecto se envia al
        #DEFAULT_FROM_MAIL
        #si el mensaje no esta asociado a un proyecto se envia un mensaje
        #al DEFAULT_FROM_MAIL
        if project_message:
            queryset = project_message.usuarios.all()
            if queryset:
                for user in queryset:
                    if user.email:
                        send_html_mail( 
                            settings.DEFAULT_FROM_EMAIL,
                            u"%s : Hay un nuevo mensaje!" % project_message,
                            "contacto_admin.html",
                            {"cliente": cliente,
                             "mensaje": self.cleaned_data["mensaje"],
                             "proyecto": project_message,
                             "sitio": Site.objects.get_current(),
                             "STATIC_URL": settings.STATIC_URL,
                             "inmobiliaria":Inmobiliaria.objects.get(id=1)},
                            user.email)
            else:
                send_html_mail( 
                    settings.DEFAULT_FROM_EMAIL,
                    u"%s : Hay un nuevo mensaje!" % project_message,
                    "contacto_admin.html",
                    {"noAdminsAssociated": True,
                     "cliente": cliente,
                     "mensaje": self.cleaned_data["mensaje"],
                     "proyecto": project_message,
                     "sitio": Site.objects.get_current(),
                     "STATIC_URL": settings.STATIC_URL,
                     "inmobiliaria":Inmobiliaria.objects.get(id=1)},
                    settings.DEFAULT_FROM_EMAIL)
        else:
            sitio = Site.objects.get_current()
            send_html_mail( 
                settings.DEFAULT_FROM_EMAIL,
                u"%s : Hay un nuevo mensaje!" % sitio.name,
                "contacto_admin_no_project.html",
                {"cliente": cliente,
                 "mensaje": self.cleaned_data["mensaje"],
                 "sitio": sitio,
                 "STATIC_URL": settings.STATIC_URL,
                 "inmobiliaria":Inmobiliaria.objects.get(id=1)},
                settings.DEFAULT_FROM_EMAIL)

                
class ChatForm(forms.Form):
    """
    Formulario para contactarse con una de las áreas de ayuda
    """
    area = forms.ModelChoiceField(widget=forms.RadioSelect,
                                  queryset=Area.objects.all(),
                                  label=_(u"Área de servicio"),
                                  empty_label=None,
                                  initial={})
    nombre = forms.CharField(
        label=_(u"Nombre de usuario"),
        help_text=_(u"Sólo son permitidas letras y números")
    )

    def clean_nombre(self):
        """
        Verficica que el nombre de usuario sea una sóla palabra y que no
        contenga caracteres especiales
        """
        nombre = self.cleaned_data['nombre']
        if not re.match(r"^[\w.@+-]+$", nombre):
            raise forms.ValidationError(u'Nombre inválido.')

        return nombre
