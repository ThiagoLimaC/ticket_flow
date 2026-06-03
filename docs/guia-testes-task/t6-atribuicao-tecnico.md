# Guia de Testes — T6: Atribuição de Técnico

Branch de origem: `t6-atribuicao-de-tecnico`

## O que esta task implementa

Permite que o admin atribua um técnico responsável a um chamado aberto. Ao atribuir, o status muda automaticamente de **Aberto** para **Em andamento** e uma movimentação é registrada. Um chamado já atribuído não pode ser reatribuído no MVP. O técnico só consegue acessar e trabalhar nos chamados vinculados a ele.

---

## Pré-requisitos

```bash
source .venv/bin/activate
python manage.py runserver 8080
```

Certifique-se de que existe ao menos um chamado com status **Aberto** e sem técnico atribuído.

Usuários necessários:

| Usuário | Senha | Perfil |
|---|---|---|
| `admin` | `admin123` | Administrador |
| `tecnico1` | `admin123` | Técnico |
| `cliente1` | `admin123` | Cliente |

---

## Testes

### Teste 1 — Botão "Atribuir Técnico" aparece apenas para admin ✅

1. Login como **admin** e acesse o detalhe de um chamado com status **Aberto**

**Resultado esperado:**
- Botão **Atribuir Técnico** visível no topo da página

2. Login como **tecnico1** e acesse o mesmo chamado (se atribuído a ele)

**Resultado esperado:**
- Botão **Atribuir Técnico** **não aparece**

---

### Teste 2 — Tela de atribuição exibe resumo do chamado ✅

1. Login como **admin**
2. No detalhe de um chamado aberto, clique em **Atribuir Técnico**

**Resultado esperado:**
- Página exibe dois cards:
  - **Resumo do Chamado**: título, cliente, equipamento, categoria, prioridade e status
  - **Selecionar Técnico**: select com os técnicos disponíveis e botão **Atribuir**

---

### Teste 3 — Atribuir técnico ao chamado ✅

1. Na tela de atribuição, selecione `tecnico1`
2. Clique em **Atribuir**

**Resultado esperado:**
- Mensagem de sucesso: `Chamado atribuído a tecnico1 com sucesso.`
- Redirecionamento para o detalhe do chamado
- Campo **Técnico** exibe `tecnico1`
- Status muda para **Em andamento** (badge azul)
- Botão **Atribuir Técnico** desaparece
- Movimentação registrada: `Aberto → Em andamento — Chamado atribuído ao técnico tecnico1.`

---

### Teste 4 — Chamado já atribuído não pode ser reatribuído ✅

1. Tente acessar `http://localhost:8080/chamados/<id>/atribuir/` de um chamado que já tem técnico

**Resultado esperado:**
- Mensagem de erro: `Este chamado já possui um técnico atribuído.`
- Redirecionamento para o detalhe do chamado

---

### Teste 5 — Somente admin pode atribuir técnico ✅

1. Login como **tecnico1**
2. Acesse `http://localhost:8080/chamados/<id>/atribuir/`

**Resultado esperado:**
- Redirecionamento para o dashboard (sem acesso)

1. Login como **cliente1**
2. Acesse `http://localhost:8080/chamados/<id>/atribuir/`

**Resultado esperado:**
- Redirecionamento para o dashboard

---

### Teste 6 — Técnico só vê chamados atribuídos a ele ✅

1. Crie dois chamados e atribua cada um a um técnico diferente (se houver dois técnicos)
   - Ou: crie um chamado e deixe sem técnico
2. Login como **tecnico1**
3. Tente acessar o detalhe de um chamado atribuído a outro técnico

**Resultado esperado:**
- Mensagem de erro: `Você não tem acesso a este chamado.`
- Redirecionamento para o dashboard

---

### Teste 7 — Chamado fechado não pode ser atribuído ✅

1. Encontre ou crie um chamado com status **Fechado**
2. Login como **admin** e acesse `http://localhost:8080/chamados/<id>/atribuir/`

**Resultado esperado:**
- Mensagem de erro: `Chamado fechado não pode ser alterado.`
- Redirecionamento para o detalhe

---

## Checklist

```
[ ] Botão "Atribuir Técnico" aparece apenas para admin em chamados abertos
[ ] Tela de atribuição exibe resumo completo do chamado
[ ] Após atribuir, status muda para "Em andamento" e técnico é exibido
[ ] Movimentação "Aberto → Em andamento" é registrada com o nome do técnico
[ ] Chamado com técnico já atribuído bloqueia nova atribuição
[ ] Técnico e cliente são redirecionados ao tentar acessar a tela de atribuição
[ ] Técnico não acessa chamados de outros técnicos
[ ] Chamado fechado bloqueia atribuição
```
