import json
import os
import time
from pathlib import Path

from openai import OpenAI
from supabase import create_client, Client

# ── Configuração ─────────────────────────────────────────────────────────────
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_KEY"]   # service_role key
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

EMBEDDING_MODEL = "text-embedding-3-small"           # 1536 dims, custo baixo
TABELA = "documentos_curadoria"
ARQUIVO_JSON = Path(__file__).parent.parent.parent / "base_conhecimento_agente_curadoria.json"

# ── Clientes ──────────────────────────────────────────────────────────────────
openai_client = OpenAI(api_key=OPENAI_API_KEY)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def gerar_embedding(texto: str) -> list[float]:
    """Gera embedding para um texto usando a API da OpenAI."""
    response = openai_client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=texto
    )
    return response.data[0].embedding


def construir_conteudo(doc: dict) -> str:
    """
    Monta o texto que será embedado.
    Combina título, autor, resumo e temas para melhor recuperação semântica.
    """
    partes = [
        f"Título: {doc.get('titulo', '')}",
        f"Autor: {doc.get('autor', '')}",
        f"Ano: {doc.get('ano', '')}",
        f"Resumo: {doc.get('resumo', '')}",
    ]
    metadados = doc.get("metadata", {})
    if temas := metadados.get("tema"):
        partes.append(f"Temas: {', '.join(temas)}")
    if nivel := metadados.get("nivel"):
        partes.append(f"Nível: {nivel}")

    return "\n".join(partes)


def inserir_documento(doc: dict) -> None:
    """Gera embedding e insere um documento no Supabase."""
    conteudo = construir_conteudo(doc)
    embedding = gerar_embedding(conteudo)

    payload = {
        "content": conteudo,
        "metadata": {
            "titulo": doc.get("titulo"),
            "autor": doc.get("autor"),
            "ano": doc.get("ano"),
            "url": doc.get("url_pdf"),
            "status": doc.get("status"),
            **doc.get("metadata", {}),
        },
        "embedding": embedding,
    }

    supabase.table(TABELA).insert(payload).execute()
    print(f"Inserido: {doc.get('titulo')}")


def main():
    print("── Iniciando injeção da base de conhecimento ──\n")

    with open(ARQUIVO_JSON, encoding="utf-8") as f:
        documentos = json.load(f)

    print(f"Total de documentos encontrados: {len(documentos)}\n")

    for i, doc in enumerate(documentos, start=1):
        titulo = doc.get("titulo", f"Documento {i}")
        print(f"[{i}/{len(documentos)}] Processando: {titulo}")

        try:
            inserir_documento(doc)
        except Exception as e:
            print(f"Erro em '{titulo}': {e}")

        # Evitar rate limit da OpenAI em contas gratuitas
        time.sleep(0.3)

    print("\n── Injeção concluída! ──")


if __name__ == "__main__":
    main()