# Guia de Testes — T9: Exibição Visual do SLA

Branch: `t9-exibicao-visual-do-sla`

## O que esta task implementa

Adiciona visibilidade do SLA diretamente no dashboard. Um quarto card de contagem exibe chamados **Atrasados** (vermelho). A tabela de chamados ganha uma coluna **SLA** com badge colorido: `No prazo` (verde), `Atrasado` (vermelho) ou `Encerrado` (cinza para resolvidos e fechados). Linhas de chamados atrasados ficam com fundo vermelho claro para destaque imediato. A lógica de atraso já existia no model (`esta_atrasado`) e no detalhe — esta task expõe essas informações no painel principal.

---

## Pré-requisitos

```bash
source .venv/bin/activate
python manage.py runserver 8080
```

Para testar os cenários de atraso, é necessário um chamado cujo prazo de SLA já tenha vencido. A forma mais rápida é:

1. Criar uma **Categoria** com `sla_horas = 0` via Django admin (`/admin/`) — isso faz o prazo vencer no momento da criação.
2. Ou editar diretamente via `manage.py shell` a data de `sla_prazo` de um chamado existente para o passado.

Usuários necessários:

| Usuário | Senha | Perfil |
|---|---|---|
| `admin` | `admin123` | Administrador |

---

## Testes

### Teste 1 — Dashboard exibe 4 cards de contagem ✅

1. Login como **admin**
2. Acesse o dashboard (`http://localhost:8080/`)

**Resultado esperado:**
- Quatro cards na linha de contadores:
  - **Total de Chamados** (azul)
  - **Abertos** (amarelo)
  - **Em Atendimento** (azul claro)
  - **Atrasados** (vermelho)
- Os cards estão distribuídos em 4 colunas iguais

---

### Teste 2 — Coluna SLA na tabela de chamados ✅

1. No dashboard, observe a tabela de chamados

**Resultado esperado:**
- Tabela tem coluna **SLA** entre **Status** e **Prioridade**
- Chamados ativos dentro do prazo exibem badge verde **No prazo**
- Chamados com status `Resolvido` ou `Fechado` exibem badge cinza **Encerrado**

---

### Teste 3 — Chamado atrasado exibe badge vermelho e linha destacada ✅

1. Certifique-se de que existe um chamado ativo (Aberto, Em andamento ou Aguardando) com SLA vencido
2. Acesse o dashboard

**Resultado esperado:**
- Badge **Atrasado** (vermelho) na coluna SLA daquele chamado
- A linha inteira do chamado tem fundo vermelho claro (`table-danger`)
- O card **Atrasados** exibe contagem ≥ 1

---

### Teste 4 — Chamado resolvido/fechado não conta como atrasado ✅

1. Resolva ou feche um chamado que esteja com SLA vencido
2. Reacesse o dashboard

**Resultado esperado:**
- O contador **Atrasados** não inclui chamados resolvidos/fechados
- A linha desse chamado mostra badge **Encerrado** (cinza), não **Atrasado**
- A linha não tem fundo vermelho

---

### Teste 5 — Técnico vê SLA dos seus chamados ❌​

1. Login como **tecnico1**
2. Acesse o dashboard

**Resultado esperado:**
- A coluna SLA aparece para todos os chamados listados
- Mesma lógica de badges e destaque de linha

---

## Checklist

```
[ ] Dashboard exibe 4 cards: Total, Abertos, Em Atendimento, Atrasados
[ ] Card "Atrasados" conta apenas chamados ativos com SLA vencido
[ ] Tabela tem coluna "SLA" entre Status e Prioridade
[ ] Chamados no prazo mostram badge verde "No prazo"
[ ] Chamados com SLA vencido (e ativos) mostram badge vermelho "Atrasado"
[ ] Chamados resolvidos/fechados mostram badge cinza "Encerrado"
[ ] Linha de chamado atrasado tem fundo vermelho claro (table-danger)
```
