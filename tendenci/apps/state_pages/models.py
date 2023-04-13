from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.fields import GenericRelation
from localflavor.us.models import USStateField

from tendenci.apps.perms.object_perms import ObjectPermission
from tendenci.apps.pages.models import BasePage
from tendenci.apps.user_groups.utils import get_default_group
from tendenci.apps.state_pages.managers import StatePageManager, StateAdminManager
from tendenci.apps.state_pages.module_meta import StatePageMeta
from tendenci.apps.user_groups.models import Group


class StatePage(BasePage):
    CONTRIBUTOR_AUTHOR = 1
    CONTRIBUTOR_PUBLISHER = 2
    CONTRIBUTOR_CHOICES = ((CONTRIBUTOR_AUTHOR, _('Author')),
                           (CONTRIBUTOR_PUBLISHER, _('Publisher')))

    group = models.ForeignKey(Group, null=True, default=None, on_delete=models.SET_NULL)
    state = USStateField()
    contributor_type = models.IntegerField(choices=CONTRIBUTOR_CHOICES,
                                           default=CONTRIBUTOR_AUTHOR)
    perms = GenericRelation(ObjectPermission,
                                      object_id_field="object_id",
                                      content_type_field="content_type")
    objects = StatePageManager()

    class Meta:
#         permissions = (("view_page", _("Can view page")),)
        app_label = 'state_pages'

    def save(self, *args, **kwargs):
        if not self.group:
            self.group_id = get_default_group()

        super(StatePage, self).save(*args, **kwargs)

    def get_meta(self, name):
        """
        This method is standard across all models that are
        related to the Meta model.  Used to generate dynamic
        meta information niche to this model.
        """
        return StatePageMeta().get_meta(self, name)

    def get_absolute_url(self):
        return reverse('state_page', args=[self.state, self.slug])

    def get_version_url(self, hash):
        return reverse('state_page.version', args=[self.state, hash])

    @property
    def has_google_author(self):
        return self.contributor_type == self.CONTRIBUTOR_AUTHOR

    @property
    def has_google_publisher(self):
        return self.contributor_type == self.CONTRIBUTOR_PUBLISHER


class StateEditor(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    state = USStateField()
    status = models.BooleanField("Active", default=True)

    objects = StateAdminManager()

    class Meta:
        unique_together = (('user', 'state'),)
