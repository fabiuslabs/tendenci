from tendenci.apps.perms.managers import TendenciBaseManager

class ChapterPageManager(TendenciBaseManager):
    """
    Model Manager
    """
    def active(self):
        return self.get_queryset().filter(status=True, status_detail='active')
