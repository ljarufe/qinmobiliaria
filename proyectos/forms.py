#-*- coding: utf-8 -*-

from django.db.models import Sum
from django import forms
from django.contrib import messages
from django.contrib.admin import widgets
from django.contrib.auth.models import Group, User
from django.contrib.sites.models import Site
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.conf import settings
from django.db import transaction
from django.db.models import Q
from django.forms.formsets import BaseFormSet, formset_factory
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from tinymce.widgets import TinyMCE
from models import Etapa, SubEtapa, Proyecto, Caracteristica, Contacto, \
    Avance, Milestone, Oferta, Rubro, Plano, Item, Beneficio, TipoItem, \
    Desarrollado
from common.models import Provincia, Referencia, Foto, Video, Telefono, \
    Poligono, Punto
from common.utils import send_html_mail
from usuarios.models import Cliente, CambioEstadoItem
from portal.models import Inmobiliaria
from datetime import timedelta, datetime, date


class AdminEtapaForm(forms.ModelForm):
    id = forms.IntegerField(widget=forms.HiddenInput, required=False)

    class Meta:
        model = Etapa

    def __init__(self, *args, **kwargs):
        """
        si el usuario es un superusuario el queryset de proyectos es de todos 
        los proyectos, en caso contrario sera solo de los proyecto a los que 
        esta asignado
        """
        try:
            user = kwargs.pop('user')
        except:
            user = ''
        super(self.__class__,self).__init__(*args, **kwargs)
        self.fields['fecha_inicio'].widget = widgets.AdminDateWidget()
        self.fields['fecha_fin'].widget = widgets.AdminDateWidget()
        self.fields['porcentaje'].help_text = 'Ingrese el porcentaje de avance \
 que representa esta etapa respecto al proyecto' 
        if user and not user.is_superuser:
            self.fields['proyecto'].queryset= user.proyecto_set.all()

    def clean(self):
        """
        validacion 1: verifica que fecha_fin >= fecha_inicio
        validacion 2: verifica que el porcentaje <= 100%
        """
        cleaned_data=super(self.__class__, self).clean()

        #validacion 1        
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')
        if fecha_inicio and fecha_fin:
            if fecha_fin < fecha_inicio:
                raise forms.ValidationError('La fecha de finalización debe ser \
mayor o igual a la fecha de inicio')
            
        #validacion 2
        proyecto = self.cleaned_data.get('proyecto')
        p = self.cleaned_data.get('porcentaje')
        if proyecto and p:
            suma = 0
            querySet = proyecto.etapa_set.all()
            if (querySet):
                suma = querySet.aggregate(s=Sum('porcentaje'))
                suma = suma['s']
            Id = self.cleaned_data.get('id')
            try:
                anterior_porcentaje = Etapa.objects.get(id=Id).porcentaje
                sum2 = suma+p-anterior_porcentaje
            except:
                sum2 = suma+p
            msg = ''
#             if suma == 100:
#                 raise forms.ValidationError('Ya se alcanzó el 100% del \
# proyecto. No puede de agregar  más etapas')
#             elif sum2 > 100:
            if sum2 > 100:
                msg = u'Con el porcentaje ingresado se obtiene  el %s%s. \
Actualmente las etapas ingresadas representan el  %s%s del \
proyecto' % (sum2,'%',suma,'%') 
                self._errors['porcentaje'] = self.error_class([msg])
                del cleaned_data['porcentaje']
        return cleaned_data

    def clean_porcentaje(self):
        """
        verifica 0 < porcentaje <= 100
        y que los porcentajes de las etapas del proyecto no excedan el 100%
        """
        p = self.cleaned_data['porcentaje']
        if  p <= 0 or p > 100:
            raise forms.ValidationError("Ingrese un valor entre 1 y 100") 
        return p

    def save(self):
        """
        si hay id (no borrado) realiza un update
        sino un insert
        """
        Id = self.cleaned_data.get('id')
        try:
            Etapa.objects.get(id=Id)
            obj = Etapa(id=Id, titulo=self.cleaned_data['titulo'], 
                        proyecto=self.cleaned_data['proyecto'],
                        descripcion=self.cleaned_data['descripcion'],
                        fecha_inicio=self.cleaned_data['fecha_inicio'],
                        fecha_fin=self.cleaned_data['fecha_fin'],
                        porcentaje=self.cleaned_data['porcentaje'],)
            obj.save()
            return obj
        except:
            return super(self.__class__,self).save()


class AdminSubEtapaForm(forms.ModelForm):
    id = forms.IntegerField(widget=forms.HiddenInput, required=False)

    class Meta:
        model = SubEtapa

    def __init__(self, *args, **kwargs):
        super(self.__class__,self).__init__(*args, **kwargs)
        self.fields['fecha_inicio'].widget = widgets.AdminDateWidget()
        self.fields['fecha_fin'].widget = widgets.AdminDateWidget()
        self.fields['etapa'].widget = forms.HiddenInput()
        self.fields['porcentaje'].help_text = 'Ingrese el porcentaje de avance \
que representa esta sub-etapa respecto a la etapa'
            
    def clean(self):
        """
        validacion 1: verifica que fecha_fin >= fecha_inicio
        validacion 2: verifica que el porcentaje <= 100%
        """
        #validacion 1
        cleaned_data=super(self.__class__, self).clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')
        if fecha_inicio and fecha_fin:
            if fecha_fin < fecha_inicio:
                raise forms.ValidationError('La fecha de finalización debe ser \
mayor o igual a la fecha de inicio')

        #validacion 2
        etapa = self.cleaned_data.get('etapa')
        p = self.cleaned_data.get('porcentaje')
        if etapa and p:
            suma = 0
            querySet = etapa.subetapa_set.all()
            if (querySet):
                suma = querySet.aggregate(s=Sum('porcentaje'))
                suma = suma['s']
            Id = self.cleaned_data.get('id')
            try:
                anterior_porcentaje = SubEtapa.objects.get(id=Id).porcentaje
                sum2 = suma+p-anterior_porcentaje
            except:
                sum2 = suma+p
            msg = ''
