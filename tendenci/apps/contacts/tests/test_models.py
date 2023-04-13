from django.test import TestCase
from ..models import Contact, ContactGroup, ContactGroupMembership

class ContactsTests(TestCase):
    def setUp(self) -> None:
        self.contact = Contact.objects.create(email="test@gmail.com", first_name="Test", last_name="Test")
        self.contact_group = ContactGroup.create(group_name="Test Group")
    def test_contact_email(self):
        self.assertEqual(self.contact.email, 'test@gmail.com')
    
    def test_contact_first_name(self):
        self.assertEqual(self.contact.first_name, 'Test')
    
    def test_contact_last_name(self):
        self.assertEqual(self.contact.last_name, 'Test')
    
    def test_contact_group_add_contact(self):
        self.membership = ContactGroupMembership.add_to_group(self.contact, self.contact_group)
        self.assertTrue(self.contact_group.is_member(self.contact))
        
        
    