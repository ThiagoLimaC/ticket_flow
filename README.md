# TicketFlow

Sistema de gestão de chamados técnicos (helpdesk) para empresas de suporte de TI, construído em Django.

Permite cadastrar empresas clientes e seus equipamentos, abrir e acompanhar chamados (com status, prioridade, SLA por categoria, atribuição de técnico, registro de atendimentos e peças utilizadas), além de um painel administrativo com indicadores e histórico de atendimentos por cliente.

Perfis de usuário: **Administrador**, **Técnico** e **Cliente**, cada um com permissões e visões próprias.

## Stack

- Python / Django 5
- PostgreSQL (via Docker)
- django-environ para configuração por variáveis de ambiente

## Arquitetura

Projeto Django organizado em dois apps:

- **`ticketflow/`** — configuração do projeto (settings, URLs raiz, WSGI/ASGI).
- **`core/`** — domínio principal do helpdesk:
  - `models.py`: `EmpresaCliente`, `Categoria`, `Equipamento`, `Chamado`, `Movimentacao`, `PecaUtilizada`.
  - `services.py`: regras de negócio (abertura de chamado, transições de status, atribuição de técnico), mantendo as views enxutas.
  - `views.py` / `urls.py`: dashboard, CRUD de clientes/equipamentos e fluxo de chamados.
  - `templates/`: `base.html` com o layout comum e templates por área (`clientes/`, `chamados/`, `equipamentos/`).
  - `management/commands/seed.py`: comando para popular o banco com dados de teste.
- **`usuarios/`** — autenticação e perfis:
  - `models.py`: `Perfil` (admin, técnico ou cliente), criado automaticamente via signal ao registrar um `User`.
  - `decorators.py`: `requer_perfil`, usado nas views do `core` para restringir acesso por tipo de perfil.
  - `templates/registration/login.html`: tela de login.

Persistência em PostgreSQL, configurada via `DATABASE_URL` (django-environ) e disponibilizada localmente por `docker-compose.yml`.

## Como rodar localmente

1. Crie e ative um ambiente virtual, e instale as dependências:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Copie `.env.example` para `.env` e ajuste as variáveis (em especial `SECRET_KEY` e `DATABASE_URL`):
   ```bash
   cp .env.example .env
   ```

3. Suba o banco PostgreSQL (e o pgAdmin) com Docker:
   ```bash
   docker compose up -d
   ```

4. Aplique as migrações e crie um superusuário:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

5. (Opcional) Popule o banco com dados de teste:
   ```bash
   python manage.py seed
   ```

6. Suba o servidor de desenvolvimento:
   ```bash
   python manage.py runserver
   ```

A aplicação estará disponível em `http://localhost:8000`.
