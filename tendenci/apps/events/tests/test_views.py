from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from tendenci.apps.events.models import Volunteer


class VolunteerTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        commands = [
            'initial_migrate',
            'deploy',
            'load_tendenci_defaults',
        ]
        fixtures = [
            'test_events.json',
        ]

        for c in commands:
            call_command(c)

        for f in fixtures:
            call_command('loaddata', f, verbosity=0)

    def setUp(self):
        self.event_id_volunteer_not_enabled = 2
        self.event_id_volunteer_enabled = 3
        self.event_id_not_exist = 4

        User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        self.login_user = User.objects.get(username='testuser1')

        self.post_values = {
            'event': self.event_id_volunteer_enabled,
            'user': self.login_user.id,
            'first_name': 'random',
            'last_name': 'random',
            'email': 'random@domain.com',
            'phone': '',
            'company_name': '',
            'comments': '',
            'commit': '',
            'confirmed': '',
        }

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(
            reverse('event.volunteer', kwargs={'event_id': self.event_id_volunteer_enabled, }),
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_404_if_event_not_exist(self):
        self.client.login(username='testuser1', password='1X<ISRUkw+tuK')

        response = self.client.get(
            reverse('event.volunteer', kwargs={'event_id': self.event_id_not_exist, }),
        )

        self.assertEqual(response.status_code, 404)

    def test_404_if_event_volunteer_not_enabled(self):
        self.client.login(username='testuser1', password='1X<ISRUkw+tuK')

        response = self.client.get(
            reverse('event.volunteer', kwargs={'event_id': self.event_id_volunteer_not_enabled, }),
        )

        self.assertEqual(response.status_code, 404)

    def test_200_if_logged_in(self):
        self.client.login(username='testuser1', password='1X<ISRUkw+tuK')

        response = self.client.get(
            reverse('event.volunteer', kwargs={'event_id': self.event_id_volunteer_enabled, }),
        )

        self.assertEqual(response.status_code, 200)

    def test_render_correct_template(self):
        self.client.login(username='testuser1', password='1X<ISRUkw+tuK')

        response = self.client.get(
            reverse('event.volunteer', kwargs={'event_id': self.event_id_volunteer_enabled, }),
        )

        self.assertTemplateUsed(response, 'events/reg8n/volunteer.html')

    def test_volunteer_created(self):
        self.client.login(username='testuser1', password='1X<ISRUkw+tuK')

        self.client.post(
            reverse('event.volunteer', kwargs={'event_id': self.event_id_volunteer_enabled, }),
            self.post_values
        )

        self.assertEqual(Volunteer.objects.filter(
            event=self.event_id_volunteer_enabled, user__id=self.login_user.id
        ).count(), 1)

    def test_success_redirect(self):
        self.client.login(username='testuser1', password='1X<ISRUkw+tuK')

        response = self.client.post(
            reverse('event.volunteer', kwargs={'event_id': self.event_id_volunteer_enabled, }),
            self.post_values
        )

        self.assertRedirects(response, reverse('event.search'))

    def test_volunteer_not_created_if_already_volunteered(self):
        self.client.login(username='testuser1', password='1X<ISRUkw+tuK')

        self.client.post(
            reverse('event.volunteer', kwargs={'event_id': self.event_id_volunteer_enabled, }),
            self.post_values
        )
        self.client.post(
            reverse('event.volunteer', kwargs={'event_id': self.event_id_volunteer_enabled, }),
            self.post_values
        )

        self.assertEqual(Volunteer.objects.filter(
            event=self.event_id_volunteer_enabled, user__id=self.login_user.id
        ).count(), 1)
