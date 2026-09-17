# Guia de Implementação --- GAIA

## Agente de Curadoria e Formatação de Questões de Programação Competitiva

> **Projeto:** `vs-code-gaia`\
> **Stack:** n8n (Docker), Supabase Vector, PostgreSQL, Python e LLM\
> **Objetivo:** construir um agente capaz de criar, revisar, validar e
> formatar problemas de programação competitiva no estilo de plataformas
> como o MOJ Naquadah.

------------------------------------------------------------------------

## 1. Objetivo do projeto

O GAIA será um agente de IA especializado em **curadoria e formatação de
questões de programação competitiva**.

O agente deverá apoiar o processo de criação de problemas, mas não deve
tratar a resposta de uma LLM como automaticamente correta. Toda questão
gerada deve passar por verificações técnicas, principalmente:

-   Clareza do enunciado;
-   Coerência entre entrada, saída e restrições;
-   Adequação da dificuldade;
-   Correção algorítmica;
-   Complexidade temporal e espacial;
-   Compatibilidade com Python;
-   Existência de casos extremos;
-   Ausência de ambiguidades;
-   Consistência entre solução, exemplos e testes;
-   Compatibilidade com o padrão esperado pelo MOJ Naquadah.

### Princípio central

> O RAG fornece contexto e referências. A validação algorítmica, a
> execução dos códigos e a revisão humana continuam sendo necessárias.

------------------------------------------------------------------------

## 2. Arquitetura geral

``` text
Usuário
   |
   v
Chat Trigger (n8n)
   |
   v
AI Agent
   |
   +--> LLM
   |
   +--> Memória
   |
   +--> Ferramenta RAG
   |       |
   |       v
   |   Supabase Vector
   |       |
   |       v
   |   Base de conhecimento
   |
   v
Curadoria e formatação
   |
   +--> Validação de estrutura
   +--> Validação de código Python
   +--> Geração de casos de teste
   |
   v
Saída estruturada
   |
   +--> Exibição ao usuário
   +--> Salvamento em PostgreSQL
```

### Componentes

  -----------------------------------------------------------------------
  Componente                          Responsabilidade
  ----------------------------------- -----------------------------------
  Docker                              Executar o n8n e serviços
                                      auxiliares

  n8n                                 Orquestrar o fluxo entre entrada,
                                      IA, RAG e validações

  AI Agent                            Interpretar solicitações e
                                      coordenar ferramentas

  LLM                                 Gerar, analisar e revisar conteúdos

  Supabase                            Armazenar documentos, embeddings e
                                      dados relacionais

  pgvector                            Permitir busca por similaridade
                                      vetorial

  Python                              Linguagem principal das soluções e
                                      dos validadores

  PostgreSQL                          Persistir documentos, questões e
                                      resultados de validação
  -----------------------------------------------------------------------

------------------------------------------------------------------------

# 3. Organização recomendada do projeto

``` text
vs-code-gaia/
├── docker-compose.yml
├── .env
├── .env.example
├── requirements.txt
├── README.md
├── base_conhecimento_agente_curadoria.json
├── src/
│   ├── scripts/
│   │   ├── injetar_base_conhecimento.py
│   │   ├── validar_questao.py
│   │   └── executar_testes.py
│   ├── validators/
│   │   ├── schema_validator.py
│   │   ├── python_validator.py
│   │   └── complexity_validator.py
│   └── prompts/
│       └── system_message.md
└── workflows/
    └── gaia-curadoria.json
```

### Pontos importantes

-   Nunca versionar chaves de API.
-   Utilizar `.env` localmente.
-   Manter um `.env.example` sem segredos.
-   Versionar a System Message e os scripts de validação.
-   Separar geração, curadoria e validação.
-   Registrar erros para facilitar a apresentação e a depuração.

------------------------------------------------------------------------

# 4. Configuração do Docker

## 4.1 Recomendação de segurança

O exemplo abaixo é adequado apenas para um ambiente local de estudo. Não
utilize senhas como `admin123` ou `n8npassword` em produção.

Também é recomendável utilizar uma versão fixada da imagem do n8n em vez
de `latest`, pois atualizações automáticas podem alterar comportamentos
dos nós.

## 4.2 Exemplo de `docker-compose.yml`