#             if suma == 100:
#                 raise forms.ValidationError('Ya se alcanzó el 100% de la \
# etapa. No puede de agregar  más sub-etapas')
#            elif sum2 > 100:
            if sum2 > 100:
                msg = u'Con el porcentaje ingresado se obtiene  el %s%s. \
Actualmente las sub-etapas ingresadas representan el  %s%s de la \
etapa' % (sum2,'%',suma,'%') 
                self._errors['porcentaje'] = self.error_class([msg])
                del cleaned_data['porcentaje']

        return cleaned_data

    def clean_porcentaje(self):
        """
        verifica 0 < porcentaje <= 100
        y que los porcentajes de las etapas del proyecto no excedan el 100%
        """
        p = self.cleaned_data['porcentaje']
        if  p <= 0 or p > 100:
            raise forms.ValidationError("Ingrese un valor entre 1 y 100") 
        return p

    def save(self):
        """
        si hay id (no borrado) realiza un update
        sino un insert
        """
        Id = self.cleaned_data.get('id')
        try:
            SubEtapa.objects.get(id=Id)
            obj = SubEtapa(id=Id, titulo=self.cleaned_data['titulo'], 
                           fecha_inicio=self.cleaned_data['fecha_inicio'],
                           fecha_fin=self.cleaned_data['fecha_fin'],
                           porcentaje=self.cleaned_data['porcentaje'],
                           etapa=self.cleaned_data['etapa'])
            obj.save()
            return obj
        except:
            return super(self.__class__,self).save()


class AdminProyectoForm(forms.ModelForm):
    """
    ToDo: se des habilito el tiny mce xq al tener estos 4 formularios juntos,
    por alguna razon no se envian los datos correctamente por post, ademas
    el programa para generar pdf no reconoce todas las etiquetas creadas
    por el tinymce, de manera que las muestra junto con el texto del pdf
    Queda pendiente arreglar estos problemas
    """
    id = forms.IntegerField(widget=forms.HiddenInput(),required=False)
    # descripcion = forms.CharField(widget=TinyMCE(attrs={'cols':80, 'rows':30}),
    #                               required=False)
    # resumen = forms.CharField(widget=TinyMCE(attrs={'cols':80, 'rows':30}),
    #                           required=False)
    # introduccion = forms.CharField(widget=TinyMCE(attrs={'cols':80, 'rows':30}),
    #                                required=False)
    # beneficios = forms.CharField(widget=TinyMCE(attrs={'cols':80, 'rows':30}),
    #                              required=False)
    descripcion = forms.CharField(required=False,
        widget=forms.Textarea(attrs={'cols':80, 'rows':15}))
    resumen = forms.CharField(required=False,
        widget=forms.Textarea(attrs={'cols':80, 'rows':15}))
    introduccion = forms.CharField(required=False,
        widget=forms.Textarea(attrs={'cols':80, 'rows':15}))
    # beneficios = forms.CharField(required=False,
    #     widget=forms.Textarea(attrs={'cols':80, 'rows':15}))

    foto_principal = forms.ImageField(widget=forms.FileInput(), required=False,
                                      help_text=_(u"Foto principal del perfil de proyecto"),)
    foto_inicio = forms.ImageField(widget=forms.FileInput(), required=False,
                                   help_text=_(u"Foto para el slider de la página de inicio"),)

    def __init__(self, *args, **kwargs):
        super(self.__class__,self).__init__(*args, **kwargs)
        self.fields['fecha_inicio'].widget = widgets.AdminDateWidget()
        self.fields['fecha_fin'].widget = widgets.AdminDateWidget()
        self.fields['logo'].widget = forms.FileInput()
        self.fields['logo_watermark'].widget = forms.FileInput()

    class Meta:
        model = Proyecto
        exclude = ('latitud', 'longitud', 'precio_minimo', 'precio_maximo', 
                   'direccion', 'avance', 'pdf', 'fotos', 'videos', 'clientes',
                   'corredores', 'provincia', 'usuarios')

    def clean(self):
        """
        validación 1: que fecha_fin >= fecha_inicio
        ###validación 2: área construída <= área ### si puede ser mayor
        validación 3: la foto principal puede estar ausente sólo si existe
                       id en la cleaned_data
        validacion 4: slug unico
        """
        #validación 1
        cleaned_data=super(AdminProyectoForm, self).clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')
        if fecha_inicio and fecha_fin:
            if fecha_fin < fecha_inicio:
                raise forms.ValidationError('La fecha de finalización debe ser \
mayor o igual a la fecha de inicio')

 #        #validación 2
 #        area = cleaned_data.get('area')
 #        area_c = cleaned_data.get('area_construida')
 #        if area and area_c:
 #            if area_c > area:
 #                raise forms.ValidationError('El área construida no puede ser\
 # mayor al área del proyecto')

        #validación 3
        Id = cleaned_data.get('id')
        foto_principal = cleaned_data.get('foto_principal')
        if not foto_principal and not Id:
            msg = u'Este campo es obligatorio'
            self._errors['foto_principal'] = self.error_class([msg])

        #validación 4
        msg = u'El slug ingresado está siendo usado por otro proyecto'
        new_slug = cleaned_data.get('slug')
        if Id:
            if new_slug != Proyecto.objects.get(id=Id).slug and \
Proyecto.objects.filter(slug=new_slug):
                self._errors['slug'] = self.error_class([msg])
        elif Proyecto.objects.filter(slug=new_slug):
            self._errors['slug'] = self.error_class([msg])

        return cleaned_data

    def save(self, user):
        """
        crea o actualiza un proyecto
        asocia el proyecto al usuario que lo creo, sólo si no es super usuario
        """
        Id = self.cleaned_data.get('id')
        if Id:
             p=get_object_or_404(Proyecto, id=Id)
            # if self.has_changed():
            #     for key in self._get_changed_data():
            #         p.__setattr__(key,self.cleaned_data.get(key))
            #     p.save()
             for k,v in self.cleaned_data.items():
                 if not v and (k== u'foto_principal' or k== u'logo' or \
k== u'logo_watermark'):
                     pass
                 else:
                     p.__setattr__(k,v)                 
             p.save()
             return p
        else:
            p = super(self.__class__, self).save()
            if not user.is_superuser:
                user.proyecto_set.add(p)
            return p

# class AdminEditSubetapa(forms.Form):
#     id = forms.IntegerField(widget=forms.HiddenInput)

#     def clean_id(self):
#         """
#         verifica que el id sea de una subetapa valida
#         """
#         etapa_id = self.cleaned_data['id']
#         try:
#             SubEtapa.objects.get(id=etapa_id)
#         except:
#             raise forms.ValidationError('el id no pertenece a ninguna subetapa')
#         return etapa_id

