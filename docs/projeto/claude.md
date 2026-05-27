1. Visão geral do projeto

TicketFlow é um sistema web de controle de ordens de serviço desenvolvido em Django para a empresa fictícia TechFix Soluções.

    Framework: Django (MVT — sem API REST, sem frontend separado)
    Banco: SQLite no desenvolvimento / PostgreSQL em produção
    Python: 3.11+
    Sem frameworks CSS externos obrigatórios (Bootstrap simples é permitido)

2. Filosofia de desenvolvimento
Regra principal: MVP primeiro, sempre.

    Não implemente o que não está no escopo da sprint atual.
    Funcionalidade simples e funcionando vale mais que funcionalidade elegante quebrada.

    Nenhuma abstração antecipada — só crie classes base, mixins ou utilitários quando houver repetição real
    Nenhuma integração externa antes do MVP estar completo
    Nenhum refactor antes de ter testes cobrindo o trecho a ser refatorado
    Se surgir uma ideia boa fora do escopo atual, registre em docs/ideias-v2.md e siga em frente

3. Arquitetura do projeto

ticketflow/               ← repositório raiz
├── manage.py
├── requirements.txt
├── .env.example
├── docs/
│   ├── CLAUDE.md         ← este arquivo
│   ├── briefing-cliente.md
│   └── ideias-v2.md
├── core/                 ← app principal
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── forms.py
│   ├── admin.py
│   └── templates/
│       └── core/
│           ├── base.html
│           ├── painel.html
│           └── ...
├── usuarios/             ← app de autenticação e perfis
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── templates/
│       └── usuarios/
├── etl/                  ← scripts de análise de dados (fora do Django)
│   ├── extrator.py
│   └── relatorio.py
└── ticketflow/           ← settings
    ├── settings.py
    ├── urls.py
    └── wsgi.py

Regras de arquitetura

    Uma app por domínio — não coloque lógica de usuários dentro de core
    Views ficam em views.py — não crie arquivos views/ com múltiplos módulos no MVP
    Templates seguem o padrão app/nome_da_view.html
    Lógica de negócio fica nos models ou em funções em core/services.py — nunca nas views
    O módulo etl/ é independente do Django — não importa models diretamente, lê via SQL ou CSV exportado

4. Regras de negócio

    Esta seção é a mais importante. Qualquer dúvida sobre comportamento do sistema, consulte aqui primeiro.

4.1 Chamados

    Todo chamado nasce com status aberto
    Um chamado só pode ser movido para em_andamento após ter um técnico atribuído
    Um chamado resolvido pode ser reaberto pelo admin — volta para aberto com nova movimentação registrada
    Um chamado fechado é imutável — nenhum campo pode ser alterado
    O campo sla_prazo é calculado automaticamente no save() do model: data_abertura + categoria.sla_horas
    Um chamado está "atrasado" quando timezone.now() > sla_prazo e status não é resolvido nem fechado

4.2 Fluxo de status permitido

aberto → em_andamento → aguardando → resolvido → fechado
aberto → em_andamento → resolvido → fechado
resolvido → aberto  (apenas admin)

Qualquer outra transição deve ser bloqueada na view e no model.
4.3 Movimentações

    Toda mudança de status gera automaticamente um registro em Movimentacao
    Movimentações nunca são editadas ou deletadas — são imutáveis por design
    O campo responsavel da movimentação é sempre o usuário logado que executou a ação

4.4 Peças utilizadas

    Peças só podem ser registradas em chamados com status em_andamento ou aguardando
    Não há controle de estoque no MVP — apenas registro descritivo de peças usadas

4.5 Perfis e permissões
Ação 	Admin 	Técnico 	Cliente
Abrir chamado 	sim 	não 	sim
Atribuir técnico 	sim 	não 	não
Mudar status 	sim 	sim (só os seus) 	não
Registrar diagnóstico/peças 	sim 	sim (só os seus) 	não
Ver todos os chamados 	sim 	não 	não
Ver histórico do cliente 	sim 	não 	sim (só o seu)
Gerenciar clientes/equipamentos 	sim 	não 	não
Acessar painel admin 	sim 	não 	não

    Técnico só acessa chamados atribuídos a ele
    Cliente só acessa chamados vinculados à sua empresa
    Verificação de permissão deve ocorrer na view — nunca confiar só no template

