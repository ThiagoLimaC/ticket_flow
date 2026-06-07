# Guia de Testes — T11: Histórico por Cliente

Branch: `t11-historico-por-cliente`

## O que esta task implementa

Adiciona uma página dedicada de histórico de atendimentos por cliente, acessível apenas pelo admin. A página exibe todos os chamados daquele cliente em ordem cronológica reversa, com todos os detalhes de atendimento: diagnóstico, solução, tempo gasto e peças utilizadas — sem precisar navegar para cada chamado individualmente.

**Onde acessar:** Detalhe do cliente → botão **Histórico de Atendimentos** (ou `/clientes/<id>/historico/`)

---

## Pré-requisitos

```bash
source .venv/bin/activate
python manage.py runserver 8080
```

Usuários necessários:

| Usuário | Senha | Perfil |
|---|---|---|
| `admin` | `admin123` | Administrador |
| `tecnico1` | `senha123` | Técnico |

> Se necessário, popule o banco com `python manage.py seed`.

---

## Testes

### Teste 1 — Botão "Histórico de Atendimentos" no detalhe do cliente ✅

1. Login como **admin**
2. Acesse a lista de clientes (`/clientes/`)
3. Clique em qualquer cliente para abrir o detalhe

**Resultado esperado:**
- No cabeçalho da página de detalhe, existe o botão **Histórico de Atendimentos** (azul, contorno)
- O botão está à esquerda dos botões "Editar" e "← Voltar"

---

### Teste 2 — Página de histórico exibe cards de resumo ✅

1. Acesse o histórico de um cliente que possui chamados

**Resultado esperado:**
- Três cards no topo da página:
  - **Total de Chamados** (azul) — contagem total de chamados do cliente
  - **Resolvidos / Fechados** (verde) — chamados nos status Resolvido ou Fechado
  - **Atrasados** (vermelho) — chamados ativos com SLA vencido

---

### Teste 3 — Lista de chamados em accordion ✅

1. Na página de histórico, observe a lista de chamados

**Resultado esperado:**
- Cada chamado aparece como um item de accordion (expansível)
- O cabeçalho de cada item exibe: **#ID**, **título**, badge de **status** e **data de abertura**
- Chamados atrasados têm borda vermelha e badge **Atrasado** no cabeçalho

---

### Teste 4 — Detalhes do atendimento ao expandir ✅

1. Clique em qualquer chamado para expandir

**Resultado esperado:**
- Bloco de informações com:
  - Equipamento, Categoria, Prioridade
  - Técnico responsável (ou "Não atribuído")
  - Prazo de SLA e Tempo gasto
- Seção **Descrição do problema**
- Seção **Diagnóstico** (ou "Não registrado" se vazio)
- Seção **Solução aplicada** (ou "Não registrada" se vazio)
- Botão **Ver Chamado Completo** que leva ao detalhe do chamado

---

### Teste 5 — Chamado com peças exibe tabela de peças ✅

1. Expanda um chamado que tenha peças registradas

**Resultado esperado:**
- Tabela de peças com colunas: **Descrição**, **Qtd**, **Custo unit.**, **Total**
- Peças sem custo exibem `—` nas colunas de valor

---

### Teste 6 — Chamado sem peças exibe mensagem adequada ✅

1. Expanda um chamado sem peças registradas

**Resultado esperado:**
- Mensagem "Nenhuma peça registrada." no lugar da tabela

---

### Teste 7 — Cliente sem chamados exibe estado vazio ✅

1. Acesse o histórico de um cliente que não tem nenhum chamado

**Resultado esperado:**
- Nenhum accordion é exibido
- Mensagem "Nenhum chamado registrado para este cliente."

---

### Teste 8 — Acesso bloqueado para não-admin ✅

1. Login como **tecnico1**
2. Tente acessar diretamente `/clientes/1/historico/`

**Resultado esperado:**
- Redirecionamento para o dashboard
- Mensagem de erro: acesso negado (comportamento padrão do `@requer_perfil('admin')`)

---

### Teste 9 — Botão "← Voltar" retorna ao detalhe do cliente ✅

1. Na página de histórico, clique em **← Voltar**

**Resultado esperado:**
- Retorna à página de detalhe daquele mesmo cliente

---

## Checklist

```
[ ] Botão "Histórico de Atendimentos" visível no detalhe do cliente
[ ] Página carrega em /clientes/<id>/historico/
[ ] Cards de resumo: Total, Resolvidos/Fechados, Atrasados
[ ] Chamados listados em accordion, do mais recente ao mais antigo
[ ] Cabeçalho do accordion: ID, título, badge status, data
[ ] Chamado atrasado tem borda vermelha e badge "Atrasado"
[ ] Ao expandir: equipamento, categoria, prioridade, técnico, SLA, tempo gasto
[ ] Ao expandir: descrição, diagnóstico e solução
[ ] Chamado com peças exibe tabela de peças
[ ] Chamado sem peças exibe "Nenhuma peça registrada."
[ ] Cliente sem chamados exibe estado vazio
[ ] Técnico e cliente não conseguem acessar a página
[ ] Botão "Ver Chamado Completo" leva ao detalhe do chamado
```
