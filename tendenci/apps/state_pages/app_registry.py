from django.utils.translation import gettext_lazy as _

from tendenci.apps.registry.sites import site
from tendenci.apps.registry.base import CoreRegistry, lazy_reverse
from tendenci.apps.state_pages.models import StatePage
from tendenci.apps.theme.templatetags.static import static


class StatePageRegistry(CoreRegistry):
    version = '1.0'
    author = _('Fabius Labs - engineering@fabiuslabs.com')
    author_email = 'programmers@tendenci.com'
    description = _('Extended Tendenci Pages App for Chapter Pages')
    icon = static('images/icons/pages-color-64x64.png')

    event_logs = {
        'page':{
            'base':('1310000','009900'),
            'add':('1311000','009933'),
            'edit':('1312000','009966'),
            'delete':('1313000','00CC00'),
            'search':('1314000','00FF00'),
            'view':('1315000','00FF33'),
            'print_view':('1316000','00FF33')
        }
    }
    url = {
        'omit': True,
        'add': lazy_reverse('chapters.add'),
        'search': lazy_reverse('chapters.search'),
    }

site.register(StatePage, StatePageRegistry)
