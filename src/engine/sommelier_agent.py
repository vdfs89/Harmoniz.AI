"""
Sommelier Agent: LangChain Agent com Ferramentas Especializadas
============================================================

Demonstra arquitetura avançada usando:
- AgentExecutor (orquestrador de ferramentas)
- Tool Decorators (ferramentas customizadas)
- Memory (histórico de conversa)
- Fallback robusto

Requisitos da vaga: "Integrar soluções de IA aos sistemas da empresa"
Resposta: Este Agent é o padrão de produção para conectar múltiplos sistemas.
"""

import os
import sys
import shutil
from datetime import datetime
from typing import Any, Dict, Optional

from dotenv import load_dotenv
import langchain_core.retrievers as _lc_retrievers

if not hasattr(_lc_retrievers, "LangSmithRetrieverParams"):
    _lc_retrievers.LangSmithRetrieverParams = dict

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_community.vectorstores import Chroma
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI, OpenAIEmbeddings


class SimpleConversationMemory:
    """Memória mínima compatível com AgentExecutor sem depender de langchain.memory."""

    def __init__(self, memory_key="chat_history"):
        self.memory_key = memory_key
        self.chat_history = []

    def load_memory_variables(self, inputs):
        return {self.memory_key: self.chat_history}

    def save_context(self, inputs, outputs):
        self.chat_history.append({"inputs": inputs, "outputs": outputs})

    def clear(self):
        self.chat_history = []


# Import com compatibilidade 0.1.20 e 0.2+
try:
    from langchain.agents import AgentExecutor, create_openai_tools_agent
except ImportError:
    # Fallback para LangChain 0.2+ usando langgraph
    try:
        from langgraph.prebuilt import create_react_agent
        from langchain.agents import create_openai_tools_agent

        # Wrapper para compatibilidade
        class AgentExecutor:
            def __init__(
                self,
                agent,
                tools,
                memory=None,
                verbose=False,
                handle_parsing_errors=False,
                max_iterations=5,
            ):
                self.agent = agent
                self.tools = tools
                self.memory = memory
                self.verbose = verbose
                self.handle_parsing_errors = handle_parsing_errors
                self.max_iterations = max_iterations
                self._agent = create_react_agent(agent.llm, tools)

            def invoke(self, inputs):
                return self._agent.invoke(inputs)
    except ImportError as e:
        raise ImportError(
            "AgentExecutor não encontrado. Instale com:\n"
            "pip install -r requirements-pinned.txt\n"
            "Ou (stack moderna): pip install 'langchain>=0.2.0' "
            "'langgraph>=0.2.0'\n"
            "Ou (stack fixa): pip install 'langchain==0.1.20' "
            "'langchain-core==0.1.53'\n"
            f"Erro original: {e}"
        )

load_dotenv()

# Configuracoes
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


# Base vetorial
try:
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vector_db = _load_vector_db_with_recovery(embeddings)
except Exception as exc:
    print(f"[ERRO] Falha ao carregar ChromaDB: {exc}")
    sys.exit(1)


# ============================================================================
# FERRAMENTAS DO AGENT (Tools)
# ============================================================================


@tool
def buscar_vinho_no_catalogo(query: str) -> str:
    """
    Busca vinhos no catalogo da Wine usando RAG (Retrieval-Augmented Generation).
    Use esta ferramenta quando o usuario pergunta sobre recomendacoes, tipos, harmonizacoes.
    
    Args:
        query: A pergunta do usuario sobre vinhos (ex: "vinho para carne assada")
    
    Returns:
        Descricoes dos vinhos encontrados com nome, tipo, uvas, harmonizacao e preco.
    """
    try:
        docs = vector_db.similarity_search(query, k=3)
        if not docs:
            return "Nenhum vinho encontrado no catalogo para essa pergunta."
        
        resultado = "Vinhos encontrados no catalogo:\n\n"
        for i, doc in enumerate(docs, 1):
            nome = doc.metadata.get("nome", "Desconhecido")
            tipo = doc.metadata.get("tipo", "Desconhecido")
            preco = doc.metadata.get("preco", "N/A")
            resultado += f"{i}. {nome} ({tipo}) - R$ {preco}\n"
            resultado += f"   Detalhes: {doc.page_content[:200]}...\n\n"
        
        return resultado
    except Exception as e:
        return f"Erro ao buscar no catalogo: {str(e)}"


