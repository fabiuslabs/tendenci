from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.utils.translation import gettext_noop as _


def create_notice_types(sender, **kwargs):
    from tendenci.apps.notifications import models as notification
    verbosity = kwargs.get('verbosity', 2)

    notification.create_notice_type("page_added",
                                    _("Chapter Page Added"),
                                    _("A page has been added."),
                                    verbosity=verbosity)
    notification.create_notice_type("page_edited",
                                    _("Chapter Page Edited"),
                                    _("A page has been edited."),
                                    verbosity=verbosity)
    notification.create_notice_type("page_deleted",
                                    _("Chapter Page Deleted"),
                                    _("A page has been deleted"),
                                    verbosity=verbosity)



class ChapterPagesConfig(AppConfig):
    name = 'tendenci.apps.chapter_pages'
    verbose_name = 'Chapter Pages'

    def ready(self):
        super(ChapterPagesConfig, self).ready()
        post_migrate.connect(create_notice_types, sender=self)
