from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile

# garante que sempre exista um Profile vinculado ao User
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)   # cria perfil automático no cadastro
    else:
        instance.profile.save()  # salva alterações se o user já tinha perfil