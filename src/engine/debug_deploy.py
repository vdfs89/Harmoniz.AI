import os
import sys

import streamlit as st


def run_diagnostics() -> None:
    print("=== HARMONIZ.AI - DIAGNOSTICO DE SISTEMA ===")

    print("\n1. VERSOES:")
    print(f"- Python: {sys.version}")
    try:
        import langchain  # type: ignore
        import langchain_community  # noqa: F401
        import chromadb  # type: ignore

        print(f"- LangChain: {langchain.__version__}")
        print(f"- ChromaDB: {chromadb.__version__}")
    except ImportError as exc:
        print(f"ERRO DE DEPENDENCIA: {exc}")

    print("\n2. SEGREDOS (Ambiente):")
    keys_to_check = ["OPENAI_API_KEY", "VECTOR_DB_PATH", "LANGCHAIN_API_KEY"]
    for key in keys_to_check:
        env_val = os.getenv(key)
        secret_val = st.secrets.get(key) if key in st.secrets else None
        effective_val = env_val or secret_val
        status = "OK" if effective_val else "EM FALTA"
        print(f"- {key}: {status}")

    print("\n3. INFRAESTRUTURA DE DADOS:")
    db_path = os.getenv("VECTOR_DB_PATH", "data/processed/chroma_db")
    print(f"- Caminho DB configurado: {db_path}")
    if os.path.exists(db_path):
        print("- Pasta da Base Vetorial: EXISTE")
        files = os.listdir(db_path)
        print(f"- Ficheiros na DB: {len(files)} detetados")
    else:
        print("- Pasta da Base Vetorial: NAO ENCONTRADA")

    print("\n4. TESTE DE MODULOS ESPECIFICOS:")
    try:
        from langchain.memory import ConversationBufferMemory  # noqa: F401

        print("- langchain.memory: CARREGADO")
    except Exception as exc:  # broad to surface precise failure
        print(f"- langchain.memory: ERRO: {exc}")
        print("   Solucao: Instala 'pip install langchain --upgrade'")


if __name__ == "__main__":
    run_diagnostics()
