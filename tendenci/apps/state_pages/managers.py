from tendenci.apps.perms.managers import TendenciBaseManager
from django.db import models


class StatePageManager(TendenciBaseManager):
    """
    Model Manager
    """
    def active(self):
        return self.get_queryset().filter(status=True, status_detail='active')


class StateAdminManager(models.Manager):
    """
    Model Manager
    """
    def active(self):
        return self.get_queryset().filter(status=True)
