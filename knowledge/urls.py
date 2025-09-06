from django.urls import path
from django.views.generic import TemplateView
from .views import ArticleListView, ArticleDetailView, ArticleCreateView, ArticleUpdateView, ArticleDeleteView, HomeView

app_name = "knowledge"

urlpatterns = [
    # path("", TemplateView.as_view(template_name="knowledge/home.html"), name="home"),
    path("", HomeView.as_view(), name="home"),
    path("about/", TemplateView.as_view(template_name="knowledge/about.html"), name="about"),
    path("pages/", ArticleListView.as_view(), name="pages_list"),
    path("pages/<int:pk>/", ArticleDetailView.as_view(), name="page_detail"),
    path("pages/new/", ArticleCreateView.as_view(), name="page_create"),
    path("pages/<int:pk>/edit/", ArticleUpdateView.as_view(), name="page_update"),
    path("pages/<int:pk>/delete/", ArticleDeleteView.as_view(), name="page_delete"),
]