``` yaml
services:
  n8n:
    image: n8nio/n8n:latest
    container_name: n8n
    restart: unless-stopped
    ports:
      - "5678:5678"
    environment:
      - N8N_HOST=localhost
      - N8N_PORT=5678
      - N8N_PROTOCOL=http
      - WEBHOOK_URL=http://localhost:5678/
      - GENERIC_TIMEZONE=America/Sao_Paulo
      - DB_TYPE=postgresdb
      - DB_POSTGRESDB_HOST=postgres
      - DB_POSTGRESDB_PORT=5432
      - DB_POSTGRESDB_DATABASE=n8n
      - DB_POSTGRESDB_USER=n8n
      - DB_POSTGRESDB_PASSWORD=${N8N_DB_PASSWORD}
    volumes:
      - n8n_data:/home/node/.n8n
      - ./src:/data/src
    depends_on:
      postgres:
        condition: service_healthy

  postgres:
    image: postgres:15
    container_name: postgres
    restart: unless-stopped
    environment:
      - POSTGRES_DB=n8n
      - POSTGRES_USER=n8n
      - POSTGRES_PASSWORD=${N8N_DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U n8n -d n8n"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  n8n_data:
  postgres_data:
```

## 4.3 Arquivo `.env`

``` env
N8N_DB_PASSWORD=defina_uma_senha_forte
```

> Não publique esse arquivo no GitHub.

## 4.4 Subir os serviços

``` bash
docker compose up -d
```

Verificar os containers:

``` bash
docker compose ps
```

Ver logs do n8n:

``` bash
docker compose logs -f n8n
```

Acessar:

``` text
http://localhost:5678
```

------------------------------------------------------------------------

# 5. Configuração do Supabase

## 5.1 Configuração inicial

Recomendação para o projeto:

-   Região: São Paulo (`sa-east-1`);
-   Banco: PostgreSQL;
-   Data API: ativada, se for utilizada pelo n8n;
-   Exposição automática de novas tabelas: desativada;
-   RLS: habilitado quando aplicável;
-   Senha do banco: gerada e armazenada com segurança.

### Chaves

Diferencie:

-   **Project URL:** endereço do projeto Supabase;
-   **Anon key:** chave destinada a usos públicos controlados;
-   **Service role key:** chave privilegiada, que não deve ser exposta
    no navegador, frontend ou GitHub.

A `service_role` deve ser utilizada apenas em ambiente confiável, como
um script local protegido ou servidor.

------------------------------------------------------------------------

# 6. Estrutura do banco vetorial

## 6.1 Ativar o pgvector

No SQL Editor do Supabase:

``` sql
CREATE EXTENSION IF NOT EXISTS vector;
```

## 6.2 Tabela de documentos

A dimensão do vetor deve ser compatível com o modelo de embeddings
utilizado.

O exemplo abaixo considera um embedding de 1536 dimensões:

