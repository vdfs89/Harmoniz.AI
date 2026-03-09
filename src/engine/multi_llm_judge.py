import json
import os
import sys
from typing import Any, Dict

from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

load_dotenv()


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(
            f"Variavel de ambiente obrigatoria nao definida: {name}"
        )
    return value


def _as_secret(value: str) -> SecretStr:
    return SecretStr(value)


def _message_to_text(message: BaseMessage) -> str:
    content = message.content
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = [str(part) for part in content]
        return "\n".join(parts)
    return str(content)


def _build_candidates() -> Dict[str, BaseChatModel]:
    openai_key = os.getenv("OPENAI_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")

    openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    groq_model = os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile")
    gemini_model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

    candidates: Dict[str, BaseChatModel] = {}

    if openai_key:
        candidates["gpt"] = ChatOpenAI(
            model=openai_model,
            api_key=_as_secret(openai_key),
            temperature=0.2,
        )

    if groq_key:
        candidates["groq"] = ChatOpenAI(
            model=groq_model,
            api_key=_as_secret(groq_key),
            base_url="https://api.groq.com/openai/v1",
            temperature=0.2,
        )

    if gemini_key:
        candidates["gemini"] = ChatGoogleGenerativeAI(
            model=gemini_model,
            google_api_key=gemini_key,
            temperature=0.2,
        )

    if not candidates:
        raise ValueError(
            "Nenhuma chave de modelo foi configurada em .env "
            "(OPENAI_API_KEY, GROQ_API_KEY, GEMINI_API_KEY)."
        )

    return candidates


def _build_judge() -> BaseChatModel:
    judge_provider = os.getenv("JUDGE_PROVIDER", "openai").strip().lower()
    judge_model = os.getenv("JUDGE_MODEL", "gpt-4o-mini")

    if judge_provider == "openai":
        return ChatOpenAI(
            model=judge_model,
            api_key=_as_secret(_require_env("OPENAI_API_KEY")),
            temperature=0,
        )

    if judge_provider == "groq":
        return ChatOpenAI(
            model=judge_model,
            api_key=_as_secret(_require_env("GROQ_API_KEY")),
            base_url="https://api.groq.com/openai/v1",
            temperature=0,
        )

    if judge_provider == "gemini":
        return ChatGoogleGenerativeAI(
            model=judge_model,
            google_api_key=_require_env("GEMINI_API_KEY"),
            temperature=0,
        )

    raise ValueError("JUDGE_PROVIDER invalido. Use: openai, groq ou gemini.")


def _load_retrieved_context(question: str) -> str:
    persist_directory = os.getenv("VECTOR_DB_PATH", "data/processed/chroma_db")
    top_k = int(os.getenv("RAG_TOP_K", "6"))

    if not os.path.isdir(persist_directory):
        return ""

    try:
        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=_as_secret(_require_env("OPENAI_API_KEY")),
        )
        vector_db = Chroma(
            persist_directory=persist_directory,
            embedding_function=embeddings,
        )
        docs = vector_db.similarity_search(question, k=top_k)
    except Exception:
        return ""

    chunks = []
    for index, doc in enumerate(docs, start=1):
        chunks.append(f"Documento {index}:\n{doc.page_content}")

    return "\n\n".join(chunks)


def _ask_all_models(question: str, context: str) -> Dict[str, Dict[str, str]]:
    candidates = _build_candidates()
    responses: Dict[str, str] = {}
    errors: Dict[str, str] = {}

    system_prompt = (
        "Voce e um especialista em vinhos da Wine.com.br. "
        "Responda de forma clara, objetiva e util para o usuario final. "
        "Use apenas o contexto recuperado quando ele estiver disponivel. "
        "Se faltar informacao no contexto, diga isso explicitamente."
    )

    user_prompt = question
    if context:
        user_prompt = (
            f"Pergunta do usuario:\n{question}\n\n"
            f"Contexto recuperado (RAG):\n{context}"
        )

    for name, llm in candidates.items():
        try:
            answer = llm.invoke(
                [
                    ("system", system_prompt),
                    ("human", user_prompt),
                ]
            )
            responses[name] = _message_to_text(answer)
        except Exception as exc:
            errors[name] = f"{type(exc).__name__}: {exc}"

    if not responses:
        details = "; ".join([f"{k}: {v}" for k, v in errors.items()])
        raise RuntimeError(f"Todos os modelos falharam: {details}")

    return {"responses": responses, "errors": errors}


def _judge(
    question: str,
    responses: Dict[str, str],
    context: str,
) -> Dict[str, str]:
    valid_models = list(responses.keys())
    if len(valid_models) == 1:
        return {
            "winner": valid_models[0],
            "reason": "Apenas um modelo respondeu com sucesso.",
        }

    judge = _build_judge()

    context_block = "Sem contexto RAG recuperado."
    if context:
        context_block = context

    prompt = (
        "Voce e um juiz imparcial. Avalie as respostas de tres modelos de IA "
        "para a mesma pergunta.\n"
        "Criterios: precisao, aderencia ao contexto RAG, utilidade pratica, "
        "clareza e seguranca.\n"
        "Retorne APENAS JSON valido no formato:\n"
        '{"winner":"gpt|groq|gemini","reason":"motivo curto"}\n\n'
        f"Pergunta:\n{question}\n\n"
        f"Contexto RAG:\n{context_block}\n\n"
        f"Resposta GPT:\n{responses.get('gpt', 'Modelo indisponivel')}\n\n"
        f"Resposta Groq:\n{responses.get('groq', 'Modelo indisponivel')}\n\n"
        f"Resposta Gemini:\n{responses.get('gemini', 'Modelo indisponivel')}\n"
    )

    try:
        decision_raw = _message_to_text(
            judge.invoke([("human", prompt)])
        ).strip()
    except Exception:
        winner = valid_models[0]
        return {
            "winner": winner,
            "reason": "Juiz indisponivel; aplicado fallback no primeiro modelo valido.",
        }

    try:
        decision = json.loads(decision_raw)
        winner = decision.get("winner", "").strip().lower()
        reason = decision.get("reason", "")
    except json.JSONDecodeError:
        winner = ""
        reason = (
            "Resposta do juiz nao veio em JSON; "
            "aplicado fallback para GPT."
        )

    if winner not in responses:
        winner = valid_models[0]
        if not reason:
            reason = (
                "Juiz retornou vencedor invalido; "
                "aplicado fallback no primeiro modelo valido."
            )

    return {"winner": winner, "reason": reason}


def ask_with_judge(question: str) -> Dict[str, Any]:
    context = _load_retrieved_context(question)
    model_run = _ask_all_models(question, context)
    responses = model_run["responses"]
    errors = model_run["errors"]
    decision = _judge(question, responses, context)

    winner = decision["winner"]
    return {
        "winner": winner,
        "reason": decision["reason"],
        "answer": responses[winner],
        "rag_context": context,
        "all_answers": responses,
        "model_errors": errors,
    }


def main():
    if len(sys.argv) < 2:
        print("Uso: python src/engine/multi_llm_judge.py \"sua pergunta\"")
        raise SystemExit(1)

    question = " ".join(sys.argv[1:]).strip()
    result = ask_with_judge(question)

    print(f"Juiz escolheu: {result['winner']}")
    print(f"Motivo: {result['reason']}")
    print("\nResposta final:\n")
    print(result["answer"])


if __name__ == "__main__":
    main()
