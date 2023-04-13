from datetime import datetime, time, timedelta, date
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

from tendenci.apps.theme.shortcuts import themed_response as render_to_resp
from tendenci.apps.donations.forms import DonationForm, DonationSearchForm
from tendenci.apps.donations.utils import donation_inv_add, donation_email_user
from tendenci.apps.donations.models import Donation, Transaction
from tendenci.apps.site_settings.utils import get_setting
from tendenci.apps.base.forms import CaptchaForm
from tendenci.apps.base.http import Http403
from tendenci.apps.base.utils import tcurrency, is_chapter_chair
from tendenci.apps.event_logs.models import EventLog
from tendenci.apps.perms.utils import get_notice_recipients
from tendenci.apps.perms.utils import has_perm
from tendenci.apps.base.utils import get_unique_username
from tendenci.apps.profiles.models import Profile

try:
    from tendenci.apps.notifications import models as notification
except:
    notification = None


def add(request, form_class=DonationForm, template_name="donations/add.html"):
    use_captcha = get_setting('site', 'global', 'captcha')

    if request.method == "POST":
        form = form_class(request.POST, user=request.user)
        captcha_form = CaptchaForm(request.POST)
        if not use_captcha:
            del captcha_form.fields['captcha']

        if form.is_valid() and captcha_form.is_valid():
            donation = form.save(commit=False)
            donation.payment_method = donation.payment_method.lower()
            # we might need to create a user record if not exist
            if request.user.is_authenticated:
                user = request.user
            else:
                try:
                    user = User.objects.get(email=donation.email)
                except:
                    user = request.user

            if not user.is_anonymous:
                donation.user = user
                donation.creator = user
                donation.creator_username = user.username
            else:
                # this is anonymous user donating and we didn't find their user record in the system,
                # so add a new user
                user = User()
                user.first_name = donation.first_name
                user.last_name = donation.last_name
                user.email = donation.email
                user.username = get_unique_username(user)
                user.set_password(User.objects.make_random_password(length=8))
                user.is_active = 0
                user.save()

                profile_kwarg = {'user':user,
                                 'company':donation.company or '',
                                 'address':donation.address or '',
                                 'address2':donation.address2 or '',
                                 'city':donation.city or '',
                                 'state':donation.state or '',
                                 'zipcode':donation.zip_code or '',
                                 'country':donation.country or '',
                                 'phone':donation.phone or ''}
                if request.user.is_anonymous:
                    profile_kwarg['creator'] = user
                    profile_kwarg['creator_username'] = user.username
                    profile_kwarg['owner'] = user
                    profile_kwarg['owner_username'] = user.username
                else:
                    profile_kwarg['creator'] = request.user
                    profile_kwarg['creator_username'] = request.user.username
                    profile_kwarg['owner'] = request.user
                    profile_kwarg['owner_username'] = request.user.username

                profile = Profile.objects.create(**profile_kwarg)
                profile.save()

            donation.save(user)

            # create invoice
            invoice = donation_inv_add(user, donation)
            # updated the invoice_id for mp, so save again
            donation.save(user)

            if request.user.profile.is_superuser:
                if donation.payment_method in ['paid - check', 'paid - cc']:
                    # the admin accepted payment - mark the invoice paid
                    invoice.tender(request.user)
                    invoice.make_payment(request.user, donation.donation_amount)

            # send notification to administrators
            # get admin notice recipients
            if not donation.payment_method.lower() in ['cc', 'credit card', 'paypal']:
                # email to admin (if payment type is credit card email is not sent until payment confirmed)
                recipients = get_notice_recipients('module', 'donations', 'donationsrecipients')
                if recipients:
                    if notification:
                        extra_context = {
                            'donation': donation,
                            'invoice': invoice,
                            'request': request,
                        }
                        notification.send_emails(recipients,'donation_added', extra_context)

            # email to user
            email_receipt = form.cleaned_data['email_receipt']
            if email_receipt:
                donation_email_user(request, donation, invoice)

            EventLog.objects.log(instance=donation)

            # redirect to online payment or confirmation page
            if donation.payment_method.lower() in ['cc', 'credit card', 'paypal']:
                return HttpResponseRedirect(reverse('payment.pay_online', args=[invoice.id, invoice.guid]))
            else:
                return HttpResponseRedirect(reverse('donation.add_confirm', args=[donation.id]))
    else:
        form = form_class(user=request.user)
        captcha_form = CaptchaForm()

    currency_symbol = get_setting("site", "global", "currencysymbol")
    if not currency_symbol: currency_symbol = "$"

    return render_to_resp(request=request, template_name=template_name,
        context={
        'form':form,
        'captcha_form' : captcha_form,
        'use_captcha' : use_captcha,
        'currency_symbol': currency_symbol})


def add_confirm(request, id, template_name="donations/add_confirm.html"):
    donation = get_object_or_404(Donation, pk=id)
    EventLog.objects.log(instance=donation)
    return render_to_resp(request=request, template_name=template_name)


