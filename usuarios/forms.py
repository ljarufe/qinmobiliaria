#-*- coding: utf-8 -*-

from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import authenticate, login
from django.contrib.admin import widgets
from django.db import transaction
from django.shortcuts import get_object_or_404
from common.models import Provincia, ViewPort
from common.utils import make_password, send_html_mail
from common.validators import validate_name, validate_user, validate_email
from django.core.exceptions import ValidationError
from proyectos.models import Rubro, Proyecto
from portal.models import Area, Inmobiliaria
from models import Cliente, AdminComercial, Corredor, Respuesta, \
                   MensajeFormularioContacto, Solicitud, AdminHelpDesk, \
                   AdminInformacion


class LoginForm(forms.Form):
    """
    Formulario para el login de los administradores de servicios
    """
    email = forms.EmailField(label=u"e-mail")
    contrasena = forms.CharField(widget=forms.PasswordInput,
                                 label=_(u"Contraseña"))

    def clean(self):
        """
        Verifica los campos antes de realizar el login
        """
        if self.cleaned_data.get('email'):
            try:
                username = User.objects.get(
                    email=self.cleaned_data['email']
                ).username
            except User.DoesNotExist:
                username = ""
            self.user_cache = authenticate(
                username=username,
                password=self.cleaned_data.get('contrasena')
            )
            if not self.user_cache:
                raise forms.ValidationError(_(u"Email o contraseña incorrectos."))
            elif not self.user_cache.is_active:
                raise forms.ValidationError(_(u"Confirme su registro en su correo \
                                            electrónico"))

        return self.cleaned_data

    def save(self, request):
        """
        Hace el logeo de un usuario
        """
        login(request, self.user_cache)


class RecuperarPassForm(forms.Form):
    """
    Formulario para recuperar el password de un usuario
    """
    email = forms.EmailField(label=_(u"email"))

    def clean(self):
        try:
            self.cliente_cache = Cliente.objects.get(
                usuario__email=self.cleaned_data.get("email"))
        except Cliente.DoesNotExist:
            self.errors["email"] = [_(u"Este email no está registrado")]

        return self.cleaned_data

    def save(self):
        """
        Manda un email con una url de confirmación del nuevo password
        """
        send_html_mail("info@quimerainmobiliaria.com",
                       u"Nueva contraseña para Quimera Inmobiliaria",
                       "recuperar.html",
                        {"cliente": self.cliente_cache,
                         "password": make_password(),
                         "sitio": Site.objects.get_current(),
                         'STATIC_URL':settings.STATIC_URL,
                         'inmobiliaria':Inmobiliaria.objects.get(id=1)
                         },
                       self.cleaned_data['email'])