#     def save(self):
#         """
#         retorna un diccionario con todos los datos de la sub-etapa
#         """
#         se = SubEtapa.objects.get(id=self.cleaned_data['id'])
#         return ({'id': se.id, 
#                  'titulo': se.titulo, 
#                  'fecha_inicio': se.fecha_inicio, 
#                  'fecha_fin': se.fecha_fin, 
#                  'porcentaje': se.porcentaje})

        
class AdminUbicacionForm(forms.Form):
    direccion = forms.CharField(
        max_length=250, 
        widget=forms.TextInput(attrs={'class':'address'}))
    latitud = forms.FloatField(widget=forms.HiddenInput)
    longitud = forms.FloatField(widget=forms.HiddenInput)
    provincia = forms.ModelChoiceField(
        queryset=Provincia.objects.all(),
        widget=forms.Select(attrs={'class':'provincia'}))

    def save(self, proyecto_id):
        """
        guarda los datos en el proyecto indicado
        y actualiza la imagen de google maps del proyecto
        en caso tenga exito retorna el proyecto, sino retorna False
        """
        try:
            p = Proyecto.objects.get(id=proyecto_id)
            p.direccion = self.cleaned_data['direccion']
            p.latitud = self.cleaned_data['latitud']
            p.longitud = self.cleaned_data['longitud']
            p.provincia = self.cleaned_data['provincia']
            p.save()
            p.create_update_gmaps_image()
            return p
        except:
            return False

    def initialize(self, p):
        """
        inicializa el form con el proyecto p,
        sino recibe p no hace nada
        """
        self.direccion = p.direccion
        self.latitud = p.latitud
        self.longitud = p.longitud
        self.provincia = p.provincia


class AdminReferenciaForm(forms.ModelForm):
    latitud = forms.FloatField(widget=forms.HiddenInput)
    longitud = forms.FloatField(widget=forms.HiddenInput)

    class Meta:
        model= Referencia

    def save(self, proyecto_id):
        """
        graba la referencia y actualiza la imagen de gmaps
        """
        try:
            super(self.__class__,self).save()
            p = Proyecto.objects.get(id=proyecto_id)
            p.create_update_gmaps_image()
            return p
        except:
            return False
    

class AdminFotoForm(forms.ModelForm):    
    id = forms.IntegerField(widget=forms.HiddenInput, required=False)
    imagen = forms.ImageField(required=False)

    class Meta:
        model = Foto

    def clean(self):
        """
        verifica que la imágen principal pueda estar ausente sólo si existe 
        id
        """
        cleaned_data = super(self.__class__, self).clean()
        Id = cleaned_data.get('id')
        imagen = cleaned_data.get('imagen')
        if not imagen and not Id:
            msg = u'Este campo es obligatorio'
            self._errors['imagen'] = self.error_class([msg])
        return cleaned_data

    def saveTo(self, p):
        """
        grava(o actualiza) la foto y la agrega a los objectos relacionados
        del objeto p, siempre y cuando el related name sea fotos
        """
        cleaned_data = self.cleaned_data
        Id = cleaned_data.get('id')
        newImg = cleaned_data.get('imagen')
        if not newImg:
            newImg = Foto.objects.get(id=Id).imagen
        f = Foto(id=Id,
                 nombre=cleaned_data.get('nombre'),
                 imagen = newImg,
                 descripcion = cleaned_data.get('descripcion'))
        f.save()
        if not Id:
            p.fotos.add(f)  
        return f        


class AdminDeleteFotoForm(forms.Form):
    id = forms.IntegerField(widget=forms.HiddenInput)
    
    def save(self):
        """
        borra la foto
        """
        f = get_object_or_404(Foto, id=self.cleaned_data['id'])
        return f.delete()


class AdminVideoForm(forms.ModelForm):    
    id = forms.IntegerField(widget=forms.HiddenInput, required=False)

    class Meta:
        model = Video

    def saveTo(self, p):
        """
        grava(o actualiza) el video y lo agrega a los objectos relacionados
        del objeto p, siempre y cuando el related name sea videos

        """
        cleaned_data = self.cleaned_data
        Id = cleaned_data.get('id')
        v = Video(id=Id,
                 nombre=cleaned_data.get('nombre'),
                 url = cleaned_data.get('url'),
                 descripcion = cleaned_data.get('descripcion'))
        v.save()
        if not Id:
            p.videos.add(v) 
        return v


class AdminDeleteVideoForm(forms.Form):
    id = forms.IntegerField(widget=forms.HiddenInput)
    
    def save(self):
        """
        borra el video
        """
        v = get_object_or_404(Video, id=self.cleaned_data['id'])
        return v.delete()


class AdminCaracteristicaForm(forms.Form):
    id = forms.IntegerField(widget=forms.HiddenInput, required=False)
    nombre = forms.CharField(max_length=120)
    descripcion = forms.CharField(widget=forms.Textarea, max_length=500)
    proyecto = forms.IntegerField(widget=forms.HiddenInput)

    def save(self):
        """
        grava(o actualiza) la característica
        """
        cleaned_data = self.cleaned_data
        Id = cleaned_data.get('id')
        c = Caracteristica(
            id=Id,
            nombre=cleaned_data.get('nombre'),
            descripcion = cleaned_data.get('descripcion'),
            proyecto=get_object_or_404(Proyecto,id=cleaned_data.get('proyecto'))
                           )
        return c.save()


class AdminBeneficioForm(forms.Form):
    id = forms.IntegerField(widget=forms.HiddenInput, required=False)
    descripcion = forms.CharField(widget=forms.Textarea, max_length=500)
    proyecto = forms.IntegerField(widget=forms.HiddenInput)

    def save(self):
        """
        grava(o actualiza) el beneficio
        """
        cleaned_data = self.cleaned_data
        Id = cleaned_data.get('id')
        c = Beneficio(
            id=Id,
            descripcion = cleaned_data.get('descripcion'),
            proyecto=get_object_or_404(Proyecto,id=cleaned_data.get('proyecto'))
                           )
        return c.save()


