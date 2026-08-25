# 🤖 Agente de Curadoria e Formatação de Problemas de Programação (com n8n + RAG)

![Status](https://img.shields.io/badge/Status-Em%20Desenvolvimento-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![n8n](https://img.shields.io/badge/n8n-Workflow%20Automation-orange)

Um agente de Inteligência Artificial especializado na seleção, avaliação, validação e estruturação de problemas de programação para uso acadêmico. Este projeto integra a capacidade de raciocínio de LLMs com a orquestração do **n8n** e a precisão técnica da arquitetura **RAG (Retrieval-Augmented Generation)** baseada em uma curadoria documental rigorosa.

## 🎯 Objetivo do Projeto

O objetivo principal deste agente é transformar um tópico ou requisito acadêmico em um conjunto de problemas de programação adequados para plataformas de avaliação automática (como URI/Beecrowd, Codeforces, HackerRank, etc.). 

O agente atua garantindo qualidade pedagógica, clareza, originalidade e verificabilidade por meio de duas fases principais: **Curadoria** e **Formatação**.

## 🧠 Arquitetura do Sistema (n8n + RAG)

O grande diferencial deste projeto é a sua arquitetura baseada em automação e recuperação de conhecimento específico:

1. **Orquestração com n8n:** Todo o fluxo de trabalho (pipeline) do agente — desde a entrada do tópico pelo usuário até a saída da questão formatada — é orquestrado de forma visual e modular utilizando o **n8n**.
2. **Base Documental Estruturada:** O agente consome um arquivo JSON contendo uma seleção curada de 20+ documentos essenciais (livros de algoritmos, manuais de Python/C++, diretrizes pedagógicas e regras de maratonas de programação).
3. **Retrieval-Augmented Generation (RAG):** Quando o agente precisa tomar decisões técnicas (ex: calcular complexidade, definir restrições de tempo/memória, ou formatar casos de teste), ele realiza buscas vetoriais nesta base documental para embasar suas respostas em literatura acadêmica e técnica confiável, evitando alucinações.

## ✨ Funcionalidades

### 🔍 Fase 1: Curadoria
- Compreensão de tópicos e conceitos de programação embasada na taxonomia educacional.
- Busca e avaliação de problemas candidatos usando RAG.
- Classificação de nível de dificuldade (Fácil, Médio, Difícil).
- Identificação de ambiguidades, complexidade e viabilidade algorítmica.

### 🛠️ Fase 2: Formatação
- Geração completa de artefatos para plataformas de correção automática.
- Criação de enunciados claros, formatos de entrada/saída e restrições.
- Desenvolvimento de **Soluções de Referência (AC - Accepted)** em Python e C++.
- Desenvolvimento de **Soluções Ineficientes (TLE - Time Limit Exceeded)** para validação.
- Geração de casos de teste abrangentes (casos mínimos, máximos, borda e desempenho).

## 🚀 Tecnologias Utilizadas

- **n8n:** Orquestrador principal do fluxo de trabalho do agente IA e integração de APIs.
- **Python**: Linguagem utilizada para processamento de dados e scripts auxiliares.
- **RAG / Vector Database:** Mecanismo de recuperação de informações baseado nos PDFs e documentos técnicos mapeados no projeto.
- **LLM (Large Language Model):** Motor de raciocínio do agente para a geração de textos, códigos e avaliações pedagógicas.
- **Docker**: Conteinerização da aplicação (incluindo a instância do n8n e bancos vetoriais locais) para garantir consistência entre os ambientes.
- **PostgreSQL**: Banco de dados relacional para armazenamento estruturado do banco de questões gerado, metadados e histórico de curadoria.

## 📁 Estrutura do Projeto

```text
├── docs/
│   ├── base_conhecimento_agente.json    # Base documental final para o pipeline RAG
│   └── pdfs/                            # (Opcional) Armazenamento local dos documentos curados
├── n8n/
│   └── workflows/                       # Workflows exportados do n8n (.json) para o Agente e RAG
├── src/
│   ├── scripts/                         # Scripts auxiliares (ex: teste de sanidade dos códigos)
│   └── database/                        # Modelos e conexão com PostgreSQL
├── Dockerfile
├── docker-compose.yml                   # Sobe o n8n, banco vetorial e Postgres
├── requirements.txt
└── README.md
```
## 🧑‍🎓🧑‍🎓🧑‍🎓 Autores
- Igor Moura
- Arthur D'Olival
- Erick Sousa Saraiva
