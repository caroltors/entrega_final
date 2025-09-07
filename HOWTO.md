# HOW TO — Projeto Base de Conhecimento (Django)

Registro **passo a passo** do que foi executado para montar o projeto: criação, configuração de modelos, rotas, templates, contas e mensageria.

> **Observações gerais**
>
> * **Não** versionar `db.sqlite3` nem a pasta `media/` (ambos no `.gitignore`).
> * Uso de **herança de templates**. O `base.html` concentra a NavBar e estilos globais.
> * Commits no padrão **Conventional Commits** (em inglês); comentários nos códigos em **português**.

---

## 1) Criação do projeto

**1.1. Pasta do projeto**

```bash
mkdir knowledge_base
cd knowledge_base
```

**1.2. Preparação do ambiente**

```bash
git init
git checkout -b dev
python -m venv venv
venv\Scripts\activate
pip install django
django-admin startproject knowledge_base .
python manage.py startapp knowledge
```

**1.3. Ajustes iniciais**

* Adicionado `'knowledge'` em `knowledge_base/settings.py`.

**1.4. Primeiro commit**

```bash
git add .
git commit -m "chore: initial project setup with Django and knowledge app"
```

---

## 2) Configuração de modelos (Articles)

**2.1. Dependências**

```bash
pip install django-ckeditor
pip install Pillow
```

**2.2. Settings**

* Adicionado `'ckeditor'` em `INSTALLED_APPS`.

**2.3. Modelo Article**

* Criado em `knowledge/models.py` o modelo `Article` com campos (2 `CharField`, texto rico via CKEditor, imagem e data).

**2.4. Admin**

```python
# knowledge/admin.py
from .models import Article
admin.site.register(Article)
```

**2.5. Migrações**

```bash
python manage.py makemigrations
python manage.py migrate
```

**2.6. Commits relacionados**

```bash
git commit -m "chore: update .gitignore to exclude cache, db and compiled files"
git commit -m "feat: add and configure Article model"
git commit -m "chore: move .gitignore to Project root"
```

---

## 3) URLs para Home e About (básico)

**3.1. `knowledge/urls.py`**

```python
from django.urls import path
from django.views.generic import TemplateView

app_name = "knowledge"

urlpatterns = [
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
    path("about/", TemplateView.as_view(template_name="about.html"), name="about"),
]
```

**3.2. Inclusão no projeto**

```python
# knowledge_base/urls.py
path("", include("knowledge.urls")),
```

**3.3. Commit**

```bash
git commit -m "feat: add initial URL routing for home and about pages"
```

---

## 4) Templates iniciais

**4.1. Criados em `knowledge/templates/knowledge/`:**

* `base.html`
* `home.html`
* `about.html`

**4.2. Validação das páginas** para aprimorar UI/UX (commits finais apenas após estabilização).

---

## 5) Views/URLs/Templates para Artigos

**5.1. Views**

* Criadas CBVs `ArticleListView` e `ArticleDetailView` em `knowledge/views.py`.

**5.2. Rotas**

```python
# knowledge/urls.py
path("pages/", ArticleListView.as_view(), name="pages_list"),
path("pages/<int:pk>/", ArticleDetailView.as_view(), name="page_detail"),
```

**5.3. Templates**

* `pages_list.html` e `page_detail.html` criados.

> (Commits desta fase aplicados somente após concluir CRUD.)

---

## 6) Forms/CRUD de Artigos (commits segmentados)

**6.1. Form**

* Criado `knowledge/forms.py` para suportar CRUD.

**6.2. Views adicionais (CBV)**

* `AuthorRequiredMixin`, `ArticleCreateView`, `ArticleUpdateView`, `ArticleDeleteView`.

**6.3. Rotas**

```python
path("pages/new/", ArticleCreateView.as_view(), name="page_create"),
path("pages/<int:pk>/edit/", ArticleUpdateView.as_view(), name="page_update"),
path("pages/<int:pk>/delete/", ArticleDeleteView.as_view(), name="page_delete"),
```

**6.4. Templates**

* `page_form.html` (criação/edição). Ajustado `page_detail.html` para modal de exclusão.

**6.5. Settings/URLs**

* Configurados para upload de imagens via CKEditor.

**6.6. Commits**

```bash
git commit -m "feat: configure CKEditor uploader and media settings"
git commit -m "feat: customize ArticleForm widgets with CKEditor and styles"
git commit -m "feat: improve article CRUD views"
git commit -m "feat: add article CRUD routes to knowledge app"
```

---

## 7) App de Contas (accounts) e configuração inicial

**7.1. Criação do app**

```bash
python manage.py startapp accounts
```

* Registrado `'accounts.apps.AccountsConfig'` no `settings.py`.

**7.2. Modelo Profile + signals**

* `Profile` com `avatar`, `bio`, `birth_date`.
* `signals.py` para criar/atualizar `Profile` automaticamente.
* `apps.py` com `ready()` para carregar signals.

**7.3. Admin e migrações**

```bash
python manage.py makemigrations accounts
python manage.py migrate
```

**Commit**

```bash
git commit -m "feat(accounts): add Profile model, signals and initial configuration"
```

---

## 8) Accounts — Forms, Views (FBV), URLs e Templates

**8.1. Forms**

* Formulários para autenticação/registro/edição de perfil.

**8.2. Views (FBV) com decoradores**

* Login, Logout, Register (solicitando username, email, senha), Profile, Profile Edit, Password Change.

