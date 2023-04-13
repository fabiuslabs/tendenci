import imghdr
from os.path import splitext, basename

from django.contrib.auth.models import User
from localflavor.us.forms import USStateSelect

from tendenci.apps.base.forms import FormControlWidgetMixin
from tendenci.apps.profiles.models import UserChoiceField
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.state_pages.models import StatePage, StateEditor
from tendenci.apps.perms.forms import TendenciBaseForm

from django.utils.safestring import mark_safe
from django import forms
from django.utils.translation import gettext_lazy as _
from django.template.defaultfilters import filesizeformat

from tendenci.apps.user_groups.models import Group
from tendenci.libs.form_utils.forms import BetterModelForm
from tendenci.libs.tinymce.widgets import TinyMCE
from tendenci.apps.base.utils import get_template_list
from tendenci.apps.files.utils import get_max_file_upload_size

ALLOWED_IMG_EXT = (
    '.jpg',
    '.jpeg',
    '.gif',
    '.png'
)
CONTRIBUTOR_CHOICES = (
    (StatePage.CONTRIBUTOR_AUTHOR, mark_safe('Author <i class="gauthor-info fa fa-lg fa-question-circle"></i>')),
    (StatePage.CONTRIBUTOR_PUBLISHER, mark_safe('Publisher <i class="gpub-info fa fa-lg fa-question-circle"></i>'))
)
GOOGLE_PLUS_HELP_TEXT = 'Additional Options for Authorship <i class="gauthor-help fa fa-lg fa-question-circle"></i><br>Additional Options for Publisher <i class="gpub-help fa fa-lg fa-question-circle"></i>'

