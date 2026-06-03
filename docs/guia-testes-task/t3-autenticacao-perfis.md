# Guia de Testes — T3: Autenticação e Perfis

Branch de origem: `main`

## O que esta task implementa

Implementa o sistema de autenticação (login/logout) e o model `Perfil`, que estende o `User` do Django com três tipos de acesso: **Admin**, **Técnico** e **Cliente**. Um signal `post_save` cria automaticamente o perfil toda vez que um novo usuário é cadastrado. O perfil do cliente pode ser vinculado a uma `EmpresaCliente`. Cada tipo de perfil enxerga uma interface diferente e tem acesso restrito a certas funcionalidades via decorator `@requer_perfil`.

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
| `tecnico1` | `admin123` | Técnico |
| `cliente1` | `admin123` | Cliente |

---

## Testes

### Teste 1 — Acesso sem autenticação redireciona para login ✅

1. Sem estar logado, acesse `http://localhost:8080`

**Resultado esperado:**
- Redirecionamento para `http://localhost:8080/accounts/login/?next=/`
- Página de login exibida

---

### Teste 2 — Login com credenciais corretas ✅

1. Acesse `http://localhost:8080/accounts/login/`
2. Preencha `admin` / `admin123` e clique em **Entrar**

**Resultado esperado:**
- Redirecionamento para o dashboard (`/`)
- Navbar exibe `Olá, admin` e botão **Sair**

---

### Teste 3 — Login com credenciais erradas ✅

1. Na tela de login, preencha `admin` / `senhaerrada`
2. Clique em **Entrar**

**Resultado esperado:**
- Permanece na tela de login
- Mensagem de erro sobre credenciais inválidas

---

### Teste 4 — Logout ✅

1. Logado como qualquer usuário, clique em **Sair**

**Resultado esperado:**
- Sessão encerrada
- Redirecionamento para a tela de login
- Tentar acessar `/` novamente redireciona para login

---

### Teste 5 — Navbar por perfil ✅

Verifique o que aparece na navbar para cada perfil:

**Admin:**
- Links: **Chamados** e **Admin**
- Botões no dashboard: **Novo Chamado** e **Gerenciar Clientes**

**Técnico:**
- Links: **Chamados** (sem link Admin)
- Dashboard: sem botão **Novo Chamado** e sem **Gerenciar Clientes**

**Cliente:**
- Links: **Chamados** (sem link Admin)
- Dashboard: botão **Novo Chamado** visível

---

### Teste 6 — Restrição de acesso por perfil ✅

**Técnico tentando acessar área de admin:**

1. Login como `tecnico1`
2. Acesse `http://localhost:8080/clientes/`

**Resultado esperado:** redirecionamento para o dashboard (sem mensagem de erro, acesso simplesmente negado)

**Cliente tentando acessar área de admin:** ✅

1. Login como `cliente1`
2. Acesse `http://localhost:8080/clientes/`

**Resultado esperado:** redirecionamento para o dashboard

---

### Teste 7 — Cada usuário vê apenas seus chamados ✅

1. Login como **admin** → crie um chamado
2. Login como **cliente1** → acesse o dashboard

**Resultado esperado:**
- Cliente vê apenas os chamados abertos por ele ✅
- Não aparece o chamado do admin na lista do cliente ✅

---

## Checklist

```
[ ] Acesso sem login redireciona para a tela de login
[ ] Login com credenciais corretas leva ao dashboard
[ ] Login com credenciais erradas exibe mensagem de erro
[ ] Logout encerra a sessão e redireciona para login
[ ] Navbar exibe links corretos para cada perfil
[ ] Técnico e cliente não conseguem acessar /clientes/
[ ] Cliente vê apenas seus próprios chamados no dashboard
```
