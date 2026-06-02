# Guia de Testes — T2: Django Admin

Branch de origem: `main`

## O que esta task implementa

Configura o painel administrativo do Django (`/admin`) com todos os modelos do sistema registrados e customizados. O admin permite que o superusuário gerencie diretamente Chamados, Categorias, Empresas Clientes, Equipamentos, Perfis, Movimentações e Peças Utilizadas. Movimentações são registradas como somente leitura por design — não é possível editá-las nem deletá-las pelo painel.

---

## Pré-requisitos

```bash
source .venv/bin/activate
python manage.py runserver 8080
```

Acesse `http://localhost:8080/admin` e faça login com o usuário **admin** / `admin123`.

---

## Testes

### Teste 1 — Acesso ao painel administrativo ✅

1. Acesse `http://localhost:8080/admin`
2. Faça login com `admin` / `admin123`

**Resultado esperado:**
- Painel do Django Admin carrega normalmente
- Usuário comum (técnico ou cliente) que tente acessar `/admin` deve receber erro 403 ou ser redirecionado para o login do admin

---

### Teste 2 — Modelos registrados no admin ✅

No painel, verifique se todos os modelos estão listados:

**App `core`:**
- Chamados
- Categorias
- Empresas Clientes
- Equipamentos
- Movimentações
- Peças Utilizadas

**App `usuarios`:**
- Perfis

**Resultado esperado:** todos os modelos acima aparecem no painel.

---

### Teste 3 — CRUD de Categoria via admin ✅

1. Clique em **Categorias → Adicionar**
2. Preencha: nome `"Rede"`, SLA `4` horas
3. Salve

**Resultado esperado:**
- Categoria aparece na lista com descrição `Rede (SLA: 4h)`

---

### Teste 4 — Movimentações são somente leitura ✅

1. Clique em **Movimentações**
2. Clique em qualquer movimentação existente

**Resultado esperado:**
- Não existe botão "Salvar" nem campos editáveis — movimentações são imutáveis por design

---

### Teste 5 — Perfil vinculado ao usuário ✅

1. Clique em **Perfis**
2. Abra o perfil de `cliente1`

**Resultado esperado:**
- Campo **Tipo** mostra `Cliente`
- Campo **Empresa** mostra `Empresa Teste`

---

## Checklist

```
[ ] Painel admin acessível para superusuário
[ ] Todos os modelos do core e usuarios aparecem listados
[ ] É possível criar/editar Categorias via admin
[ ] Movimentações não têm botão de salvar (somente leitura)
[ ] Perfil de cliente exibe empresa vinculada
```