class AdminContactoForm(forms.Form):
    id = forms.IntegerField(widget=forms.HiddenInput, required=False)
    proyecto = forms.IntegerField(widget=forms.HiddenInput)
    direccion = forms.CharField(max_length=200)
    email = forms.EmailField(u'e-mail')
    # telefono = forms.CharField()
    # tipo_telefono = forms.ModelChoiceField(empty_label = 'tipo',
    #                                        queryset=TipoTelefono.objects.all())
    def save(self):
        """
        grava la informacion del contacto
        """
        cleaned_data = self.cleaned_data
        c = Contacto(
            id=cleaned_data.get('id'),
            proyecto=get_object_or_404(Proyecto, 
                                       id=cleaned_data.get('proyecto')),
            direccion=cleaned_data.get('direccion'),
            email=cleaned_data.get('email'))
        return c.save()

        
class AdminTelefonoForm(forms.ModelForm):
#    id = forms.IntegerField(widget=forms.HiddenInput, required=False)

    class Meta:
        model = Telefono

    def saveTo(self, obj):
        """
        graba y añade el telefono a la lista de teléfonos
        requiere que el related_name a telefono sea telefonos
        """
        #Id=self.cleaned_data.get('id')
        t = self.save()
        obj.telefonos.add(t)
        return t


class BaseAdminTelefonoFormSet(BaseFormSet):
    def save(self, obj):
        """
        guarda todos los forms no vacios
        """
        for f in self.forms:
            if f.has_changed():
                f.saveTo(obj)
        

AdminFonoFormSet = formset_factory(AdminTelefonoForm,
                                   formset=BaseAdminTelefonoFormSet,
                                   extra=1, max_num=10)


class AdminDeleteTelefonoForm(forms.Form):
    id = forms.IntegerField(widget=forms.HiddenInput)
    
    def save(self):
        """
        borra el telefono
        """
        v = get_object_or_404(Telefono, id=self.cleaned_data['id'])
        return v.delete()


class AdminAvanceForm(forms.ModelForm):
    id = forms.IntegerField(widget=forms.HiddenInput, required=False)
    # etapa = forms.ModelChoiceField(queryset=Etapa.objects.none())
    # subetapa = forms.ModelChoiceField(queryset=SubEtapa.objects.none())
    ESTADO_CHOICES = (
        (u"B", _(u"borrador")),
        (u"O", _(u"oculto")),
        (u"P", _(u"publicado")),
    )
    estado = forms.ChoiceField(choices=ESTADO_CHOICES, required=False, 
                               initial=u'B')

    class Meta:
        model = Avance
        exclude = ('fotos', 'videos', 'subetapa')

    def __init__(self, *args, **kwargs):
        """
        si el usuario es un superusuario el queryset de proyectos es de todos 
        los proyectos, en caso contrario sera solo de los proyecto a los que 
        esta asignado
        """
        try:
            user=kwargs.pop('user')
        except:
            user=''
        super(AdminAvanceForm,self).__init__(*args, **kwargs)
        if user and not user.is_superuser:
            self.fields['proyecto'].queryset= user.proyecto_set.all()

    def clean(self):
        """
        Validación 1: verifica que la etapa este dentro del proyecto 
                       seleccionado        
        Validación 2: verifica que la subetapa este dentro de la etapa
                       seleccionada
        Validación 3: verifica si se cambio de subetapa a un avance creado,
                      si es el caso verifica que la nueva subetapa no tenga
                      ya un avance asociado
                      CORRECCION:
                      verifica que solo se puedan cambiar de subetapa aquellos
                      avances que no tengan milestones asociados, esto para 
                      evitar conflictos entre los milestones
        Validación 4: verifica que si es una nuevo avance la subetapa 
                      seleccionada no tenga ya un avance asociado
                      CORRECCION:
                      verifica que si es un nuevo avance la subetapa
                      seleccionada no este completada al 100% segun sus
                      milestones asociados
        """
        cleaned_data = super(self.__class__, self).clean()
        proyecto = self.cleaned_data.get('proyecto')
        etapa = self.data.get('etapa')
        subetapa = self.data.get('subetapa')
        error_msg = u'No olvide seleccionar la etapa y sub-etapa'
        Id = cleaned_data.get('id')
        #Validación 1
        if not etapa or int(etapa) not in [i[0] for i in \
proyecto.etapa_set.values_list('id')]:
            self.data = self.data.copy()
            self.data['proyecto']=''
            raise forms.ValidationError(error_msg)
        
        #Validación 2
        etapa = Etapa.objects.get(id=etapa)
        if not subetapa or int(subetapa) not in [i[0] for i in \
etapa.subetapa_set.values_list('id')]:
            self.data = self.data.copy()
            self.data['proyecto']=''
            raise forms.ValidationError(error_msg)

        #Validacion 3
#         if Id:
#             old = get_object_or_404(Avance, id=cleaned_data.get('id'))
#             if proyecto and etapa and subetapa:
#                 if int(subetapa) != int(old.subetapa.id) and \
# SubEtapa.objects.get(id=subetapa).avance_set.all():
#                     msg = u'La etapa seleccionada ya tiene asociado un avance'
#                     raise forms.ValidationError(msg)
        if Id:
            avance = get_object_or_404(Avance, id=cleaned_data.get('id'))
            if proyecto and etapa and subetapa:
                if int(subetapa) != int(avance.subetapa.id) and \
avance.milestone_set.all():
                    msg = u'Sólo se pueden cambiar de subetapa a los avances \
que no tienen milestones asociados'
                    raise forms.ValidationError(msg)
                    
        #Validación 4