**8.3. URLs**

* Arquivo `accounts/urls.py` e inclusão no `urls.py` principal.

**8.4. Templates**

* `login.html`, `register.html`, `profile.html`, `profile_edit.html`, `password_change.html`, `password_change_done.html`.

**8.5. Ajustes de layout**

* Ajustes em `knowledge/templates/knowledge/base.html`.

**Commits**

```bash
git commit -m "feat(accounts): add authentication, profile management and routing"
git commit -m "layout(accounts): add custom templates for login, register, profile and password change"
```

---

## 9) Ajustes gerais + Middleware de Profile

**9.1. Home/Layout**

* Ajustes em `home.html`, views e `urls.py` para melhorar layout da home.

**9.2. Middleware**

* `accounts/middleware.py` para garantir `Profile` e adicionado a `MIDDLEWARE`:

  ```python
  "accounts.middleware.EnsureProfileMiddleware",
  ```

**9.3. Estilos e About**

* Estilo do `base.html` aprimorado.
* Ajuste no form de novo artigo.
* `about` com avatar fixo em `static/images/me.jpg`.

**Commits**

```bash
git commit -m "feat: add about page content with avatar"
git commit -m "chore: add fixed avatar image for about page (me.jpg)"
git commit -m "style: update base.html styles (navbar search, UI tweaks)"
git commit -m "feat: improve home layout and routing to list articles"
git commit -m "style: adjust new article form layout"
git commit -m "fix: ensure Profile is created for all users via EnsureProfileMiddleware"
```

---

## 10) Criação do app de Mensageria (CBV)

**10.1. App e registro**

```bash
python manage.py startapp messenger
```

* Adicionado `'messenger.apps.MessengerConfig'` ao `settings.py`.

**10.2. Nav**

* Ajuste no template base para adicionar **Chat** ao dropdown do usuário.

  ```
  style(nav): add chat icon to user dropdown for consistency
  ```

**10.3. Config inicial**

* Estrutura de `urls`, `views` e template base do chat.

  ```
  feat(messenger): add initial configs to messenger app
  ```

---

## 11) Models para Mensagens

**11.1. Modelo Message**

* `thread`, `author`, `body (texto)`, `image (ImageField)`, `attachment (FileField)`, `created_at`.
* `clean()` exigindo ao menos um conteúdo (texto/ imagem/ anexo).
* `short_body` para resumo em listas.

**11.2. Migrações e validação no admin**

```bash
python manage.py makemigrations messenger
python manage.py migrate
```

* Verificação em `/admin`.

---

## 12) Configuração dos Chats

**12.1. Views**

* `ChatListView` (inbox + detalhe na mesma página, `?t=<thread_id>`), `ChatNewView` (inicia conversa 1:1 evitando duplicadas), `ChatDeleteView` (exclui conversa), `ChatMessagesAPI` (polling JSON).
* Envio por **POST** no mesmo template (FormMixin) e **enter-to-send**.

**12.2. URLs**

* Inclusão das rotas do `messenger` no projeto.

**12.3. Template `chat_list.html`**

* Inbox + painel de conversa na mesma página.
* Campo de busca de usuário e fallback por lista.
* Composer com **ícones** (imagem/anexo), **chips** de preview, **enviar sem texto** quando há arquivo/imagem.
* Balões com avatar, imagem (preview) e link de anexo (ícone por tipo, nome + tamanho).
* **Polling** a cada 5s para novas mensagens.

**12.4. Alerta no base**

* Mensagem de erro para “usuário inexistente”.

**12.5. Settings — limites e whitelist de upload**

* `CHAT_MAX_FILE_MB` e `CHAT_ALLOWED_FILE_EXTS` em `knowledge_base/settings.py`.

**12.6. Template tags**

* `messenger/templatetags/messenger_extras.py` com filtros `basename`, `file_icon`, `filesize`, etc.

**12.7. Commits segmentados**

```bash
git commit -m "feat(messenger): add Message model with image/attachment and register in admin"
git commit -m "feat(messenger): implement chat views (inbox/new/delete/API), MessageForm and routes"
git commit -m "feat(messenger): build single-page chat UI with composer (enter-to-send, image/file upload)"
git commit -m "feat(messenger): enforce upload limits and allowed file types in settings"
git commit -m "feat(messenger): add template tags for file-type icons, basename and human-readable file size -- erro"
git commit -m "feat(messenger): migrations"
```

**12.8. Correção de mensagem de commit**

```bash
git rebase -i HEAD~2
# alterada para:
# feat(messenger): add template tags for file-type icons, basename and human-readable file size
```

---

## 13) Finalização

**13.1. Requirements**

```bash
pip freeze > requirements.txt
git add requirements.txt
git commit -m "chore: add requirements.txt (frozen from venv)"
```

**13.2. README (execução do projeto)**

* Guia com instruções de setup, execução e funcionalidades (separado deste HOW TO).

**13.3. Push**

```bash
git push origin dev
```

---

### Anexos / Observações de Execução

* Ambiente Windows; ativação do venv via `venv\\Scripts\\activate`.
* CKEditor habilitado com upload de imagens.
* Media servida em dev (`MEDIA_URL`/`MEDIA_ROOT` + `urlpatterns` apropriados).
* `EnsureProfileMiddleware` posicionado em `MIDDLEWARE`.
* Chat com polling simples (5s); futuro: melhorias opcionais (badge de não lidas, AJAX no envio, etc.).
