"""
URL configuration for pychamp project.
"""

from django.contrib import admin
from django.urls import path
from pyeditor.views import (
    editor_view,
    run_code,
    login_view,
    register_view,
    logout_view,
    profile_view,
)
from pyeditor.dsa_views import dsa_view, dsa_invoke

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", editor_view, name="editor"),
    path("login/", login_view, name="login"),
    path("register/", register_view, name="register"),
    path("logout/", logout_view, name="logout"),
    path("profile/", profile_view, name="profile"),
    path("run_code/", run_code, name="run_code"),
    path("dsa/", dsa_view, name="dsa"),
    path("dsa/invoke/", dsa_invoke, name="dsa_invoke"),
]
