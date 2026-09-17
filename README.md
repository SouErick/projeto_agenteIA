# Agente GAIA de Curadoria e Formatação de Questões

> **Artefato principal:** leia o [Guia de Implementação do GAIA](guia_gaia_curadoria_expandido.md) para consultar a arquitetura detalhada, a configuração do Docker e do Supabase, o pipeline de curadoria, os scripts, os testes e o checklist técnico do projeto.

![Status](https://img.shields.io/badge/Status-Em%20Desenvolvimento-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![n8n](https://img.shields.io/badge/n8n-Workflow%20Automation-orange)

O **GAIA** é um agente de Inteligência Artificial para curadoria, validação e formatação de problemas de programação competitiva. O projeto combina **n8n**, **RAG (Retrieval-Augmented Generation)**, **Supabase Vector**, **PostgreSQL**, **Python** e **LLMs** para transformar um tema ou requisito acadêmico em uma questão estruturada, verificável e adequada a plataformas como o MOJ Naquadah.

> O RAG fornece contexto e referências. A validação algorítmica, a execução dos códigos e a revisão humana continuam sendo necessárias.

## Objetivos

- Criar questões claras e adequadas ao público-alvo.
- Pesquisar referências técnicas em uma base documental curada.
- Avaliar dificuldade, algoritmo, complexidade temporal e complexidade espacial.
- Validar a coerência entre enunciado, entrada, saída, restrições, exemplos e testes.
- Gerar soluções de referência em Python e, quando necessário, soluções deliberadamente ineficientes para análise de desempenho.
- Registrar questões, metadados, validações, alertas e limitações para permitir rastreabilidade e revisão.

## Arquitetura

```text
Usuário
   |
   v
Chat Trigger (n8n)
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
| --- | --- |
| Docker | Executar o n8n e os serviços auxiliares. |
| n8n | Orquestrar entrada, IA, RAG e validações. |
| AI Agent | Interpretar solicitações e coordenar ferramentas. |
| LLM | Gerar, analisar e revisar conteúdos. |
| Supabase Vector | Armazenar documentos, embeddings e dados relacionados. |
| pgvector | Realizar busca por similaridade vetorial. |
| Python | Implementar soluções e validadores. |
| PostgreSQL | Persistir documentos, questões e resultados de validação. |

## Pipeline de curadoria

1. **Interpretação:** extrair tema, subtema, dificuldade, público-alvo, linguagem e restrições.
2. **Pesquisa no RAG:** recuperar definições, algoritmos, complexidades, referências e armadilhas de implementação.
3. **Análise técnica:** verificar algoritmo, limites de entrada, uso de memória, casos degenerados e viabilidade em Python.
4. **Formatação:** produzir título, enunciado, entrada, saída, restrições, exemplos, explicação, solução e complexidade.
5. **Validação:** executar validações estruturais, semânticas, de código e de testes, mantendo a revisão humana como etapa final.

## Funcionalidades

### Curadoria

- Identificação do tópico algorítmico e do nível de dificuldade.
- Consulta à base de conhecimento por busca vetorial.
- Detecção de ambiguidades e informações ausentes.
- Análise de complexidade e compatibilidade com as restrições.
- Sugestão de casos mínimos, máximos, de borda e de desempenho.

### Formatação e validação

- Geração de enunciado, entrada, saída, restrições e exemplos.
- Solução de referência em Python 3.
- Código AC testado com exemplos e casos extremos.
- Código potencialmente TLE acompanhado de justificativa de complexidade ou evidência de execução.
- Validação sintática com Python e execução isolada, com limites de tempo, memória, rede e acesso a arquivos.
- Testes diferenciais entre solução de referência, solução candidata e, quando possível, um oráculo de força bruta.
- Persistência do status e das validações da questão.

## Tecnologias

- **n8n:** orquestração do workflow e integração de APIs.
- **Supabase Vector / pgvector:** embeddings e recuperação semântica.
- **PostgreSQL:** armazenamento de documentos, questões, metadados e histórico.
- **Python 3.10+:** soluções, ingestão e validadores.
- **LLM:** geração, análise e revisão assistida.
- **Docker:** execução reprodutível dos serviços.

## Estrutura do projeto

```text
vs-code-gaia/
├── docker-compose.yml
├── Dockerfile
├── .env                         # Configuração local; não versionar segredos
├── .env_example                 # Modelo de variáveis de ambiente
├── requirements.txt
├── README.md
├── guia.md                      # Visão geral da arquitetura
├── guia_gaia_curadoria_expandido.md
├── base_conhecimento_agente_curadoria.json
├── docs/                        # Documentação e materiais auxiliares
├── n8n/                         # Workflows exportados do n8n
└── src/                         # Scripts, validadores e integração com o banco
```

O guia expandido apresenta uma organização recomendada para os próximos módulos, incluindo scripts de ingestão, validadores de schema, Python e complexidade, prompts versionados e workflows exportados.

## Configuração rápida

### Pré-requisitos

- Docker e Docker Compose.
- Uma conta ou projeto Supabase com PostgreSQL e `pgvector` habilitado.
- Chaves de acesso do provedor de LLM e do Supabase.

### Variáveis de ambiente

Crie ou ajuste o arquivo `.env` localmente com os valores necessários. Nunca publique chaves de API, senhas ou a `service_role` no repositório.

Exemplo:

```env
N8N_DB_PASSWORD=defina_uma_senha_forte
SUPABASE_URL=https://SEU_PROJETO.supabase.co
SUPABASE_SERVICE_KEY=sua_service_role_key
OPENAI_API_KEY=sua_openai_key
```

### Executar os serviços

```bash
docker compose up -d
docker compose ps
docker compose logs -f n8n
```

Depois, acesse o n8n em [http://localhost:5678](http://localhost:5678).

Para a configuração completa do Supabase, da tabela vetorial, da função de busca semântica, da tabela de questões e das credenciais do n8n, consulte o [guia expandido](guia_gaia_curadoria_expandido.md).

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

## Segurança e boas práticas

- Não versionar chaves de API, senhas ou arquivos `.env`.
- Preferir versões fixadas das imagens Docker em ambientes estáveis.
- Utilizar credenciais internas do n8n e limitar permissões.
- Não expor a chave `service_role` ao frontend ou ao GitHub.
- Executar código gerado em ambiente isolado e controlado.
- Registrar erros, limitações, origem dos documentos e versões dos prompts.
- Controlar duplicações por identificador de origem e índice do chunk.
- Não afirmar que um código foi executado ou que ocorreu TLE sem evidência.

## Testes de aceitação

O protótipo deve conseguir:

- Receber uma solicitação de questão.
- Consultar a base de conhecimento.
- Produzir uma questão estruturada.
- Gerar uma solução Python e explicar sua complexidade.
- Criar casos de teste, incluindo casos extremos.
- Identificar ambiguidades e limitações.
- Registrar a questão como rascunho com suas validações.
- Informar claramente o que foi e o que não foi validado.

O guia expandido também contém exemplos de testes de curadoria, complexidade, formatação e uso restritivo do RAG.

## Evoluções futuras

- Classificação automática de dificuldade.
- Detecção de duplicidade entre questões.
- Geração automática de testes e validação diferencial.
- Execução em sandbox.
- Versionamento de prompts e métricas de qualidade do RAG.
- Painel de acompanhamento e aprovação humana dentro do n8n.
- Suporte a outras linguagens e exportação para formatos do MOJ Naquadah.

## Autores

- Igor Moura
- Arthur D'Olival
- Erick Sousa Saraiva