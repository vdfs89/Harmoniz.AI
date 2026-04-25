import os
import re
import shutil
from datetime import datetime
from typing import Any, Dict, Optional

from dotenv import load_dotenv
import langchain_core.retrievers as _lc_retrievers

if not hasattr(_lc_retrievers, "LangSmithRetrieverParams"):
    _lc_retrievers.LangSmithRetrieverParams = dict

from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# 1. Configuracoes iniciais
load_dotenv()
persist_directory = os.getenv("VECTOR_DB_PATH", "data/processed/chroma_db")
chat_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def _load_vector_db_with_recovery(embedding_model: OpenAIEmbeddings) -> Chroma:
    """Carrega ChromaDB e recria o diretório se detectar schema legado incompatível."""
    try:
        return Chroma(
            persist_directory=persist_directory,
            embedding_function=embedding_model,
        )
    except Exception as exc:
        if "no such column: collections.topic" not in str(exc):
            raise

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        legacy_path = f"{persist_directory}_legacy_{timestamp}"

        print(
            "[WARN] Schema legado do ChromaDB detectado. "
            f"Movendo base antiga para: {legacy_path}"
        )

        target_directory = persist_directory
        try:
            if os.path.isdir(persist_directory):
                shutil.move(persist_directory, legacy_path)
            os.makedirs(persist_directory, exist_ok=True)
        except PermissionError:
            # Windows pode manter o sqlite bloqueado por outro processo.
            target_directory = f"{persist_directory}_recovered_{timestamp}"
            os.makedirs(target_directory, exist_ok=True)
            print(
                "[WARN] Nao foi possivel mover a base antiga (arquivo bloqueado). "
                f"Usando novo diretorio: {target_directory}"
            )

        print("[INFO] Criando nova base Chroma vazia e compatível...")
        return Chroma(
            persist_directory=target_directory,
            embedding_function=embedding_model,
        )


def _extract_price_cap(question: str) -> Optional[float]:
    # Captura frases como: "ate 100", "ate R$ 89,90".
    match = re.search(r"\bate\s*(?:r\$\s*)?(\d+[\.,]?\d*)", question.lower())
    if not match:
        return None

    try:
        return float(match.group(1).replace(",", "."))
    except ValueError:
        return None


def _extract_country_filter(question: str) -> Optional[str]:
    # Captura filtros por pais: "argentino", "chileno", "italiano", etc
    countries = {
        "argentina": "Argentina",
        "argentino": "Argentina",
        "chile": "Chile",
        "chileno": "Chile",
        "italia": "Italia",
        "italiano": "Italia",
        "portugal": "Portugal",
        "portugues": "Portugal",
        "españa": "Espanha",
        "espanha": "Espanha",
        "espanhol": "Espanha",
        "franca": "França",
        "france": "França",
        "frances": "França",
    }
    question_lower = question.lower()
    for key, val in countries.items():
        if key in question_lower:
            return val
    return None


def _format_price(value: Any) -> str:
    if isinstance(value, (int, float)):
        return f"{value:.2f}"
    return str(value)


# 2. Carregar base vetorial com resiliencia
try:
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vector_db = _load_vector_db_with_recovery(embeddings)
except Exception as exc:
    print(f"[ERRO] Falha critica ao carregar ChromaDB: {exc}")
    raise


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


def _build_retriever_with_filters(question: str):
    """
    Cria um retriever com filtros inteligentes baseados na pergunta do usuario.
    Implementa Self-Querying RAG: o LLM detecta automaticamente filtros desejados.
    """
    search_kwargs: Dict[str, Any] = {"k": 4}
    filters_applied = []

    # Filtro 1: Preco (pre-filtragem)
    price_cap = _extract_price_cap(question)
    if price_cap is not None:
        search_kwargs["filter"] = {"preco": {"$lte": price_cap}}
        filters_applied.append(f"preco <= R${price_cap:.2f}")

    # Filtro 2: Pais (pre-filtragem para Self-Querying)
    country = _extract_country_filter(question)
    if country is not None:
        if "filter" in search_kwargs:
            search_kwargs["filter"]["pais"] = country
        else:
            search_kwargs["filter"] = {"pais": country}
        filters_applied.append(f"pais = {country}")

    return vector_db.as_retriever(search_kwargs=search_kwargs), filters_applied