@tool
def verificar_preco_promocional(nome_vinho: str) -> str:
    """
    Verifica preco promocional e descontos (simulacao de conexao com base de dados SQL).
    Use quando o usuario pergunta sobre promocoes, descontos ou quer saber preco atualizado.
    
    Args:
        nome_vinho: Nome do vinho (ex: "Malbec Argentino")
    
    Returns:
        Informacao de preco promocional e desconto.
    """
    # Simulacao de base de dados de promocoes
    promocoes = {
        "malbec": {"desconto": 15, "validade": "30/04/2026"},
        "tinto": {"desconto": 10, "validade": "30/04/2026"},
        "branco": {"desconto": 8, "validade": "30/04/2026"},
        "espumante": {"desconto": 20, "validade": "30/04/2026"},
    }
    
    nome_lower = nome_vinho.lower()
    for key, promo in promocoes.items():
        if key in nome_lower:
            return (
                f"✓ PROMOCAO ATIVA: {promo['desconto']}% de desconto em {nome_vinho}\n"
                f"Válida até: {promo['validade']}"
            )
    
    return f"Sem promocao ativa para {nome_vinho} no momento."


@tool
def verificar_disponibilidade(nome_vinho: str) -> str:
    """
    Verifica disponibilidade de estoque (simulacao de conexao com sistema de inventario).
    Use quando o usuario pergunta se tem estoque, quando chega novo lote, etc.
    
    Args:
        nome_vinho: Nome do vinho (ex: "Cabernet Sauvignon")
    
    Returns:
        Status de disponibilidade e quantidade em estoque.
    """
    # Simulacao de inventario
    inventario = {
        "malbec argentino": 45,
        "cabernet": 30,
        "pinot noir": 12,
        "chardonnay": 67,
        "sauvignon blanc": 28,
    }
    
    nome_lower = nome_vinho.lower()
    for produto, qtd in inventario.items():
        if produto in nome_lower:
            status = "✓ EM ESTOQUE" if qtd > 5 else "⚠ ESTOQUE BAIXO"
            return f"{status}\n{nome_vinho}: {qtd} garrafas disponíveis"
    
    return f"Produto '{nome_vinho}' não encontrado no inventário."


@tool
def recomendar_harmonizacao(prato: str) -> str:
    """
    Recomenda vinhos baseado no prato que o usuario quer harmonizar.
    Use quando o usuario menciona comida ou ocasiao especifica.
    
    Args:
        prato: Tipo de prato ou ocasiao (ex: "frutos do mar", "churrasco", "pizza")
    
    Returns:
        Recomendacoes de tipo de vinho para aquele prato.
    """
    harmonizacoes = {
        "peixe": "Brancos leves como Sauvignon Blanc ou Pinot Grigio",
        "frutos do mar": "Brancos crispy ou Espumantes",
        "carne": "Tintos encorpados como Cabernet ou Malbec",
        "churrasco": "Malbec Argentino ou Cabernet forte",
        "massa": "Tintos médios como Pinot Noir ou Barbera",
        "pizza": "Tintos leves ou Espumantes",
        "queijo": "Tintos estruturados ou Brancos encorpados",
        "sobremesa": "Vinhos doces ou Espumantes moscatel",
        "aperitivo": "Espumantes ou Brancos secos",
    }
    
    prato_lower = prato.lower()
    for key, valor in harmonizacoes.items():
        if key in prato_lower:
            return f"Para {prato}:\n→ Recomendo: {valor}\n\nUse 'buscar vinho no catalogo' para encontrar opcoes."
    
    return f"Não tenho recomendacao específica para '{prato}'. Tente descrever melhor o prato."


