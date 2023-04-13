from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Add any missing permissions
    """
    def handle(self, *args, **options):
        from django.contrib.auth.management import create_permissions
        from django.apps import apps

        verbosity = int(options['verbosity'])

        for app in apps.get_app_configs():
            create_permissions(app, verbosity=verbosity)
