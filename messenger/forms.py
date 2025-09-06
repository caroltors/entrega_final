from django import forms
from .models import Message
from pathlib import Path
from django.conf import settings


# Formulário para enviar uma nova mensagem em uma thread
class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ["body", "image", "attachment"]
        widgets = {
            "body": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Escreva sua mensagem…",
                    "rows": 1,
                }
            )
        }

    def clean(self):
        cleaned = super().clean()
        body = (cleaned.get("body") or "").strip()
        image = cleaned.get("image")
        attachment = cleaned.get("attachment")

        # precisa pelo menos 1 conteúdo
        if not body and not image and not attachment:
            raise forms.ValidationError("Digite uma mensagem ou anexe um arquivo.")

        # valida anexo genérico
        if attachment:
            self._validate_attachment(attachment)

        return cleaned

    def _validate_attachment(self, f):
        # tamanho
        max_mb = getattr(settings, "CHAT_MAX_FILE_MB", 15)
        if f.size and f.size > max_mb * 1024 * 1024:
            raise forms.ValidationError(f"Arquivo muito grande (máx. {max_mb} MB).")

        # extensão
        allowed = set(getattr(settings, "CHAT_ALLOWED_FILE_EXTS", []))
        ext = Path(getattr(f, "name", "")).suffix.lower().lstrip(".")
        if allowed and ext not in allowed:
            allow_str = ", ".join(sorted(allowed))
            raise forms.ValidationError(f"Tipo de arquivo não permitido ({ext}). Permitidos: {allow_str}.")