4.6 Clientes e equipamentos

    Um equipamento pertence a exatamente um cliente — não pode ser transferido no MVP
    Ao abrir um chamado, o cliente seleciona um dos seus equipamentos cadastrados
    Se o cliente não tiver equipamentos cadastrados, o admin deve cadastrar antes

5. Padrão de código
Nomenclatura — tudo em português

# Models
class Chamado(models.Model): ...
class Movimentacao(models.Model): ...
class PecaUtilizada(models.Model): ...

# Campos
data_abertura = models.DateTimeField()
status_atual = models.CharField()
tecnico_responsavel = models.ForeignKey()

# Views
def abrir_chamado(request): ...
def atribuir_tecnico(request, chamado_id): ...
def painel_admin(request): ...

# URLs
path('chamados/abrir/', abrir_chamado, name='abrir_chamado')
path('chamados/<int:chamado_id>/atribuir/', atribuir_tecnico, name='atribuir_tecnico')

# Templates
chamados/detalhe_chamado.html
chamados/lista_chamados.html

Choices como constantes no model

class Chamado(models.Model):
    class Status(models.TextChoices):
        ABERTO = 'aberto', 'Aberto'
        EM_ANDAMENTO = 'em_andamento', 'Em andamento'
        AGUARDANDO = 'aguardando', 'Aguardando'
        RESOLVIDO = 'resolvido', 'Resolvido'
        FECHADO = 'fechado', 'Fechado'

Views — função simples, sem class-based no MVP

# preferir assim
def detalhe_chamado(request, chamado_id):
    chamado = get_object_or_404(Chamado, id=chamado_id)
    ...

# evitar no MVP
class DetalheChaMadoView(LoginRequiredMixin, DetailView):
    ...

Formulários sempre via forms.py

Nunca manipular request.POST diretamente nas views — sempre usar ModelForm ou Form.
6. Padrão de commits

Formato: tipo(escopo): descrição curta em português
Tipo 	Uso
feat 	nova funcionalidade
fix 	correção de bug
refactor 	refatoração sem mudança de comportamento
docs 	documentação
style 	formatação, sem lógica
test 	testes
chore 	tarefas de configuração/infra
Exemplos

feat(chamado): adiciona fluxo de abertura de chamado pelo cliente
fix(status): bloqueia transição de fechado para qualquer outro status
docs(claude): atualiza regras de negócio de peças utilizadas
feat(etl): adiciona extração de tempo médio por categoria
chore(deps): adiciona django-environ ao requirements.txt

Regras

    Commits em português, imperativos ("adiciona", "corrige", "remove")
    Um commit por funcionalidade — não acumular dias de trabalho em um único commit
    Nunca commitar com o projeto quebrado (migrations não aplicadas, imports com erro)

7. Fluxo de desenvolvimento

    Verificar qual tarefa está no topo do backlog (docs/backlog.md)
    Criar branch: feat/nome-da-funcionalidade ou fix/nome-do-bug
    Implementar seguindo as regras deste documento
    Testar manualmente o fluxo completo da funcionalidade
    Commitar seguindo o padrão de commits
    Abrir PR para a branch main com descrição do que foi feito

Ordem de implementação (MVP)

1. Setup inicial + models + migrations
2. Django Admin configurado para todas as entidades
3. Autenticação e perfis de acesso
4. CRUD de clientes e equipamentos (admin)
5. Abertura de chamado (cliente e admin)
6. Atribuição de técnico (admin)
7. Fluxo de status + movimentações
8. Registro de diagnóstico e peças (técnico)
9. Cálculo e exibição de SLA
10. Painel admin
11. Histórico por cliente
12. ETL — extração e relatório

8. O que a IA não deve fazer

    Não sugerir DRF (Django REST Framework) — o projeto é MVT puro
    Não criar serializadores, ViewSets ou routers
    Não introduzir Celery, Redis ou filas de tarefas no MVP
    Não usar async views — Django síncrono por enquanto
    Não criar abstrações (managers customizados, mixins complexos) antes de haver repetição real
    Não refatorar código que está funcionando sem solicitação explícita
    Não alterar regras de negócio da seção 4 sem confirmação do time

Atualizado sempre que uma decisão de arquitetura ou regra de negócio mudar.
