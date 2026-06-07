# Guia de Testes — T10: Painel Admin com Filtros

Branch: `t10-painel-admin-filtros`

## O que esta task implementa

Melhora o dashboard do administrador com quatro funcionalidades:

1. **Barra de filtros** — admin pode filtrar chamados por técnico, cliente, categoria e status via formulário no topo do dashboard.
2. **Coluna "Técnico"** — a tabela de chamados exibe diretamente qual técnico está atribuído a cada chamado (sem precisar clicar no detalhe).
3. **Comparativo de técnicos** — seção exclusiva do admin mostra quantos chamados cada técnico tem no total e quantos estão ativos (Em andamento / Aguardando).
4. **Correções diversas:**
   - Técnico agora vê apenas os chamados atribuídos a ele (não mais todos os chamados do sistema).
   - Botões "Novo Chamado" e "Gerenciar Clientes" agrupados lado a lado no canto direito.
   - Footer limpo: removido "TechFix Soluções 2024".

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
| `tecnico2` | `senha123` | Técnico |

> Se necessário, popule o banco com `python manage.py seed`.

---

## Testes

### Teste 1 — Filtro por técnico ✅

1. Login como **admin**
2. Acesse o dashboard (`http://localhost:8080/`)
3. No painel "Filtrar Chamados", selecione um técnico no dropdown **Técnico** e clique em **Filtrar**

**Resultado esperado:**
- A tabela exibe apenas chamados atribuídos ao técnico selecionado
- Os cards de contagem (Total, Abertos, Em Atendimento, Atrasados) refletem apenas os chamados filtrados
- A URL muda para `/?tecnico=<id>`

---

### Teste 2 — Filtro por cliente ✅

1. Login como **admin**
2. No painel de filtros, selecione um cliente e clique em **Filtrar**

**Resultado esperado:**
- Apenas chamados daquele cliente aparecem na tabela

---

### Teste 3 — Filtro por categoria ✅

1. Login como **admin**
2. No painel de filtros, selecione uma categoria e clique em **Filtrar**

**Resultado esperado:**
- Apenas chamados dessa categoria aparecem na tabela

---

### Teste 4 — Filtro por status ✅

1. Login como **admin**
2. No painel de filtros, selecione um status (ex: "Aberto") e clique em **Filtrar**

**Resultado esperado:**
- Apenas chamados com aquele status aparecem na tabela

---

### Teste 5 — Botão Limpar remove filtros ✅

1. Aplique qualquer filtro
2. Clique no botão **Limpar**

**Resultado esperado:**
- Todos os chamados voltam a ser exibidos
- O formulário de filtros está vazio

---

### Teste 6 — Coluna "Técnico" na tabela (admin) ✅

1. Login como **admin**
2. Observe a tabela de chamados

**Resultado esperado:**
- Tabela tem coluna **Técnico** entre **SLA** e **Prioridade**
- Chamados atribuídos exibem o username do técnico
- Chamados sem técnico exibem `—`

---

### Teste 7 — Comparativo de técnicos ✅

1. Login como **admin**
2. Role a página abaixo da tabela principal

**Resultado esperado:**
- Seção **Comparativo de Técnicos** com tabela listando todos os técnicos cadastrados
- Coluna **Total de Chamados**: quantidade total de chamados atribuídos a cada técnico (clicável — aplica filtro)
- Coluna **Em Atendimento / Aguardando**: chamados ativos daquele técnico (badge amarelo se > 0, cinza se 0)
- Tabela ordenada do técnico com mais chamados para o com menos

---

### Teste 8 — Técnico vê apenas seus próprios chamados ✅

1. Login como **tecnico1**
2. Acesse o dashboard

**Resultado esperado:**
- A tabela exibe apenas chamados atribuídos a `tecnico1`
- Os cards de contagem refletem apenas os chamados de `tecnico1`
- Chamados de outros técnicos não aparecem

---

### Teste 9 — Técnico não vê barra de filtros nem comparativo ✅

1. Login como **tecnico1**
2. Observe o dashboard

**Resultado esperado:**
- Nenhum painel de filtros é exibido
- Nenhuma seção "Comparativo de Técnicos" é exibida
- Coluna "Técnico" não aparece na tabela

---

### Teste 10 — Botões "Novo Chamado" e "Gerenciar Clientes" agrupados ✅

1. Login como **admin**
2. Observe o cabeçalho do dashboard

**Resultado esperado:**
- Os dois botões estão lado a lado no canto direito
- "Novo Chamado" (azul) e "Gerenciar Clientes" (contorno cinza) separados por pequeno espaço

---

### Teste 11 — Footer sem "TechFix Soluções" ✅

1. Em qualquer página do sistema, observe o rodapé

**Resultado esperado:**
- Footer exibe apenas `TicketFlow © 2024` (sem "TechFix Soluções")

---

## Checklist

```
[ ] Barra de filtros aparece apenas para admin
[ ] Filtro por técnico funciona e reflete nos cards
[ ] Filtro por cliente funciona
[ ] Filtro por categoria funciona
[ ] Filtro por status funciona
[ ] Botão "Limpar" remove todos os filtros
[ ] Coluna "Técnico" aparece na tabela para admin
[ ] Chamado sem técnico exibe "—" na coluna técnico
[ ] Seção comparativo de técnicos aparece para admin
[ ] Comparativo lista total e ativos por técnico
[ ] Técnico vê apenas seus próprios chamados no dashboard
[ ] Técnico não vê barra de filtros nem comparativo
[ ] Botões "Novo Chamado" e "Gerenciar Clientes" agrupados à direita
[ ] Footer exibe apenas "TicketFlow © 2024"
```