``` sql
CREATE TABLE IF NOT EXISTS documentos_curadoria (
    id BIGSERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    embedding VECTOR(1536),
    criado_em TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### Significado das colunas

  Campo         Finalidade
  ------------- ---------------------------------------------
  `id`          Identificador único
  `content`     Texto utilizado na recuperação
  `metadata`    Título, autor, tema, nível, origem e versão
  `embedding`   Vetor semântico do conteúdo
  `criado_em`   Data de inserção

### Atenção sobre a dimensão

Não escolha `1536` apenas por conveniência. Confirme a dimensão do
modelo de embeddings. Se o modelo gerar outra quantidade de valores, a
tabela e a função de busca deverão ser ajustadas.

------------------------------------------------------------------------

## 6.3 Índice vetorial

Uma alternativa é o HNSW:

``` sql
CREATE INDEX IF NOT EXISTS documentos_curadoria_embedding_idx
ON documentos_curadoria
USING hnsw (embedding vector_cosine_ops);
```

O índice melhora a busca por similaridade, mas não resolve problemas de:

-   Embeddings inadequados;
-   Chunks muito grandes;
-   Documentos irrelevantes;
-   Metadados ausentes;
-   Consultas mal formuladas.

------------------------------------------------------------------------

## 6.4 Função de busca semântica

``` sql
CREATE OR REPLACE FUNCTION match_documentos_curadoria(
    query_embedding VECTOR(1536),
    match_count INT DEFAULT 5,
    filter JSONB DEFAULT '{}'::jsonb
)
RETURNS TABLE (
    id BIGINT,
    content TEXT,
    metadata JSONB,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        d.id,
        d.content,
        d.metadata,
        1 - (d.embedding <=> query_embedding) AS similarity
    FROM documentos_curadoria AS d
    WHERE d.embedding IS NOT NULL
      AND (
          filter = '{}'::jsonb
          OR d.metadata @> filter
      )
    ORDER BY d.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;
```

### Por que filtrar embeddings nulos?

Documentos sem embedding não podem participar corretamente da busca
vetorial. O filtro evita resultados inválidos.

### Por que utilizar metadados?

Metadados permitem restringir a busca, por exemplo:

-   Somente documentos sobre grafos;
-   Somente material de nível intermediário;
-   Somente fontes oficiais;
-   Somente documentos em português;
-   Somente conteúdos relacionados a Python.

------------------------------------------------------------------------

# 7. Tabela de questões

``` sql
CREATE TABLE IF NOT EXISTS questoes (
    id BIGSERIAL PRIMARY KEY,
    titulo TEXT NOT NULL,
    topico TEXT,
    dificuldade TEXT CHECK (
        dificuldade IN ('Fácil', 'Médio', 'Difícil')
    ),
    enunciado TEXT,
    entrada TEXT,
    saida TEXT,
    restricoes TEXT,
    exemplos JSONB,
    tags TEXT[],
    solucao_python TEXT,
    codigo_ac TEXT,
    codigo_tle TEXT,
    casos_teste JSONB,
    validacoes JSONB,
    metadados JSONB NOT NULL DEFAULT '{}'::jsonb,
    status TEXT DEFAULT 'rascunho',
    criado_em TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

## 7.1 Status sugeridos

``` text
rascunho
em_revisao
aprovada
reprovada
necessita_ajustes
```

A questão não deve ser considerada pronta apenas porque foi gerada pela
IA.

## 7.2 O que registrar em `validacoes`

Exemplo:

``` json
{
  "estrutura": "aprovada",
  "exemplos": "aprovada",
  "python": "pendente",
  "complexidade": "pendente",
  "casos_extremos": "pendente",
  "revisao_humana": "pendente"
}
```

------------------------------------------------------------------------

# 8. Preparação da base de conhecimento

## 8.1 Fontes possíveis

A base pode conter:

-   Livros de algoritmos;
-   Manuais de programação competitiva;
-   Documentação oficial do Python;
-   Regras e orientações de maratonas;
-   Materiais sobre complexidade;
-   Documentos sobre elaboração de problemas;
-   Referências sobre testes e avaliação de soluções.

### Critério de qualidade das fontes

Para cada documento, registrar:

-   Título;
-   Autor ou instituição;
-   Ano;
-   URL ou referência;
-   Tema;
-   Nível;
-   Idioma;
-   Tipo de fonte;
-   Status de confiabilidade;
-   Data de inclusão.

Não utilizar uma fonte sem verificar sua procedência e relevância.

------------------------------------------------------------------------

## 8.2 Estrutura sugerida do JSON

``` json
{
  "titulo": "Nome da referência",
  "autor": "Autor ou instituição",
  "ano": 2024,
  "resumo": "Resumo objetivo do conteúdo.",
  "url_pdf": "https://exemplo.com/documento.pdf",
  "status": "validado",
  "metadata": {
    "tema": [
      "algoritmos",
      "complexidade"
    ],
    "nivel": "intermediario",
    "idioma": "pt-BR",
    "tipo": "livro"
  }
}
```

------------------------------------------------------------------------

## 8.3 Chunking

Evite inserir documentos longos como um único bloco.

O processo recomendado é:

``` text
Documento
   |
   v
Limpeza
   |
   v
Divisão em chunks
   |
   v
Preservação dos metadados
   |
   v
Embeddings
   |
   v
Supabase Vector
```

### Cuidados no chunking

-   Não cortar uma definição no meio;
-   Preservar título e seção;
-   Manter contexto suficiente;
-   Evitar chunks excessivamente pequenos;
-   Evitar repetição exagerada;
-   Associar cada chunk ao documento de origem;
-   Registrar ordem ou número do chunk.

Exemplo de metadados:

``` json
{
  "titulo": "Competitive Programmer's Handbook",
  "secao": "Busca binária",
  "chunk_index": 3,
  "total_chunks": 8,
  "tema": ["busca", "complexidade"],
  "origem": "livro"
}
```

------------------------------------------------------------------------

# 9. Script Python de ingestão

## 9.1 Dependências

``` txt
openai>=1.30.0
supabase>=2.4.0
python-dotenv>=1.0.0
```

Instalação:

``` bash
pip install -r requirements.txt
```

## 9.2 Variáveis de ambiente

``` env
SUPABASE_URL=https://SEU_PROJETO.supabase.co
SUPABASE_SERVICE_KEY=sua_service_role_key
OPENAI_API_KEY=sua_openai_key
```

Nunca registrar essas variáveis em logs ou mensagens de erro.

## 9.3 Regras para o script

O script deve:

1.  Ler o JSON;
2.  Validar a estrutura mínima;
3.  Montar o conteúdo textual;
4.  Dividir documentos em chunks, quando necessário;
5.  Gerar embeddings;
6.  Inserir os registros;
7.  Informar sucesso ou falha por documento;
8.  Evitar duplicação quando executado novamente;
9.  Registrar quantidade de documentos e chunks;
10. Permitir reprocessamento controlado.

### Controle de duplicação

É recomendável criar um identificador de origem, como:

``` json
{
  "source_id": "livro-busca-binaria-v1",
  "chunk_index": 0
}
```

Antes de inserir, o script pode verificar se aquele `source_id` e
`chunk_index` já existem.

------------------------------------------------------------------------

# 10. Configuração do n8n

## 10.1 Credenciais

Configurar de acordo com os nós utilizados:

  Credencial   Dados
  ------------ ---------------------------------------------------
  OpenAI       API Key
  Supabase     Project URL e chave apropriada
  PostgreSQL   Host, banco, usuário e senha do PostgreSQL do n8n

### Segurança

-   Não enviar `service_role` para o frontend;
-   Não colocar chaves em campos de texto visíveis;
-   Não compartilhar screenshots com credenciais;
-   Usar credenciais internas do n8n;
-   Limitar permissões sempre que possível.

------------------------------------------------------------------------

## 10.2 Workflow inicial

``` text
Chat Trigger
    |
    v
AI Agent
    |
    +--> OpenAI Chat Model
    |
    +--> Window Buffer Memory
    |
    +--> Supabase Vector Store
    |
    v
Resposta estruturada
```

### Ordem de evolução

1.  Testar o Chat Trigger;
2.  Testar o modelo sem RAG;
3.  Testar o Supabase Vector Store;
4.  Adicionar a System Message;
5.  Testar curadoria;
6.  Adicionar validação;
7.  Persistir a questão no banco.

Essa ordem facilita identificar em qual etapa ocorre um erro.

------------------------------------------------------------------------

# 11. System Message do agente

A System Message deve definir claramente:

## 11.1 Papel

Você é um agente especializado em curadoria e formatação de problemas de
programação competitiva.

## 11.2 Linguagem

-   A linguagem de solução padrão é Python 3;
-   O código deve ser compatível com a versão definida pelo projeto;
-   A solução deve considerar limites de tempo e memória;
-   Não utilizar bibliotecas externas sem autorização explícita.

## 11.3 Regras de curadoria

O agente deve:

-   Identificar o tópico algorítmico;
-   Estimar a dificuldade;
-   Verificar se o problema possui objetivo claro;
-   Avaliar se as restrições são suficientes;
-   Conferir a coerência entre exemplos e especificação;
-   Identificar ambiguidades;
-   Verificar a complexidade esperada;
-   Sugerir casos extremos;
-   Indicar informações ausentes;
-   Consultar o RAG quando precisar de referência técnica.

## 11.4 Restrições de comportamento

O agente não deve:

-   Inventar uma fonte como se tivesse sido consultada;
-   Afirmar que um código foi executado sem execução real;
-   Afirmar que uma questão está correta sem validação;
-   Definir limites de entrada arbitrariamente;
-   Produzir casos de teste incompatíveis com o enunciado;
-   Confundir uma solução lenta com uma solução correta;
-   Tratar a similaridade vetorial como prova de validade.

------------------------------------------------------------------------

# 12. Pipeline de curadoria

A curadoria deve ser organizada em fases.

## Fase 1 --- Interpretação

Extrair:

-   Tema;
-   Subtema;
-   Dificuldade;
-   Público-alvo;
-   Linguagem;
-   Tipo de problema;
-   Restrições conhecidas.

## Fase 2 --- Pesquisa no RAG

Consultar a base para encontrar:

-   Definições;
-   Algoritmos relacionados;
-   Complexidades;
-   Restrições usuais;
-   Armadilhas de implementação;
-   Referências relevantes.

## Fase 3 --- Análise técnica

Verificar:

-   Se o algoritmo escolhido resolve o problema;
-   Se a complexidade é compatível com `N`;
-   Se a memória necessária é viável;
-   Se há casos degenerados;
-   Se a solução funciona com entradas mínimas;
-   Se há risco de overflow ou problemas de precisão;
-   Se Python consegue atender aos limites.

## Fase 4 --- Formatação

Produzir:

-   Título;
-   Descrição;
-   Entrada;
-   Saída;
-   Restrições;
-   Exemplos;
-   Explicação;
-   Solução Python;
-   Complexidade;
-   Casos de teste.

## Fase 5 --- Validação

Separar:

-   Validação estrutural;
-   Validação semântica;
-   Validação do código;
-   Validação dos testes;
-   Revisão humana.

------------------------------------------------------------------------

# 13. Critérios técnicos de curadoria

## 13.1 Enunciado

O enunciado deve responder:

-   Qual é o problema?
-   O que o participante precisa calcular?
-   Quais dados são fornecidos?
-   Qual resultado deve ser produzido?
-   Existem condições especiais?
-   A definição é inequívoca?

Evitar:

-   Termos vagos;
-   Regras implícitas;
-   Informações desnecessárias;
-   Exemplos que não correspondem à descrição;
-   Requisitos escondidos na explicação.

## 13.2 Entrada e saída

Conferir:

-   Quantidade de casos de teste;
-   Formato de cada linha;
-   Tipos dos valores;
-   Ordem dos dados;
-   Possibilidade de valores vazios;
-   Formato exato da saída;
-   Necessidade ou não de casas decimais;
-   Espaços e quebras de linha relevantes.

## 13.3 Restrições

As restrições precisam ser compatíveis com o algoritmo.

Exemplo:

``` text
N <= 10^5
```

Uma solução `O(N²)` provavelmente não será adequada para todos os casos,
mas a decisão final depende dos limites de tempo, hardware,
implementação e operações realizadas.

O agente deve justificar a complexidade e não apenas rotular uma solução
como rápida ou lenta.

## 13.4 Casos extremos

Considerar, quando aplicável:

-   Menor entrada possível;
-   Maior entrada possível;
-   Todos os valores iguais;
-   Valores negativos;
-   Valores zero;
-   Dados ordenados;
-   Dados invertidos;
-   Resposta inexistente;
-   Resposta única;
-   Respostas repetidas;
-   Estruturas desconectadas;
-   Grafos com ciclos;
-   Strings vazias ou de tamanho mínimo.

------------------------------------------------------------------------

# 14. Validação da solução Python

A geração de código deve ser acompanhada por validações.

## 14.1 Validação sintática

Verificar se o código pode ser analisado pelo Python:

``` python
import ast

def validar_sintaxe(codigo: str) -> bool:
    try:
        ast.parse(codigo)
        return True
    except SyntaxError:
        return False
```

## 14.2 Execução isolada

A execução de código gerado por IA deve ocorrer em ambiente isolado e
controlado.

Cuidados:

-   Não executar código diretamente no host sem proteção;
-   Limitar tempo de execução;
-   Limitar memória;
-   Restringir acesso à rede;
-   Não disponibilizar segredos;
-   Impedir acesso a arquivos sensíveis;
-   Registrar stdout e stderr;
-   Encerrar processos que excedam os limites.

## 14.3 Testes diferenciais

Quando possível, utilizar:

-   Uma solução de referência confiável;
-   Uma solução candidata;
-   Entradas aleatórias;
-   Casos extremos;
-   Comparação das saídas.

Para problemas pequenos, uma solução força-bruta pode funcionar como
oráculo de teste.

------------------------------------------------------------------------

# 15. Código AC e código TLE

A geração de código AC e TLE deve ser tratada com cuidado.

## Código AC

O código AC deve:

-   Resolver o problema;
-   Respeitar entrada e saída;
-   Atender às restrições;
-   Possuir complexidade compatível;
-   Ser testado com exemplos e casos extremos.

## Código TLE

Um código TLE não deve ser simplesmente um código incorreto.

Ele deve:

-   Produzir a resposta correta em entradas pequenas;
-   Utilizar uma estratégia deliberadamente ineficiente;
-   Ter complexidade maior que a solução esperada;
-   Ser acompanhado de explicação;
-   Ser testado em ambiente controlado;
-   Ser classificado como potencialmente lento, caso o TLE não tenha
    sido comprovado experimentalmente.

> O rótulo `TLE` deve ser baseado em evidência de execução ou em uma
> justificativa de complexidade. Não afirmar que ocorreu TLE sem teste
> real.

------------------------------------------------------------------------

# 16. Testes recomendados

## Teste 1 --- Curadoria

``` text
Quero uma questão de programação dinâmica para nível intermediário,
utilizando Python e adequada a uma maratona de programação.
```

Verificar:

-   O agente identifica o tema;
-   Consulta o RAG;
-   Apresenta possíveis ambiguidades;
-   Não inventa referências;
-   Justifica a dificuldade.

## Teste 2 --- Complexidade

``` text
Analise a complexidade esperada de uma solução para
Longest Common Subsequence e explique como os limites de N
influenciam a escolha do algoritmo.
```

Verificar:

-   A resposta distingue tempo e memória;
-   O agente apresenta ressalvas;
-   O RAG é consultado;
-   Não existe uma recomendação de limite sem justificativa.

## Teste 3 --- Formatação

``` text
Formate um problema de soma de subarray máximo,
com solução Python, explicação de complexidade e cinco casos de teste.
```

Verificar:

-   Entrada e saída são coerentes;
-   A solução funciona;
-   Os testes incluem casos extremos;
-   A complexidade é informada;
-   A questão não depende de informação ausente.

## Teste 4 --- RAG restritivo

``` text
Utilize somente as referências recuperadas para indicar
quais conceitos precisam ser revisados antes de aprovar esta questão.
Caso a base não possua informação suficiente, informe a limitação.
```

O objetivo é demonstrar que o RAG orienta a resposta e que o agente sabe
declarar insuficiência de contexto.

------------------------------------------------------------------------

# 17. Persistência das questões

Antes de salvar uma questão, validar a estrutura da resposta.

Exemplo de saída estruturada:

``` json
{
  "titulo": "Soma Máxima",
  "topico": "programacao-dinamica",
  "dificuldade": "Medio",
  "enunciado": "...",
  "entrada": "...",
  "saida": "...",
  "restricoes": "...",
  "exemplos": [],
  "solucao_python": "...",
  "complexidade": {
    "tempo": "O(n)",
    "espaco": "O(1)"
  },
  "casos_teste": [],
  "validacoes": {
    "estrutura": "pendente",
    "codigo": "pendente",
    "testes": "pendente",
    "revisao_humana": "pendente"
  },
  "status": "rascunho"
}
```

A persistência deve acontecer somente depois de:

1.  Verificar campos obrigatórios;
2.  Validar a dificuldade;
3.  Validar o formato;
4.  Registrar o status;
5.  Armazenar alertas e limitações.

------------------------------------------------------------------------

# 18. Problemas comuns e soluções

  -----------------------------------------------------------------------
  Problema                Possível causa          Ação
  ----------------------- ----------------------- -----------------------
  RAG retorna documentos  Chunks ruins ou         Melhorar chunking,
  irrelevantes            consulta genérica       metadados e descrição
                                                  da ferramenta

  Embedding incompatível  Dimensão errada         Conferir o modelo e a
                                                  coluna `vector`

  Questão com limite      Ausência de validação   Adicionar análise de
  incoerente              algorítmica             complexidade

  Código não executa      Geração incompleta ou   Usar validação
                          erro de sintaxe         sintática e testes

  Questões repetidas      Falta de controle de    Usar identificador de
                          origem                  fonte e hash

  Resposta inventada      Prompt permissivo ou    Exigir indicação de
                          RAG insuficiente        incerteza e referências

  Workflow difícil de     Muitos nós em um único  Separar ingestão,
  depurar                 fluxo                   geração e validação

  Chave exposta           Configuração insegura   Utilizar credenciais do
                                                  n8n e `.env`
  -----------------------------------------------------------------------

------------------------------------------------------------------------

# 19. Checklist técnico

## Docker

-   [ ] Docker está instalado;
-   [ ] Containers estão em execução;
-   [ ] Volumes persistentes configurados;
-   [ ] Senhas não estão hardcoded;
-   [ ] Logs podem ser consultados.

## Supabase

-   [ ] Projeto criado;
-   [ ] Região selecionada;
-   [ ] Extensão `vector` ativada;
-   [ ] Tabela de documentos criada;
-   [ ] Função de busca criada;
-   [ ] Tabela de questões criada;
-   [ ] Políticas de acesso revisadas.

## Ingestão

-   [ ] JSON validado;
-   [ ] Documentos limpos;
-   [ ] Chunks definidos;
-   [ ] Embeddings gerados;
-   [ ] Metadados preservados;
-   [ ] Duplicações controladas;
-   [ ] Quantidade de inserções conferida.

## n8n

-   [ ] Credenciais configuradas;
-   [ ] Chat Trigger funcionando;
-   [ ] AI Agent configurado;
-   [ ] System Message versionada;
-   [ ] Memória testada;
-   [ ] Supabase Vector Store conectado;
-   [ ] RAG testado;
-   [ ] Saída estruturada validada.

## Curadoria

-   [ ] Enunciado revisado;
-   [ ] Entrada e saída coerentes;
-   [ ] Restrições justificadas;
-   [ ] Complexidade analisada;
-   [ ] Casos extremos criados;
-   [ ] Código Python verificado;
-   [ ] Limitações registradas;
-   [ ] Revisão humana realizada.

------------------------------------------------------------------------

# 20. Roteiro para apresentação de aproximadamente 10 minutos

  Tempo       Demonstração
  ----------- -----------------------------------------------------
  0--2 min    Apresentar a System Message e as fases de curadoria
  2--4 min    Mostrar JSON, script Python, embeddings e Supabase
  4--7 min    Executar uma solicitação e demonstrar o RAG
  7--9 min    Exibir questão formatada, solução Python e testes
  9--10 min   Apresentar dificuldades, decisões e próximos passos

## Pontos para destacar oralmente

-   O agente não depende apenas de conhecimento interno da LLM;
-   O RAG recupera referências selecionadas pelo grupo;
-   A base possui metadados para melhorar a recuperação;
-   A geração é separada da validação;
-   A linguagem de implementação é Python;
-   Os limites de entrada precisam ser compatíveis com a complexidade;
-   A execução dos códigos é necessária para confirmar resultados;
-   A revisão humana continua fazendo parte do processo.

------------------------------------------------------------------------

# 21. Evoluções futuras

Possíveis melhorias:

1.  Classificação automática de dificuldade;
2.  Detecção de duplicidade entre questões;
3.  Geração automática de testes;
4.  Execução em sandbox;
5.  Validação diferencial com solução de referência;
6.  Avaliação de qualidade do RAG;
7.  Registro de versões de prompts;
8.  Painel de acompanhamento das questões;
9.  Aprovação humana dentro do n8n;
10. Métricas de precisão, taxa de erro e retrabalho;
11. Suporte a outras linguagens;
12. Exportação para formatos aceitos pelo MOJ Naquadah.

------------------------------------------------------------------------

# 22. Critérios de sucesso do protótipo

O protótipo poderá ser considerado funcional quando conseguir:

-   Receber uma solicitação de questão;
-   Consultar a base de conhecimento;
-   Produzir uma questão estruturada;
-   Gerar solução em Python;
-   Explicar a complexidade;
-   Criar casos de teste;
-   Identificar possíveis problemas;
-   Registrar a questão como rascunho;
-   Informar claramente o que foi ou não validado.

> **Resultado esperado:** um agente de apoio à criação e curadoria de
> problemas, com rastreabilidade, referências, validações e
> possibilidade de revisão humana.
