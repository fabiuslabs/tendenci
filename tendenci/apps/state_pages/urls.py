from django.urls import re_path
from tendenci.apps.site_settings.utils import get_setting
from . import views
from .feeds import LatestEntriesFeed

urlpath = get_setting('module', 'state_pages', 'url')
if not urlpath:
    urlpath = r'[uU][sS][aA]/(?P<state_slug>[a-zA-Z]{2})'

urlpatterns = [
    re_path(r'^[uU][sS][aA]/find$', views.state_redirect, name="state_pages.find"),
    re_path(r'^[uU][sS][aA]/assign$', views.state_editor, name="state_assign"),
    re_path(r'^%s/$' % urlpath, views.index, name="state_pages"),
    re_path(r'^%s/search/$' % urlpath, views.search, name="state_page.search"),
    re_path(r'^%s/print-view/(?P<slug>[\w\-\/]+)/$' % urlpath, views.print_view, name="state_page.print_view"),
    re_path(r'^%s/preview/$' % urlpath, views.preview, name="state_page.preview"),
    re_path(r'^%s/preview/(?P<id>\d+)/$' % urlpath, views.preview, name="state_page.preview"),
    re_path(r'^%s/add/$' % urlpath, views.add, name="state_page.add"),
    re_path(r'^%s/edit/(?P<id>\d+)/$' % urlpath, views.edit, name="state_page.edit"),
    re_path(r'^%s/versions/(?P<hash>[\w\-]+)/$' % urlpath, views.index, name="state_page.version"),
    re_path(r'^%s/inactive/(?P<id>\d+)/$' % urlpath, views.index, name="state_page.inactive"),
    re_path(r'^%s/edit/meta/(?P<id>\d+)/$' % urlpath, views.edit_meta, name="state_page.edit.meta"),
    re_path(r'^%s/delete/(?P<id>\d+)/$' % urlpath, views.delete, name="state_page.delete"),
    re_path(r'^%s/feed/$' % urlpath, LatestEntriesFeed(), name='state_page.feed'),
    re_path(r'^%s/header_image/(?P<id>\d+)/$' % urlpath, views.display_header_image, name="state_page.header_image"),
    re_path(r'^%s/state-pages-export/$' % urlpath, views.export, name="state_page.export"),
    re_path(r'^%s/state-pages-export/$' % urlpath, views.export, name="state_page.export"),
    re_path(r'^%s/(?P<slug>[\w\-]+)/$' % urlpath, views.index, name="state_page"),
]
