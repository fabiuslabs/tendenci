from django import forms
from django.conf import settings
# from captcha.fields import CaptchaField
from django.utils.translation import gettext_lazy as _
from tendenci.apps.chapters.models import Chapter

from tendenci.apps.contacts.models import Contact, ContactGroup
from tendenci.apps.base.fields import EmailVerificationField
from tendenci.apps.base.forms import CustomCatpchaField
from tendenci.apps.site_settings.utils import get_setting


class ContactForm(forms.ModelForm):
    contact_group = forms.ModelChoiceField(queryset=ContactGroup.objects.all())
    class Meta:
        model = Contact
        fields = (
            'first_name',
            'last_name',
            'email',
            'contact_group'
        )
    def __init__(self, *args, **kwargs):
        chapter_id = kwargs.pop('chapter_id', None)
        super(ContactForm, self).__init__(*args, **kwargs)
        if chapter_id:
            self.fields['contact_group'].queryset = ContactGroup.objects.filter(chapter=chapter_id)


class SubmitContactForm(forms.Form):

    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100, required=False)
    email = EmailVerificationField(label=_("Email"))
    captcha = CustomCatpchaField(label=_('Type the code below'))



class ContactGroupForm(forms.ModelForm):
    '''
    Contact Group Form
    '''
    
    class Meta:
        model = ContactGroup
        fields = (
            'group_name',
            'chapter',
            'is_newsletter'
        )
    def __init__(self, *args, **kwargs):
        chapter_choices = kwargs.pop('chapter', None)
        super(ContactGroupForm, self).__init__(*args, **kwargs)
        self.fields['chapter'].queryset = Chapter.objects.filter(pk=chapter_choices.id)
        self.fields['is_newsletter'].label = 'Is this group for your newsletter?'
    
    def clean(self):
        cleaned_data = super().clean()
        is_newsletter = cleaned_data.get('is_newsletter')
        chapter = cleaned_data.get('chapter')
        if is_newsletter and ContactGroup.objects.filter(is_newsletter=True, chapter=chapter).exclude(pk=self.instance.pk):
            self.add_error('is_newsletter', 'Only one Contact Group can be the newsletter')
        return cleaned_data