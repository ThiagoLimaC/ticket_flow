# TicketFlow

Sistema de gestão de chamados técnicos (helpdesk) para empresas de suporte de TI, construído em Django.

Permite cadastrar empresas clientes e seus equipamentos, abrir e acompanhar chamados (com status, prioridade, SLA por categoria, atribuição de técnico, registro de atendimentos e peças utilizadas), além de um painel administrativo com indicadores e histórico de atendimentos por cliente.

Perfis de usuário: **Administrador**, **Técnico** e **Cliente**, cada um com permissões e visões próprias.

## Stack

- Python / Django 5
- PostgreSQL (via Docker)
- django-environ para configuração por variáveis de ambiente

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
