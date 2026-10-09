# Agente GAIA de Curadoria e Formatação de Questões

![Status](https://img.shields.io/badge/Status-Em%20Desenvolvimento-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![n8n](https://img.shields.io/badge/n8n-Workflow%20Automation-orange)

O **GAIA** é um agente de Inteligência Artificial para curadoria, validação e formatação de problemas de programação competitiva. O projeto combina **n8n**, **RAG (Retrieval-Augmented Generation)**, **Supabase Vector**, **PostgreSQL**, **Python** e **LLMs** para transformar um tema ou requisito acadêmico em uma questão estruturada, verificável e adequada a plataformas como o MOJ Naquadah.

> O RAG fornece contexto e referências. A validação algorítmica, a execução dos códigos e a revisão humana continuam sendo necessárias.

---

## 🚀 Acesso ao Agente (Avaliação II — Webhook)

O agente está disponível como serviço HTTP no **n8n Cloud**:

| | |
|---|---|
| **Workflow n8n Cloud** | [gaia123.app.n8n.cloud](https://gaia123.app.n8n.cloud/workflow/r6V1YhwN2HrIh85H) |
| **Endpoint principal** | `POST https://gaia123.app.n8n.cloud/webhook/gaia/chat` |
| **Documentação da API** | [`docs/API_GAIA.md`](docs/API_GAIA.md) |
| **Workflow exportado** | [`n8n/workflows/gaia_webhook.json`](n8n/workflows/gaia_webhook.json) |

### Exemplo rápido

```bash
curl -X POST https://gaia123.app.n8n.cloud/webhook/gaia/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Formate um problema de busca binária nível Médio para o MOJ Naquadah",
    "session_id": "minha-sessao-001",
    "operation": "formatar"
  }'
```

```json
{
  "response": "## Problema\n\n### Metadados\n- Título: Busca no Vetor Ordenado\n...",
  "session_id": "minha-sessao-001",
  "operation": "formatar",
  "status": "success",
  "timestamp": "2026-10-09T15:00:00.000Z"
}
```

### Operações disponíveis

| `operation`          | O que faz                                              |
|----------------------|--------------------------------------------------------|
| `chat` *(padrão)*    | Conversa geral com o agente                            |
| `curar`              | Fase 1 — curadoria de problemas por tema/dificuldade   |
| `formatar`           | Fase 2 — formatação completa para o MOJ Naquadah       |
| `buscar_problemas`   | Busca problemas existentes na API do MOJ por tag       |
| `health`             | Verifica se o serviço está disponível                  |

---

## Objetivos

- Criar questões claras e adequadas ao público-alvo.
- Pesquisar referências técnicas em uma base documental curada.
- Avaliar dificuldade, algoritmo, complexidade temporal e complexidade espacial.
- Validar a coerência entre enunciado, entrada, saída, restrições, exemplos e testes.
- Gerar soluções de referência em Python e, quando necessário, soluções deliberadamente ineficientes para análise de desempenho.
- Registrar questões, metadados, validações, alertas e limitações para permitir rastreabilidade e revisão.

---

## Arquitetura

### Avaliação II — Webhook (atual)

```text
Aplicação (web / mobile / CLI)
   |
   | HTTP POST /webhook/gaia/chat
   v
Webhook n8n Cloud
   |
   v
Rotear Operação (Switch)
   |
   +--[chat / curar / formatar]--> AI Agent
   |                                  +--> LLM (GPT-4o mini)
   |                                  +--> Memória (session_id)
   |                                  +--> RAG (Supabase Vector)
   |                                           |
   |                                           v
   |                                    Base de conhecimento
   |                                    (20 documentos técnicos)
   |
   +--[buscar_problemas]-----------> HTTP Request
                                         |
                                         v
                                    MOJ Naquadah API
                                    /api/v1/treino/contest-create/draw
   |
   v
Respond to Webhook
   |
   | JSON { response, session_id, status, timestamp }
   v
Aplicação
```

### Avaliação I — Local com Docker (referência)

```text
Usuário
   |
   v
Chat Trigger (n8n local :5678)
   |
   v
AI Agent
   +--> LLM
   +--> Memória
   +--> Ferramenta RAG
   |       |
   |       v
   |   Supabase Vector / pgvector
   |       |
   |       v
   |   Base de conhecimento
   |
   v
Curadoria e formatação
   +--> Validação estrutural
   +--> Validação do código Python
   +--> Geração de casos de teste
   |
   v
Saída estruturada
   +--> Exibição ao usuário
   +--> Persistência no PostgreSQL
```

### Componentes

| Componente | Responsabilidade |
|---|---|
| n8n Cloud | Orquestrar entrada, IA, RAG, MOJ API e resposta HTTP. |
| Webhook | Expor o agente como serviço HTTP consumível por qualquer aplicação. |
| AI Agent | Interpretar solicitações e coordenar ferramentas. |
| LLM (GPT-4o mini) | Gerar, analisar e revisar conteúdos. |
| Supabase Vector | Armazenar documentos, embeddings e dados relacionados. |
| pgvector / HNSW | Realizar busca por similaridade vetorial (1536 dims). |
| MOJ Naquadah API | Buscar problemas existentes por tag e dificuldade. |
| Python | Ingestão da base de conhecimento e validadores. |
| Docker | Execução reprodutível dos serviços (Avaliação I). |

---

## Pipeline de curadoria

1. **Interpretação:** extrair tema, subtema, dificuldade, público-alvo, linguagem e restrições.
2. **Pesquisa no RAG:** recuperar definições, algoritmos, complexidades, referências e armadilhas de implementação.
3. **Análise técnica:** verificar algoritmo, limites de entrada, uso de memória, casos degenerados e viabilidade em Python.
4. **Formatação:** produzir título, enunciado, entrada, saída, restrições, exemplos, explicação, solução e complexidade.
5. **Validação:** executar validações estruturais, semânticas, de código e de testes, mantendo a revisão humana como etapa final.

---

## Funcionalidades

### Curadoria

- Identificação do tópico algorítmico e do nível de dificuldade.
- Consulta à base de conhecimento por busca vetorial (RAG).
- Busca de problemas similares na API do MOJ Naquadah.
- Detecção de ambiguidades e informações ausentes.
- Análise de complexidade e compatibilidade com as restrições.
- Sugestão de casos mínimos, máximos, de borda e de desempenho.

### Formatação e validação

- Geração de enunciado, entrada, saída, restrições e exemplos.
- Solução de referência em Python 3.
- Código AC testado com exemplos e casos extremos.
- Código potencialmente TLE acompanhado de justificativa de complexidade.
- Validação sintática com Python e execução isolada.
- Testes diferenciais entre solução de referência e solução candidata.
- Persistência do status e das validações da questão.

---

## Tecnologias

- **n8n Cloud:** orquestração do workflow e exposição via Webhook HTTP.
- **Supabase Vector / pgvector:** embeddings e recuperação semântica (índice HNSW).
- **MOJ Naquadah API:** busca de problemas existentes na plataforma.
- **OpenAI GPT-4o mini:** geração, análise e revisão assistida.
- **OpenAI text-embedding-3-small:** geração de embeddings (1536 dims).
- **PostgreSQL:** armazenamento de documentos, questões, metadados e histórico.
- **Python 3.10+:** ingestão da base de conhecimento e validadores.
- **Docker:** execução reprodutível dos serviços em ambiente local.

---

## Estrutura do projeto

```text
projeto_agenteIA/
├── docker-compose.yml
├── Dockerfile
├── .env.example                 # Modelo de variáveis de ambiente
├── requirements.txt
├── README.md
├── guia_gaia_curadoria_expandido.md
├── docs/
│   ├── intro_para_agente.md     # System message do agente
│   ├── base_conhecimento_agente_curadoria.json  # 20 documentos técnicos
│   └── API_GAIA.md              # Especificação completa da API (Avaliação II)
├── n8n/
│   └── workflows/
│       ├── agente_curadoria.json   # Workflow Avaliação I (Chat Trigger)
│       └── gaia_webhook.json       # Workflow Avaliação II (Webhook)
└── src/
    ├── scripts/
    │   └── injetar_base_conhecimento.py
    └── database/
        └── models.py
```

---

## Compilar e executar (Avaliação I — Local)

### Pré-requisitos

- Docker Desktop com Docker Compose habilitado.
- Chaves de acesso do OpenAI e do Supabase.

### 1. Configurar o ambiente

```powershell
Copy-Item .env.example .env
```

O arquivo `.env` deve conter, no mínimo:

```env
SUPABASE_URL=https://SEU_PROJETO.supabase.co
SUPABASE_SERVICE_KEY=sua_service_role_key
OPENAI_API_KEY=sua_openai_key
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=defina_uma_senha_forte
POSTGRES_DB=n8n
POSTGRES_USER=n8n
POSTGRES_PASSWORD=defina_uma_senha_forte
```

### 2. Compilar e iniciar os serviços

```bash
docker compose up -d --build
```

### 3. Verificar a execução

```bash
docker compose ps
docker compose logs -f n8n
```

Acesse o n8n em [http://localhost:5678](http://localhost:5678).

### 4. Injetar a base de conhecimento

```bash
pip install -r requirements.txt
python src/scripts/injetar_base_conhecimento.py
```

Para encerrar sem apagar dados:

```bash
docker compose down
```

Para a configuração completa do Supabase, da tabela vetorial, da função de busca semântica, da tabela de questões e das credenciais do n8n, consulte o [guia expandido](guia_gaia_curadoria_expandido.md).

---

## Modelo de validação

Uma questão não deve ser considerada pronta apenas porque foi gerada pela IA. O registro deve indicar, no mínimo:

```json
{
  "estrutura": "pendente",
  "codigo": "pendente",
  "complexidade": "pendente",
  "testes": "pendente",
  "revisao_humana": "pendente"
}
```

Status sugeridos para uma questão:

```text
rascunho
em_revisao
aprovada
reprovada
necessita_ajustes
```

---
## Autores

- Igor Moura
- Arthur D'Olival
- Erick Sousa Saraiva

---

*IFB — Instituto Federal de Brasília · Disciplina: Agentes de IA · 2026*
