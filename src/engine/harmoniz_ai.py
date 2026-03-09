import os

from dotenv import load_dotenv
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# 1. Configuracoes iniciais
load_dotenv()
persist_directory = os.getenv("VECTOR_DB_PATH", "data/processed/chroma_db")
chat_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# 2. Carregar a base vetorial criada no ingest.py
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vector_db = Chroma(
    persist_directory=persist_directory,
    embedding_function=embeddings,
)

# 3. Definicao da personalidade (system prompt)
template = """
Voce e o Harmoniz.AI, o Sommelier Digital oficial da Wine.com.br.
Sua missao e ajudar os socios do clube a encontrarem o vinho perfeito.

Diretrizes:
1. Use APENAS as informacoes do contexto abaixo para recomendar vinhos.
2. Se nao encontrar um vinho que combine perfeitamente, sugira o mais proximo e explique o porque.
3. Seja elegante, tecnico e cordial. Mencione detalhes como uvas, paladar e preco.
4. Ao final, convide o usuario a conferir o rotulo no app da Wine.

Contexto:
{context}

Pergunta do Cliente:
{question}

Resposta do Harmoniz.AI:"""

PROMPT = PromptTemplate(
    template=template,
    input_variables=["context", "question"],
)

# 4. Configuracao do modelo e da chain
llm = ChatOpenAI(model=chat_model, temperature=0.2)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vector_db.as_retriever(search_kwargs={"k": 2}),
    chain_type_kwargs={"prompt": PROMPT},
)


def perguntar_ao_sommelier(pergunta: str) -> str:
    resposta = qa_chain.invoke({"query": pergunta})
    return resposta.get("result", "Nao consegui gerar resposta.")


def main() -> None:
    print("Harmoniz.AI: Ola! Sou seu Sommelier Digital. Como posso ajudar seu paladar hoje?")
    while True:
        user_input = input("\nVoce: ").strip()
        if user_input.lower() in ["sair", "tchau", "exit"]:
            break
        if not user_input:
            continue

        print("\nConsultando adega...")
        resposta = perguntar_ao_sommelier(user_input)
        print(f"\nHarmoniz.AI: {resposta}")


if __name__ == "__main__":
    main()
