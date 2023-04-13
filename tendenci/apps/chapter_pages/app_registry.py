from django.utils.translation import gettext_lazy as _

from tendenci.apps.registry.sites import site
from tendenci.apps.registry.base import CoreRegistry, lazy_reverse
from tendenci.apps.chapter_pages.models import ChapterPage
from tendenci.apps.theme.templatetags.static import static


class ChapterPageRegistry(CoreRegistry):
    version = '1.0'
    author = _('Fabius Labs - engineering@fabiuslabs.com')
    author_email = 'programmers@tendenci.com'
    description = _('Extended Tendenci Pages App for Chapter Pages')
    icon = static('images/icons/pages-color-64x64.png')

    event_logs = {
        'page':{
            'base':('1300000','009900'),
            'add':('1301000','009933'),
            'edit':('1302000','009966'),
            'delete':('1303000','00CC00'),
            'search':('1304000','00FF00'),
            'view':('1305000','00FF33'),
            'print_view':('1306000','00FF33')
        }
    }
    url = {
        'omit': True,
        'add': lazy_reverse('chapters.add'),
        'search': lazy_reverse('chapters.search'),
    }

site.register(ChapterPage, ChapterPageRegistry)
