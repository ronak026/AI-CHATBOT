from django.urls import path
from .views import (
    register_view,
    login_view,
    logout_view,
    chat_view,
    chat_history_view,
    profile_view,
    home_view,
    ajax_chat_view,
)

urlpatterns = [
    path("", home_view, name="home"),
    path("login/", login_view, name="login"),
    path("register/", register_view, name="register"),
    path("logout/", logout_view, name="logout"),
    path("chat/", chat_view, name="chat"),
    path("history/", chat_history_view, name="history"),
    path("profile/", profile_view, name="profile"),
    path("ajax/chat/", ajax_chat_view, name="ajax_chat"),
]
