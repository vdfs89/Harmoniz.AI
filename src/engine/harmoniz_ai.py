import os
import re
import sys
from typing import Any, Dict

from dotenv import load_dotenv
from langchain.chains import RetrievalQA
from langchain.prompts import ChatPromptTemplate
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# 1. Configuracoes iniciais
load_dotenv()
persist_directory = os.getenv("VECTOR_DB_PATH", "data/processed/chroma_db")
chat_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def _extract_price_cap(question: str) -> float | None:
    # Captura frases como: "ate 100", "ate R$ 89,90".
    match = re.search(r"\bate\s*(?:r\$\s*)?(\d+[\.,]?\d*)", question.lower())
    if not match:
        return None

    try:
        return float(match.group(1).replace(",", "."))
    except ValueError:
        return None


def _format_price(value: Any) -> str:
    if isinstance(value, (int, float)):
        return f"{value:.2f}"
    return str(value)


# 2. Carregar base vetorial com resiliencia
try:
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vector_db = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings,
    )
except Exception as exc:
    print(f"[ERRO] Falha critica ao carregar ChromaDB: {exc}")
    sys.exit(1)


# 3. Persona do sommelier com ChatPromptTemplate
PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Voce e o Harmoniz.AI, o Sommelier Digital oficial da Wine.com.br.\n"
            "Sua missao e ajudar os socios do clube a encontrarem o vinho perfeito.\n\n"
            "Diretrizes:\n"
            "1. Use APENAS as informacoes do contexto abaixo para recomendar vinhos.\n"
            "2. Se nao encontrar um vinho que combine perfeitamente, sugira o mais proximo e explique o porque.\n"
            "3. Seja elegante, tecnico e cordial. Mencione detalhes como uvas, paladar e preco.\n"
            "4. Ao final, convide o usuario a conferir o rotulo no app da Wine.",
        ),
        (
            "human",
            "Contexto recuperado da adega:\n{context}\n\n"
            "Pergunta do Cliente:\n{question}\n\n"
            "Resposta do Harmoniz.AI:",
        ),
    ]
)

# 4. Modelo principal
llm = ChatOpenAI(model=chat_model, temperature=0.2)


def _build_qa_chain(question: str) -> RetrievalQA:
    search_kwargs: Dict[str, Any] = {"k": 4}

    # Pre-filtragem por metadado numerico para reduzir custo e aumentar precisao.
    price_cap = _extract_price_cap(question)
    if price_cap is not None:
        search_kwargs["filter"] = {"preco": {"$lte": price_cap}}

    retriever = vector_db.as_retriever(search_kwargs=search_kwargs)
    return RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": PROMPT},
        return_source_documents=True,
    )


def perguntar_ao_sommelier(pergunta: str) -> Dict[str, Any]:
    qa_chain = _build_qa_chain(pergunta)
    return qa_chain.invoke({"query": pergunta})


def main() -> None:
    print("\nHarmoniz.AI: Ola! Sou seu Sommelier Digital. Como posso ajudar seu paladar hoje?")
    print("(Digite 'sair' para encerrar)")

    while True:
        try:
            user_input = input("\nVoce: ").strip()

            if user_input.lower() in ["sair", "tchau", "exit", "quit"]:
                print("\nHarmoniz.AI: Foi um prazer! Um brinde e ate a proxima.\n")
                break

            if not user_input:
                continue

            print("\nConsultando adega e analisando rotulos...")
            resposta_completa = perguntar_ao_sommelier(user_input)

            texto_ia = resposta_completa.get("result", "Nao consegui gerar resposta.")
            fontes = resposta_completa.get("source_documents", [])

            print(f"\nHarmoniz.AI:\n{texto_ia}")

            if fontes:
                print("\n--- Rotulos analisados (Source Documents) ---")
                for i, doc in enumerate(fontes, 1):
                    nome_vinho = doc.metadata.get("nome", "Vinho sem nome")
                    preco_vinho = _format_price(
                        doc.metadata.get("preco", "Preco indisponivel")
                    )
                    print(f" {i}. {nome_vinho} | R$ {preco_vinho}")
                print("--------------------------------------------")

        except KeyboardInterrupt:
            print("\n\nHarmoniz.AI: Atendimento interrompido. Ate logo!\n")
            break
        except Exception as exc:
            print(f"\n[Erro de sistema] Nao consegui acessar a adega agora: {exc}")
            print("Tente novamente em instantes.")


if __name__ == "__main__":
    main()
