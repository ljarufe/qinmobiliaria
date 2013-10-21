# -*- coding: utf-8 -*-

from django import forms
from django.db.models import ManyToOneRel
from django.db.models import ManyToManyRel
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper

from tinymce.widgets import TinyMCE

from zinnia.models import Entry
from zinnia.models import Category
from zinnia.admin.widgets import TreeNodeChoiceField
from zinnia.admin.widgets import MPTTFilteredSelectMultiple
from zinnia.admin.widgets import MPTTModelMultipleChoiceField


class CategoryAdminForm(forms.ModelForm):
    """Form for Category's Admin"""
    parent = TreeNodeChoiceField(
        label=_('parent category').capitalize(),
        required=False, empty_label=_('No parent category'),
        queryset=Category.tree.all())

    def __init__(self, *args, **kwargs):
        super(CategoryAdminForm, self).__init__(*args, **kwargs)
        rel = ManyToOneRel(Category, 'id')
        self.fields['parent'].widget = RelatedFieldWidgetWrapper(
            self.fields['parent'].widget, rel, self.admin_site)

    def clean_parent(self):
        """Check if category parent is not selfish"""
        data = self.cleaned_data['parent']
        if data == self.instance:
            raise forms.ValidationError(
                _('A category cannot be parent of itself.'))
        return data

    class Meta:
        """CategoryAdminForm's Meta"""
        model = Category


class EntryAdminForm(forms.ModelForm):
    """Form for Entry's Admin"""
    categories = MPTTModelMultipleChoiceField(
        label=_('Categories'), required=False,
        queryset=Category.objects.all(),
        widget=MPTTFilteredSelectMultiple(_('categories'), False,
                                          attrs={'rows': '10'}))
    content = forms.CharField(widget=TinyMCE(attrs={'cols':80, 'rows':30}))

    def __init__(self, *args, **kwargs):
        super(EntryAdminForm, self).__init__(*args, **kwargs)
        rel = ManyToManyRel(Category, 'id')
        self.fields['categories'].widget = RelatedFieldWidgetWrapper(
            self.fields['categories'].widget, rel, self.admin_site)
        self.fields['sites'].initial = [Site.objects.get_current()]
        #self.fields['status'].required = False

    class Meta:
        """EntryAdminForm's Meta"""
        model = Entry

    # def save(self, *args, **kwargs):
    #     """
    #     si no recibio status por post modifica la data y le pone es estado 
    #     por defecto que es DRAF
    #     """
    #     from zinnia.managers import DRAFT, HIDDEN, PUBLISHED
    #     print self.cleaned_data['status']

    #     status = self.cleaned_data.get('status')
    #     if not status:
    #         self.cleaned_data = self.cleaned_data.copy()
    #         self.cleaned_data['status'] = DRAFT
    #     return super( EntryAdminForm, self ).save( *args, **kwargs )