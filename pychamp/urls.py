"""
URL configuration for pychamp project.
"""

from django.contrib import admin
from django.urls import path
from pyeditor.views import (
    home_view,
    editor_view,
    run_code,
    login_view,
    register_view,
    logout_view,
    profile_view,
    saved_notes_view,
    saved_note_content,
    delete_saved_note,
)
from pyeditor.dsa_views import dsa_view, dsa_invoke, dsa_save_notes

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home_view, name="home"),
    path("editor/", editor_view, name="editor"),
    path("login/", login_view, name="login"),
    path("register/", register_view, name="register"),
    path("logout/", logout_view, name="logout"),
    path("profile/", profile_view, name="profile"),
    path("run_code/", run_code, name="run_code"),
    path("dsa/", dsa_view, name="dsa"),
    path("dsa/invoke/", dsa_invoke, name="dsa_invoke"),
    path("dsa/save/", dsa_save_notes, name="dsa_save"),
    path("notes/", saved_notes_view, name="saved_notes"),
    path("notes/content/", saved_note_content, name="saved_note_content"),
    path("notes/delete/", delete_saved_note, name="delete_saved_note"),
]

