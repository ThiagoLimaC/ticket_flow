# Guia de Testes — T8: Registro de Diagnóstico e Peças

Branch: `t8-registro-diagnostico-pecas`

## O que esta task implementa

Permite que técnicos e admins registrem o atendimento realizado em um chamado: diagnóstico do problema, solução aplicada, tempo gasto em horas e peças utilizadas (descrição, quantidade e custo unitário). O registro só é possível enquanto o chamado estiver em andamento ou aguardando. Não há controle de estoque — é apenas um registro descritivo.

---

## Pré-requisitos

```bash
source .venv/bin/activate
python manage.py runserver 8080
```

Certifique-se de ter um chamado com status **Em andamento** atribuído ao `tecnico1`.

Usuários necessários:

| Usuário | Senha | Perfil |
|---|---|---|
| `admin` | `admin123` | Administrador |
| `tecnico1` | `admin123` | Técnico |
| `cliente1` | `admin123` | Cliente |

---

## Testes

### Teste 1 — Cards de registro aparecem no detalhe do chamado ✅

1. Login como **tecnico1**
2. Acesse o detalhe de um chamado **Em andamento** atribuído a você

**Resultado esperado:**
- Card **Registro de Atendimento** visível com campos:
  - Diagnóstico (textarea)
  - Solução aplicada (textarea)
  - Tempo gasto em horas (campo numérico com placeholder `Ex: 1.5`)
  - Botão **Salvar atendimento**
- Card **Peças Utilizadas** visível com formulário de adição inline:
  - Descrição, Qtd. e Custo unitário (R$)
  - Botão **Adicionar**

---

### Teste 2 — Técnico registra diagnóstico e solução ✅

1. No card **Registro de Atendimento**, preencha:
   - Diagnóstico: `Fonte do computador queimada`
   - Solução aplicada: `Substituição da fonte de alimentação`
   - Tempo gasto: `2.5`
2. Clique em **Salvar atendimento**

**Resultado esperado:**
- Mensagem de sucesso: `Atendimento registrado com sucesso.`
- Os textos preenchidos aparecem na seção **Diagnóstico** e **Solução** do card "Dados do Chamado"
- O form volta pré-preenchido com os valores salvos para edição futura

---

### Teste 3 — Técnico atualiza o diagnóstico (sobrescreve) ✅

1. Com o diagnóstico já salvo, altere o campo **Diagnóstico** para `Fonte e placa-mãe danificadas`
2. Clique em **Salvar atendimento**

**Resultado esperado:**
- Mensagem de sucesso
- O card "Dados do Chamado" exibe o novo diagnóstico
- O valor anterior foi substituído (não acumula)

---

### Teste 4 — Técnico adiciona peças ✅

1. No form **Adicionar peça**, preencha:
   - Descrição: `Fonte ATX 500W`
   - Qtd.: `1`
   - Custo unitário: `189.90`
2. Clique em **Adicionar**

**Resultado esperado:**
- Mensagem de sucesso: `Peça "Fonte ATX 500W" adicionada com sucesso.`
- Peça aparece na tabela do card **Peças Utilizadas** com custo `R$ 189.90`

3. Adicione uma segunda peça sem custo unitário:
   - Descrição: `Cabo de força`
   - Qtd.: `2`
   - Custo unitário: (vazio)

**Resultado esperado:**
- Peça adicionada com custo exibido como `—`

---

### Teste 5 — Peças acumulam na tabela ✅

1. Adicione mais de uma peça ao mesmo chamado

**Resultado esperado:**
- Todas as peças aparecem listadas na tabela, uma por linha
- Peças já adicionadas não desaparecem ao adicionar novas

---

### Teste 6 — Campos obrigatórios do form de peça ✅

1. Tente adicionar uma peça sem preencher a **Descrição**

**Resultado esperado:**
- Mensagem de erro: `Erro ao adicionar peça. Verifique os campos.`
- Nenhuma peça é criada

---

### Teste 7 — Status "Aguardando" também permite registro ✅

1. No card **Alterar Status**, mude o chamado para **Aguardando**
2. Tente salvar o atendimento e adicionar uma peça

**Resultado esperado:**
- Card **Registro de Atendimento** e form de peças continuam visíveis
- Operações funcionam normalmente

---

### Teste 8 — Chamado resolvido bloqueia registro ✅

1. Mude o status do chamado para **Resolvido**
2. Verifique a página de detalhe

**Resultado esperado:**
- Card **Registro de Atendimento** **não aparece**
- Form de **Adicionar peça** **não aparece**
- Tentativa via URL direta (`/chamados/<id>/atendimento/`) retorna erro: `Ação não permitida.`

---

### Teste 9 — Cliente não pode registrar ✅

1. Login como **cliente1**
2. Acesse o detalhe de um chamado da empresa dele

**Resultado esperado:**
- Cards de registro e peças **não aparecem**
- Tentativa via URL (`/chamados/<id>/pecas/`) retorna erro: `Ação não permitida.`

---

### Teste 10 — Técnico não registra em chamado de outro técnico ✅

1. Login como **tecnico1**
2. Acesse via URL direta `/chamados/<id>/atendimento/` de um chamado atribuído a outro técnico

**Resultado esperado:**
- Mensagem de erro: `Ação não permitida.`
- Redirecionamento para o detalhe do chamado

---

### Teste 11 — Admin pode registrar em qualquer chamado ativo ✅

1. Login como **admin**
2. Acesse o detalhe de um chamado **Em andamento**

**Resultado esperado:**
- Cards de **Registro de Atendimento** e **Peças Utilizadas** aparecem normalmente
- Admin consegue salvar diagnóstico e adicionar peças

---

## Checklist

```
[ ] Card "Registro de Atendimento" aparece para técnico e admin em chamados em_andamento/aguardando
[ ] Diagnóstico, solução e tempo gasto são salvos corretamente
[ ] Form volta pré-preenchido com os valores já salvos
[ ] Peças são adicionadas e acumulam na tabela
[ ] Custo unitário é opcional (exibe "—" quando vazio)
[ ] Descrição da peça é obrigatória
[ ] Status "Aguardando" também permite registro
[ ] Chamado resolvido ou fechado oculta os cards de registro
[ ] Cliente não vê os cards e é bloqueado via URL
[ ] Técnico não registra em chamado de outro técnico
[ ] Admin pode registrar em qualquer chamado ativo
```
