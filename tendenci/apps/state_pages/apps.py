from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.utils.translation import gettext_noop as _


def create_notice_types(sender, **kwargs):
    from tendenci.apps.notifications import models as notification
    verbosity = kwargs.get('verbosity', 2)

    notification.create_notice_type("page_added",
                                    _("State Page Added"),
                                    _("A page has been added."),
                                    verbosity=verbosity)
    notification.create_notice_type("page_edited",
                                    _("State Page Edited"),
                                    _("A page has been edited."),
                                    verbosity=verbosity)
    notification.create_notice_type("page_deleted",
                                    _("State Page Deleted"),
                                    _("A page has been deleted"),
                                    verbosity=verbosity)



class StatePagesConfig(AppConfig):
    name = 'tendenci.apps.state_pages'
    verbose_name = 'State Pages'

    def ready(self):
        super(StatePagesConfig, self).ready()
        post_migrate.connect(create_notice_types, sender=self)
