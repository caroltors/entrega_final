from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile

# registro com e-mail obrigatório
class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_email(self):
        # evita duplicidade de e-mail na base
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Já existe um usuário com este e-mail.")
        return email

# atualização dos dados do próprio User
class UserUpdateForm(forms.ModelForm):

    username = forms.CharField(disabled=True, required=False)

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")
        widgets = {
            "username":  forms.TextInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name":  forms.TextInput(attrs={"class": "form-control"}),
            "email":      forms.EmailInput(attrs={"class": "form-control"}),
        }

    def clean_email(self):
        # mantém e-mail único entre usuários
        email = self.cleaned_data.get("email", "").strip().lower()
        if not email:
            return email
        qs = User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Este e-mail já está em uso.")
        return email
    
    def clean_username(self):
        # mantém username único (case-insensitive), ignorando o próprio usuário
        username = self.cleaned_data["username"].strip()
        qs = User.objects.filter(username__iexact=username).exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Este nome de usuário já está em uso.")
        return username

# edição do perfil estendido (avatar/bio/data nasc.)
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("avatar", "bio", "birth_date")
        widgets = {
            # input oculto; abrimos via botão da câmera no template
            "avatar": forms.FileInput(attrs={
                "class": "d-none",
                "id": "id_avatar",
                "accept": "image/*",
            }),
            "bio": forms.Textarea(attrs={"rows": 4, "class": "form-control"}),
            "birth_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        }

    # garante que o avatar não seja obrigatório na edição
    avatar = forms.ImageField(required=False, widget=forms.FileInput(attrs={
        "class": "d-none",
        "id": "id_avatar",
        "accept": "image/*",
    }))