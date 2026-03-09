import os
from typing import Any

import pandas as pd
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

# Carregar variaveis de ambiente (.env)
load_dotenv()


def _parse_preco(value: Any) -> float:
    # Suporta preco numerico, com virgula decimal e/ou com simbolo de moeda.
    text = str(value).replace("R$", "").replace(" ", "").replace(",", ".")
    return float(text)


def _load_wine_table(file_path: str):
    extension = os.path.splitext(file_path)[1].lower()
    if extension == ".csv":
        return pd.read_csv(file_path)
    if extension in {".xlsx", ".xls"}:
        return pd.read_excel(file_path)
    raise ValueError(
        "Formato nao suportado. Use um ficheiro .csv, .xlsx ou .xls."
    )


def ingest_data():
    data_path = os.getenv("WINE_DATA_PATH") or os.getenv("WINE_CSV_PATH")
    persist_directory = os.getenv("VECTOR_DB_PATH")

    print(f"A carregar dados de: {data_path}")

    # 1. Ler dados do CSV/Excel (utilizando os dados que carregaste)
    df = _load_wine_table(data_path)

    # Limpeza basica: remover linhas sem nome ou descricao essencial
    df = df.dropna(subset=["Nome", "Harmonização"])

    # 2. Criar o "Contexto Rico" para cada vinho
    # Concatenamos colunas tecnicas para montar um perfil sensorial rico.
    documents = []
    for _, row in df.iterrows():
        content = (
            f"Vinho: {row['Nome']}\n"
            f"Tipo: {row['Tipo']} | Uvas: {row['Uvas']}\n"
            f"Olfato: {row['Olfato']}\n"
            f"Paladar: {row['Paladar']}\n"
            f"Harmonização: {row['Harmonização']}\n"
            f"Preço: R$ {row['Preço']}"
        )

        # Metadados permitem filtros futuros (tipo, pais, faixa de preco).
        doc = Document(
            page_content=content,
            metadata={
                "nome": row["Nome"],
                "tipo": row["Tipo"],
                "pais": row["País"],
                "preco": _parse_preco(row["Preço"]),
            },
        )
        documents.append(doc)

    print(f"Gerando embeddings para {len(documents)} vinhos...")

    # 3. Inicializar o modelo de Embeddings e a Vector Store (ChromaDB)
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=persist_directory,
    )

    print(f"Sucesso! Base vetorial criada e guardada em: {persist_directory}")


if __name__ == "__main__":
    ingest_data()