#         if not cleaned_data.get('id') and proyecto and subetapa and etapa and \
# SubEtapa.objects.get(id=subetapa).avance_set.all():
#             self.data = self.data.copy()
#             self.data['proyecto']=''
#             msg = u'La etapa seleccionada ya tiene asociado un avance'
#             raise forms.ValidationError(msg)
        if not cleaned_data.get('id') and proyecto and subetapa and etapa:
            querySet=SubEtapa.objects.get(id=subetapa).milestone_set.all()
            suma = 0
            if querySet:
                suma = querySet.aggregate(s=Sum('porcentaje'))
                suma = suma['s']
            if suma == 100:
                self.data = self.data.copy()
                self.data['proyecto']=''
                msg = u'Según los milestones de la etapa seleccionada, esta ya \
está representada al 100%. No puede agregar más avances.'
                raise forms.ValidationError(msg)


        if self._errors:
            self.data = self.data.copy()
            self.data['proyecto']=''
            
        return cleaned_data                

    @transaction.commit_on_success
    def save(self, request):
        """
        graba o actualiza el avance
        si se cambio de subetapa y el avance ya tenia milestones se actualizan
        las fk's subetapa de los milestones del avance y se recalcula el avance
        del proyecto en el save de cada milestone
        si se cambio de proyecto y habian milestones asociados se recalcula el
        avance del donde estuvo asociado
        """
        Id = self.cleaned_data.get('id')
        subetapa = SubEtapa.objects.get(id=self.data['subetapa'])
        proyecto = self.cleaned_data.get('proyecto')
        a = Avance(id=Id, notas=self.cleaned_data.get('notas'),
                   estado=self.cleaned_data.get('estado'),
                   proyecto=proyecto, subetapa=subetapa,
                   fecha_creacion=datetime.now(),
                   )
        if Id:
            old = Avance.objects.get(id=Id)
            a.fecha_creacion=old.fecha_creacion
            mSet= old.milestone_set.all()
            if subetapa != old.subetapa and mSet:
                mList = u''
                for m in mSet:
                    m.subetapa = subetapa
                    m.save()
                    mList+='%s, ' % m.titulo
                mList = mList[:-2] + '.'
                messages.warning(request, 'Los siguientes milestones fueron \
asignados a la subetapa %s: %s' % (subetapa.titulo,mList)) 
            if proyecto != old.proyecto and mSet:
                old.proyecto.recalcular_avance();
        a.save()
        return a


class AdminMilestoneForm(forms.ModelForm):
    id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    fecha_fin = forms.DateField(widget=widgets.AdminDateWidget(), required=False)
    subetapa = forms.IntegerField(widget=forms.HiddenInput())
    avance = forms.IntegerField(widget=forms.HiddenInput())

    class Meta:
        model = Milestone
        exclude = ('subetapa', 'avance',)

    def clean(self):
        """
        validacion 1: verifica que
          fecha_inicio(subetapa) <= fecha_fin(milestone) <= fecha_fin(subetapa)
          siempre y cuando se tengan todas las fechas ingresadas
        validacion 2: verifica que el porcentaje <= 100%
        """
        cleaned_data=super(self.__class__, self).clean()
        subetapa = self.cleaned_data.get('subetapa')

        #validacion 1
        if 'fecha_fin' in cleaned_data :
            if subetapa.fecha_inicio and subetapa.fecha_fin:
                if subetapa.fecha_inicio > cleaned_data['fecha_fin'] or \
subetapa.fecha_fin < cleaned_data['fecha_fin']:
                    msg = 'La fecha de finalización está fuera de las fecha de \
inicio (%s) y fin (%s) de la subetapa' % \
( subetapa.fecha_inicio.strftime('%d/%m/%Y'), \
subetapa.fecha_fin.strftime('%d/%m/%Y') )
                    self._errors['fecha_fin'] = self.error_class([msg])
                    del cleaned_data['fecha_fin']

        #validacion 2
        p = self.cleaned_data.get('porcentaje')
        if subetapa and p:
            suma = 0
            querySet = subetapa.milestone_set.all()
            if (querySet):
                suma = querySet.aggregate(s=Sum('porcentaje'))
                suma = suma['s']
            Id = self.cleaned_data.get('id')
            try:
                anterior_porcentaje = Milestone.objects.get(id=Id).porcentaje
                sum2 = suma+p-anterior_porcentaje
            except:
                sum2 = suma+p
            msg = ''
#             if suma == 100:
#                 raise forms.ValidationError('Ya se alcanzó el 100% de la \
# sub-etapa. No puede de agregar  más Milestones')
#             elif sum2 > 100:
            if sum2 > 100:
                msg = u'Con el porcentaje ingresado se obtiene  el %s%s. \
Actualmente los milestones ingresados representan el  %s%s de la \
sub-etapa' % (sum2,'%',suma,'%') 
                self._errors['porcentaje'] = self.error_class([msg])
                del cleaned_data['porcentaje']

        return cleaned_data

    def clean_subetapa(self):
        """
        verifica que la subetapa existe
        """
        try:
            return SubEtapa.objects.get(id=self.cleaned_data['subetapa'])
        except:
            raise forms.ValidationError(u'La subetapa no existe')
        
    def clean_avance(self):
        """
        verifica que el avance existe
        """
        try:
            return Avance.objects.get(id=self.cleaned_data['avance'])
        except:
            raise forms.ValidationError(u'El avance no existe')

    def clean_porcentaje(self):
        """
        verifica 0 < porcentaje <= 100
        y que los porcentajes de las etapas del proyecto no excedan el 100%
        """
        p = self.cleaned_data['porcentaje']
        if  p <= 0 or p > 100:
            raise forms.ValidationError("Ingrese un valor entre 1 y 100") 
        return p

    def save(self):
        """
        graba o actualiza el Milestone
        """
        m = Milestone(
            id=self.cleaned_data.get('id'),
            titulo=self.cleaned_data.get('titulo'),
            fecha_fin=self.cleaned_data.get('fecha_fin'),
            porcentaje=self.cleaned_data.get('porcentaje'),
            alcanzado=self.cleaned_data.get('alcanzado'),
            subetapa=self.cleaned_data['subetapa'],
            avance=self.cleaned_data['avance'])
        m.save()
        return m


class AdminOfertaForm(forms.ModelForm):
    id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    descripcion = forms.CharField(widget=TinyMCE(attrs={'cols':80, 'rows':30}))
    fecha_inicio = forms.DateField(widget=widgets.AdminDateWidget())

    class Meta:
        model = Oferta

    def __init__(self, *args, **kwargs):
        super(self.__class__,self).__init__(*args, **kwargs)
#         self.fields['tipo_item'].help_text = u'Los tipos de items cambian \
# según los proyectos seleccionados'
        self.fields['item'].help_text = u'Los items cambian \
según los proyectos seleccionados'

    def clean(self):
        """
        verifica que las ofertas del proyecto del mismo tipo_item no se
        superpongan en fechas
        """
        cd = super(self.__class__,self).clean()
        fecha_inicio = cd.get('fecha_inicio')
        #tipo_item = cd.get('tipo_item')
        item = cd.get('item')
        duracion = cd.get('duracion')            
        proyecto = cd.get('proyecto')
        #if not proyecto or not tipo_item or not fecha_inicio or not duracion:
        if not proyecto or not item or not fecha_inicio or not duracion:
            return cd
        ofertas = proyecto.oferta_set.all()
        id = cd.get('id')
        #extrayendo a la oferta para que no se interrumpa con sus propias fechas
        #en caso es este actualizando
        if id:
            ofertas=ofertas.exclude(id=id)
        #if fecha_inicio and tipo_item and duracion:
        if fecha_inicio and item and duracion:
            fecha_fin = ''
            #for o in Oferta.objects.filter(tipo_item=tipo_item):
            #for o in ofertas.filter(tipo_item=tipo_item):
            for o in ofertas.filter(item=item):
                #la fecha de inicio esta incluida dentro de otra oferta
                if fecha_inicio >= o.fecha_inicio and \
