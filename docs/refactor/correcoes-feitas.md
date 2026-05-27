# Correções — Branch `refactor-correcoes-antes-de-prosseguir`

Este documento descreve todas as correções aplicadas antes de prosseguir para as
próximas tasks do MVP (fluxo de status, diagnóstico e peças). Serve também como
guia de setup para novos membros do time.

---

## 1. Bugs corrigidos

### 1.1 `atribuir.html` — HTML corrompido

**Arquivo:** `core/templates/core/chamados/atribuir.html`

**Problema:** a linha 15 continha o fragmento `<int:chamado_id/card-header">` no
meio do HTML — resíduo de uma edição que colou parte de uma URL do Django no lugar
do markup correto. O card "Resumo do Chamado" estava completamente ausente; só o
formulário de seleção aparecia.

**Correção:** o template foi reconstruído com dois cards corretos:
- **Resumo do Chamado** — exibe título, cliente, equipamento, categoria, prioridade e status
- **Selecionar Técnico** — formulário com select e botão Atribuir

---

### 1.2 `AbrirChamadoForm` — cliente via lista vazia de equipamentos

**Arquivo:** `core/forms.py`

**Problema:** o queryset de equipamentos para usuários não-admin estava hardcoded
como `Equipamento.objects.none()`. A DT01 (campo `empresa` no model `Perfil`) já
havia sido implementada, mas o formulário nunca foi atualizado para usá-la. Resultado:
clientes viam o select de equipamentos vazio e não conseguiam abrir chamados.

**Correção:**

```python
# antes
else:
    self.fields['equipamento'].queryset = Equipamento.objects.none()

# depois
elif perfil.empresa:
    self.fields['equipamento'].queryset = Equipamento.objects.filter(cliente=perfil.empresa)
else:
    self.fields['equipamento'].queryset = Equipamento.objects.none()
```

> O `else` final cobre o caso de cliente sem empresa associada (usuário mal configurado).

---

### 1.3 `dashboard.html` — mensagens de erro não apareciam

**Arquivo:** `core/templates/core/dashboard.html`

**Problema:** quando uma view redirecionava para o dashboard com `messages.error()`
(ex: técnico tentando acessar chamado de outro), a mensagem sumia. O template não
tinha o bloco `{% if messages %}`, então a mensagem ficava na sessão e reaparecia
na próxima página que tivesse o bloco — geralmente o detalhe de outro chamado.

**Correção:** adicionado o bloco de mensagens no topo do `{% block content %}` do
dashboard, antes do título da página.

---

### 1.4 `dashboard.html` — badge de status com valor inexistente

**Arquivo:** `core/templates/core/dashboard.html`

**Problema:** a tabela de chamados usava `chamado.status == 'concluido'` para
colorir o badge, mas esse valor não existe no model. Os choices reais são
`aberto`, `em_andamento`, `aguardando`, `resolvido` e `fechado`. Qualquer chamado
que não fosse "aberto" caía no `else` e recebia badge `bg-info` genérico.

**Correção:** substituído por um bloco completo cobrindo os 5 status:

```django
{% if chamado.status == 'aberto' %}bg-warning text-dark
{% elif chamado.status == 'em_andamento' %}bg-primary
{% elif chamado.status == 'aguardando' %}bg-secondary
{% elif chamado.status == 'resolvido' %}bg-success
{% elif chamado.status == 'fechado' %}bg-dark
{% endif %}
```

---

### 1.5 `base.html` — link "Chamados" na navbar apontava para `#`

**Arquivo:** `core/templates/base.html`

**Problema:** o link "Chamados" na navbar estava com `href="#"` e não navegava
a lugar algum.

**Correção:** `href="{% url 'dashboard' %}"`.

---

### 1.6 `docker-compose.yml` — dependência errada no pgadmin

**Arquivo:** `docker-compose.yml`

**Problema:** o serviço `pgadmin_ticketFlow` declarava `depends_on: - postgres`,
mas o serviço correto se chama `postgres_ticketFlow`. O compose falhava ao tentar
subir o pgadmin.

