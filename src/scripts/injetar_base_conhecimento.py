import json
import os
import time
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from supabase import create_client, Client

# ── Carrega .env da raiz do projeto ──────────────────────────────────────────
load_dotenv(Path(__file__).parents[2] / ".env")

SUPABASE_URL      = os.environ["SUPABASE_URL"]
SUPABASE_KEY      = os.environ["SUPABASE_SERVICE_KEY"]
OPENAI_API_KEY    = os.environ["OPENAI_API_KEY"]

EMBEDDING_MODEL   = "text-embedding-3-small"  
TABELA            = "documentos_curadoria"
ARQUIVO_JSON      = Path(__file__).parents[2] / "docs" / "base_conhecimento_agente_curadoria.json"

openai_client = OpenAI(api_key=OPENAI_API_KEY)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def gerar_embedding(texto: str) -> list[float]:
    resposta = openai_client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=texto.strip()
    )
    return resposta.data[0].embedding


def construir_conteudo(doc: dict) -> str:
    meta = doc.get("metadata", {})
    temas = meta.get("tema", [])
    nivel = meta.get("nivel", "")
    idioma = meta.get("idioma", "")
    contexto = meta.get("contexto_educacional", "")

    partes = [
        f"Título: {doc.get('titulo', '')}",
        f"Autor: {doc.get('autor', '')}",
        f"Ano: {doc.get('ano', '')}",
        f"Resumo: {doc.get('resumo', '')}",
    ]

    if temas:
        partes.append(f"Temas: {', '.join(temas)}")
    if nivel:
        partes.append(f"Nível: {nivel}")
    if idioma:
        partes.append(f"Idioma: {idioma}")
    if contexto:
        partes.append(f"Contexto: {contexto}")

    return "\n".join(partes)


def doc_ja_existe(titulo: str) -> bool:
    resultado = (
        supabase.table(TABELA)
        .select("id")
        .eq("metadata->>titulo", titulo)
        .limit(1)
        .execute()
    )
    return len(resultado.data) > 0


def inserir_documento(doc: dict, posicao: int, total: int) -> bool:

    titulo = doc.get("titulo", f"Documento {posicao}")

    if doc_ja_existe(titulo):
        print(f"Já existe: {titulo}")
        return False

    conteudo = construir_conteudo(doc)
    embedding = gerar_embedding(conteudo)

    # Payload compatível com a tabela criada no Supabase
    payload = {
        "content": conteudo,
        "metadata": {
            "titulo":   doc.get("titulo"),
            "autor":    doc.get("autor"),
            "ano":      str(doc.get("ano", "")),
            "url":      doc.get("url_pdf"),
            "status":   doc.get("status"),
            "embedding_status": "done",
            **doc.get("metadata", {}),
        },
        "embedding": embedding,
    }

    supabase.table(TABELA).insert(payload).execute()
    return True


def main():
    print("=" * 55)
    print("  Injeção da base de conhecimento → Supabase Vector")
    print("=" * 55)
    print(f"\n  Arquivo: {ARQUIVO_JSON.name}")
    print(f"  Tabela:  {TABELA}")
    print(f"  Modelo:  {EMBEDDING_MODEL}\n")

    with open(ARQUIVO_JSON, encoding="utf-8") as f:
        documentos = json.load(f)

    total = len(documentos)
    print(f"  {total} documentos encontrados\n")
    print("-" * 55)

    inseridos = 0
    pulados   = 0
    erros     = 0

    for i, doc in enumerate(documentos, start=1):
        titulo = doc.get("titulo", f"Documento {i}")
        print(f"[{i:2}/{total}] {titulo[:50]}")

        try:
            foi_inserido = inserir_documento(doc, i, total)
            if foi_inserido:
                print(f"       Inserido com sucesso")
                inseridos += 1
            else:
                pulados += 1
        except Exception as e:
            print(f"       Erro: {e}")
            erros += 1

        time.sleep(0.4)

    print("-" * 55)
    print(f"\n  Resumo:")
    print(f"    Inseridos: {inseridos}")
    print(f"    Pulados:  {pulados}")
    print(f"    Erros:    {erros}")
    print("\n  Injeção concluída!")


if __name__ == "__main__":
    main()