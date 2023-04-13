from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.fields import GenericRelation

from tendenci.apps.chapters.models import Chapter
from tendenci.apps.perms.object_perms import ObjectPermission
from tendenci.apps.pages.models import BasePage
from tendenci.apps.user_groups.utils import get_default_group
from tendenci.apps.chapter_pages.managers import ChapterPageManager
from tendenci.apps.chapter_pages.module_meta import ChapterPageMeta
from tendenci.apps.user_groups.models import Group


class ChapterPage(BasePage):
    CONTRIBUTOR_AUTHOR = 1
    CONTRIBUTOR_PUBLISHER = 2
    CONTRIBUTOR_CHOICES = ((CONTRIBUTOR_AUTHOR, _('Author')),
                           (CONTRIBUTOR_PUBLISHER, _('Publisher')))

    group = models.ForeignKey(Group, null=True, default=None, on_delete=models.SET_NULL)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='pages')
    contributor_type = models.IntegerField(choices=CONTRIBUTOR_CHOICES,
                                           default=CONTRIBUTOR_AUTHOR)
    perms = GenericRelation(ObjectPermission,
                                      object_id_field="object_id",
                                      content_type_field="content_type")
    objects = ChapterPageManager()

    class Meta:
        app_label = 'chapter_pages'

    def save(self, *args, **kwargs):
        if not self.group:
            self.group_id = get_default_group()

        super(ChapterPage, self).save(*args, **kwargs)

    def get_meta(self, name):
        """
        This method is standard across all models that are
        related to the Meta model.  Used to generate dynamic
        meta information niche to this model.
        """
        return ChapterPageMeta().get_meta(self, name)

    def get_absolute_url(self):
        return reverse('chapter_page', args=[self.chapter.slug, self.slug])

    def get_version_url(self, hash):
        return reverse('chapter_page.version', args=[self.chapter.slug, hash])

    @property
    def has_google_author(self):
        return self.contributor_type == self.CONTRIBUTOR_AUTHOR

    @property
    def has_google_publisher(self):
        return self.contributor_type == self.CONTRIBUTOR_PUBLISHER
