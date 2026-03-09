import os


def create_structure():
    # Definicao da estrutura de pastas
    folders = [
        "data/raw",  # Para o CSV original dos vinhos
        "data/processed",  # Para a base vetorial (ChromaDB)
        "src/engine",  # Logica do RAG e LLM
        "src/utils",  # Scripts de limpeza de dados
        "notebooks",  # Para testes rapidos e visualizacoes
    ]

    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        print(f"[OK] Pasta criada: {folder}")

    # 1. Criar o ficheiro .env (Template)
    with open(".env", "w", encoding="utf-8") as f:
        f.write("# Configuracoes de API\n")
        f.write("OPENAI_API_KEY=teu_token_aqui\n")
        f.write("GROQ_API_KEY=teu_token_aqui\n")
        f.write("GEMINI_API_KEY=teu_token_aqui\n\n")
        f.write("# Configuracao dos modelos\n")
        f.write("OPENAI_MODEL=gpt-4o-mini\n")
        f.write("GROQ_MODEL=llama-3.3-70b-versatile\n")
        f.write("GEMINI_MODEL=gemini-2.0-flash\n")
        f.write("JUDGE_PROVIDER=openai\n")
        f.write("JUDGE_MODEL=gpt-4o-mini\n\n")
        f.write("# Caminhos de Dados\n")
        f.write("WINE_DATA_PATH=data/raw/wines_from_winecombr.xlsx\n")
        f.write("# Opcional (retrocompatibilidade): WINE_CSV_PATH=data/raw/wines_from_winecombr.csv\n")
        f.write("VECTOR_DB_PATH=data/processed/chroma_db\n")
    print("[OK] Ficheiro .env criado (adiciona as tuas chaves la).")

    # 2. Criar o .gitignore
    with open(".gitignore", "w", encoding="utf-8") as f:
        f.write("venv/\n")
        f.write(".env\n")
        f.write("__pycache__/\n")
        f.write(".ipynb_checkpoints/\n")
        f.write("data/processed/*\n")
        f.write("*.log\n")
    print("[OK] Ficheiro .gitignore criado.")

    # 3. Criar o requirements.txt
    with open("requirements.txt", "w", encoding="utf-8") as f:
        f.write("pandas\n")
        f.write("langchain\n")
        f.write("langchain-community\n")
        f.write("langchain-openai\n")
        f.write("chromadb\n")
        f.write("python-dotenv\n")
        f.write("ipykernel\n")
        f.write("openpyxl\n")
        f.write("langchain-google-genai\n")
    print("[OK] Ficheiro requirements.txt criado.")

    # 4. Criar um README inicial focado no projeto Wine
    with open("README.md", "w", encoding="utf-8") as f:
        f.write("# Sommelier de Dados - Wine Intelligence RAG\n\n")
        f.write(
            "Projeto de IA Generativa para recomendacao personalizada de vinhos "
        )
        f.write("utilizando RAG (Retrieval-Augmented Generation).\n\n")
        f.write("## Como executar:\n")
        f.write("1. Cria o ambiente virtual: `python -m venv venv`\n")
        f.write(
            "2. Ativa o venv: `source venv/bin/activate` (ou `.\\venv\\Scripts\\activate` no Windows)\n"
        )
        f.write("3. Instala as dependencias: `pip install -r requirements.txt`\n")
    print("[OK] README.md criado.")


if __name__ == "__main__":
    create_structure()
    print("\nProjeto Wine pronto para o VS Code!")
