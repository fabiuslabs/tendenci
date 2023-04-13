
from builtins import str

from django.contrib.auth.decorators import login_required
from django.forms import HiddenInput
from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.models import User
from tendenci.apps.chapters.models import Chapter

from tendenci.apps.theme.shortcuts import themed_response as render_to_resp
from tendenci.apps.base.http import Http403
from tendenci.apps.base.utils import create_salesforce_contact
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.contacts.models import Contact, ContactGroup, ContactGroupMembership
from tendenci.apps.contacts.forms import ContactForm, ContactGroupForm, SubmitContactForm
from tendenci.apps.contacts.utils import listed_in_email_block
from tendenci.apps.perms.object_perms import ObjectPermission
from tendenci.apps.perms.utils import has_perm, has_view_perm, get_query_filters, get_notice_recipients
from tendenci.apps.event_logs.models import EventLog

try: from tendenci.apps.notifications import models as notification
except: notification = None


@login_required
def details(request, id=None, template_name="contacts/view.html"):
    if not id: return HttpResponseRedirect(reverse('contacts'))
    contact = get_object_or_404(Contact, pk=id)

    if has_view_perm(request.user,'contacts.view_contact',contact):
        return render_to_resp(request=request, template_name=template_name,
            context={'contact': contact})
    else:
        raise Http403

def search(request, template_name="contacts/search.html"):
    if request.user.is_anonymous:
        raise Http403
    if not has_perm(request.user,'contacts.view_contact'):
        raise Http403

    query = request.GET.get('q', None)
    if get_setting('site', 'global', 'searchindex') and query:
        contacts = Contact.objects.search(query, user=request.user)
    else:
        filters = get_query_filters(request.user, 'contacts.view_contact')
        contacts = Contact.objects.filter().distinct()
        if not request.user.is_anonymous:
            contacts = contacts.select_related()

    contacts = contacts.order_by('-create_dt')

    return render_to_resp(request=request, template_name=template_name,
        context={'contacts':contacts})

def search_redirect(request):
    return HttpResponseRedirect(reverse('contacts'))

@login_required
def print_view(request, id, template_name="contacts/print-view.html"):
    contact = get_object_or_404(Contact, pk=id)

    if has_view_perm(request.user,'contacts.view_contact',contact):
        return render_to_resp(request=request, template_name=template_name,
            context={'contact': contact})
    else:
        raise Http403

@login_required
def add_contact(request, slug=None, form_class=ContactForm, template_name="contacts/add.html"):
    current_user = request.user
    if slug:
        chapter = get_object_or_404(Chapter, slug=slug)
        contact_groups = ContactGroup.objects.filter(chapter=chapter.pk)
        print(contact_groups)
        if not (current_user.profile.is_superuser or (current_user.profile.is_chapter_coordinator and current_user.profile.is_chapter_member(chapter.id))):
            return HttpResponseForbidden()
        if request.method == "POST":
            form = form_class(request.POST)
            if form.is_valid():
                contact = form.save()
                contact_group_member = ContactGroupMembership.add_to_group(
                    contact = contact,
                    contact_group = form.cleaned_data.get('contact_group')
                )
                contact_group_member.save()
                return HttpResponseRedirect(reverse('contact.chapter.add_contact', args=[contact.pk]))
        else:
            form = form_class(chapter_id=chapter.pk)
        
        return render_to_resp(request=request, template_name=template_name,
            context={'form':form})
    else:
        if not current_user.profile.is_superuser:
            return HttpResponseForbidden()
        if request.method == "POST":
            form = form_class(request.POST)
            if form.is_valid():
                contact = form.save()
                contact_group_member = ContactGroupMembership.add_to_group(
                    contact = contact,
                    contact_group = form.cleaned_data.get('contact_group')
                )
                contact_group_member.save()
                return HttpResponseRedirect(reverse('contact', args=[contact.pk]))
        else:
            form = form_class()

        return render_to_resp(request=request, template_name=template_name,
            context={'form':form})

@login_required
def add_contact_group(request, slug, form_class=ContactGroupForm, template_name="contacts/add-group.html"):
    chapter = get_object_or_404(Chapter, slug=slug)
    current_user = request.user
    if current_user.profile.is_superuser or (current_user.profile.is_chapter_coordinator and current_user.profile.is_chapter_member(chapter.id)):
        if request.method == "POST":
            form = form_class(request.POST, chapter=chapter)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(reverse('contact.chapter.groups', args=[chapter.slug]))
        else:
            form = form_class(chapter=chapter)
    else:
        return HttpResponseRedirect(reverse('profile.index'))
        
    
    return render_to_resp(request=request, template_name=template_name,
        context={'form':form, 'slug': slug})