@login_required
def detail(request, id=None, template_name="donations/view.html"):
    donation = get_object_or_404(Donation, pk=id)
    if not has_perm(request.user,'donations.view_donation'): raise Http403

    EventLog.objects.log(instance=donation)

    donation.donation_amount = tcurrency(donation.donation_amount)
    return render_to_resp(request=request, template_name=template_name,
        context={'donation':donation})


def receipt(request, id, guid, template_name="donations/receipt.html"):
    donation = get_object_or_404(Donation, pk=id, guid=guid)

    donation.donation_amount = tcurrency(donation.donation_amount)

    EventLog.objects.log(instance=donation)

    if (not donation.invoice) or donation.invoice.balance > 0 or (not donation.invoice.is_tendered):
        template_name="donations/view.html"
    return render_to_resp(request=request, template_name=template_name,
        context={'donation':donation})


@login_required
def search(request, template_name="donations/search.html"):
    form = DonationSearchForm(request.GET)
    if form.is_valid():
        start_dt = form.cleaned_data.get('start_dt')
        end_dt = form.cleaned_data.get('end_dt')
        entity = form.cleaned_data.get('entity')
        default_membership = form.cleaned_data.get('default_membership')
        chapter_membership = form.cleaned_data.get('chapter_membership')
        start_amount = form.cleaned_data.get('start_amount')
        end_amount = form.cleaned_data.get('end_amount')
        search_criteria = form.cleaned_data.get('search_criteria')
        search_text = form.cleaned_data.get('search_text')
        search_method = form.cleaned_data.get('search_method')

    donations = Transaction.objects.all()

    if start_dt:
        donations = donations.filter(donation_dt__gte=datetime.combine(start_dt, time.min))
    if end_dt:
        donations = donations.filter(donation_dt__lte=datetime.combine(end_dt, time.max))

    if entity:
        donations = donations.filter(donate_to_entity=entity)

    if default_membership:
        donations = donations.filter(user__membershipdefault__membership_type=default_membership)

    if chapter_membership:
        donations = donations.filter(user__chaptermembership__chapter=chapter_membership)

    if start_amount:
        donations = donations.filter(donation_amount__gte=start_amount)
    if end_amount:
        donations = donations.filter(donation_amount__lte=end_amount)

    if search_criteria and search_text:
        if search_method == 'starts_with':
            if isinstance(search_text, str):
                search_type = '__istartswith'
            else:
                search_type = '__startswith'
        elif search_method == 'contains':
            if isinstance(search_text, str):
                search_type = '__icontains'
            else:
                search_type = '__contains'
        else:
            if isinstance(search_text, str):
                search_type = '__iexact'
            else:
                search_type = '__exact'

        search_filter = {'%s%s' % (search_criteria, search_type): search_text}
        donations = donations.filter(**search_filter)

    if request.user.profile.is_superuser or has_perm(request.user, 'donations.view_donation'):
        donations = donations.order_by('-donation_dt')
    elif is_chapter_chair(request.user):
        chapter_ids = request.user.chapters_officer_user.filter(position__title='Chapter Chair').values_list('chapter', flat=True)
        donations = donations.filter(donate_to_entity__chapter__in=chapter_ids).order_by('-donation_dt')
    else:
        donations = donations.filter(user=request.user).order_by('-donation_dt')

    total_amount = donations.aggregate(Sum('donation_amount'))['donation_amount__sum'] or 0

    total_amount_by_donate_to_entity = donations.values('donate_to_entity__entity_name').annotate(sum=Sum('donation_amount')).order_by('-sum')
    total_amount_by_default_membership = donations.values('user__membershipdefault__membership_type__name').annotate(sum=Sum('donation_amount')).order_by('-sum')
    total_amount_by_chapter_membership = donations.values('user__chaptermembership__chapter__title').annotate(sum=Sum('donation_amount')).order_by('-sum')

    total_amount_by_donate_to_entity_d = {}
    total_amount_by_membership_d = {}

    for item in total_amount_by_donate_to_entity:
        if item['sum']:
            total_amount_by_donate_to_entity_d[item['donate_to_entity__entity_name'] or 'unknown'] = [item['sum'], '{0:.2%}'.format(item['sum'] / total_amount)]

    for item in total_amount_by_default_membership:
        if item['sum']:
            total_amount_by_membership_d[item['user__membershipdefault__membership_type__name'] or 'Anonymous'] = [item['sum'], '{0:.2%}'.format(item['sum'] / total_amount)]
    for item in total_amount_by_chapter_membership:
        if item['sum']:
            total_amount_by_membership_d[item['user__chaptermembership__chapter__title'] or 'Anonymous'] = [item['sum'], '{0:.2%}'.format(item['sum'] / total_amount)]

    EventLog.objects.log()

    return render_to_resp(request=request, template_name=template_name, context={
        'donations': donations,
        'form': form,
        'total_amount': total_amount,
        'total_amount_by_donate_to_entity_d': total_amount_by_donate_to_entity_d,
        'total_amount_by_membership_d': total_amount_by_membership_d,
    })
