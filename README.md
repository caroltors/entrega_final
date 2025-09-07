# Knowledge Base — Django

> Aplicação web estilo **blog** com páginas (Articles), autenticação e perfis de usuário, além de **mensageria** (chat 1:1) — tudo em **Django 5**.

---

## Sumário

* [Visão geral](#visão-geral)
* [Tecnologias](#tecnologias)
* [Requisitos e preparação](#requisitos-e-preparação)
* [Estrutura do projeto](#estrutura-do-projeto)
* [Configuração](#configuração)

  * [Variáveis/importantes do `settings.py`](#variáveisimportantes-do-settingspy)
  * [URLs e arquivos estáticos/mídia](#urls-e-arquivos-estáticosmídia)
* [Apps e principais modelos](#apps-e-principais-modelos)

  * [Knowledge (páginas)](#knowledge-páginas)
  * [Accounts (contas e perfis)](#accounts-contas-e-perfis)
  * [Messenger (chat)](#messenger-chat)
* [Rotas principais](#rotas-principais)
* [Fluxo de trabalho (commits)](#fluxo-de-trabalho-commits)
* [Como executar](#como-executar)
* [Testes rápidos de verificação](#testes-rápidos-de-verificação)
* [Checklist de entrega](#checklist-de-entrega)
* [Melhorias futuras](#melhorias-futuras)

---

## Visão geral

Este projeto implementa um **blog** com CRUD de páginas (Article) — incluindo **CKEditor** para conteúdo rico —, autenticação e **perfil de usuário** com avatar, e um módulo de **mensageria** para conversas privadas 1:1. O layout usa herança de templates (um `base.html` centraliza a NavBar/estilos) e as operações sensíveis (criar/editar/excluir) exigem usuário autenticado.

---

## Tecnologias

* **Python 3.x**
* **Django 5.x**
* **Pillow** (imagens)
* **django-ckeditor** (texto rico + upload)
* Bootstrap/Icons via templates (UI)

---

## Requisitos e preparação

* **Não** versionar `db.sqlite3` nem a pasta `media/` (listados no `.gitignore`).
* Recomendado usar ambiente virtual.

```bash
# clonar e preparar
git clone https://github.com/caroltors/entrega_final.git
cd knowledge_base
python -m venv venv
venv\Scripts\activate  # Windows

# instalar dependências
pip install -r requirements.txt
```

---

## Estrutura do projeto

```text
knowledge_base/                # raiz do projeto Django
├─ knowledge_base/             # config do projeto
│  ├─ settings.py
│  ├─ urls.py
│  └─ ...
├─ knowledge/                  # app de páginas (Articles)
│  ├─ templates/knowledge/
│  │  ├─ base.html
│  │  ├─ home.html
│  │  ├─ about.html
│  │  ├─ pages_list.html
│  │  ├─ page_detail.html
│  │  └─ page_form.html
│  ├─ models.py
│  ├─ views.py
│  ├─ forms.py
│  └─ urls.py
├─ accounts/                   # app de contas e perfis
│  ├─ templates/accounts/
│  │  ├─ login.html
│  │  ├─ register.html
│  │  ├─ profile.html
│  │  ├─ profile_edit.html
│  │  ├─ password_change.html
│  │  └─ password_change_done.html
│  ├─ models.py                # Profile
│  ├─ signals.py               # cria/atualiza Profile
│  ├─ middleware.py            # EnsureProfileMiddleware
│  ├─ views.py (FBV)
│  └─ urls.py
├─ messenger/                  # app de chat (1:1)
│  ├─ templates/messenger/chat_list.html
│  ├─ templatetags/
│  │  ├─ __init__.py
│  │  └─ messenger_extras.py   # ícones p/ anexos, basename, tamanho legível
│  ├─ models.py                # Thread, ThreadParticipant, Message
│  ├─ forms.py                 # MessageForm
│  ├─ views.py                 # ChatList, ChatNew, ChatDelete, ChatMessagesAPI
│  └─ urls.py
├─ media/                      # uploads (desversionado)
├─ static/                     # assets estáticos do projeto
├─ requirements.txt
└─ manage.py
```

---

## Configuração

### Variáveis/importantes do `settings.py`

* `INSTALLED_APPS` inclui: `knowledge`, `accounts`, `messenger`, `ckeditor`.
* **CKEditor** habilitado (opcionalmente com uploader, se configurado).
* **Uploads**:

  ```python
  MEDIA_URL = "/media/"
  MEDIA_ROOT = BASE_DIR / "media"

  # Regras do chat (exemplo usado)
  CHAT_MAX_FILE_MB = 15
  CHAT_ALLOWED_FILE_EXTS = [
      "pdf", "doc", "docx", "xls", "xlsx", "csv",
      "ppt", "pptx", "txt", "json",
      "zip", "rar", "7z",
      "mp4", "mp3", "wav",
  ]
  ```
* **Middleware** inclui `accounts.middleware.EnsureProfileMiddleware` (garante `Profile`).

### URLs e arquivos estáticos/mídia

Em `knowledge_base/urls.py`:

```python
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

urlpatterns = [
    path("", include("knowledge.urls")),
    path("accounts/", include("accounts.urls")),
    path("chat/", include("messenger.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

---

## Apps e principais modelos

### Knowledge (páginas)

**Article** — atende requisitos mínimos: dois `CharField`, **rich text (CKEditor)**, `ImageField`, campo de data.

* Listagem, detalhe, criação, edição e exclusão (CBV)
* Mensagem quando não há páginas

### Accounts (contas e perfis)

**Profile** — `avatar`, `bio`, data de nascimento, etc.

* Registro, login/logout, perfil e edição, alteração de senha
* Middleware garante criação de `Profile` para todo `User`

### Messenger (chat)

Modelos:

* **Thread** (conversa)
* **ThreadParticipant** (participantes da thread)
* **Message** (`body`, `image`, `attachment`, `created_at`)

Funcionalidades:

* Inbox + detalhe **na mesma tela** (`/chat/` via `ChatListView`)
* **Nova conversa** por username, prevenindo duplicadas
* **Enter** para enviar (Shift+Enter = nova linha)
* **Uploads**: imagem (preview) e anexos em geral (ícones por tipo + nome/tamanho)
* **Avatares** nas mensagens
* **Exclusão** da conversa
* Polling leve (5s) para novas mensagens

---

## Rotas principais

| Rota                         | Descrição             |
| ---------------------------- | --------------------- |
| `/`                          | Home                  |
| `/about/`                    | Sobre mim/Projeto     |
| `/pages/`                    | Lista de artigos      |
| `/pages/<id>/`               | Detalhe do artigo     |
| `/pages/new/`                | Criar artigo (auth)   |
| `/pages/<id>/edit/`          | Editar artigo (auth)  |
| `/pages/<id>/delete/`        | Excluir artigo (auth) |
| `/accounts/login/`           | Login                 |
| `/accounts/register/`        | Registro              |
| `/accounts/profile/`         | Perfil                |
| `/accounts/profile/edit/`    | Editar perfil         |
| `/accounts/password_change/` | Alterar senha         |
| `/chat/`                     | Inbox + conversa      |
| `/chat/new?username=<u>`     | Iniciar conversa 1:1  |

> Há também endpoints auxiliares do chat (ex.: `/chat/api/<thread_id>/messages/?after=<id>` para polling).

---

## Fluxo de trabalho (commits)

* Padrão **Conventional Commits** (ex.: `feat(messenger): ...`, `fix: ...`, `chore: ...`).
* Ajustes relevantes deste projeto:

  * `feat(messenger): add Message model with image/attachment and register in admin`
  * `feat(messenger): implement chat views (inbox/new/delete/API), MessageForm and routes`
  * `feat(messenger): build single-page chat UI with composer (enter-to-send, image/file upload)`
  * `feat(messenger): enforce upload limits and allowed file types in settings`
  * `feat(messenger): add template tags for file-type icons, basename and human-readable file size`
  * `chore: add requirements.txt (frozen from venv)`

---

## Como executar

```bash
# 1) instalar dependências
pip install -r requirements.txt

# 2) aplicar migrações
python manage.py migrate

# 3) criar superusuário (opcional, para admin)
python manage.py createsuperuser

# 4) subir o servidor
python manage.py runserver
# acesse http://127.0.0.1:8000/
```

> Para validar uploads localmente, mantenha `DEBUG=True` e a configuração do `MEDIA_URL`/`MEDIA_ROOT`.

---

## Testes rápidos de verificação

1. Acessar `/about/` e ver informações do autor.
2. Em `/pages/`, criar novo artigo com CKEditor e imagem; verificar listagem, detalhe, edição e exclusão.
3. Criar usuário, logar e editar o perfil (avatar/bio).
4. Em `/chat/`, iniciar conversa digitando um username válido; enviar mensagem com Enter; anexar imagem e/ou arquivo.

---

## Checklist de entrega

* `README.md` e `requirements.txt` incluídos
* `.gitignore` na raiz, com `__pycache__/`, `db.sqlite3`, `media/`
* **Admin** acessível e com modelos registrados
* **Vídeo (≤ 10 min)** mostrando: Home, About, CRUD de páginas, autenticação/perfil, chat (conversa + anexos)

---

## Melhorias futuras

* Badges de **não lidas** e "digitando…"
* **WebSockets** (Django Channels) para chat em tempo real
* Pré-visualização de documentos (PDF, DOCX) no próprio chat
* Pesquisa/filtragem de conversas
* Reações e respostas encadeadas
* Paginação de mensagens antigas

---

> Projeto acadêmico / educacional. Ajuste livremente para seu fluxo de trabalho, deploy e CI/CD.
