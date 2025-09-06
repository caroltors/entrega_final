from django.urls import path
from .views import ChatListView  # CBV placeholder

app_name = "messenger"

urlpatterns = [
    path("", ChatListView.as_view(), name="chat_list"),
]