fecha_inicio < o.fecha_fin:
                    msg = u'La fecha de inicio cae dentro de otra oferta de \
este mismo tipo de item con fechas %s - %s' % (
                        o.fecha_inicio.strftime('%d/%m/%Y'),
                        o.fecha_fin.strftime('%d/%m/%Y')
                        )
                    self._errors['fecha_inicio'] = self.error_class([msg])
                    del cd['fecha_inicio']
                    break
                fecha_fin = fecha_inicio + timedelta(days=duracion)
                #la fecha fin esta incluida dentro de otra oferta
                if fecha_fin > o.fecha_inicio and fecha_fin <= o.fecha_fin:
                    msg = u'La fecha de finalización cae dentro de otra oferta \
de este mismo tipo de item con fechas %s - %s' % (
                        o.fecha_inicio.strftime('%d/%m/%Y'),
                        o.fecha_fin.strftime('%d/%m/%Y')
                        )
                    self._errors['duracion'] = self.error_class([msg])
                    del cd['duracion']
                    break
                #la oferta inicio antes y termina despues que la oferta 'o'
                if fecha_inicio < o.fecha_inicio and fecha_fin > o.fecha_inicio:
                    msg = u'Esta oferta incluye los dias de vigencia de otra  \
oferta (en este mismo item) con fechas %s - %s' % (
                        o.fecha_inicio.strftime('%d/%m/%Y'),
                        o.fecha_fin.strftime('%d/%m/%Y')
                        )
                    self._errors['duracion'] = self.error_class([msg])
                    del cd['duracion']
                    break
        return cd

    def clean_tasa_descuento(self):
        """
        verifica que el descuento este entre 1 u 100
        """
        dcto = self.cleaned_data.get('tasa_descuento')
        if dcto < 1 or dcto > 100:
            raise forms.ValidationError(u'El porcentaje de descuento debe\
 estar entre 1 y 100')
        return dcto

    def clean_duracion(self):
        """
        verifica que la duracion sea mayor que 0
        """
        duracion = self.cleaned_data.get('duracion')
        if 'duracion' in self.cleaned_data and duracion <= 0:
            raise forms.ValidationError(u'La duración debe ser mayor que 0')
        return duracion

    # def clean_item(self):
    #     """
    #     Verifica que la oferta se aplica sobre un item que no tenga ofertas
    #     vigentes sobre el
    #     """
    #     item = self.cleaned_data.get('item')
    #     item.oferta_set.filter(fecha_fin__lte=date.today())
        
                    
    def save(self):
        """
        si hay id (no borrado) realiza un update
        sino un insert
        """
        obj = Oferta(id=self.cleaned_data.get('id'),
                     descripcion=self.cleaned_data['descripcion'],
                     proyecto=self.cleaned_data['proyecto'],
                     #tipo_item=self.cleaned_data['tipo_item'],
                     item=self.cleaned_data['item'],
                     tasa_descuento=self.cleaned_data['tasa_descuento'],
                     fecha_inicio=self.cleaned_data['fecha_inicio'],
                     duracion=self.cleaned_data['duracion'],)
        obj.save()
        return obj


class SendMail1(forms.Form):
    receivers = forms.CharField(label=u'Para:', max_length=120, 
        help_text=u'Escriba las direcciones separadas por comas')
    subject = forms.CharField(label=u'Asunto', max_length=100)
    content = forms.CharField(label=u'Contenido', widget=forms.Textarea, max_length=250)

    def clean_receivers(self):
        """
        verifica que los correos ingresados sean correcto y devuelve
        una lista de los correos
        """
        receivers = self.cleaned_data.get('receivers')
        if receivers:
            receivers = [e.strip() for e in receivers.split(',')]
            for receiver in receivers:
                try:
                    validate_email( receiver )
                except ValidationError:
                    raise forms.ValidationError(u'Uno o más correos no son \
válidos')
        return receivers

    def save(self, sender):
        """
        envia el o los correos
        """
        cd= self.cleaned_data
        data={'sender': sender.get_full_name(),
              'content': cd['content'],
              'sitio':Site.objects.get(id=1),
              'STATIC_URL':settings.STATIC_URL,
              'inmobiliaria':Inmobiliaria.objects.get(id=1)}

        for receiver in cd['receivers']:
            send_html_mail(settings.DEFAULT_FROM_EMAIL, cd['subject'], 
                           'simple_mail.html', data, receiver, cd['content'], 
                           path='email_templates/')


class SendMail2(forms.Form):
    allusers = forms.BooleanField(label='A Todos', required=False,
                                  help_text=u'Envía el correo a todos los \
usuarios del portal (excluyendo a los administratores)')
    rubros = forms.ModelMultipleChoiceField(label=u'Por Rubros',
        queryset=Rubro.objects.all(), required=False,
        widget=widgets.FilteredSelectMultiple(u'Rubros de Interés',False),
        help_text=u'Envía el correo a todos los usuarios interesados en los \
rubros seleccionados')
    proyectos = forms.ModelMultipleChoiceField(label=u'Por Proyectos',
        queryset=Proyecto.accepted.all(), required=False,
        widget=widgets.FilteredSelectMultiple(u'Proyectos de Interés',False),
        help_text=u'Envía el correo a todos los usuarios interesados en los \
proyectos seleccionados')
    subject = forms.CharField(label=u'Asunto', max_length=100)
    content = forms.CharField(label=u'Contenido', widget=forms.Textarea, max_length=250)

    def clean(self):
        """
        Verificación 1: que se selecciono alguna opcion de envio
        Verificación 2: que se haya seleccionado solo una de las 3 opciones de
        envio de correos
        """
        cleaned_data = super( self.__class__, self ).clean()
        allusers = cleaned_data.get('allusers')
        rubros = cleaned_data.get('rubros')
        proyectos =  cleaned_data.get('proyectos')
        
        #Verificación 1
        if not allusers and not rubros and not proyectos:
            raise forms.ValidationError(u'Debe seleccionar una de las 3 \
opciones de envio')

        #Verificación 2
        if allusers and rubros and proyectos or \
