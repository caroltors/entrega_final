from django.urls import path
from .views import ChatListView, ChatNewView, ChatMessagesAPI , ThreadDeleteView # CBV placeholder

app_name = "messenger"

urlpatterns = [
    path("", ChatListView.as_view(), name="chat_list"),
    path("new/", ChatNewView.as_view(), name="chat_new"),
    path("api/<int:pk>/messages/", ChatMessagesAPI.as_view(), name="chat_messages_api"), # rota para API
    path("delete/<int:pk>/", ThreadDeleteView.as_view(), name="chat_delete"), # rota para deletar conversa
]
