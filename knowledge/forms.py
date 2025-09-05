from django import forms
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from .models import Article

class ArticleForm(forms.ModelForm):
    # Conteúdo com CKEditor
    content = forms.CharField(
        label="Conteúdo",
        widget=CKEditorUploadingWidget(),  
        help_text="Use formatação rica para estruturar o artigo."
    )

    class Meta:
        model = Article
        fields = ["title", "subtitle", "content", "cover_image"]
        labels = {
            "title": "Título",
            "subtitle": "Subtítulo",
            "cover_image": "Imagem de capa",
        }
        help_texts = {
            "subtitle": "Opcional — breve descrição que aparece na listagem.",
            "cover_image": "Opcional — JPG/PNG.",
        }
        error_messages = {
            "title": {"required": "Informe um título."},
            "content": {"required": "Escreva o conteúdo do artigo."},
        }
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "kb-title-input",
                "placeholder": "Dê um título claro e direto",
                "autocomplete": "off"
            }),
            "subtitle": forms.TextInput(attrs={
                "class": "kb-subtitle-input",
                "placeholder": "Uma breve descrição (opcional)",
                "autocomplete": "off"
            }),
            "cover_image": forms.FileInput(attrs={
                "class": "form-control"
            }),
        }
