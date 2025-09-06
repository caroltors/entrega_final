# accounts/middleware.py
from django.utils.deprecation import MiddlewareMixin

class EnsureProfileMiddleware(MiddlewareMixin):
    """Garante que todo usuário autenticado tenha um Profile associado.
    Evita RelatedObjectDoesNotExist em qualquer rota (inclui /admin)."""
    def process_request(self, request):
        user = getattr(request, "user", None)
        if user and user.is_authenticated:
            # Import local para evitar import circular
            from accounts.models import Profile
            Profile.objects.get_or_create(user=user)
