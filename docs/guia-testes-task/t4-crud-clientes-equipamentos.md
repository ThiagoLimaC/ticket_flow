# Guia de Testes — T4: CRUD de Clientes e Equipamentos

Branch de origem: `t4-crud-clientes`

## O que esta task implementa

Cria o fluxo completo de cadastro e edição de **Empresas Clientes** e seus **Equipamentos**, acessível somente pelo perfil Admin. Cada empresa pode ter múltiplos equipamentos vinculados (tipo, modelo, número de série e localização). O detalhe da empresa lista todos os equipamentos cadastrados. Ao criar um equipamento a partir do detalhe de um cliente, o campo cliente vem pré-selecionado automaticamente.

---

## Pré-requisitos

```bash
source .venv/bin/activate
python manage.py runserver 8080
```

Todos os testes desta task exigem login como **admin** (`admin123`).

---

## Testes — Clientes

### Teste 1 — Listar clientes ✅

1. Login como **admin**
2. No dashboard, clique em **Gerenciar Clientes**

**Resultado esperado:**
- Tabela com os clientes cadastrados
- Botão **Novo Cliente** no topo
- Cada linha tem link para o detalhe

---

### Teste 2 — Criar novo cliente ✅

1. Clique em **Novo Cliente**
2. Preencha:
   - Nome: `Construtora ABC`
   - CNPJ: `98.765.432/0001-10`
   - Contato: `Maria Silva`
   - Telefone: `(11) 99999-0000`
   - Endereço: `Rua das Flores, 100`
3. Clique em **Salvar**

**Resultado esperado:**
- Mensagem de sucesso: `Cliente cadastrado com sucesso.`
- Redirecionamento para o detalhe da empresa criada
- Dados exibidos corretamente

---

### Teste 3 — Editar cliente ✅

1. Na lista de clientes, acesse o detalhe de qualquer cliente
2. Clique em **Editar**
3. Altere o campo **Contato**
4. Salve

**Resultado esperado:**
- Mensagem de sucesso: `Cliente atualizado com sucesso.`
- Novo valor do contato aparece no detalhe

---

### Teste 4 — Criar cliente com CNPJ duplicado ✅

1. Tente cadastrar um novo cliente com o mesmo CNPJ de um já existente

**Resultado esperado:**
- Formulário não é submetido
- Mensagem de erro de validação no campo CNPJ

---

### Teste 5 — Técnico e cliente não têm acesso ao CRUD ✅

1. Login como **tecnico1**
2. Acesse `http://localhost:8080/clientes/novo/`

**Resultado esperado:** redirecionamento para o dashboard

---

## Testes — Equipamentos

### Teste 6 — Criar equipamento para um cliente ✅

1. Acesse o detalhe de um cliente (ex: `Empresa Teste`)
2. Clique em **Novo Equipamento**
3. Preencha:
   - Tipo: `Servidor`
   - Modelo: `HP ProLiant DL380`
   - Número de série: `SRV-002`
   - Localização: `Sala de TI`
4. Clique em **Salvar**

**Resultado esperado:**
- Mensagem de sucesso: `Equipamento cadastrado com sucesso.`
- Redirecionamento para o detalhe do cliente
- Equipamento aparece na lista de equipamentos do cliente

---

### Teste 7 — Editar equipamento ✅

1. No detalhe do cliente, clique em **Editar** ao lado do equipamento
2. Altere a **Localização**
3. Salve

**Resultado esperado:**
- Mensagem de sucesso: `Equipamento atualizado com sucesso.`
- Novo valor da localização aparece no detalhe do cliente

---

### Teste 8 — Equipamento pré-selecionado ao criar pelo detalhe do cliente ✅

1. Acesse o detalhe de um cliente específico
2. Clique em **Novo Equipamento**
3. Observe o campo **Cliente** no formulário

**Resultado esperado:**
- Campo **Cliente** já vem pré-selecionado com o cliente da página atual

---

## Checklist

```
[ ] Admin consegue listar, criar e editar clientes
[ ] CNPJ duplicado é rejeitado com mensagem de erro
[ ] Técnico e cliente são redirecionados ao tentar acessar /clientes/
[ ] Admin consegue criar e editar equipamentos a partir do detalhe do cliente
[ ] Ao criar equipamento via detalhe do cliente, o campo cliente vem pré-selecionado
[ ] Equipamento aparece na lista do cliente após ser criado
```
