# -*- coding: utf-8 -*-

import datetime
from django.conf import settings
from django import forms
from django.contrib.comments.forms import CommentSecurityForm
from django.utils.encoding import force_unicode
from django.utils.translation import ungettext, ugettext_lazy as _
from django.contrib.comments.models import Comment
from django.utils.text import get_text_list
from django.contrib.contenttypes.models import ContentType


class CommentForm(CommentSecurityForm):
    """
    Formulario para un comentario
    """
    name = forms.CharField(label=_("Name"), max_length=50)
    email = forms.EmailField(label=_("e-mail"))
    comment = forms.CharField(label=_('Comment'), widget=forms.Textarea,
                              max_length=300)

    def save(self):
        """
        Graba el comentario
        """
        comment = self.get_comment_object()
        comment.save()
        return comment

    def get_comment_object(self):
        """
        Return a new (unsaved) comment object based on the information in this
        form. Assumes that the form is already validated and will throw a
        ValueError if not.

        Does not set any of the fields that would come from a Request object
        (i.e. ``user`` or ``ip_address``).
        """
        if not self.is_valid():
            raise ValueError("get_comment_object may only be called on valid forms")

        CommentModel = self.get_comment_model()
        new = CommentModel(**self.get_comment_create_data())
        new = self.check_for_duplicate_comment(new)

        return new

    def get_comment_model(self):
        """
        Get the comment model to create with this form. Subclasses in custom
        comment apps should override this, get_comment_create_data, and perhaps
        check_for_duplicate_comment to provide custom comment models.
        """
        return Comment

    def get_comment_create_data(self):
        """
        Returns the dict of data to be used to create a comment. Subclasses in
        custom comment apps that override get_comment_model can override this
        method to add extra fields onto a custom comment model.
        """
        return dict(
            content_type = ContentType.objects.get_for_model(self.target_object),
            object_pk    = force_unicode(self.target_object._get_pk_val()),
            user_name    = self.cleaned_data["name"],
            user_email   = self.cleaned_data["email"],
            comment      = self.cleaned_data["comment"],
            submit_date  = datetime.datetime.now(),
            site_id      = settings.SITE_ID,
            is_public    = True,
            is_removed   = False,
        )

    def check_for_duplicate_comment(self, new):
        """
        Check that a submitted comment isn't a duplicate. This might be caused
        by someone posting a comment twice. If it is a dup, silently return the *previous* comment.
        """
        possible_duplicates = self.get_comment_model()._default_manager.using(
            self.target_object._state.db
        ).filter(
            content_type = new.content_type,
            object_pk = new.object_pk,
            user_name = new.user_name,
            user_email = new.user_email,
            user_url = new.user_url,
        )
        for old in possible_duplicates:
            if old.submit_date.date() == new.submit_date.date() and old.comment == new.comment:
                return old

        return new

    def clean_comment(self):
        """
        If COMMENTS_ALLOW_PROFANITIES is False, check that the comment doesn't
        contain anything in PROFANITIES_LIST.
        """
        # TODO: Cambiar el contenido de PROFANITIES_LIST
        comment = self.cleaned_data["comment"]
        if not settings.COMMENTS_ALLOW_PROFANITIES:
            bad_words = [w for w in settings.PROFANITIES_LIST if w in comment.lower()]
            if bad_words:
                plural = len(bad_words) > 1
                raise forms.ValidationError(ungettext(
                    "La palabra %s no está permitida.",
                    "Las palabras %s no están permitidas.", plural) %\
                                            get_text_list(['"%s%s%s"' % (i[0], '-'*(len(i)-2), i[-1]) for i in bad_words], 'and'))
        return comment