**Correção:** `depends_on: - postgres_ticketFlow`.

---

## 2. Setup para novos membros do time

### 2.1 Pré-requisitos

- Python 3.11+
- Docker + Docker Compose
- Git

---

### 2.2 Clonar e configurar o ambiente

```bash
git clone <url-do-repositorio>
cd ticket_flow

# criar e ativar o ambiente virtual
python3 -m venv .venv
source .venv/bin/activate

# instalar dependências
pip install -r requirements.txt
```

---

### 2.3 Criar o arquivo `.env`

O projeto usa `django-environ` — sem o `.env` ele não inicia. Crie o arquivo na
raiz do projeto (ao lado do `manage.py`):

```bash
cat > .env << 'EOF'
SECRET_KEY=dev-secret-key-ticketflow-2026
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgres://admin:admin@localhost:5498/postgres
EOF
```

> Nunca commite o `.env`. Ele já está no `.gitignore`.

---

### 2.4 Subir o banco de dados

```bash
docker compose up -d postgres_ticketFlow
```

Aguarde alguns segundos até o container estar saudável (`docker compose ps`).

---

### 2.5 Aplicar as migrations

```bash
python manage.py migrate
```

---

### 2.6 Criar dados de teste

```bash
python manage.py shell -c "
from django.contrib.auth.models import User
from core.models import EmpresaCliente, Categoria, Equipamento

u_admin, _ = User.objects.get_or_create(username='admin')
u_admin.set_password('admin123')
u_admin.is_superuser = True
u_admin.is_staff = True
u_admin.save()
u_admin.perfil.tipo = 'admin'
u_admin.perfil.save()

u_tec, _ = User.objects.get_or_create(username='tecnico1')
u_tec.set_password('admin123')
u_tec.save()
u_tec.perfil.tipo = 'tecnico'
u_tec.perfil.save()

empresa, _ = EmpresaCliente.objects.get_or_create(cnpj='12.345.678/0001-99', defaults={'nome': 'Empresa Teste', 'contato': 'Joao'})

u_cli, _ = User.objects.get_or_create(username='cliente1')
u_cli.set_password('admin123')
u_cli.save()
u_cli.perfil.tipo = 'cliente'
u_cli.perfil.empresa = empresa
u_cli.perfil.save()

Categoria.objects.get_or_create(nome='Hardware', defaults={'sla_horas': 8})
Equipamento.objects.get_or_create(numero_serie='SN-001', defaults={'cliente': empresa, 'tipo': 'Computador', 'modelo': 'Dell OptiPlex'})
print('Setup completo!')
"
```

---

### 2.7 Rodar o servidor

```bash
python manage.py runserver
```

Acesse `http://localhost:8000`.

---

### 2.8 Usuários de teste disponíveis

| Usuário | Senha | Perfil | Observação |
|---|---|---|---|
| `admin` | `admin123` | Administrador | Acesso total, painel `/admin/` |
| `tecnico1` | `admin123` | Técnico | Vê apenas chamados atribuídos a ele |
| `cliente1` | `admin123` | Cliente | Vinculado à "Empresa Teste" |

---

### 2.9 pgAdmin (opcional)

Para inspecionar o banco via interface gráfica:

```bash
docker compose up -d pgadmin_ticketFlow
```

Acesse `http://localhost:56` e faça login com:
- **Email:** `admin@admin.com`
- **Senha:** `admin123`

Ao cadastrar o servidor no pgAdmin, use:
- **Host:** `postgres_ticketFlow`
- **Port:** `5432`
- **Database:** `postgres`
- **Username:** `admin`
- **Password:** `admin`

---

## 3. Estado da branch após as correções

Todos os 6 bugs foram verificados manualmente no navegador. A branch está pronta
para merge e para prosseguir com as tasks 7 e 8 do MVP:

- **Task 7:** fluxo completo de status + movimentações (técnico muda status, admin fecha/reabre)
- **Task 8:** registro de diagnóstico, solução, tempo gasto e peças utilizadas (técnico)
