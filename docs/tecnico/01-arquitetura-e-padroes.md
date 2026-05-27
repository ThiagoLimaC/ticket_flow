# Documentação Técnica — Parte 1: Arquitetura e Padrões

Visão geral das decisões de arquitetura do TicketFlow e dos padrões Django utilizados.
Este documento é o ponto de partida para entender como o projeto está organizado e por quê.

---

## 1. Padrão MVT (Model–View–Template)

O TicketFlow usa o padrão arquitetural nativo do Django: **MVT**.

| Camada | Responsabilidade | Onde fica no projeto |
|---|---|---|
| **Model** | Define a estrutura dos dados e as regras que vivem no banco | `core/models.py`, `usuarios/models.py` |
| **View** | Recebe requisições HTTP, executa lógica e devolve resposta | `core/views.py`, `usuarios/views.py` |
| **Template** | Renderiza HTML com os dados recebidos da view | `core/templates/`, `usuarios/templates/` |

O MVT é semelhante ao MVC clássico, com uma diferença: o "Controller" do MVC é responsabilidade compartilhada entre as **views** (lógica de roteamento e orquestração) e o próprio **framework Django** (que recebe a requisição HTTP e a encaminha para a view correta via `urls.py`).

### Como o ciclo funciona

```
Navegador → urls.py (roteamento) → views.py (lógica) → template (HTML) → Navegador
                                         ↕
                                    models.py (dados)
```

1. O usuário acessa uma URL no navegador
2. Django percorre o `urls.py` e encontra a view correspondente
3. A view consulta ou salva dados via ORM (usando os models)
4. A view passa os dados para um template via `context`
5. O template renderiza o HTML com os dados
6. O HTML é enviado de volta ao navegador

---

## 2. Apps Django

O projeto está dividido em duas apps:

```
ticket_flow/
├── core/           # domínio principal: chamados, clientes, equipamentos
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── forms.py
│   ├── services.py
│   └── templates/core/
├── usuarios/       # autenticação e perfis
│   ├── models.py
│   ├── views.py    # só gerencia login/logout
│   ├── urls.py
│   ├── decorators.py
│   └── templates/usuarios/
└── ticketflow/     # configurações do projeto
    ├── settings.py
    └── urls.py     # inclui as urls de core e usuarios
```

**Por que duas apps?** O Django encoraja separar domínios em apps independentes. A app `usuarios` cuida exclusivamente de quem pode acessar o sistema; a app `core` cuida do negócio em si. Isso mantém os models de negócio sem acoplamento direto ao sistema de autenticação — `core/models.py` nem importa `Perfil`, por exemplo.

---

## 3. Function-Based Views (FBV)

Optamos por **views baseadas em funções** em vez de class-based views (CBV).

```python
# FBV — padrão adotado no projeto
@login_required
def detalhe_chamado(request, chamado_id):
    chamado = get_object_or_404(Chamado, id=chamado_id)
    ...
    return render(request, 'core/chamados/detalhe.html', context)

# CBV — evitado no MVP
class DetalheChaMadoView(LoginRequiredMixin, DetailView):
    model = Chamado
    ...
```

**Por quê FBV?** Class-based views são poderosas para CRUD simples, mas introduzem "mágica" difícil de depurar quando há lógica de negócio personalizada (como controle de permissão por tipo de perfil). Com FBVs, o fluxo é linear e fácil de ler de cima para baixo.

---

## 4. Camada de serviços (`services.py`)

A lógica de negócio **não fica nas views**. Ela fica em funções no arquivo `core/services.py`.

```python
# core/services.py
def abrir_chamado(form, usuario):
    chamado = form.save(commit=False)
    chamado.status = Chamado.Status.ABERTO
    chamado.aberto_por = usuario
    chamado.cliente = chamado.equipamento.cliente
    chamado.save()
    Movimentacao.objects.create(...)
    return chamado

def atribuir_tecnico(chamado, tecnico, responsavel):
    chamado.tecnico_responsavel = tecnico
    chamado.status = Chamado.Status.EM_ANDAMENTO
    chamado.save()
    Movimentacao.objects.create(...)

def mudar_status(chamado, novo_status, responsavel, comentario=''):
    ...
```