class StatePageAdminForm(TendenciBaseForm):
    content = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style':'width:100%'},
        mce_attrs={'storme_app_label':StatePage._meta.app_label,
        'storme_model':StatePage._meta.model_name.lower()}))

    syndicate = forms.BooleanField(label=_('Include in RSS Feed'), required=False, initial=True)

    status_detail = forms.ChoiceField(
        choices=(('active',_('Active')),('inactive',_('Inactive')), ('pending',_('Pending')),))

    template_choices = [('default.html',_('Default'))]
    template_choices += get_template_list()
    template = forms.ChoiceField(choices=template_choices)

    meta_title = forms.CharField(required=False)
    meta_description = forms.CharField(required=False,
        widget=forms.widgets.Textarea(attrs={'style':'width:100%'}))
    meta_keywords = forms.CharField(required=False,
        widget=forms.widgets.Textarea(attrs={'style':'width:100%'}))
    meta_canonical_url = forms.CharField(required=False)

    class Meta:
        model = StatePage
        fields = (
        'title',
        'slug',
        'content',
        'group',
        'tags',
        'template',
        'meta_title',
        'meta_description',
        'meta_keywords',
        'meta_canonical_url',
        'allow_anonymous_view',
        'user_perms',
        'group_perms',
        'member_perms',
        'syndicate',
        'status_detail',
        )

    def __init__(self, *args, **kwargs):
        super(StatePageAdminForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['content'].widget.mce_attrs['app_instance_id'] = self.instance.pk
            if self.instance.meta:
                self.fields['meta_title'].initial = self.instance.meta.title
                self.fields['meta_description'].initial = self.instance.meta.description
                self.fields['meta_keywords'].initial = self.instance.meta.keywords
                self.fields['meta_canonical_url'].initial = self.instance.meta.canonical_url
        else:
            self.fields['content'].widget.mce_attrs['app_instance_id'] = 0

    def clean_syndicate(self):
        """
        clean method for syndicate added due to the update
        done on the field BooleanField -> NullBooleanField
        NOTE: BooleanField is converted to NullBooleanField because
        some Boolean data has value of None than False. This was updated
        on Django 1.6. BooleanField cannot have a value of None.
        """
        data = self.cleaned_data.get('syndicate', False)
        if data:
            return True
        else:
            return False

    def clean(self):
        cleaned_data = super(StatePageAdminForm, self).clean()
        slug = cleaned_data.get('slug')

        # Check if duplicate slug from different page (i.e. different guids)
        # Case 1: Page is edited
        if self.instance:
            guid = self.instance.guid
            if StatePage.objects.filter(slug=slug).exclude(guid=guid).exists():
                self._errors['slug'] = self.error_class([_('Duplicate value for slug.')])
                del cleaned_data['slug']
        # Case 2: Add new Page
        else:
            if StatePage.objects.filter(slug=slug).exists():
                self._errors['slug'] = self.error_class([_('Duplicate value for slug.')])
                del cleaned_data['slug']

        return cleaned_data


class StatePageForm(TendenciBaseForm):
    header_image = forms.ImageField(required=False)
    remove_photo = forms.BooleanField(label=_('Remove the current header image'), required=False)

    content = forms.CharField(required=False,
        widget=TinyMCE(attrs={'style':'width:100%'},
        mce_attrs={'storme_app_label':StatePage._meta.app_label,
        'storme_model':StatePage._meta.model_name.lower()}))

    contributor_type = forms.ChoiceField(choices=CONTRIBUTOR_CHOICES,
                                         initial=StatePage.CONTRIBUTOR_AUTHOR,
                                         widget=forms.RadioSelect())

    syndicate = forms.BooleanField(label=_('Include in RSS Feed'), required=False, initial=True)

    status_detail = forms.ChoiceField(
        choices=(('active', _('Active')), ('inactive', _('Inactive')), ('pending', _('Pending'))))

    tags = forms.CharField(required=False, help_text=mark_safe('<a href="/tags/" target="_blank">%s</a>' % _('Open All Tags list in a new window')))

    template = forms.ChoiceField(choices=[])

    state = USStateSelect()


    class Meta:
        model = StatePage
        fields = (
        'title',
        'slug',
        'content',
        'tags',
        'template',
        'group',
        'state',
        'contributor_type',
        'allow_anonymous_view',
        'syndicate',
        'user_perms',
        'group_perms',
        'member_perms',
        'status_detail',
        )

        fieldsets = [(_('Page Information'), {
                      'fields': ['title',
                                 'slug',
                                 'content',
                                 'tags',
                                 'header_image',
                                 'template',
                                 'group',
                                 'state',
                                 ],
                      'legend': ''
                      }),
                      (_('Contributor'), {
                       'fields': ['contributor_type',],
                       'classes': ['boxy-grey'],
                      }),
                      (_('Permissions'), {
                      'fields': ['allow_anonymous_view',
                                 'user_perms',
                                 'member_perms',
                                 'group_perms',
                                 ],
                      'classes': ['permissions'],
                      }),
                     (_('Administrator Only'), {
                      'fields': ['syndicate',
                                 'status_detail'],
                      'classes': ['admin-only'],
                    })]

    def __init__(self, *args, **kwargs):
        super(StatePageForm, self).__init__(*args, **kwargs)
        if self.instance.header_image:
            self.fields['header_image'].help_text = '<input name="remove_photo" id="id_remove_photo" type="checkbox"/> %s: <a target="_blank" href="/files/%s/">%s</a>' % (_('Remove current image'), self.instance.header_image.pk, basename(self.instance.header_image.file.name))
        else:
            self.fields.pop('remove_photo')

        if self.instance.pk:
            self.fields['content'].widget.mce_attrs['app_instance_id'] = self.instance.pk
        else:
            self.fields['content'].widget.mce_attrs['app_instance_id'] = 0

        if not self.user.profile.is_superuser:
            if 'syndicate' in self.fields: self.fields.pop('syndicate')
            if 'status_detail' in self.fields: self.fields.pop('status_detail')

        self.fields['template'].choices = [('default.html', _('Default'))] + get_template_list()
        self.fields['state'].widget = self.fields['state'].hidden_widget()

    def clean_syndicate(self):
        """
        clean method for syndicate added due to the update
        done on the field BooleanField -> NullBooleanField
        NOTE: BooleanField is converted to NullBooleanField because
        some Boolean data has value of None than False. This was updated
        on Django 1.6. BooleanField cannot have a value of None.
        """
        data = self.cleaned_data.get('syndicate', False)
        if data:
            return True
        else:
            return False

    def clean(self):
        cleaned_data = super(StatePageForm, self).clean()
        slug = cleaned_data.get('slug')

        # Check if duplicate slug from different page (i.e. different guids)
        # Case 1: Page is edited
        if self.instance:
            guid = self.instance.guid
            if StatePage.objects.filter(slug=slug).exclude(guid=guid).exists():
                self._errors['slug'] = self.error_class([_('Duplicate value for slug.')])
                del cleaned_data['slug']
        # Case 2: Add new Page
        else:
            if StatePage.objects.filter(slug=slug).exists():
                self._errors['slug'] = self.error_class([_('Duplicate value for slug.')])
                del cleaned_data['slug']

        return cleaned_data

    def clean_header_image(self):
        header_image = self.cleaned_data['header_image']
        if header_image:
            extension = splitext(header_image.name)[1]

            # check the extension
            if extension.lower() not in ALLOWED_IMG_EXT:
                raise forms.ValidationError(_('The header image must be of jpg, gif, or png image type.'))

            # check the image header_image
            image_type = '.%s' % imghdr.what('', header_image.read())
            if image_type not in ALLOWED_IMG_EXT:
                raise forms.ValidationError(_('The header image is an invalid image. Try uploading another image.'))

            max_upload_size = get_max_file_upload_size()
            if header_image.size > max_upload_size:
                raise forms.ValidationError(_('Please keep filesize under %(max_upload_size)s. Current filesize %(header_image)s') % {
                                            'max_upload_size': filesizeformat(max_upload_size),
                                            'header_image': filesizeformat(header_image.size)})

        return header_image

    def save(self, *args, **kwargs):
        page = super(StatePageForm, self).save(*args, **kwargs)
        if self.cleaned_data.get('remove_photo'):
            page.header_image = None
        return page


class StateEditorForm(FormControlWidgetMixin, BetterModelForm):
    state = USStateSelect()
    user = UserChoiceField(queryset=User.objects.filter(is_active=True), blank=True)

    class Meta:
        model = StateEditor
        fields = (
            'user',
            'state',
            'status',
        )

    def __init__(self, *args, **kwargs):
        super(StateEditorForm, self).__init__(*args, **kwargs)


def get_state_coordinators():
    sort = ('last_name', 'first_name', 'email')
    try:
        group_slug = get_setting('module', 'chapters', 'statecoordinatorgroup')
        group = Group.objects.get(slug=group_slug)
        members = group.active_members
        member_ids = User.objects.filter(pk__in=members.values_list('member_id'))
        return member_ids
    except Group.DoesNotExist:
        return User.objects.filter(is_active=False).order_by(*sort)
    except Exception as e:
        raise e


class UserChoiceForm(BetterModelForm):
    user = UserChoiceField(
        queryset=get_state_coordinators(),
        blank=True
    )

    class Meta:
        model = User
        fields = ('user',)

    def __init__(self, *args, **kwargs):
        super(UserChoiceForm, self).__init__(*args, **kwargs)
