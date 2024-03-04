from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("new_entry/", views.new_entry, name="new_entry"),
    path("edit_entry/<str:entry_title>", views.edit_entry, name="edit_entry"),
    path("search/", views.search_entries, name="search_entries"),
    path("random", views.random_entry, name="random_entry"),
    path("wiki/<str:entry_name>/", views.view_entry, name="view_entry")
]