class RegistroClienteForm(forms.Form):
    """
    Formulario de registro para un cliente
    """
    nombre = forms.CharField(label=_(u"Nombre"),
                             validators=[validate_name])
    apellido = forms.CharField(label=_(u"Apellido"),
                               validators=[validate_name])
    email = forms.EmailField(label=_(u"e-mail"),
                             validators=[validate_user, validate_email])
    contrasena = forms.CharField(widget=forms.PasswordInput,
                                 label=_(u"Contraseña"))
    direccion = forms.CharField(label=_(u"Dirección"), required=False)
    provincia = forms.ModelChoiceField(
        label=_(u"Provincia"),
        queryset=Provincia.objects.all(),
        required=False,
    )
    rubros_interes = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        queryset=Rubro.objects.all(),
        label=_(u"Rubros de interés")
    )
    recibir_email = forms.BooleanField(label=_(u"Recibir e-mails"),
                                       required=False)
    rastrear_proyectos = forms.BooleanField(label=_(u"Rastrear proyectos"),
                                            required=False)
    
    @transaction.commit_on_success
    def save(self, formset_telefonos, formset_areas):
        """
        Guarda al nuevo cliente con sus preferencias y crea un usuario
        """
        usuario = User.objects.create_user(
            username=self.cleaned_data['email'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['contrasena']
        )
        usuario.first_name = self.cleaned_data['nombre']
        usuario.last_name = self.cleaned_data['apellido']
        usuario.is_active = False
        usuario.save()
        cliente = Cliente(usuario=usuario)
        cliente.recibir_email = self.cleaned_data['recibir_email']
        cliente.rastrear_proyectos = self.cleaned_data['rastrear_proyectos']
        cliente.direccion = self.cleaned_data['direccion']
        cliente.provincia = self.cleaned_data['provincia']
        cliente.save()
        for rubro in self.cleaned_data['rubros_interes']:
            cliente.rubros.add(rubro)
        for form_telefono in formset_telefonos.forms:
            telefono = form_telefono.save()
            cliente.telefonos.add(telefono)
        proyectos = []
        for form_area in formset_areas.forms:
            area_interes = form_area.save()
            proyectos += list(Proyecto.accepted.filter(
                latitud__lte=area_interes.high_latitud,
                latitud__gte=area_interes.low_latitud,
                longitud__lte=area_interes.high_longitud,
                longitud__gte=area_interes.low_longitud,
            ))
            cliente.areas_interes.add(area_interes)
        cliente.save()
        for proyecto in proyectos:
            proyecto.clientes.add(cliente)

        send_html_mail("info@quimerainmobiliaria.com",
                       u"Confirmar registro en Quimera Inmobiliaria",
                       "confirmar_registro.html",
                        {"cliente": cliente,
                         "sitio": Site.objects.get_current(),
                         #"proyectos": proyectos,
                         'STATIC_URL':settings.STATIC_URL,
                         'inmobiliaria':Inmobiliaria.objects.get(id=1)
                         },
                       cliente.usuario.email)

    def clean_contrasena(self):
        """
        Longitud mínima de 6 caracteres
        """
        password = self.cleaned_data.get('contrasena')
        if len(password) < 6:
            raise ValidationError(_(u'La contraseña debe tener como mínimo 6 caracteres'))
        return password


class EditarClienteForm(forms.Form):
    """
    Formulario de registro para un cliente
    """
    nombre = forms.CharField(label=_(u"Nombre"), validators=[validate_name])
    apellido = forms.CharField(label=_(u"Apellido"),
                               validators=[validate_name])
    email = forms.EmailField(label=_(u"e-mail"), validators=[validate_user])
    direccion = forms.CharField(label=_(u"Dirección"), required=False)
    provincia = forms.ModelChoiceField(
        label=_(u"Provincia"),
        queryset=Provincia.objects.all(),
        required=False,
    )

    def save(self, usuario, formset_telefonos):
        """
        Guarda al nuevo cliente con sus preferencias y crea un usuario
        """
        usuario.first_name = self.cleaned_data['nombre']
        usuario.last_name = self.cleaned_data['apellido']
        usuario.email = self.cleaned_data['email']
        usuario.save()
        cliente = Cliente.objects.get(usuario=usuario)
        cliente.direccion = self.cleaned_data['direccion']
        cliente.provincia = self.cleaned_data['provincia']
        for form_telefono in formset_telefonos.forms:
            if 'numero' in form_telefono.cleaned_data:
                telefono = form_telefono.save()
                cliente.telefonos.add(telefono)
        cliente.save()


class CambiarPasswordForm(forms.Form):
    """
    Formulario para la edición de password por el propio usuario
    """
    old_password = forms.CharField(widget=forms.PasswordInput,
                                   label=_(u"Contraseña anterior"))
    new_password = forms.CharField(widget=forms.PasswordInput,
                                   label=_(u"Contraseña nueva"))
    new_password2 = forms.CharField(widget=forms.PasswordInput,
                                    label=_(u"Contraseña nueva (por segunda vez)"))

    def __init__(self, *args, **kwargs):
        self.username = kwargs.pop('username', None)
        super(CambiarPasswordForm, self).__init__(*args, **kwargs)

    def clean(self):
        """
        Verifica que ambas contraseñas nuevas sean iguales
        """
        cleaned_data = super(CambiarPasswordForm, self).clean()
        new_password = self.cleaned_data.get('new_password')
        new_password2 = self.cleaned_data.get('new_password2')
        if new_password != new_password2:
            raise forms.ValidationError(u"Las contraseñas no coinciden")

        return cleaned_data

    def clean_old_password(self):
        """
        Autentica al usuario con su contraseña anterior
        """
        password = self.cleaned_data['old_password']
        self.user_cache = authenticate(
            username=self.username,
            password=password
        )
        if not self.user_cache:
            raise forms.ValidationError(u"La contraseña es incorrecta")

        return password

    def save(self, request):
        """
        Cambia la contraseña
        """
        cliente = Cliente.objects.get(usuario=self.user_cache)
        cliente.set_password(self.cleaned_data["new_password"])


class InteresesClienteForm(forms.Form):
    """
    Formulario para editar los intereses de un cliente
    """
    recibir_email = forms.BooleanField(label=_(u"Recibir e-mails"),
                                       required=False)
    rastrear_proyectos = forms.BooleanField(label=_(u"Rastrear proyectos"),
                                            required=False)

    def save(self, cliente, formset_areas):
        """
        Guarda los cambios en los intereses del cliente
        """
        cliente.recibir_email = self.cleaned_data['recibir_email']
        cliente.rastrear_proyectos = self.cleaned_data['rastrear_proyectos']
        for form_area in formset_areas.forms:
            area_interes = form_area.save()
            if not area_interes.borrar:
                cliente.areas_interes.add(area_interes)
            else:
                cliente.areas_interes.remove(area_interes)
                area_interes.delete()
        cliente.save()


class AreaInteresForm(forms.ModelForm):
    """
    Guarda un viewport que representa un área de interés de un usuario
    """
    nombre = forms.CharField(widget=forms.HiddenInput)
    high_latitud = forms.FloatField(widget=forms.HiddenInput)
    high_longitud = forms.FloatField(widget=forms.HiddenInput)
    low_latitud = forms.FloatField(widget=forms.HiddenInput)
    low_longitud = forms.FloatField(widget=forms.HiddenInput)
    delete = forms.CharField(widget=forms.HiddenInput, required=False)

    class Meta:
        model = ViewPort

    def save(self, commit=True):
        """
        Guarda el área de interés si tiene todos los datos
        """
        area = super(AreaInteresForm, self).save(commit=False)
        if not self.cleaned_data["delete"]:
            if commit:
                area.save()
            area.borrar = False
        else:
            area.borrar = True

        return area


class AdminClienteForm(forms.Form):
    """
    formulario para editar al usuario y sus datos como cliente
    """
    username = forms.RegexField(
        label=_(u'Username'), max_length=30, regex=r'^[\w.@+-]+$',
        help_text=_(u'Required. 30 characters or fewer. Letters, digits and\
 @/./+/-/_ only.'),
        error_messages = {'invalid': _("This value may contain only letters, \
numbers and @/./+/-/_ characters.")})
    first_name = forms.CharField(label=_(u'first name'), max_length=30)
    last_name = forms.CharField(label=_(u'last name'), max_length=30)
    email = forms.EmailField(label=_(u'email'))
    password1 = forms.CharField(label=_(u'Password'), required=False,
                                max_length=20, widget=forms.PasswordInput)
    password2 = forms.CharField(label=_(u'Password (again)'), required=False,
                                max_length=20, widget=forms.PasswordInput)
    id = forms.IntegerField(widget=forms.HiddenInput, required=False)
    direccion = forms.CharField(max_length=200)
    provincia = forms.ModelChoiceField(queryset=Provincia.objects.all())
    recibir_email = forms.BooleanField(required=False,
        widget=forms.CheckboxInput())
    rastrear_proyectos = forms.BooleanField(required=False,
        widget=forms.CheckboxInput())
    rubros = forms.ModelMultipleChoiceField(
        queryset=Rubro.objects.all(), required=False,
        widget=widgets.FilteredSelectMultiple(u'Rubros de Interés',False),)
    proyectos = forms.ModelMultipleChoiceField(
        queryset=Proyecto.objects.all(), required=False,
        widget=widgets.FilteredSelectMultiple(u'Proyectos de Interés',False),)

    codigo_corredor = forms.CharField(label=_(u'código del corredor'), 
                                      max_length=10, required=False)

    def init(self, c):
        """
        retorna un form inicializado con los datos basicos del usuario y del
        cliente
        """
        if c.corredor:
            codigo_corredor = c.corredor.codigo
        else:
            codigo_corredor = ''
        return self.__class__(initial={
                'username':c.usuario.username,
                'first_name':c.usuario.first_name,
                'last_name':c.usuario.last_name,
                'email':c.usuario.email,
                'id':c.id,
                'direccion':c.direccion,
                'provincia':c.provincia,
                'recibir_email':c.recibir_email,
                'rastrear_proyectos':c.rastrear_proyectos,
                'rubros':c.rubros.all(),
                'proyectos':c.proyectos.all(),
                'codigo_corredor': codigo_corredor})            

    def clean_codigo_corredor(self):
        """
        verifica que el codigo del corredor pertenezca a un corredor
        """
        cc = self.cleaned_data.get('codigo_corredor')
        if cc:
            try:
                return Corredor.objects.get(codigo=cc)
            except:
                raise forms.ValidationError(u'El código es incorrecto')
        return cc
        
            
    def clean(self):
        """
        Verificación 1: username único si no se está editando un cliente,
        si se está editando un cliente debe ser igual a su nombre de usuario
        ya establecido o debe ser único
        Verificación 2: Los passwords sólo puedan estar ausentes si se está 
        editando un objeto cliente
        Verificación 3: Los passwords ingresados sean iguales
        Verificacion 4: Passwords ingresados tengan por lo menos 6 caracteres
        Verificación 5: email único si no se está editando un cliente,
        si se está editando un cliente debe ser igual a su email ingresado
        o debe ser único
        """
        cd = super(self.__class__, self).clean()
        pw1 = cd.get('password1')
        pw2 = cd.get('password2')
        Id = cd.get('id')
        msg = u'Este campo es obligatorio'
        username = cd.get('username')
        email = cd.get('email')

        #Verificación 1:
        if username:
            notUniqueUsername = User.objects.filter(username=username)
            msg0 = u'Este nombre de usuario ya está siendo utilizado. Ingrese\
 otro.'
            if not Id and notUniqueUsername:
                self._errors['username'] = self.error_class([msg0])
                del cd['username']
            elif Id and cd['username'] != get_object_or_404(Cliente, id=Id).\
usuario.username and notUniqueUsername:
                self._errors['username'] = self.error_class([msg0])
                del cd['username']                

        #Verificación 2:
        if not pw1 and not Id:
            self._errors['password1'] = self.error_class([msg])
            del cd['password1']

        if not pw2 and not Id:
            msg = u'Este campo es obligatorio'
            self._errors['password2'] = self.error_class([msg])
            del cd['password2']

        #Verificación 3:
        if pw1 and pw2 and pw1 != pw2:
            raise forms.ValidationError(u'Los passwords ingresado no son \
iguales.')

        #Verificación 4:
        if pw1 and len(pw1) < 6:
            msg = u'Los passwords deben tener por lo menos 6 caractéres.'
            self._errors['password1'] = self.error_class([msg])
            self._errors['password2'] = self.error_class([msg])
            del cd['password1']
            del cd['password2']

        #Verificación 5:
        if email:
            notUniqueEmail = User.objects.filter(email=email)
            msg0 = u'Este correo ya está siendo utilizado. Ingrese otro.'
            if not Id and notUniqueEmail:
                self._errors['email'] = self.error_class([msg0])
                del cd['email']
            elif Id and email != get_object_or_404(Cliente, id=Id).\
usuario.email and notUniqueEmail:
                self._errors['email'] = self.error_class([msg0])
                del cd['email']                

        return cd
        
    @transaction.commit_on_success
    def save(self, *args, **kwargs):
        """
        guarda o actualiza a el usuario y a los datos del cliente
        retorna el cliente creado o actualizado
        """
        cd=self.cleaned_data
        Id = cd.get('id')
        try:
            u = Cliente.objects.get(id=Id).usuario
        except:
            u = ''

        if u:
            u.username=cd['username']
            u.first_name=cd['first_name']
            u.last_name=cd['last_name']
            u.email=cd['email']
        else:
            u = User(username=cd['username'],
                     first_name=cd['first_name'],
                     last_name=cd['last_name'],
                     email=cd['email'],
                     is_active=True)
        pw = cd.get('password1')
        if pw:
            u.set_password(cd['password1'])
        u.save()
        c = Cliente(id = Id,
                    usuario = u,
                    direccion = cd['direccion'],
                    provincia = cd['provincia'],
                    recibir_email = cd['recibir_email'],
                    rastrear_proyectos = cd['rastrear_proyectos'],)
        if cd['codigo_corredor']:
            c.corredor = cd['codigo_corredor']
            c.tipo = 'C'

        c.save()
        
        c.rubros.clear()
        for rubro in cd['rubros']:
            c.rubros.add(rubro)

        c.proyectos.clear()
        for proyecto in cd['proyectos']:
            c.proyectos.add(proyecto)
        
        return c


class AdminAdminComercialForm(forms.Form):
    """
    formulario para editar al usuario y sus datos como Admincomercial
    """
    username = forms.RegexField(
        label=_(u'Username'), max_length=30, regex=r'^[\w.@+-]+$',
        help_text=_(u'Required. 30 characters or fewer. Letters, digits and\
 @/./+/-/_ only.'),
        error_messages = {'invalid': _("This value may contain only letters, \
numbers and @/./+/-/_ characters.")})
    first_name = forms.CharField(label=_(u'first name'), max_length=30)
    last_name = forms.CharField(label=_(u'last name'), max_length=30)
    email = forms.EmailField(label=_(u'email'))
    password1 = forms.CharField(label=_(u'Password'), required=False,
                                max_length=20, widget=forms.PasswordInput)
    password2 = forms.CharField(label=_(u'Password (again)'), required=False,
                                max_length=20, widget=forms.PasswordInput)
    id = forms.IntegerField(widget=forms.HiddenInput, required=False)

    asignar_proyectos = forms.BooleanField(required=False,
        widget=forms.CheckboxInput())
    proyectos = forms.ModelMultipleChoiceField(
        queryset=Proyecto.objects.all(), required=False,
        widget=widgets.FilteredSelectMultiple(u'Proyectos',False),)

    def init(self, c):
        """
        retorna un form inicializado con los datos basicos del usuario y del
        administrador comercial
        """
        return self.__class__(initial={
                'username':c.usuario.username,
                'first_name':c.usuario.first_name,
                'last_name':c.usuario.last_name,
                'email':c.usuario.email,
                'id':c.id,
                'asignar_proyectos': c.asignar_proyectos,
                'proyectos': c.usuario.proyecto_set.all(),})            
            
    def clean(self):
        """
        Verificación 1: username único si no se está editando un administrador,
        si se está editando un administrador debe ser igual a su nombre de 
        usuario ya establecido o debe ser único
        Verificación 2: Los passwords sólo puedan estar ausentes si se está 
        editando un objeto cliente
        Verificación 3: Los passwords ingresados sean iguales
        Verificacion 4: Passwords ingresados tengan como minimo 6 caracteres
        Verificación 5: email unico si no se esta editando un administrador,
        si se esta editando un administrador debe ser igual a su correo ya 
        ingresado o debe ser unico
        """
        cd = super(self.__class__, self).clean()
        pw1 = cd.get('password1')
        pw2 = cd.get('password2')
        Id = cd.get('id')
        msg = u'Este campo es obligatorio'
        username = cd.get('username')
        email =  cd.get('email')

        #Verificación 1:
        if username:
            notUniqueUsername = User.objects.filter(username=username)
            msg0 = u'Este nombre de usuario ya está siendo utilizado. Ingrese\
 otro.'
            if not Id and notUniqueUsername:
                self._errors['username'] = self.error_class([msg0])
                del cd['username']
            elif Id and cd['username'] != get_object_or_404(AdminComercial, \
id=Id).usuario.username and notUniqueUsername:
                self._errors['username'] = self.error_class([msg0])
                del cd['username']                

        #Verificación 2:
        if not pw1 and not Id:
            self._errors['password1'] = self.error_class([msg])
            del cd['password1']

        if not pw2 and not Id:
            msg = u'Este campo es obligatorio'
            self._errors['password2'] = self.error_class([msg])
            del cd['password2']

        #Verificación 3:
        if pw1 and pw2 and pw1 != pw2:
            raise forms.ValidationError(u'Los passwords ingresado no son \
iguales.')

        #Verificación 4:
        if pw1 and len(pw1) < 6:
            msg = u'Los passwords deben tener por lo menos 6 caractéres.'
            self._errors['password1'] = self.error_class([msg])
            self._errors['password2'] = self.error_class([msg])
            del cd['password1']
            del cd['password2']

        #Verificación 5:
        if email:
            notUniqueEmail = User.objects.filter(email=email)
            msg0 = u'Este correo ya está siendo utilizado. Ingrese\
 otro.'
            if not Id and notUniqueEmail:
                self._errors['email'] = self.error_class([msg0])
                del cd['email']
            elif Id and email != get_object_or_404(AdminComercial, \
id=Id).usuario.email and notUniqueEmail:
                self._errors['email'] = self.error_class([msg0])
                del cd['email']                

        return cd
        
        
    @transaction.commit_on_success
    def save(self, *args, **kwargs):
        """
        guarda o actualiza a el usuario y a los datos del administrador 
        comercial 
        retorna el administrador comercial creado o actualizado
        """
        cd=self.cleaned_data
        Id = cd.get('id')
        try:
            u = AdminComercial.objects.get(id=Id).usuario
        except:
            u = ''

        if u:
            u.username=cd['username']
            u.first_name=cd['first_name']
            u.last_name=cd['last_name']
            u.email=cd['email']
        else:
            u = User(username=cd['username'],
                     first_name=cd['first_name'],
                     last_name=cd['last_name'],
                     email=cd['email'],
                     is_staff=True,)
        pw = cd.get('password1')
        if pw:
            u.set_password(cd['password1'])
        u.save()
        c = AdminComercial(
            id = Id,
            usuario = u,
            asignar_proyectos = cd['asignar_proyectos'],)
        c.save()
        
        c.usuario.proyecto_set.clear()
        for proyecto in cd['proyectos']:
            c.usuario.proyecto_set.add(proyecto)
        
        return c


class AdminAdminInformacionForm(forms.Form):
    """
    formulario para editar al usuario y sus datos como AdminInformacion
    """
    username = forms.RegexField(
        label=_(u'Username'), max_length=30, regex=r'^[\w.@+-]+$',
        help_text=_(u'Required. 30 characters or fewer. Letters, digits and\
 @/./+/-/_ only.'),
        error_messages = {'invalid': _("This value may contain only letters, \
numbers and @/./+/-/_ characters.")})
    first_name = forms.CharField(label=_(u'first name'), max_length=30)
    last_name = forms.CharField(label=_(u'last name'), max_length=30)
    email = forms.EmailField(label=_(u'email'))
    password1 = forms.CharField(label=_(u'Password'), required=False,
                                max_length=20, widget=forms.PasswordInput)
    password2 = forms.CharField(label=_(u'Password (again)'), required=False,
                                max_length=20, widget=forms.PasswordInput)
    id = forms.IntegerField(widget=forms.HiddenInput, required=False)

    # asignar_proyectos = forms.BooleanField(required=False,
    #     widget=forms.CheckboxInput())
    proyectos = forms.ModelMultipleChoiceField(
        queryset=Proyecto.objects.all(), required=False,
        widget=widgets.FilteredSelectMultiple(u'Proyectos',False),)

    def init(self, c):
        """
        retorna un form inicializado con los datos basicos del usuario y del
        administrador comercial
        """
        return self.__class__(initial={
                'username':c.usuario.username,
                'first_name':c.usuario.first_name,
                'last_name':c.usuario.last_name,
                'email':c.usuario.email,
                'id':c.id,
#                'asignar_proyectos': c.asignar_proyectos,
                'proyectos': c.usuario.proyecto_set.all(),})            
            
    def clean(self):
        """
        Verificación 1: username único si no se está editando un administrador,
        si se está editando un administrador debe ser igual a su nombre de 
        usuario ya establecido o debe ser único
        Verificación 2: Los passwords sólo puedan estar ausentes si se está 
        editando un objeto cliente
        Verificación 3: Los passwords ingresados sean iguales
        Verificacion 4: Passwords ingresados tengan como minimo 6 caracteres
        Verificación 4: email unico si no se esta editando un administrador,
        si se esta editando un administrador debe ser igual a su correo ya 
        ingresado o debe ser unico
        """
        cd = super(self.__class__, self).clean()
        pw1 = cd.get('password1')
        pw2 = cd.get('password2')
        Id = cd.get('id')
        msg = u'Este campo es obligatorio'
        username = cd.get('username')
        email =  cd.get('email')

        #Verificación 1:
        if username:
            notUniqueUsername = User.objects.filter(username=username)
            msg0 = u'Este nombre de usuario ya está siendo utilizado. Ingrese\
 otro.'
            if not Id and notUniqueUsername:
                self._errors['username'] = self.error_class([msg0])
                del cd['username']
            elif Id and cd['username'] != get_object_or_404(AdminInformacion, \
id=Id).usuario.username and notUniqueUsername:
                self._errors['username'] = self.error_class([msg0])
                del cd['username']                

        #Verificación 2:
        if not pw1 and not Id:
            self._errors['password1'] = self.error_class([msg])
            del cd['password1']

        if not pw2 and not Id:
            msg = u'Este campo es obligatorio'
            self._errors['password2'] = self.error_class([msg])
            del cd['password2']

        #Verificación 3:
        if pw1 and pw2 and pw1 != pw2:
            raise forms.ValidationError(u'Los passwords ingresado no son \
iguales.')

        #Verificación 4:
        if pw1 and len(pw1) < 6:
            msg = u'Los passwords deben tener por lo menos 6 caractéres.'
            self._errors['password1'] = self.error_class([msg])
            self._errors['password2'] = self.error_class([msg])
            del cd['password1']
            del cd['password2']

        #Verificación 5:
        if email:
            notUniqueEmail = User.objects.filter(email=email)
            msg0 = u'Este correo ya está siendo utilizado. Ingrese\
 otro.'
            if not Id and notUniqueEmail:
                self._errors['email'] = self.error_class([msg0])
                del cd['email']
            elif Id and email != get_object_or_404(AdminInformacion, \
id=Id).usuario.email and notUniqueEmail:
                self._errors['email'] = self.error_class([msg0])
                del cd['email']                

        return cd
        
    @transaction.commit_on_success
    def save(self, *args, **kwargs):
        """
        guarda o actualiza a el usuario y a los datos del administrador 
        de informacion
        retorna el administrador de informacion creado o actualizado
        """
        cd=self.cleaned_data
        Id = cd.get('id')
        try:
            u = AdminInformacion.objects.get(id=Id).usuario
        except:
            u = ''

        if u:
            u.username=cd['username']
            u.first_name=cd['first_name']
            u.last_name=cd['last_name']
            u.email=cd['email']
        else:
            u = User(username=cd['username'],
                     first_name=cd['first_name'],
                     last_name=cd['last_name'],
                     email=cd['email'],
                     is_staff=True,)
        pw = cd.get('password1')
        if pw:
            u.set_password(cd['password1'])
        u.save()
        c = AdminInformacion(
            id = Id,
            usuario = u,
            #asignar_proyectos = cd['asignar_proyectos'],
            )
        c.save()
        
        c.usuario.proyecto_set.clear()
        for proyecto in cd['proyectos']:
            c.usuario.proyecto_set.add(proyecto)
        
        return c


class AdminAdminHelpDeskForm(forms.Form):
    """
    formulario para editar al usuario y sus datos como Help Desk
    """
    username = forms.RegexField(
        label=_(u'Username'), max_length=30, regex=r'^[\w.@+-]+$',
        help_text=_(u'Required. 30 characters or fewer. Letters, digits and\
 @/./+/-/_ only.'),
        error_messages = {'invalid': _("This value may contain only letters, \
numbers and @/./+/-/_ characters.")})
    first_name = forms.CharField(label=_(u'first name'), max_length=30)
    last_name = forms.CharField(label=_(u'last name'), max_length=30)
    email = forms.EmailField(label=_(u'email'))
    password1 = forms.CharField(label=_(u'Password'), required=False,
                                max_length=20, widget=forms.PasswordInput)
    password2 = forms.CharField(label=_(u'Password (again)'), required=False,
                                max_length=20, widget=forms.PasswordInput)
    id = forms.IntegerField(widget=forms.HiddenInput, required=False)

    auto_asignar_salas = forms.BooleanField(required=False,
        widget=forms.CheckboxInput())
    areas  = forms.ModelMultipleChoiceField(
        queryset=Area.objects.all(), required=False,
        widget=widgets.FilteredSelectMultiple(u'Áreas',False),)

    def init(self, c):
        """
        retorna un form inicializado con los datos basicos del usuario y del
        administrador help desk
        """
        return self.__class__(initial={
                'username':c.usuario.username,
                'first_name':c.usuario.first_name,
                'last_name':c.usuario.last_name,
                'email':c.usuario.email,
                'id':c.id,
                'auto_asignar_salas': c.auto_asignar_salas,
                'areas': c.areas.all(),})            
            
    def clean(self):
        """
        Verificación 1: username único si no se está editando un administrador,
        si se está editando un administrador debe ser igual a su nombre de 
        usuario ya establecido o debe ser único
        Verificación 2: Los passwords sólo puedan estar ausentes si se está 
        editando un objeto cliente
        Verificación 3: Los passwords ingresados sean iguales
        Verificacion 4: Passwords ingresados tengan por lo menos 6 caracteres
        Verificación 5: email unico si no se esta editando un administrador,
        si se esta editando un administrador debe ser igual a su correo ya 
        ingresado o debe ser unico
        """
        cd = super(self.__class__, self).clean()
        pw1 = cd.get('password1')
        pw2 = cd.get('password2')
        Id = cd.get('id')
        msg = u'Este campo es obligatorio'
        username = cd.get('username')
        email =  cd.get('email')

        #Verificación 1:
        if username:
            notUniqueUsername = User.objects.filter(username=username)
            msg0 = u'Este nombre de usuario ya está siendo utilizado. Ingrese\
 otro.'
            if not Id and notUniqueUsername:
                self._errors['username'] = self.error_class([msg0])
                del cd['username']
            elif Id and cd['username'] != get_object_or_404(AdminHelpDesk, \
id=Id).usuario.username and notUniqueUsername:
                self._errors['username'] = self.error_class([msg0])
                del cd['username']                

        #Verificación 2:
        if not pw1 and not Id:
            self._errors['password1'] = self.error_class([msg])
            del cd['password1']

        if not pw2 and not Id:
            msg = u'Este campo es obligatorio'
            self._errors['password2'] = self.error_class([msg])
            del cd['password2']

        #Verificación 3:
        if pw1 and pw2 and pw1 != pw2:
            raise forms.ValidationError(u'Los passwords ingresado no son \
iguales.')

        #Verificación 4:
        if pw1 and len(pw1) < 6:
            msg = u'Los passwords deben tener por lo menos 6 caractéres.'
            self._errors['password1'] = self.error_class([msg])
            self._errors['password2'] = self.error_class([msg])
            del cd['password1']
            del cd['password2']

        #Verificación 5:
        if email:
            notUniqueEmail = User.objects.filter(email=email)
            msg0 = u'Este correo ya está siendo utilizado. Ingrese\
 otro.'
            if not Id and notUniqueEmail:
                self._errors['email'] = self.error_class([msg0])
                del cd['email']
            elif Id and email != get_object_or_404(AdminHelpDesk, \
id=Id).usuario.email and notUniqueEmail:
                self._errors['email'] = self.error_class([msg0])
                del cd['email']                

        return cd
        
    @transaction.commit_on_success
    def save(self, *args, **kwargs):
        """
        guarda o actualiza a el usuario y a los datos del administrador 
        help desk
        retorna el administrador help desk creado o actualizado
        """
        cd=self.cleaned_data
        Id = cd.get('id')
        try:
            u = AdminHelpDesk.objects.get(id=Id).usuario
        except:
            u = ''

        if u:
            u.username=cd['username']
            u.first_name=cd['first_name']
            u.last_name=cd['last_name']
            u.email=cd['email']
        else:
            u = User(username=cd['username'],
                     first_name=cd['first_name'],
                     last_name=cd['last_name'],
                     email=cd['email'],
                     is_staff=True,)
        pw = cd.get('password1')
        if pw:
            u.set_password(cd['password1'])
        u.save()
        c = AdminHelpDesk(
            id = Id,
            usuario = u,
            auto_asignar_salas = cd['auto_asignar_salas'],)
        c.save()
        
        #c.usuario.proyecto_set.clear()
        c.areas.clear()
        for area in cd['areas']:
            #c.usuario.proyecto_set.add(proyecto)
            c.areas.add(area)
        
        return c


class AdminRespuestaForm(forms.ModelForm):    
    class Meta:
        model = Respuesta
        exclude = ('admin', 'mensaje', 'fecha')

    def save(self, user, mensaje_id):
        """
        graba la respuesta y la envia el mensaje usuario implicado
        
        """
        mensaje = get_object_or_404(MensajeFormularioContacto, id=mensaje_id)
        
        r = Respuesta.objects.create(
            admin = user, 
            mensaje = mensaje, 
            respuesta=self.cleaned_data['respuesta'])

        send_html_mail("info@quimerainmobiliaria.com",
                       #u"Re: %s" % mensaje.proyecto,
                       u"Re: Quimera Inmobiliaria",
                       "mensaje_respuesta.html",
                        {"sender": user.get_full_name(),
                         "respuesta": self.cleaned_data['respuesta'],
                         'STATIC_URL':settings.STATIC_URL,
                         'inmobiliaria':Inmobiliaria.objects.get(id=1),
                         "sitio": Site.objects.get_current()},
                       mensaje.cliente.usuario.email)
        return r

        
class SolicitudForm(forms.ModelForm):
    class Meta:
        model = Solicitud
        exclude= ('estado', 'tipo', 'admin')

    def __init__(self, *args, **kwargs):
        super(self.__class__,self).__init__(*args, **kwargs)
        self.fields['cliente'].widget = forms.HiddenInput()
        self.fields['item'].widget = forms.HiddenInput()

    def clean(self):
        """
        verifica que no exista ya una solicitud con estado espera entre el 
        cliente y el item
        """
        cd = self.cleaned_data
        cliente = cd.get('cliente')
        item  = cd.get('item')
        if Solicitud.objects.filter(cliente=cliente.id).filter(item=item.id).\
filter(estado=u'E'):
            raise forms.ValidationError(u'Ya envió una solicitud para separar este item.')
        return cd

    def save(self, cliente, item):
        """
        guarda la solicitud del cliente
        """
        obj, created = Solicitud.objects.get_or_create(
            mensaje = self.cleaned_data['mensaje'], cliente=cliente, item=item,
            proyecto = item.plano.proyecto)
        return obj


class AdminSolicitudForm(forms.ModelForm):
    """
    Formulario de solicitud para los administradores
    """
    ACCION_CHOICES = (
        (u"S", u"Aceptado y en trámite"),
        (u"V", u"Aceptado y tramitado"),
        (u"R", u"Rechazado"),
    )
    accion = forms.ChoiceField(label=u"Acción", choices=ACCION_CHOICES)

    class Meta:
        model = Solicitud
        fields = ("accion", "tipo", "mensaje", "cliente", "proyecto", "item")
