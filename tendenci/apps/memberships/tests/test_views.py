from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from tendenci.apps.chapters.models import ChapterMembership
from tendenci.apps.memberships.models import MembershipDefault


class MembershipDefaultAddTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        commands = [
            'initial_migrate',
            'deploy',
            'load_tendenci_defaults',
        ]
        fixtures = [
            'test_chapter_data.json',
            'test_chapterappfields.json',
        ]

        for c in commands:
            call_command(c)

        for f in fixtures:
            call_command('loaddata', f, verbosity=0)

    def setUp(self):
        self.post_values = {
            'first_name': 'TestUser',
            'last_name': '01',
            'email': 'testuser01@fabiuslabs.com',
            'phone': '1234567890',
            'address': '',
            'county': 'county',
            'state': 'CO',
            'zipcode': '123456',
            'ud2': '',
            'membership_type': '1',
            'payment_method': '1',
        }

        self.post_values_with_chapter = {
            'first_name': 'TestUser',
            'last_name': '02',
            'email': 'testuser02@fabiuslabs.com',
            'phone': '1234567890',
            'address': '',
            'county': 'county',
            'state': 'CO',
            'zipcode': '123456',
            'ud2': '',
            'membership_type': '1',
            'payment_method': '1',
            'chapter': '1',
            'chapter-ud1': 'district',
            'chapter-school_name': '',
            'chapter-school_type': '',
            'chapter-ud2': '',
            'chapter-ud3': '',
            'chapter-expertise': '',
            'chapter-occupation': '',
            'chapter-social_media_links': '',
            'chapter-ud5': '',
            'chapter-ud4': 'Yes',
            'chapter-membership_type': '1',
            'chapter-payment_method': '1',
        }

    def test_get_404_if_no_membership_app(self):
        membership_app_slug = 'membership-application-fake'
        response = self.client.get(
            reverse('membership_default.add', kwargs={'slug': membership_app_slug, }),
        )
        self.assertEqual(response.status_code, 404)

    def test_post_404_if_no_membership_app(self):
        membership_app_slug = 'membership-application-fake'
        response = self.client.post(
            reverse('membership_default.add', kwargs={'slug': membership_app_slug, }),
            self.post_values
        )
        self.assertEqual(response.status_code, 404)

    def test_signup_without_chapter_membership_response_redirect(self):
        membership_app_slug = 'membership-application'
        response = self.client.post(
            reverse('membership_default.add', kwargs={'slug': membership_app_slug, }),
            self.post_values
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/memberships/default-confirmation/'))

    def test_signup_without_chapter_membership_user_created(self):
        membership_app_slug = 'membership-application'
        response = self.client.post(
            reverse('membership_default.add', kwargs={'slug': membership_app_slug, }),
            self.post_values
        )
        self.assertEqual(User.objects.filter(email=self.post_values['email']).count(), 1)

    def test_signup_without_chapter_membership_default_membership_created(self):
        membership_app_slug = 'membership-application'
        self.client.post(
            reverse('membership_default.add', kwargs={'slug': membership_app_slug, }),
            self.post_values
        )
        user = User.objects.get(email=self.post_values['email'])
        self.assertEqual(MembershipDefault.objects.filter(user=user).count(), 1)

    def test_signup_with_chapter_membership_response_redirect(self):
        membership_app_slug = 'membership-application'
        response = self.client.post(
            reverse('membership_default.add', kwargs={'slug': membership_app_slug, }),
            self.post_values_with_chapter
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/memberships/default-confirmation/'))

    def test_signup_with_chapter_membership_user_created(self):
        membership_app_slug = 'membership-application'
        self.client.post(
            reverse('membership_default.add', kwargs={'slug': membership_app_slug, }),
            self.post_values_with_chapter
        )
        self.assertEqual(User.objects.filter(email=self.post_values_with_chapter['email']).count(), 1)

    def test_signup_with_chapter_membership_default_membership_created(self):
        membership_app_slug = 'membership-application'
        response = self.client.post(
            reverse('membership_default.add', kwargs={'slug': membership_app_slug, }),
            self.post_values_with_chapter
        )
        user = User.objects.get(email=self.post_values_with_chapter['email'])
        self.assertEqual(MembershipDefault.objects.filter(user=user).count(), 1)

    def test_signup_with_chapter_membership_chapter_membership_created(self):
        membership_app_slug = 'membership-application'
        response = self.client.post(
            reverse('membership_default.add', kwargs={'slug': membership_app_slug, }),
            self.post_values_with_chapter
        )
        user = User.objects.get(email=self.post_values_with_chapter['email'])
        self.assertEqual(
            ChapterMembership.objects.filter(user=user, chapter=self.post_values_with_chapter['chapter']).count(), 1
        )


