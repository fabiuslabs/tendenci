from django.urls import re_path
from . import views

urlpatterns = [
    # all contacts
    re_path(r'^contacts/$', views.search, name="contacts"),
    re_path(r'^contacts/(?P<id>\d+)/$', views.details, name="contact"),
    re_path(r'^contacts/search/$', views.search_redirect, name="contact.search"),
    re_path(r'^contacts/print-view/(?P<id>\d+)/$', views.print_view, name="contact.print_view"),
    re_path(r'^contacts/delete/(?P<id>\d+)/$', views.delete, name="contact.delete"),
    
    # add a contact (select which group) (admin)
    re_path(r'^contacts/add/$', views.add_contact, name="contact.add_contact"),
    # add a contact (select which group) (chapter)
    re_path(r'^contacts/chapter/(?P<slug>[-\w]+)/add/', views.add_contact, name="contact.chapter.add_contact"),
    # add a contact_group to a chapter
    re_path(r'^contacts/chapter/(?P<slug>[-\w]+)/group/add/$', views.add_contact_group, name="contact.add_contact_group"),
    
    # chapter urls
    # list all chapter's contacts
    #re_path(r'^contacts/chapter/(?P<id>)/$)', views.chapter_contacts, name="contacts.chapter")
    # list all of a chapter's groups
    re_path(r'^contacts/chapter/(?P<slug>[-\w]+)/groups/$', views.chapter_groups, name="contact.chapter.groups"),
    # list all of a chapter's group's contacts
    re_path(r'^contacts/chapter/(?P<slug>[-\w]+)/group/(?P<id>\d+)/$', views.group_contacts, name="contact.chapter.group.contacts" ),
    
    # site contact form
    re_path(r'^contact/$', views.index, name="form"),
    re_path(r'^contact/confirmation$', views.confirmation, name="form.confirmation"),

]
