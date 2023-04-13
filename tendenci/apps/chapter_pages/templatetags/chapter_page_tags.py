from django.template import Library, TemplateSyntaxError, Variable, Node
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

from tendenci.apps.base.template_tags import ListNode, parse_tag_kwargs
from tendenci.apps.chapter_pages.models import ChapterPage

register = Library()


@register.simple_tag(takes_context=True)
def chapter_url(context, viewname, *args, **kwargs):
    """like {% url %}, but includes chapter_slug=chapter.slug, so you don't have to %}"""
    chapter = context.get('chapter')
    if chapter:
        # kwargs.update({'chapter_slug': chapter.slug})
        args = (chapter.slug,) + args
        return reverse(viewname, args=args, kwargs=kwargs)


@register.inclusion_tag("chapter_pages/options.html", takes_context=True)
def page_options(context, user, page):
    context.update({
        "opt_object": page,
        "user": user
    })
    return context


@register.inclusion_tag("chapter_pages/nav.html", takes_context=True)
def page_nav(context, user, page=None):
    context.update({
        'nav_object': page,
        "user": user
    })
    return context


@register.inclusion_tag("chapter_pages/search-form.html", takes_context=True)
def page_search(context):
    return context


@register.inclusion_tag("chapter_pages/top_nav_items.html", takes_context=True)
def page_current_app(context, user, page=None):
    context.update({
        "app_object": page,
        "user": user
    })
    return context


class ListPageNode(ListNode):
    model = ChapterPage
    perms = 'chapter_pages.view_page'


@register.tag
def list_pages(parser, token):
    """
    Used to pull a list of :model:`chapter_pages.ChapterPage` items.

    Usage::

        {% list_pages as [varname] [options] %}

    Be sure the [varname] has a specific name like ``pages_sidebar`` or
    ``pages_list``. Options can be used as [option]=[value]. Wrap text values
    in quotes like ``tags="cool"``. Options include:

        ``limit``
           The number of items that are shown. **Default: 3**
        ``order``
           The order of the items. **Default: Newest Added**
        ``user``
           Specify a user to only show public items to all. **Default: Viewing user**
        ``query``
           The text to search for items. Will not affect order.
        ``tags``
           The tags required on items to be included.
        ``random``
           Use this with a value of true to randomize the items included.

    Example::

        {% list_pages as pages_list limit=5 tags="cool" %}
        {% for page in pages_list %}
            {{ page.title }}
        {% endfor %}
    """
    args, kwargs = [], {}
    bits = token.split_contents()
    context_var = bits[2]

    if len(bits) < 3:
        message = "'%s' tag requires at least 2 parameters" % bits[0]
        raise TemplateSyntaxError(_(message))

    if bits[1] != "as":
        message = "'%s' second argument must be 'as'" % bits[0]
        raise TemplateSyntaxError(_(message))

    kwargs = parse_tag_kwargs(bits)

    if 'order' not in kwargs:
        kwargs['order'] = '-create_dt'

    return ListPageNode(context_var, *args, **kwargs)


class InChapterNode(Node):
    def __init__(self, chapter, user, context_var=None):
        self.chapter = Variable(chapter)
        self.user = Variable(user)
        self.context_var = context_var

    def render(self, context):
        if not all([self.chapter, self.user]):
            return ''

        try:
            chapter = self.chapter.resolve(context)
            user = self.user.resolve(context)

            passes = chapter.is_in_chapter(user)
            if self.context_var:
                context[self.context_var] = passes
                return ''
            else:
                return passes
        except:
            return ''


@register.tag
def in_chapter(parser, token):
    bits = token.split_contents()
    try:
        chapter = bits[1]
    except:
        chapter = None

    try:
        user = bits[2]
    except:
        user = None


    try:
        object = bits[3]
    except:
        object = None

    if object == 'as':
        object = None
        try:
            context_var = bits[4]
        except:
            context_var = None
    else:
        try: context_var = bits[5]
        except: context_var = None

    return InChapterNode(chapter, user, context_var=context_var)
