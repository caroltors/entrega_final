from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

# Create your views here.
class ChatListView(LoginRequiredMixin, TemplateView):
    """
    View inicial do mensageiro. Por enquanto só renderiza o template
    base com um placeholder. Exige login.
    """
    template_name = "messenger/chat_list.html"