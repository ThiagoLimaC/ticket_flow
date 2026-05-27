# Guia de Testes — T5: Abertura de Chamado

Branch de origem: `t5-abertura-de-chamado`

## O que esta task implementa

Permite que admins e clientes abram chamados de suporte. O formulário coleta título, descrição, categoria, prioridade e equipamento. O cliente só enxerga os equipamentos da sua própria empresa. O prazo de SLA é calculado automaticamente no momento da criação (`data_abertura + categoria.sla_horas`). Técnicos são bloqueados de abrir chamados. A primeira movimentação (`Aberto → Aberto`) é registrada automaticamente ao criar o chamado.

---

## Pré-requisitos

```bash
source .venv/bin/activate
python manage.py runserver 8080
```

Certifique-se de que existe pelo menos:
- Uma **Categoria** cadastrada (ex: `Hardware`)
- Uma **Empresa** com ao menos um **Equipamento** cadastrado
- O usuário **cliente1** com o campo **Empresa** vinculado no perfil

Usuários necessários:

| Usuário | Senha | Perfil |
|---|---|---|
| `admin` | `admin123` | Administrador |
| `tecnico1` | `admin123` | Técnico |
| `cliente1` | `admin123` | Cliente |

---

## Testes

### Teste 1 — Admin abre um chamado

1. Login como **admin**
2. Clique em **Novo Chamado**
3. Preencha:
   - Título: `Impressora não imprime`
   - Descrição: `Impressora do RH parou de funcionar após atualização`
   - Categoria: `Hardware`
   - Prioridade: `Alta`
   - Equipamento: qualquer um da lista
4. Clique em **Abrir Chamado**

**Resultado esperado:**
- Redirecionamento para o detalhe do chamado recém-criado
- Mensagem de sucesso: `Chamado #X aberto com sucesso.`
- Status exibido como **Aberto** (badge amarelo)
- Campo **SLA** exibe prazo calculado e badge **No prazo**
- Histórico de movimentações exibe: `Aberto → Aberto — Chamado aberto.`

---

### Teste 2 — Cliente abre um chamado

1. Login como **cliente1**
2. Clique em **Novo Chamado**
3. Observe o campo **Equipamento**

**Resultado esperado:**
- Select de **Equipamento** lista apenas os equipamentos da empresa do `cliente1`
- Não aparecem equipamentos de outras empresas

4. Preencha o formulário normalmente e clique em **Abrir Chamado**

**Resultado esperado:**
- Chamado criado com sucesso
- Cliente é redirecionado para o detalhe do próprio chamado

---

### Teste 3 — Cliente sem empresa associada não consegue abrir chamado

1. Crie um usuário cliente sem empresa vinculada no admin Django
2. Login com esse usuário
3. Acesse **Novo Chamado**

**Resultado esperado:**
- Select de **Equipamento** aparece vazio (sem opções além do traço)
- Formulário não pode ser submetido sem equipamento selecionado

---

### Teste 4 — Técnico não pode abrir chamado

1. Login como **tecnico1**
2. Clique em **Novo Chamado** (se visível) ou acesse `http://localhost:8080/chamados/abrir/`

**Resultado esperado:**
- Mensagem de erro: `Técnicos não podem abrir chamados.`
- Redirecionamento para o dashboard
- Botão **Novo Chamado** não aparece na navbar do técnico

---

### Teste 5 — SLA calculado automaticamente

1. Abra um chamado com a categoria **Hardware** (SLA: 8h)
2. Acesse o detalhe do chamado criado

**Resultado esperado:**
- Campo SLA exibe o prazo: `data de abertura + 8 horas`
- Badge **No prazo** (verde) aparece se ainda dentro do prazo

---

### Teste 6 — Campos obrigatórios

1. Acesse **Novo Chamado** como admin
2. Clique em **Abrir Chamado** sem preencher nenhum campo

**Resultado esperado:**
- Formulário não é submetido
- Mensagens de erro em todos os campos obrigatórios (título, descrição, categoria, equipamento)

---

### Teste 7 — Cliente só vê seus próprios chamados

1. Abra um chamado como **admin**
2. Login como **cliente1**
3. Verifique o dashboard

**Resultado esperado:**
- O chamado do admin **não aparece** na lista do cliente1
- Tentativa de acessar `http://localhost:8080/chamados/<id_do_admin>/` redireciona para o dashboard com mensagem de erro

---

## Checklist

```
[ ] Admin consegue abrir chamado com todos os campos
[ ] Cliente consegue abrir chamado e vê apenas equipamentos da sua empresa
[ ] Cliente sem empresa vê select de equipamento vazio
[ ] Técnico é bloqueado ao tentar abrir chamado
[ ] SLA é calculado automaticamente com base na categoria
[ ] Campos obrigatórios são validados no formulário
[ ] Cliente não acessa chamados de outros usuários
[ ] Movimentação "Aberto → Aberto" é criada ao abrir o chamado
```
