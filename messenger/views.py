from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import AbstractUser
from django.db.models import Count
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.generic import ListView
from django.views.generic.edit import FormMixin
from django.http import JsonResponse # para respostas AJAX
from django.http import HttpResponseForbidden # para respostas 403
import os

from .forms import MessageForm
from .models import Thread, ThreadParticipant, Message

User = get_user_model()


class ChatListView(LoginRequiredMixin, FormMixin, ListView):
    """
    Inbox do chat + detalhe na mesma página.
    Usa ?t=<thread_id> para selecionar a conversa ativa.
    A lista (self.get_queryset) mostra apenas threads com mensagens.
    """
    model = Thread
    template_name = "messenger/chat_list.html"
    context_object_name = "threads"
    paginate_by = 10
    form_class = MessageForm

    # QS base: todas as threads do usuário (com ou sem mensagens)
    def base_threads_qs(self):
        return Thread.objects.filter(participants=self.request.user)

    # Inbox: apenas threads com pelo menos 1 mensagem
    def get_queryset(self):
        return (
            self.base_threads_qs()
            .annotate(num_msgs=Count("messages"))
            .filter(num_msgs__gt=0)
            .prefetch_related("participants", "messages__author")
            .order_by("-updated_at")
        )

    # Consegue abrir a conversa ativa mesmo que esteja vazia
    def get_active_thread(self):
        pk = self.request.GET.get("t")
        if not pk:
            return None
        try:
            return (
                self.base_threads_qs()
                .prefetch_related("participants", "messages__author")
                .get(pk=pk)
            )
        except Thread.DoesNotExist:
            return None

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        # Usuários para "Nova conversa"
        ctx["users"] = (
            User.objects.filter(is_active=True)
            .exclude(id=self.request.user.id)
            .order_by("username")
        )

        # 🔧 Corrige vírgula: cria atributo .other_display em cada thread
        threads = list(ctx["threads"])
        for t in threads:
            others_qs = t.participants.exclude(id=self.request.user.id)
            others = [(u.get_full_name() or u.username) for u in others_qs]
            t.other_display = ", ".join(others) if others else "(você)"
        ctx["threads"] = threads

        # Detalhe (painel direito)
        active = self.get_active_thread()
        ctx["active_thread"] = active
        ctx["other_participants"] = (
            active.participants.exclude(id=self.request.user.id) if active else []
        )
        ctx["form"] = self.get_form()
        return ctx

    def post(self, request, *args, **kwargs):
        """
        Envia mensagem na própria tela /chat/?t=<id>
        """
        self.object_list = self.get_queryset()  # requerido pelo ListView
        thread = self.get_active_thread()
        form = self.get_form()
        if not thread:
            messages.error(request, "Conversa não encontrada.")
            return self.get(request, *args, **kwargs)

        if form.is_valid():
            msg = form.save(commit=False)
            msg.thread = thread
            msg.author = request.user
            msg.save()
            thread.updated_at = timezone.now()
            thread.save(update_fields=["updated_at"])
            return redirect(f"{reverse('messenger:chat_list')}?t={thread.pk}")

        messages.error(request, "Não foi possível enviar a mensagem.")
        return self.get(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.method in ("POST", "PUT"):
            kwargs.update({"data": self.request.POST, "files": self.request.FILES})
        return kwargs

class ChatNewView(LoginRequiredMixin, View):
    """
    Cria (ou reabre) conversa 1:1 e redireciona para /chat/?t=<id>
    """
    def get(self, request):
        target = None
        to_id = request.GET.get("to")
        username = request.GET.get("username")

        if to_id:
            try:
                target = User.objects.get(id=int(to_id))
            except (ValueError, User.DoesNotExist):
                target = None
        elif username:
            username = username.strip()
            if username:
                target = User.objects.filter(username__iexact=username).first()

        if not target or target == request.user:
            # vira "warning" (amarelo) e sem redirecionar para uma view diferente
            messages.warning(request, "Usuário destino inválido.")
            return redirect("messenger:chat_list")

        thread = self._get_or_create_1to1(request.user, target)
        # não mostramos mais mensagem de sucesso aqui
        return redirect(f"{reverse('messenger:chat_list')}?t={thread.id}")

    def _get_or_create_1to1(self, a: AbstractUser, b: AbstractUser) -> Thread:
        """
        Reutiliza a mesma thread 1×1 se já existir.
        """
        qs = (
            Thread.objects.filter(participants=a)
            .filter(participants=b)
            .annotate(num_participants=Count("participants", distinct=True))
            .filter(num_participants=2)
        )
        thread = qs.first()
        if thread:
            return thread

        # Cria nova
        thread = Thread.objects.create()
        ThreadParticipant.objects.bulk_create(
            [
                ThreadParticipant(thread=thread, user=a),
                ThreadParticipant(thread=thread, user=b),
            ]
        )
        return thread
    
class ChatMessagesAPI(LoginRequiredMixin, View):
    def get(self, request, pk: int):
        try:
            thread = Thread.objects.get(pk=pk, participants=request.user)
        except Thread.DoesNotExist:
            return HttpResponseForbidden("Thread não encontrada ou sem permissão.")

        after = request.GET.get("after")
        qs = thread.messages.all()
        if after and after.isdigit():
            qs = qs.filter(pk__gt=int(after))

        payload = []
        for m in qs:
            avatar = ""
            try:
                if getattr(m.author, "profile", None) and m.author.profile.avatar:
                    avatar = m.author.profile.avatar.url
            except Exception:
                avatar = ""

            payload.append({
                "id": m.pk,
                "author": (m.author.get_full_name() or m.author.username),
                "author_username": m.author.username,
                "is_self": (m.author_id == request.user.id),
                "body": m.body or "",
                "created_at": m.created_at.strftime("%d/%m/%Y %H:%M"),
                "avatar": avatar,
                "image": (m.image.url if m.image else ""),
                "attachment": (
                    {"url": m.attachment.url, "name": os.path.basename(m.attachment.name)}
                    if m.attachment else None
                ),
            })
        return JsonResponse({"messages": payload})
    
class ThreadDeleteView(LoginRequiredMixin, View):
    """Remove a conversa inteira (mensagens + participantes) se o usuário for participante."""
    def post(self, request, pk: int):
        try:
            thread = Thread.objects.get(pk=pk, participants=request.user)
        except Thread.DoesNotExist:
            messages.warning(request, "Conversa não encontrada.")
            return redirect("messenger:chat_list")

        # segurança extra: garante participação
        if not thread.participants.filter(id=request.user.id).exists():
            return HttpResponseForbidden("Sem permissão para excluir esta conversa.")

        thread.delete()  # PT-BR: Mensagens/participantes são apagados via CASCADE
        messages.info(request, "Conversa excluída.")
        return redirect("messenger:chat_list")