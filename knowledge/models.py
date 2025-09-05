from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField

class Article(models.Model):
    # Título da página
    title = models.CharField(max_length=200)

    # Subtítulo ou descrição curta
    subtitle = models.CharField(max_length=300, blank=True, null=True)

    # Conteúdo principal
    content = RichTextField()

    # Imagem de destaque (capa)
    cover_image = models.ImageField(upload_to="articles/", blank=True, null=True)

    # Autor vinculado ao usuário
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="articles")

    # Datas automáticas
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title