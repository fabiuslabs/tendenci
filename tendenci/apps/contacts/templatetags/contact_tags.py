from django.forms import HiddenInput
from django.template import Library
from django.contrib.auth.models import AnonymousUser

from tendenci.apps.contacts.forms import ContactForm
from django.utils.safestring import mark_safe


register = Library()


@register.inclusion_tag("contacts/options.html", takes_context=True)
def contact_options(context, user, contact):
    context.update({
        "opt_object": contact,
        "user": user
    })
    return context


@register.inclusion_tag("contacts/nav.html", takes_context=True)
def contact_nav(context, user, contact=None):
    context.update({
        "nav_object" : contact,
        "user": user
    })
    return context


@register.inclusion_tag("contacts/search-form.html", takes_context=True)
def contact_search(context):
    return context


@register.inclusion_tag("contacts/top_nav_items.html", takes_context=True)
def contact_current_app(context, user, contact=None):
    context.update({
        "app_object": contact,
        "user": user
    })
    return context

@register.simple_tag(takes_context=True)
def embed_form(context, pk, *args, **kwargs):
    """
    Example:
        {% embed_form 123 [template] [gsize='compact'] %}
    """
    if len(args) > 0:
        template_name = args[0]
    else:
        template_name = 'forms/embed_form_new.html'

    form = ContactForm(AnonymousUser())
    form.field["contact_group"] =  HiddenInput()
    if not form:
        return ""
    try:
        context['embed_form'] = form
        if 'captcha' in context['embed_form'].fields and 'gsize' in kwargs:
#             if hasattr(context['embed_form_for_form'].fields['captcha'].widget, 'gtag_attrs'):
            context['embed_form'].fields['captcha'].widget.attrs.update(
                            {'data-size': kwargs['gsize']})
        template = context.template.engine.get_template(template_name)
        output = '<div class="embed-form">%s</div>' % template.render(context=context)
        return mark_safe(output)
    except:
        return ""