A view chama o serviço e só cuida da parte HTTP (receber POST, redirecionar, exibir mensagem):

```python
# core/views.py
def abrir_chamado_view(request):
    if request.method == 'POST':
        form = AbrirChamadoForm(request.user, request.POST)
        if form.is_valid():
            chamado = abrir_chamado(form, request.user)   # ← serviço
            messages.success(request, f'Chamado #{chamado.id} aberto com sucesso.')
            return redirect('detalhe_chamado', chamado_id=chamado.id)
```

**Por quê?** Facilita testes (você pode testar o serviço sem precisar de um objeto `request`), evita duplicação de lógica se uma operação for chamada de mais de um lugar, e mantém as views limpas.

---

## 5. Roteamento de URLs (`urls.py`)

O Django usa o arquivo `urls.py` para mapear URLs a views:

```python
# core/urls.py
urlpatterns = [
    path('chamados/<int:chamado_id>/', views.detalhe_chamado, name='detalhe_chamado'),
    path('chamados/<int:chamado_id>/atribuir/', views.atribuir_tecnico_view, name='atribuir_tecnico'),
    path('chamados/<int:chamado_id>/status/', views.mudar_status_view, name='mudar_status'),
]
```

**`<int:chamado_id>`** é um **conversor de caminho** — o Django extrai o número da URL e passa como argumento `chamado_id` para a view. O tipo `int` garante que só dígitos sejam aceitos; qualquer outra coisa retorna 404 automaticamente.

**`name=`** permite referenciar a URL por nome nos templates:

```html
<a href="{% url 'detalhe_chamado' chamado.id %}">Ver detalhes</a>
```

Se a URL mudar no `urls.py`, todos os templates e redirects que usam `{% url %}` continuam funcionando sem alteração.

---

## 6. Django Messages Framework

Para exibir mensagens de sucesso ou erro após um redirect, usamos o **messages framework** nativo do Django:

```python
# na view — adiciona a mensagem na sessão
messages.success(request, 'Chamado atribuído com sucesso.')
return redirect('detalhe_chamado', chamado_id=chamado.id)
```

```html
<!-- no template — lê e exibe as mensagens -->
{% if messages %}
    {% for message in messages %}
        <div class="alert alert-{{ message.tags }}">{{ message }}</div>
    {% endfor %}
{% endif %}
```

O padrão **POST → Redirect → GET** (PRG) é fundamental aqui: a view que processa o formulário nunca renderiza HTML diretamente — ela redireciona. Se renderizasse, um F5 no navegador reenviaria o formulário e duplicaria a operação.

---

## 7. Template inheritance (herança de templates)

Todo template do projeto estende o `base.html`:

```html
<!-- base.html — layout base com navbar e estrutura Bootstrap -->
<!DOCTYPE html>
<html>
  <head>...</head>
  <body>
    <nav>...</nav>
    {% block content %}{% endblock %}
  </body>
</html>

<!-- detalhe.html — só define o conteúdo da página -->
{% extends "base.html" %}
{% block content %}
  <h2>{{ chamado.titulo }}</h2>
  ...
{% endblock %}
```

Isso garante que qualquer mudança na navbar ou no layout base é propagada automaticamente para todas as páginas.

---

## 8. Configuração via variáveis de ambiente

O projeto usa `django-environ` para ler configurações de um arquivo `.env`:

```python
# ticketflow/settings.py
import environ
env = environ.Env()
environ.Env.read_env(BASE_DIR / '.env')

SECRET_KEY = env('SECRET_KEY')
DATABASE_URL = env.db()   # lê postgres://user:senha@host:porta/banco
```

O `.env` **nunca é commitado** (está no `.gitignore`). Cada desenvolvedor cria o seu localmente. Isso evita que senhas e chaves secretas entrem no repositório.
