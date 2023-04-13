from django.urls import re_path
from tendenci.apps.site_settings.utils import get_setting
from . import views
from .feeds import LatestEntriesFeed

urlpath = get_setting('module', 'chapter_pages', 'url')
if not urlpath:
    urlpath = r'chapter/(?P<chapter_slug>[\w\-]+)'

urlpatterns = [
    re_path(r'^%s/$' % urlpath, views.index, name="chapter_pages"),
    re_path(r'^%s/search/$' % urlpath, views.search, name="chapter_page.search"),
    re_path(r'^%s/print-view/(?P<slug>[\w\-\/]+)/$' % urlpath, views.print_view, name="chapter_page.print_view"),
    re_path(r'^%s/preview/$' % urlpath, views.preview, name="chapter_page.preview"),
    re_path(r'^%s/preview/(?P<id>\d+)/$' % urlpath, views.preview, name="chapter_page.preview"),
    re_path(r'^%s/add/$' % urlpath, views.add, name="chapter_page.add"),
    re_path(r'^%s/edit/(?P<id>\d+)/$' % urlpath, views.edit, name="chapter_page.edit"),
    re_path(r'^%s/versions/(?P<hash>[\w\-]+)/$' % urlpath, views.index, name="chapter_page.version"),
    re_path(r'^%s/inactive/(?P<id>\d+)/$' % urlpath, views.index, name="chapter_page.inactive"),
    re_path(r'^%s/edit/meta/(?P<id>\d+)/$' % urlpath, views.edit_meta, name="chapter_page.edit.meta"),
    re_path(r'^%s/delete/(?P<id>\d+)/$' % urlpath, views.delete, name="chapter_page.delete"),
    re_path(r'^%s/feed/$' % urlpath, LatestEntriesFeed(), name='chapter_page.feed'),
    re_path(r'^%s/header_image/(?P<id>\d+)/$' % urlpath, views.display_header_image, name="chapter_page.header_image"),
    re_path(r'^%s/chapter-pages-export/$' % urlpath, views.export, name="chapter_page.export"),
    re_path(r'^%s/(?P<slug>[\w\-]+)/$' % urlpath, views.index, name="chapter_page"),
]
