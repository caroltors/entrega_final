from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from django.conf import settings

# Create your models here.
User = get_user_model()

class Thread(models.Model):
    """
    Conversa. Usa M2M via tabela explícita ThreadParticipant
    para permitir 2+ participantes (futuro: grupos).
    """
    participants = models.ManyToManyField(
        User,
        through='ThreadParticipant',
        related_name='chat_threads',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-updated_at',)

    def __str__(self) -> str:
        users = ", ".join(self.participants.values_list('username', flat=True)[:3])
        return f"Thread #{self.pk} ({users})"

    @property
    def last_message(self):
        # último recado da conversa (útil para listagens)
        return self.messages.order_by('-created_at').first()

    @property
    def messages_count(self) -> int:
        return self.messages.count()

class ThreadParticipant(models.Model):
    """
    Participação de um usuário em uma thread (conversa).
    """
    thread = models.ForeignKey(
        Thread, on_delete=models.CASCADE, related_name='participants_through'
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='thread_participations'
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('thread', 'user')
        indexes = [
            models.Index(fields=['thread']),
            models.Index(fields=['user']),
        ]

    def __str__(self) -> str:
        return f"{self.user} in T{self.thread_id}"


class Message(models.Model):
    thread = models.ForeignKey(Thread, related_name="messages", on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    body = models.TextField(blank=True)

    # uma única imagem (com validador)
    image = models.ImageField(
        upload_to="chat/images/",
        blank=True,
        null=True,
        validators=[FileExtensionValidator(["jpg", "jpeg", "png", "gif", "webp"])],
    )

    # anexo genérico
    attachment = models.FileField(
        upload_to="chat/files/",
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("created_at",)
        indexes = [
            models.Index(fields=["thread", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"Msg #{self.pk} by {self.author} in T{self.thread_id}"

    @property
    def short_body(self) -> str:
        text = (self.body or "").strip()
        return (text[:40] + "…") if len(text) > 40 else text

    def clean(self):
        # Exige ao menos um conteúdo: texto OU imagem OU anexo
        if not self.body and not self.image and not self.attachment:
            raise ValidationError("É necessário texto, imagem ou anexo.")
    
