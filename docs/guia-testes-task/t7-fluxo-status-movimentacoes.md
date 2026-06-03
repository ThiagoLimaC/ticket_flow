# Guia de Testes — T7: Fluxo de Status e Movimentações

Branch: `t7-fluxo-status-movimentacoes`

## O que esta task implementa

Implementa o fluxo completo de mudança de status dos chamados com registro automático de movimentações. Técnicos podem mover seus chamados entre `Em andamento`, `Aguardando` e `Resolvido`. Apenas o admin pode fechar (`Resolvido → Fechado`) ou reabrir (`Resolvido → Aberto`) um chamado. Ao reabrir, o técnico responsável é desvinculado automaticamente para permitir nova atribuição. Chamados fechados são imutáveis. Um card inline no detalhe exibe apenas as transições válidas para o perfil e status atual.

---

## Pré-requisitos

Servidor rodando e banco com os dados de teste criados.

```bash
source .venv/bin/activate
python manage.py runserver 8080
```

Usuários necessários:

| Usuário | Senha | Perfil |
|---|---|---|
| `admin` | `admin123` | Administrador |
| `tecnico1` | `admin123` | Técnico |
| `cliente1` | `admin123` | Cliente |

---

## Preparação: criar um chamado de teste

1. Acesse `http://localhost:8080` e faça login como **admin**
2. Clique em **Novo Chamado** e preencha qualquer título/descrição
3. Selecione a categoria **Hardware** e um equipamento
4. Clique em **Abrir Chamado** — anote o número do chamado criado (ex: #7)
5. No detalhe do chamado, clique em **Atribuir Técnico** e selecione `tecnico1`
6. O status agora deve ser **Em andamento**

---

## Testes

### Teste 1 — Técnico vê o card "Alterar Status" ✅

1. Faça logout e login como **tecnico1**
2. Acesse o detalhe do chamado criado na preparação
3. Role até o final da página

**Resultado esperado:**
- Card **Alterar Status** visível
- Select com as opções: **Aguardando** e **Resolvido** (apenas essas duas)
- Campo de comentário opcional
- Botão **Confirmar**

---

### Teste 2 — Técnico: Em andamento → Aguardando ✅

1. Como **tecnico1**, no card "Alterar Status":
   - Selecione **Aguardando**
   - Digite um comentário: `"Aguardando chegada da peça"`
   - Clique em **Confirmar**

**Resultado esperado:**
- Mensagem de sucesso: `Status atualizado para "Aguardando"`
- Badge no topo do card muda para **Aguardando** (cinza)
- Nova movimentação aparece no histórico: `Em andamento → Aguardando` com o comentário

---

### Teste 3 — Técnico: Aguardando → Resolvido ✅

1. Como **tecnico1**, selecione **Resolvido** e clique em **Confirmar**

**Resultado esperado:**
- Mensagem de sucesso: `Status atualizado para "Resolvido"`
- Badge muda para **Resolvido** (verde)
- Card "Alterar Status" **desaparece** (técnico não tem mais transições disponíveis)
- Movimentação registrada: `Aguardando → Resolvido`

---

### Teste 4 — Técnico não pode fechar nem reabrir ✅

1. Ainda como **tecnico1**, tente acessar diretamente via URL:
   `http://localhost:8080/chamados/<id>/status/`
   com os dados `novo_status=fechado` (via formulário ou curl)

**Resultado esperado:**
- Mensagem de erro: `Transição de status inválida.`
- O chamado permanece com status **Resolvido**

---

### Teste 5 — Admin: Resolvido → Aberto (reabrir) ✅

1. Faça logout e login como **admin**
2. Acesse o chamado (agora resolvido)
3. No card "Alterar Status", as opções disponíveis devem ser **Fechado** e **Aberto**
4. Selecione **Aberto** com comentário: `"Reaberto para revisão"`

**Resultado esperado:**
- Mensagem de sucesso: `Status atualizado para "Aberto"`
- Badge muda para **Aberto** (amarelo)
- Campo **Técnico** no card de dados mostra **Não atribuído** — o técnico foi liberado automaticamente ao reabrir
- Card "Alterar Status" desaparece (status "aberto" volta pelo fluxo de atribuição)
- Botão **Atribuir Técnico** reaparece no topo da página

---

### Teste 6 — Admin: Resolvido → Fechado ✅

1. Re-atribua o técnico (`tecnico1`) ao chamado reaberto
2. Login como **tecnico1** e mude o status para **Resolvido**
3. Login como **admin** e selecione **Fechado**

**Resultado esperado:**
- Mensagem de sucesso: `Status atualizado para "Fechado"`
- Badge muda para **Fechado** (preto)
- Card "Alterar Status" **não aparece** — chamado fechado é imutável

---

### Teste 7 — Chamado fechado é imutável

1. Com o chamado no status **Fechado**, tente acessar:
   `http://localhost:8080/chamados/<id>/status/`

**Resultado esperado:**
- Mensagem de erro: `Chamado fechado não pode ser alterado.`
- Redirecionamento para o detalhe do chamado

---

### Teste 8 — Cliente não vê o card e não pode alterar status ✅

1. Faça login como **cliente1**
2. Abra um chamado (Novo Chamado)
3. Acesse o detalhe do chamado criado

**Resultado esperado:**
- Card "Alterar Status" **não aparece**
- Tentativa direta via URL `/chamados/<id>/status/` redireciona com mensagem de erro: `Você não tem permissão para alterar o status de um chamado.`

---

### Teste 9 — Histórico completo de movimentações ✅

Após executar os testes acima, verifique o histórico de movimentações no detalhe do chamado.

**Resultado esperado** (sequência completa de um ciclo fechado):

```
Aberto       → Aberto         (abertura)
Aberto       → Em andamento   (atribuição do técnico)
Em andamento → Aguardando     (técnico aguardando peça)
Aguardando   → Resolvido      (técnico resolveu)
Resolvido    → Aberto         (admin reabriu)
Aberto       → Em andamento   (re-atribuição)
Em andamento → Resolvido      (técnico resolveu novamente)
Resolvido    → Fechado        (admin fechou)
```

Cada movimentação deve exibir: **data/hora**, **usuário responsável** e **comentário** (quando preenchido).

---

## Checklist

```
[ ] Card "Alterar Status" aparece para técnico e admin em chamados ativos
[ ] Técnico vê apenas "Aguardando" e "Resolvido" como opções
[ ] Admin vê "Fechado" e "Aberto" quando chamado está resolvido
[ ] Movimentação é criada a cada mudança de status
[ ] Ao reabrir, técnico é desvinculado e botão "Atribuir Técnico" reaparece
[ ] Chamado fechado não exibe o card e bloqueia tentativas via URL
[ ] Cliente não vê o card e é bloqueado via URL
[ ] Comentário opcional aparece em cada movimentação do histórico
```