def _format_docs(docs: list[Document]) -> str:
    """Formata documentos recuperados para o prompt."""
    return "\n\n".join(doc.page_content for doc in docs)


def _build_lcel_chain(question: str):
    """
    Constroi uma chain usando LCEL (LangChain Expression Language).
    Isso e a forma moderna e recomendada pela equipe do LangChain.
    """
    retriever, filters_applied = _build_retriever_with_filters(question)

    # LCEL: Define a sequencia de operacoes de forma declarativa
    chain = (
        {
            "context": retriever | _format_docs,
            "question": RunnablePassthrough(),
        }
        | PROMPT
        | llm
        | StrOutputParser()
    )

    return chain, retriever, filters_applied


def perguntar_ao_sommelier(pergunta: str) -> Dict[str, Any]:
    """
    Interface publica que mantém compatibilidade com o codigo anterior,
    mas agora usa LCEL + Self-Querying internamente.
    """
    chain, retriever, filters_applied = _build_lcel_chain(pergunta)

    # Executa a chain LCEL (entrada deve ser apenas a pergunta)
    resposta_texto = chain.invoke(pergunta)

    # Recupera tambem os documentos para exibicao (API nova do LangChain 0.2/0.3)
    if hasattr(retriever, "invoke"):
        docs = retriever.invoke(pergunta)
    elif hasattr(retriever, "get_relevant_documents"):
        docs = retriever.get_relevant_documents(pergunta)
    else:
        docs = []

    return {
        "result": resposta_texto,
        "source_documents": docs,
        "filters_applied": filters_applied,
    }


def main() -> None:
    print("\nHarmoniz.AI: Ola! Sou seu Sommelier Digital. Como posso ajudar seu paladar hoje?")
    print("Teste filtros como: 'tinto argentino ate 80 reais' ou 'vinho italiano para frutos do mar'")
    print("(Digite 'sair' para encerrar)\n")

    while True:
        try:
            user_input = input("Voce: ").strip()

            if user_input.lower() in ["sair", "tchau", "exit", "quit"]:
                print("\nHarmoniz.AI: Foi um prazer! Um brinde e ate a proxima.\n")
                break

            if not user_input:
                continue

            print("\nConsultando adega e analisando rotulos...")
            resposta_completa = perguntar_ao_sommelier(user_input)

            texto_ia = resposta_completa.get("result", "Nao consegui gerar resposta.")
            fontes = resposta_completa.get("source_documents", [])
            filtros = resposta_completa.get("filters_applied", [])

            print(f"\nHarmoniz.AI:\n{texto_ia}")

            # Exibe filtros detectados (Self-Querying)
            if filtros:
                print("\n--- Filtros detectados automaticamente (Self-Querying) ---")
                for filtro in filtros:
                    print(f" • {filtro}")
                print("-------------------------------------------------------")

            # Exibe as fontes (Source Documents)
            if fontes:
                print("\n--- Rotulos analisados (Source Documents) ---")
                for i, doc in enumerate(fontes, 1):
                    nome_vinho = doc.metadata.get("nome", "Vinho sem nome")
                    preco_vinho = _format_price(
                        doc.metadata.get("preco", "Preco indisponivel")
                    )
                    pais_vinho = doc.metadata.get("pais", "Pais desconhecido")
                    print(f" {i}. {nome_vinho} | {pais_vinho} | R$ {preco_vinho}")
                print("--------------------------------------------")

        except KeyboardInterrupt:
            print("\n\nHarmoniz.AI: Atendimento interrompido. Ate logo!\n")
            break
        except Exception as exc:
            print(f"\n[Erro de sistema] Nao consegui acessar a adega agora: {exc}")
            print("Tente novamente em instantes.")


if __name__ == "__main__":
    main()