allusers and rubros and not proyectos or \
allusers and not rubros and proyectos or not allusers and rubros and proyectos:
            raise forms.ValidationError(u'Sólo debe seleccionar una de las 3 \
opciones de envío')
        return cleaned_data

    def save(self, sender):
        """
        envia el o los correos
        """
        cd= self.cleaned_data
        allusers = cd.get('allusers')
        rubros = cd.get('rubros')
        proyectos =  cd.get('proyectos')
        receivers = []
        if allusers:
            receivers = Cliente.objects.values_list('usuario__email')
        elif rubros:
            for rubro in rubros:
                receivers.extend(
                    rubro.cliente_set.values_list('usuario__email'))
        else:
            for proyecto in proyectos:
                receivers.extend(
                    proyecto.clientes.values_list('usuario__email'))
                
        data={'sender': sender.get_full_name(),
              'content': cd['content'],
              'sitio':Site.objects.get(id=1),
              'STATIC_URL':settings.STATIC_URL,
              'inmobiliaria':Inmobiliaria.objects.get(id=1)}

        for receiver in receivers:
            send_html_mail(settings.DEFAULT_FROM_EMAIL, cd['subject'], 
                           'simple_mail.html', data, receiver[0], cd['content'],
                           path='email_templates/')


class SendMail3(forms.Form):
    allusers = forms.BooleanField(label='A Todos', required=False,
                                  help_text=u'Envía el correo a todos los \
administradores del portal')
    grupos = forms.ModelMultipleChoiceField(label=u'Por Tipos',
       queryset=Group.objects.all(), required=False,
       widget=widgets.FilteredSelectMultiple(u'Tipos de Administradores',False),
       help_text=u'Envía el correo a todos los administradores de los tipos \
seleccionados')    
    proyectos = forms.ModelMultipleChoiceField(label=u'Filtrar Por Proyectos',
        queryset=Proyecto.accepted.all(), required=False,
        widget=widgets.FilteredSelectMultiple(u'Proyectos de Interés',False),
        help_text=u'Envía el correo a todos los administradores relacionados \
con los proyectos seleccionados')
    subject = forms.CharField(label=u'Asunto', max_length=100)
    content = forms.CharField(label=u'Contenido', widget=forms.Textarea, 
                              max_length=250)

    def clean(self):
        """
        Verificación 1: que se selecciono alguna opcion de envio
        Verificación 2: que se haya seleccionado solo una de las 2 opciones de
        envio de correos
        """
        cleaned_data = super( self.__class__, self ).clean()
        allusers = cleaned_data.get('allusers')
        grupos = cleaned_data.get('grupos')
        
        #Verificación 1
        if not allusers and not grupos:
            raise forms.ValidationError(u'Debe seleccionar una de las 2 \
opciones de envio')

        #Verificación 2
        if allusers and grupos:
            raise forms.ValidationError(u'Sólo debe seleccionar una de las 2 \
opciones de envío')
        return cleaned_data

    def save(self, sender):
        """
        envia el o los correos
        """
        cd= self.cleaned_data
        allusers = cd.get('allusers')
        grupos = cd.get('grupos')
        proyectos =  cd.get('proyectos')
        receivers = []
        if allusers:
            if not proyectos:
                receivers = User.objects.filter(is_staff=True).values_list(
                    'email')
            else:
                for proyecto in proyectos:
                    receivers.extend(proyecto.usuarios.filter(is_staff=True).\
values_list('email'))
        else:
            if not proyectos:
                for grupo in grupos:
                    receivers.extend(grupo.user_set.values_list('email'))
            if proyectos:
                tmp = []
                for proyecto in proyectos:
                    receivers.extend(proyecto.usuarios.filter(is_staff=True))
                for u in receivers:
                    for g in u.groups.all():
                        if g in grupos and (u.email,) not in tmp:
                            tmp.append((u.email,))
                receivers = tmp
                
        data={'sender': sender.get_full_name(),
              'content': cd['content'],
              'sitio':Site.objects.get(id=1),
              'STATIC_URL':settings.STATIC_URL,
              'inmobiliaria':Inmobiliaria.objects.get(id=1)}

        for receiver in receivers:
            send_html_mail(settings.DEFAULT_FROM_EMAIL, cd['subject'], 
                           'simple_mail.html', data, receiver[0], cd['content'],
                           path='email_templates/')


class AdminPlanoForm(forms.ModelForm):
    id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    plano = forms.ImageField(required=False, widget=forms.FileInput())

    class Meta:
        model = Plano
        exclude = ('plano_dibujado','actualizacion',)

    def clean(self):
        """
        validación 1: verifica que la imagen del plano este ausente solo si el
        id esta presente
        """
        #validación 1
        cleaned_data = super(self.__class__, self).clean()
        id = cleaned_data.get('id')
        plano = cleaned_data.get('plano')
        if not plano and not id:
            msg = u'Este campo es obligatorio'
            self._errors['plano'] = self.error_class([msg])
        return cleaned_data

    def save(self):
        """
        graba o actualiza el objeto

        si el plano ya existe y se subio uno nuevo, borra las imagenes 
        anteriores(del plano y plano dibujado) para que no se acumulen
        y luego de grabar el plano genera el plano dibujado
        """
        cd = self.cleaned_data
        id = cd.get('id')
        plano_dibujado = None
        if id and not cd.get('plano'):
            p = get_object_or_404(Plano, id = id)
            self.cleaned_data = self.cleaned_data.copy()
            cd = self.cleaned_data
            cd['plano'] = p.plano
            plano_dibujado = p.plano_dibujado

        elif id and cd.get('plano'):
            #removiendo imagenes anteriores 
            plano = Plano.objects.get(id=id)
            plano.plano.delete()
            try:
                plano.plano_dibujado.delete()
            except:
                a=1

        if not id:
            plano_dibujado = cd['plano']
                
        p = Plano(id = id,
                  titulo = cd['titulo'],
                  descripcion = cd['descripcion'],
                  proyecto = cd['proyecto'],
                  plano = cd['plano'],
                  plano_dibujado = plano_dibujado)
        p.save()
        
        if id and cd.get('plano'):
            p.create_plano_image()

        return p


