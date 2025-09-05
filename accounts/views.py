from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.shortcuts import render, redirect
from django.urls import reverse
from .models import Profile

from .forms import RegisterForm, UserUpdateForm, ProfileUpdateForm

# Create your views here.
def login_view(request):
    if request.user.is_authenticated:
        return redirect("accounts:profile")

    form = AuthenticationForm(request, data=request.POST or None)

    form.fields["username"].label = "Usuário"
    form.fields["password"].label = "Senha"

    # aplica classe base e placeholders toda vez
    form.fields["username"].widget.attrs.update({
        "class": "form-control",
        "placeholder": "Seu usuário",
        "autocomplete": "username",
        "autofocus": True,
    })
    form.fields["password"].widget.attrs.update({
        "class": "form-control",
        "placeholder": "Sua senha",
        "autocomplete": "current-password",
        "id": "id_password",  # para o toggle de visibilidade
    })

    # se houver erros, marca os campos como inválidos (Bootstrap)
    if request.method == "POST" and not form.is_valid():
        for name, field in form.fields.items():
            css = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{css} is-invalid".strip()

    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        messages.success(request, "Login realizado com sucesso.")
        next_url = request.GET.get("next") or reverse("knowledge:home")
        return redirect(next_url)

    return render(request, "accounts/login.html", {"form": form})

@login_required
def logout_view(request):
    # encerra a sessão e redireciona para a home
    logout(request)
    messages.info(request, "Você saiu da sua conta.")
    return redirect("knowledge:home")

def register_view(request):
    if request.user.is_authenticated:
        return redirect("accounts:profile")

    form = RegisterForm(request.POST or None)

    # sobrescreve labels em português
    form.fields["username"].label = "Usuário"
    form.fields["email"].label = "Email"
    form.fields["password1"].label = "Senha"
    form.fields["password2"].label = "Confirmação de senha"

    # aplica classes e placeholders
    form.fields["username"].widget.attrs.update({
        "class": "form-control",
        "placeholder": "Digite um nome de usuário",
        "autocomplete": "username",
    })
    form.fields["email"].widget.attrs.update({
        "class": "form-control",
        "placeholder": "Digite seu email",
        "autocomplete": "email",
    })
    form.fields["password1"].widget.attrs.update({
        "class": "form-control",
        "placeholder": "Crie uma senha",
        "autocomplete": "new-password",
        "id": "id_password1",
    })
    form.fields["password2"].widget.attrs.update({
        "class": "form-control",
        "placeholder": "Confirme a senha",
        "autocomplete": "new-password",
        "id": "id_password2",
    })

    if request.method == "POST" and form.is_valid():
        user = form.save()
        Profile.objects.get_or_create(user=user)  # garante perfil
        login(request, user)
        messages.success(request, "Conta criada com sucesso! Complete seu perfil.")
        edit_url = reverse("accounts:profile_edit")
        return redirect(f"{edit_url}?first=1")  # mostra modo "completar perfil"

    return render(request, "accounts/register.html", {"form": form})

@login_required
def profile_view(request):
    # exibe dados do próprio usuário; template usa request.user/profile
    return render(request, "accounts/profile.html", {"user_obj": request.user})

@login_required
def profile_edit_view(request):
    is_first_time = request.GET.get("first") == "1"  # modo onboarding

    if request.method == "POST":
        uform = UserUpdateForm(request.POST, instance=request.user)
        pform = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
    else:
        uform = UserUpdateForm(instance=request.user)
        pform = ProfileUpdateForm(instance=request.user.profile)

    # >>> garante que o username SEMPRE apareça preenchido no input (é readonly)
    uname = (request.user.username or "").strip()
    if uname:
        # reforça initial (útil no GET e quando form POST inválido)
        uform.initial.setdefault("username", uname)
        uform.fields["username"].initial = uname
        # remove qualquer placeholder legado e injeta value no widget (readonly)
        uform.fields["username"].widget.attrs.pop("placeholder", None)
        uform.fields["username"].widget.attrs["value"] = uname
    # <<<

    if request.method == "POST" and uform.is_valid() and pform.is_valid():
        uform.save()
        pform.save()
        messages.success(request, "Perfil atualizado com sucesso.")
        return redirect("accounts:profile")

    # labels
    uform.fields["first_name"].label = "Nome"
    uform.fields["last_name"].label  = "Sobrenome"
    uform.fields["email"].label      = "Email"
    pform.fields["bio"].label        = "Biografia"
    pform.fields["birth_date"].label = "Data de nascimento"
    uform.fields["username"].label   = "Nome de usuário"

    # estilos/attrs (inputs de nome como “título”)
    uform.fields["first_name"].widget.attrs.update({
        "class": "kb-title-input",
        "placeholder": "Seu nome",
    })
    uform.fields["last_name"].widget.attrs.update({
        "class": "kb-title-input",
        "placeholder": "Seu sobrenome",
    })
    uform.fields["email"].widget.attrs.update({
        "class": "form-control",
        "placeholder": "seu@email.com",
    })

    uform.fields["username"].widget.attrs.update({
        "class": "form-control text-muted",
        "readonly": "readonly",  # não editável
    })

    # se for primeira vez, marca os campos principais como required (HTML)
    if is_first_time:
        for f in ("first_name", "last_name", "email"):
            uform.fields[f].widget.attrs["required"] = True
        for f in ("bio", "birth_date"):
            pform.fields[f].widget.attrs["required"] = True

    return render(
        request,
        "accounts/profile_edit.html",
        {"uform": uform, "pform": pform, "is_first_time": is_first_time},
    )

@login_required
def password_change_view(request):
    # troca de senha sem CBV; mantém a sessão válida após a alteração
    form = PasswordChangeForm(user=request.user, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)  # evita logout imediato
        messages.success(request, "Senha alterada com sucesso.")
        return redirect("accounts:password_change_done")

    return render(request, "accounts/password_change_form.html", {"form": form})

@login_required
def password_change_done_view(request):
    # página simples de confirmação
    return render(request, "accounts/password_change_done.html")