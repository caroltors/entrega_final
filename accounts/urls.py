from django.urls import path
from .views import (
    login_view, logout_view, register_view,
    profile_view, profile_edit_view,
    password_change_view, password_change_done_view,
)

app_name = "accounts"

urlpatterns = [
    path("login/",  login_view,  name="login"),
    path("logout/", logout_view, name="logout"),
    path("register/", register_view, name="register"),
    path("profile/",       profile_view,      name="profile"),
    path("profile/edit/",  profile_edit_view, name="profile_edit"),
    path("password/change/",       password_change_view,      name="password_change"),
    path("password/change/done/",  password_change_done_view, name="password_change_done"),
]