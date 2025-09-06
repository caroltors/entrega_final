from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from .models import Article
from .forms import ArticleForm
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse, reverse_lazy
from django.db.models import Q

# Create your views here.
class ArticleListView(ListView):
    model = Article
    template_name = "knowledge/pages_list.html"
    context_object_name = "articles"
    paginate_by = 10  # opcional
    ordering = ["-created_at"]

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(title__icontains=q)  # busca simples
        return qs
class ArticleDetailView(DetailView):
    model = Article
    template_name = "knowledge/page_detail.html"
    context_object_name = "article"
class AuthorRequiredMixin(UserPassesTestMixin):
    """
    Permite acesso apenas ao autor do objeto.
    """
    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user
class ArticleCreateView(LoginRequiredMixin, CreateView):
    model = Article
    form_class = ArticleForm
    template_name = "knowledge/page_form.html"

    def form_valid(self, form):
        # Define o autor como o usuário logado
        form.instance.author = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, "Artigo criado com sucesso.")
        return response

    def get_success_url(self):
        return reverse("knowledge:page_detail", kwargs={"pk": self.object.pk})
class ArticleUpdateView(LoginRequiredMixin, AuthorRequiredMixin, UpdateView):
    model = Article
    form_class = ArticleForm
    template_name = "knowledge/page_form.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Artigo atualizado com sucesso.")
        return response

    def get_success_url(self):
        return reverse("knowledge:page_detail", kwargs={"pk": self.object.pk})
class ArticleDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Article
    success_url = reverse_lazy("knowledge:pages_list")

    def test_func(self):
        # Garante que só o autor pode excluir
        article = self.get_object()
        return self.request.user == article.author

    def delete(self, request, *args, **kwargs):
        article = self.get_object()
        messages.success(request, f'O artigo "{article.title}" foi excluído com sucesso.')
        return super().delete(request, *args, **kwargs)
    
# View para a página inicial com artigos recentes e busca
class HomeView(TemplateView):
    template_name = "knowledge/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        q = self.request.GET.get("q", "").strip()
        qs = Article.objects.all().order_by("-created_at")
        if q:
            qs = qs.filter(
                Q(title__icontains=q) |
                Q(subtitle__icontains=q) |
                Q(content__icontains=q)
            )
        ctx["latest"] = list(qs[:6])   # mostra 6 na home
        ctx["query"] = q
        return ctx