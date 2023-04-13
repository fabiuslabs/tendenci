from django.template import Library

register = Library()


@register.inclusion_tag("donations/nav.html", takes_context=True)
def donation_nav(context, user, donation=None):
    context.update({
        'nav_object': donation,
        "user": user
    })
    return context


@register.inclusion_tag("donations/top_nav_items.html", takes_context=True)
def donation_current_app(context, user, donation=None):
    context.update({
        'app_object': donation,
        "user": user
    })
    return context


@register.inclusion_tag("donations/search-form.html", takes_context=True)
def donation_search(context):
    return context


@register.inclusion_tag("donations/donation_item.html")
def donations_search_results_line(request, donation):

    search_line_display = None
    from django.template.loader import render_to_string
    from django.template import TemplateDoesNotExist

    try:
        search_line_display = render_to_string(
            template_name="donations/donation_search_result_line.html",
            context={'donation': donation},
            request=request
        )
    except (TemplateDoesNotExist, IOError):
        pass

    return {'request': request, 'donation': donation, 'search_line_display': search_line_display}