# ============================================================================
# CONFIGURACAO DO AGENT
# ============================================================================


def criar_sommelier_agent():
    """
    Cria e configura o AgentExecutor com todas as ferramentas especializadas.
    """
    llm = ChatOpenAI(model=chat_model, temperature=0.2)
    
    # Define as ferramentas disponiveis
    tools = [
        buscar_vinho_no_catalogo,
        verificar_preco_promocional,
        verificar_disponibilidade,
        recomendar_harmonizacao,
    ]
    
    # Prompt do Agent com instrucoes claras
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """Voce e o Harmoniz.AI Agent, um Sommelier Digital expert da Wine.com.br.
Sua missao e ajudar clientes a encontrar o vinho perfeito.

Você tem acesso a 4 ferramentas especializadas:
1. buscar_vinho_no_catalogo: Para buscar vinhos por tipo, harmonizacao, etc
2. verificar_preco_promocional: Para consultar descontos e promocoes ativas
3. verificar_disponibilidade: Para confirmar estoque
4. recomendar_harmonizacao: Para sugerir vinhos baseado no prato

Estrategia:
- Primeiro, entenda o que o cliente quer (que ocasiao, qual comida, qual orcamento)
- Se ele mencionou comida, use 'recomendar_harmonizacao'
- Use 'buscar_vinho_no_catalogo' para encontrar opcoes reais
- Se ele quer saber sobre preco ou promocao, use 'verificar_preco_promocional'
- Se ele quer garantir que tem em estoque, use 'verificar_disponibilidade'
- Ao final, convide o cliente a conferir no app da Wine.com.br

Sempre seja elegante, cordial e tecnico nas respostas."""
            ),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )
    
    # Cria o agent
    agent = create_openai_tools_agent(llm=llm, tools=tools, prompt=prompt)
    
    # Cria o executor com memoria de conversa
    memory = SimpleConversationMemory(memory_key="chat_history")
    
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=False,  # Mude para True para debug
        handle_parsing_errors=True,
        max_iterations=5,
    )
    
    return agent_executor


# ============================================================================
# INTERFACE DE CONVERSA
# ============================================================================


def main():
    """Loop interativo do Agent."""
    print("\n" + "=" * 70)
    print("🍷 HARMONIZ.AI AGENT — Sommelier Digital com Ferramentas Avançadas")
    print("=" * 70)
    print("\nOlá! Sou o Sommelier Agent. Posso ajudar com:")
    print("  • Recomendacoes baseadas em prato/ocasiao")
    print("  • Consulta de precos e promocoes")
    print("  • Verificacao de disponibilidade em estoque")
    print("  • Busca no catalogo completo da Wine.com.br")
    print("\nDigite 'sair' para encerrar.\n")
    
    agent = criar_sommelier_agent()
    
    while True:
        try:
            user_input = input("Você: ").strip()
            
            if user_input.lower() in ["sair", "tchau", "exit", "quit"]:
                print("\nHarmoniz.AI Agent: Um brinde! Até logo na Wine.com.br 🥂\n")
                break
            
            if not user_input:
                continue
            
            print("\n🔄 Agent consultando ferramentas...\n")
            
            # Executa o agent (orquestra automaticamente qual ferramenta usar)
            resultado = agent.invoke({"input": user_input})
            
            resposta = resultado.get("output", "Desculpe, não consegui processar sua solicitação.")
            print(f"Harmoniz.AI Agent:\n{resposta}\n")
            print("-" * 70 + "\n")
            
        except KeyboardInterrupt:
            print("\n\nHarmoniz.AI Agent: Atendimento interrompido. Até logo!\n")
            break
        except Exception as exc:
            print(f"\n[ERRO] Falha ao processar: {exc}")
            print("Tente novamente.\n")


if __name__ == "__main__":
    main()
