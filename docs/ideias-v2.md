# Ideias e Dívidas Técnicas — v2

Items registrados durante o desenvolvimento do MVP para endereçar futuramente.

---

## DT01 — Ligação entre Perfil e EmpresaCliente

**Contexto:** Atualmente não existe vínculo direto entre o `User` que faz login
e a `EmpresaCliente` que ele representa. A view de abertura de chamado contorna
isso filtrando por `cliente__chamados__aberto_por=usuario`, o que falha para
clientes novos sem chamados anteriores.

**Solução proposta:** Adicionar `empresa = ForeignKey(EmpresaCliente, null=True,
blank=True)` ao model `Perfil`. Admin associa o User à empresa no cadastro.
Filtro de equipamentos passa a usar `request.user.perfil.empresa`.

**Impacto:** migration em `usuarios`, ajuste no `PerfilAdmin`, ajuste na
view `abrir_chamado` e no `AbrirChamadoForm`.