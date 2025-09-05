from django.contrib import admin
from .models import Profile

# Register your models here.
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    # mostra esses campos na listagem do admin
    list_display = ("user", "birth_date")
    # permite buscar pelo nome/email do usuário
    search_fields = (
        "user__username",
        "user__email",
        "user__first_name",
        "user__last_name",
    )