@login_required
def chapter_groups(request, slug, template_name="contacts/chapter-groups.html"):
    current_user = request.user
    chapter = get_object_or_404(Chapter, slug=slug)
    
    contact_groups = ContactGroup.objects.filter(chapter=chapter.pk) 
    if current_user.profile.is_superuser or (current_user.profile.is_chapter_coordinator and current_user.profile.is_chapter_member(chapter.id)):
        return render_to_resp(request=request, template_name=template_name, context={'chapter': chapter, 'contact_groups': contact_groups})
    else:
        return HttpResponseRedirect(reverse('profile.index'))

@login_required
def group_contacts(request, slug, id, template_name="contacts/search.html"):
    current_user = request.user
    contact_group = get_object_or_404(ContactGroup, pk=id)
    chapter = Chapter.objects.get(slug=slug)
    contacts = ContactGroupMembership.objects.filter(contact_group=contact_group.pk)
    if current_user.profile.is_superuser or (current_user.profile.is_chapter_coordinator and current_user.profile.is_chapter_member(chapter.id)):
        return render_to_resp(request=request, template_name=template_name, context={'chapter': chapter, 'contacts': contacts, 'contact_group': contact_group})
    else:
        return HttpResponseRedirect(reverse('profile.index'))
    

@login_required
def delete(request, id, template_name="contacts/delete.html"):
    contact = get_object_or_404(Contact, pk=id)

    if has_perm(request.user,'contacts.delete_contact'):
        if request.method == "POST":
            contact.delete()
            return HttpResponseRedirect(reverse('contact.search'))

        return render_to_resp(request=request, template_name=template_name,
            context={'contact': contact})
    else:
        raise Http403


def index(request, form_class=SubmitContactForm, template_name="form.html"):

    if request.method == "GET":
        # event-log view
        EventLog.objects.log(instance=Contact(), action='viewed')

    if request.method == "POST":
        event_log_dict = {}
        form = form_class(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')

            if listed_in_email_block(email):
                # listed in the email blocks - it's a spam email we want to block
                # log the spam
                EventLog.objects.log()

                # redirect normally so they don't suspect
                return HttpResponseRedirect(reverse('form.confirmation'))

            # exists_user = User.objects.filter(
            #     first_name__iexact=first_name,
            #     last_name__iexact=last_name,
            #     email__iexact=email,
            # ).exists()

            # if request.user.is_anonymous:
            #     # create_salesforce_contact(profile)  # Returns sf_id #Tony Comment Could possibly use this to create HubSpot Contact
            #     event_log_dict['description'] = 'logged-out submission as anonymous'
            # else:  # logged in user
            #     self_submit = all([
            #         request.user.first_name.lower().strip() == first_name.lower().strip(),
            #         request.user.last_name.lower().strip() == last_name.lower().strip(),
            #         request.user.email.lower().strip() == email.lower().strip(),
            #     ])

            #     if exists_user:
            #         if self_submit:
            #             event_log_dict['description'] = 'logged-in submission as self'
            #         else:
            #             event_log_dict['description'] = 'logged-in submission as existing user'
            #     else:
            #         event_log_dict['description'] = 'logged-in submission as non-existing user'

            contact_kwargs = {
                'first_name': first_name,
                'last_name': last_name,
                'email': email
            }

            contact = Contact(**contact_kwargs)
            contact.allow_anonymous_view = False
            contact.save()


            site_name = get_setting('site', 'global', 'sitedisplayname')
            message_link = get_setting('site', 'global', 'siteurl')

            # send notification to administrators
            # get admin notice recipients
            recipients = get_notice_recipients('module', 'contacts', 'contactrecipients')
            if recipients:
                if notification:
                    extra_context = {
                    'reply_to': email,
                    'contact': contact,
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'message_link': message_link,
                    'site_name': site_name,
                    }
                    notification.send_emails(recipients, 'contact_submitted', extra_context)

            # event-log (logged in)
            event_log = EventLog.objects.log(
                instance=contact,
                user=request.user,
                action='submitted',
                **event_log_dict
            )

            event_log.url = contact.get_absolute_url()
            event_log.save()

            return HttpResponseRedirect(reverse('form.confirmation'))
        else:
            return render_to_resp(request=request, template_name=template_name,
                context={'form': form})

    form = form_class()
    return render_to_resp(request=request, template_name=template_name,
        context={'form': form})


def confirmation(request, form_class=SubmitContactForm, template_name="form-confirmation.html"):
    return render_to_resp(request=request, template_name=template_name)
