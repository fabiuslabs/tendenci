import uuid
from django.db import models
from django.urls import reverse
from django.contrib.contenttypes.fields import GenericRelation
from django.utils.translation import gettext_lazy as _

from timezone_field import TimeZoneField

from tendenci.apps.base.utils import get_timezone_choices
from tendenci.apps.perms.object_perms import ObjectPermission
from tendenci.apps.perms.models import TendenciBaseModel
from tendenci.apps.contacts.managers import ContactManager
from tendenci.apps.chapters.models import Chapter
from tendenci.apps.site_settings.utils import get_setting
from django.core.exceptions import ValidationError



class Contact(models.Model):
    """
    Contact records are created when someone fills out a form.
    The form creates the contact with a message.
    Later the contact can be updated to include comments for
    further communication.
    """
    STATUS_ACTIVE = 'active'
    STATUS_INACTIVE = 'inactive'
    STATUS_CHOICES = (
        (STATUS_ACTIVE,  'Active'),       
        (STATUS_INACTIVE, 'Inactive'),
    )

    sort_order =  models.IntegerField(_('Sort Order'), default=0, blank=True)

    status = models.BooleanField(default=True)
    status_detail = models.CharField(max_length=50,
                                     choices=STATUS_CHOICES,
                                     default=STATUS_ACTIVE)

    create_dt = models.DateTimeField(auto_now_add=True, editable=False)
    update_dt = models.DateTimeField(auto_now=True)
    first_name = models.CharField(max_length=100, blank=True)
    middle_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)

    email = models.EmailField(max_length=254, default='')

    perms = GenericRelation(ObjectPermission,
        object_id_field="object_id", content_type_field="content_type")
    
    objects = ContactManager()

    class Meta:
        app_label = 'contacts'

    def get_absolute_url(self):
        return reverse('contact', args=[self.pk])

    def save(self, *args, **kwargs):
        if not self.id:
            self.guid = str(uuid.uuid4())

        super(Contact, self).save(*args, **kwargs)

    def __str__(self):
            return self.email


class ContactGroup(models.Model):
    """
    Contact records can be associated with Contact Groups. 
    This should happen whenever a new Chapter is created.
    
    """
    
    STATUS_ACTIVE = 'active'
    STATUS_INACTIVE = 'inactive'
    STATUS_CHOICES = (
        (STATUS_ACTIVE,  'Active'),       
        (STATUS_INACTIVE, 'Inactive'),
    )

    sort_order =  models.IntegerField(_('Sort Order'), default=0, blank=True)

    status = models.BooleanField(default=True)
    status_detail = models.CharField(max_length=50,
                                     choices=STATUS_CHOICES,
                                     default=STATUS_ACTIVE)

    create_dt = models.DateTimeField(auto_now_add=True, editable=False)
    update_dt = models.DateTimeField(auto_now=True)
    guid = models.CharField(max_length=40)
    group_name = models.CharField(max_length=254)
    chapter = models.ForeignKey(Chapter,on_delete=models.CASCADE, blank=True)
    contacts = models.ManyToManyField(Contact, through='ContactGroupMembership', related_name='contact_groups')
    is_newsletter = models.BooleanField(default=False)
    
    class Meta:
        app_label = 'contacts'

    def clean(self):
        if self.is_newsletter and  ContactGroup.objects.filter(is_newsletter=True).filter(chapter=self.chapter).exclude(pk=self.pk).exists():
            return ValidationError("Only one Contact Group can be the newsletter group")
    
    def save(self, *args, **kwargs):
        if not self.id:
            self.guid = str(uuid.uuid4())
        self.full_clean()
        super(ContactGroup, self).save(*args, **kwargs)

    def __str__(self):
            return self.group_name
    
    def is_member(self, contact):
        if isinstance(contact, Contact):
            return self.contacts.filter(id=contact.id).exists()

        return False
        


class ContactGroupMembership(models.Model):

    STATUS_ACTIVE = 'active'
    STATUS_INACTIVE = 'inactive'
    STATUS_CHOICES = (
        (STATUS_ACTIVE,  'Active'),       
        (STATUS_INACTIVE, 'Inactive'),
    )

    sort_order =  models.IntegerField(_('Sort Order'), default=0, blank=True)

    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    contact_group = models.ForeignKey(ContactGroup, related_name="contact_group_member", on_delete=models.CASCADE)
    
    
    status = models.BooleanField(default=True)
    status_detail = models.CharField(max_length=50,
                                     choices=STATUS_CHOICES,
                                     default=STATUS_ACTIVE)

    create_dt = models.DateTimeField(auto_now_add=True, editable=False)
    update_dt = models.DateTimeField(auto_now=True)

    # The following fields are for Newletter Subscribe and Unsubscribe
    is_newsletter_subscribed = models.BooleanField(default=True)
    newsletter_key = models.CharField(max_length=50, null=True, blank=True) # will be the secret key for unsubscribe

    def __str__(self):
        return self.group.name

    class Meta:
        unique_together = ('contact', 'contact_group',)
        verbose_name = _("Contact Group Membership")
        verbose_name_plural = _(" Contact Group Memberships")
        app_label = 'contacts'

    @classmethod
    def add_to_group(cls, **kwargs):
        """
        Easily add someone to a group, we're setting basic defaults
        e.g. GroupMembership.add_to_group(member=member, group=group)
        """
        contact = kwargs['contact']
        contact_group = kwargs['contact_group']
        status = kwargs.get('status', True)
        status_detail = kwargs.get('status_detail', 'active')

        return cls.objects.create(
            contact=contact,
            contact_group=contact_group,
            status=status,
            status_detail=status_detail
        )

    def subscribe_to_newsletter(self):
        if not self.is_newsletter_subscribed:
            self.is_newsletter_subscribed = True
            # change newsletter_key when subscribing
            self.newsletter_key = uuid.uuid4()
            self.save()
            return True
        elif self.newsletter_key is None:
            self.newsletter_key = uuid.uuid4()
            self.save()
            return True
        return False

    def unsubscribe_to_newsletter(self):
        if self.is_newsletter_subscribed:
            self.is_newsletter_subscribed = False
            # change newsletter_key when unsubscribing
            self.newsletter_key = uuid.uuid4()
            self.save()
            return True

        return False

        

    # TODO Implement this for Contact Groups
    # @property
    # def noninteractive_unsubscribe_url(self):
    #     site_url = get_setting('site', 'global', 'siteurl')
    #     if not self.newsletter_key:
    #         self.newsletter_key = uuid.uuid4()
    #         self.save()
    #     unsubscribe_path = reverse('group.newsletter_unsubscribe_noninteractive', kwargs={
    #         'contact_group_slug': self.group.slug,
    #         'newsletter_key': self.newsletter_key
    #         })

    #     return site_url + unsubscribe_path
