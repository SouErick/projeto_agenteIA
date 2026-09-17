# Guia: Agente de Curadoria de Questões no n8n + Supabase RAG

## Projeto

**vs-code-gaia** — Agente de Curadoria e Formatação de Problemas de Programação.

## Stack

- n8n (Docker)
- Supabase Vector
- Python
- PostgreSQL
- LLM

## Visão Geral da Arquitetura

```text
Usuário (Chat)
     │
     ▼
 n8n AI Agent Node
     │
     ├──► RAG Tool (Supabase Vector Store)
     │         │
     │         └──► base_conhecimento_agente_curadoria.json
     │                (livros, manuais, regras de maratonas)
     │
     ├──► Memory (Window Buffer / Postgres)
     │
     └──► Output → Questão formatada (MOJ Naquadah)
```