class AdminItemForm(forms.ModelForm):
    id = forms.IntegerField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Item
        exclude = ('poligono', 'estado')

    def __init__(self, *args, **kwargs):
        """
        pone hidden al plano y si el objeto fue inicializado, filtra los tipos
        de item correspondiente al proyecto
        """
        super(AdminItemForm,self).__init__(*args, **kwargs)
        self.fields['plano'].widget = forms.HiddenInput()
        if 'initial' in kwargs:
            self.fields['tipo_item'].queryset= kwargs['initial']['plano'].\
proyecto.tipoitem_set.all()

    def get_list_of_coordinates(self):
        """
        retorna una lista con las coordenadas de la region
        """
        #si se vuelve a poner el campo estado ponerle -7
        numPoints = len(self.data) - 6
        return [self.data[unicode(i)].split(',') for i in xrange(numPoints)]

    @transaction.commit_on_success
    def save(self):
        """
        Crea el poligono, asocia sus puntos y guarda el item
        """
        cd = self.cleaned_data
        d = self.data
        colores_relleno = {'D':'#009900', 'S':'#FFFF00', 'V':'#FF0000'}
        poligono = Poligono(nombre='%s - poligono' % (cd['plano']) ,
                             color_borde= colores_relleno['D'],
                             color_relleno= colores_relleno['D'])
        poligono.save()
        #si se vuelve a poner el campo estado ponerle -7        
        numPoints = len(self.data) - 6
        for i in xrange(numPoints):
            coordinate = d[unicode(i)].split(',')
            point=Punto(x=coordinate[0], y=coordinate[1], poligono=poligono)
            point.save()

        item = Item(numero = cd['numero'], tipo_item = cd['tipo_item'],
                    plano = cd['plano'], 
                    detalles = cd['detalles'], poligono  = poligono)
        item.save(update_poligon=False)

        return item


class AdminEditItemForm(AdminItemForm):
    """
    en este form hay q trabajar todo la logica al cambiar el estado de un item

    todas las solicitudes se van a tratar en su interface

    solo se podra cambiar el estado a aquellos items que esten disponibles y no
    tengan solicitudes en espera

    si un item esta disponible cualquiera puede cambiar su estado
    sino solo quien cambio el estado puede cambiarlo

    la seleccion del cliente sera obligatoria si se cambia el estado a separado
    o vendido    
    """
    id = forms.IntegerField(widget=forms.HiddenInput(), required=False)    
    #ver si es factible cambiarlo por un iterador
    cliente = forms.ModelChoiceField(label=u'Cliente',
                                     queryset=Cliente.objects.all(), 
                                     required=False)
    user_id = forms.IntegerField(required=False, widget = forms.HiddenInput())

    class Meta:
        model = Item

    def __init__(self, *args, **kwargs):
        super(AdminEditItemForm,self).__init__(*args, **kwargs)
        self.fields['poligono'].widget = forms.HiddenInput()
        if 'instance' in kwargs:
            self.fields['tipo_item'].queryset= kwargs['instance'].plano.\
proyecto.tipoitem_set.all()


    @transaction.commit_on_success
    def save(self):
        """
        guarda el objecto
        crea el registro en la tabla CambioEstadoItem
        """
        cd = self.cleaned_data
        item = Item(id = cd['id'],
                    numero = cd['numero'],
                    tipo_item = cd['tipo_item'],
                    plano = cd['plano'],
                    estado = cd['estado'],
                    detalles = cd['detalles'],
                    poligono = cd['poligono'],
                    cliente = cd['cliente'])
        item.save()

        CambioEstadoItem.objects.create(
            estado = cd['estado'],
            admin = User.objects.get(id=self.data['user_id']),
            item = item,
            cliente = cd['cliente'])
            
        return item
        
    def clean(self):
        """
        verificación 1: el item esta disponible o fue modificado por el usuario
        que intenta realizar un cambio
        verificación 2: el item no tiene solicitudes en estado de espera o 
        tramite
        verificacion 3: se ingreso un cliente porque el estado es diferente a
        disponible
        """
        cd = super(AdminEditItemForm,self).clean()
        user = User.objects.get(id=self.data['user_id'])
        item = get_object_or_404(Item, id=cd['id'])
        try:
            last_modificator = item.cambioestadoitem_set.latest('id').admin
        except:
            last_modificator = ''
        solicitudes_esperando = item.solicitud_set.filter(
            Q(estado=u'E') | Q(estado=u'T'))
        cliente = cd.get('cliente')

        # verificación 1
        # TODO: Se ha deshabilitado por el momento esta restricción
#        if item.estado != u'D':
#            if user != last_modificator:
#                msg = u'Sólo puede modificar items con estado disponible o \
#                        aquellos que usted haya cambiado de estado.'
#                raise forms.ValidationError(msg)

        #verificación 2        
        if solicitudes_esperando:
            msg = u'Este item tiene solicitudes en trámite o espera.'
            raise forms.ValidationError(msg)            

        #verificación 3
        if not cliente and cd['estado'] != u'D':
            msg = u'El estado ingresado requiere que seleccione un cliente'
            self._errors['cliente'] = self.error_class([msg])

        return cd
        
    def set_user_id(self, user_id):
        """
        pone el user_id en la data del form
        """
        self.data = self.data.copy()
        self.data['user_id'] = user_id        


class AdminTipoItemForm(forms.ModelForm):
    class Meta:
        model =  TipoItem

    def save(self,*args, **kwargs):
        """
        si no se pone una imagen x defecto al tipo de item:
        1- Si el proyecto tiene logo este se asigna como imagen
        2- Sino, se le asigna una imagen x defecto
        """
        tipoitem = super(AdminTipoItemForm,self).save(*args, **kwargs)
        if not tipoitem.foto:
            name  = tipoitem.proyecto.logo.name
            if not name:
                name = 'no-image.png'
            tipoitem.foto = name
            tipoitem.save()
        return tipoitem


class DesarrolladoAdminForm(forms.ModelForm):
    """
    Formulario para el admin de un proyecto desarrollado
    """
    descripcion = forms.CharField(
        widget=TinyMCE(attrs={'cols': 100, 'rows': 20}), required=False)

    class Meta:
        model = Desarrollado