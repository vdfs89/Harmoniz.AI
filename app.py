"""
🍷 Harmoniz.AI — Streamlit Web Interface
========================================

Interface visual profissional que integra:
  • Chat RAG (Rápido)
  • Agent com ferramentas (Completo)
  • Judge multi-modelo (Qualidade máxima)

Deploy: streamlit run app.py
Streamlit Cloud: https://harmonizai.streamlit.app/
"""

import os
from typing import Dict, Any, Optional

import streamlit as st
from dotenv import load_dotenv
from src.engine.ingest import ingest_data

# Carrega variáveis de ambiente
load_dotenv()

VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "data/processed/chroma_db")
DEFAULT_HERO_IMAGE = "img/ChatGPT Image 24 de abr. de 2026, 21_52_30.png"
PREFERRED_HERO_IMAGE = os.getenv("HERO_IMAGE_PATH", "image_fe97d0.jpg")


def _ensure_vector_db_ready() -> None:
    if os.path.isdir(VECTOR_DB_PATH):
        try:
            with os.scandir(VECTOR_DB_PATH) as entries:
                if any(entries):
                    return
        except FileNotFoundError:
            pass

    with st.spinner("Primeira vez aqui? A preparar a adega digital..."):
        try:
            ingest_data()
        except Exception as exc:
            st.error(
                "❌ Erro ao preparar a base vetorial. Confirme WINE_DATA_PATH e API Keys."
            )
            st.exception(exc)
            st.stop()


_ensure_vector_db_ready()


def _resolve_hero_image_path() -> Optional[str]:
    candidates: list[str] = []

    base_candidate = PREFERRED_HERO_IMAGE.strip() if PREFERRED_HERO_IMAGE else ""
    if base_candidate:
        candidates.append(base_candidate)
        basename = os.path.basename(base_candidate)
        if basename and basename != base_candidate:
            candidates.append(basename)
        if basename:
            candidates.append(os.path.join("img", basename))

    candidates.append(DEFAULT_HERO_IMAGE)

    seen: set[str] = set()
    for path in candidates:
        if not path:
            continue
        normalized = os.path.normpath(path)
        if normalized in seen:
            continue
        seen.add(normalized)
        if os.path.exists(normalized):
            return normalized
    return None


def _render_hero_banner() -> None:
    hero_path = _resolve_hero_image_path()
    if not hero_path:
        return

    st.image(
        hero_path,
        caption="Harmoniz.AI — Adega Generativa",
        use_container_width=True,
    )


# Imports dos 3 modos
try:
    from src.engine.harmoniz_ai import perguntar_ao_sommelier
    from src.engine.sommelier_agent import criar_sommelier_agent
    from src.engine.multi_llm_judge import ask_with_judge
except ImportError as e:
    st.error(f"❌ Erro ao carregar módulos: {e}")
    st.stop()

# ============================================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================================

st.set_page_config(
    page_title="Harmoniz.AI — Sommelier Digital",
    page_icon="🍷",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS + Identidade Visual
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Montserrat:wght@300;400;600&display=swap');

    /* 1. Fundo da Página (Bordô Profundo da Imagem) */
    .stApp {
        background-color: #5D101D;
    }

    /* 2. Título Centralizado */
    .logo-container {
        text-align: center;
        padding: 20px 0;
    }

    .logo-text {
        font-family: 'Playfair Display', serif;
        font-size: 5rem;
        font-weight: 900;
        margin-bottom: 0;
        line-height: 1;
    }

    /* AMARELO OURO para 'Harmoniz' */
    .harmoniz {
        color: #F1C40F;
        text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.4);
    }

    /* VERMELHO BRILHANTE para '.AI' e Tagline */
    .ai-suffix, .tagline {
        color: #FF0033 !important;
        text-transform: uppercase;
    }

    .tagline {
        font-family: 'Montserrat', sans-serif;
        letter-spacing: 4px;
        font-weight: 600;
        font-size: 0.8rem;
        margin-top: 10px;
        opacity: 1;
    }

    /* 3. Textos do Chat e Labels */
    .stMarkdown, p, span, label {
        color: #FFFFFF !important;
        font-family: 'Montserrat', sans-serif;
    }

    /* Balões de Chat Elegantes */
    [data-testid="stChatMessage"] {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border-radius: 20px;
        border: 1px solid #FF0033;
    }

    /* 4. Imagem do Logo (Selo Circular) */
    .hero-img {
        display: block;
        margin: 0 auto 15px auto;
        width: 140px;
        height: 140px;
        object-fit: cover;
        border-radius: 50%;
        border: 4px solid #F1C40F;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.6);
    }

    /* 5. Sidebar e botões mantêm coerência luxuosa */
    [data-testid="stSidebar"] {
        background-color: #3D0A13 !important;
        border-right: 1px solid #FF0033;
    }

    .stButton>button {
        background-color: transparent;
        color: #F1C40F !important;
        border: 2px solid #F1C40F !important;
        border-radius: 30px;
        font-weight: 600;
        transition: 0.3s;
    }

    .stButton>button:hover {
        background-color: #F1C40F;
        color: #5D101D !important;
    }

    /* 6. Badges do modo */
    .mode-badge {
        display: inline-block;
        padding: 0.35rem 1.2rem;
        border-radius: 999px;
        font-weight: 600;
        border: 1px solid rgba(255, 255, 255, 0.3);
    }

    .mode-chat { background-color: rgba(244, 196, 48, 0.15); color: #F4C430; }
    .mode-agent { background-color: rgba(255, 0, 51, 0.15); color: #FF0033; }
    .mode-judge { background-color: rgba(255, 255, 255, 0.15); color: #FFFFFF; }
    </style>

    <div class="logo-container">
        <img src="https://github.com/vdfs89/Harmoniz.AI/raw/main/image_fe2a58.jpg" class="hero-img">
        <h1 class="logo-text">
            <span class="harmoniz">Harmoniz</span><span class="ai-suffix">.AI</span>
        </h1>
        <p class="tagline">Sommelier Digital — Inteligência Wine.com.br</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================================
# SIDEBAR — CONFIGURAÇÃO
# ============================================================================

with st.sidebar:
    st.markdown("# ⚙️ Configurações")
    st.divider()

    # Seleção de modo
    st.markdown("## Modo de Operação")
    modo = st.radio(
        label="Escolha como deseja consultar:",
        options=["💨 Chat RAG (Rápido)", "🤖 Agente (Completo)", "🏆 Juiz (Multi-LLM)"],
        help="Cada modo tem diferentes trade-offs de latência vs. qualidade",
    )

    st.divider()

    # Descrição do modo
    st.markdown("### ℹ️ Sobre este Modo")
    if "Chat RAG" in modo:
        st.markdown("""
        **⚡ Modo RAG Ultra-Rápido**
        
        - Latência: **< 500ms**
        - Custo: **Mínimo**
        - Melhor para: Buscas simples, dia-a-dia
        
        *Usa Self-Querying + ChromaDB + LCEL*
        """)
    elif "Agente" in modo:
        st.markdown("""
        **🤖 Modo Agent Inteligente**
        
        - Latência: **1-3s**
        - Custo: **Médio**
        - Melhor para: Consultas complexas, CRM/ERP
        
        *Orquestra 4 ferramentas automaticamente:*
        - 🔍 Busca no catálogo
        - 💰 Verifica promoções
        - 📦 Consulta estoque
        - 🍴 Harmonização
        """)
    else:
        st.markdown("""
        **🏆 Modo Judge (Multi-LLM)**
        
        - Latência: **3-5s**
        - Custo: **3x maior (máxima qualidade)**
        - Melhor para: Consultas críticas, curadoria
        
        *Compara 3 modelos em paralelo:*
        - 🔵 GPT-4o-mini (OpenAI)
        - 🟢 Llama-3.3 (Groq)
        - 🟡 Gemini-2.0 (Google)
        """)

    st.divider()

    # Controles
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Limpar Histórico", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

    with col2:
        if st.button("📊 Métricas", use_container_width=True):
            st.session_state.show_metrics = not st.session_state.get(
                "show_metrics", False
            )
            st.rerun()

    st.divider()

    # Info Footer
    st.markdown("""
    ---
    **📍 Harmoniz.AI v1.0**
    
    Sommelier Digital para Wine.com.br
    
    [🔗 GitHub](https://github.com/vdfs89/Harmoniz.AI) | 
    [📚 Docs](https://github.com/vdfs89/Harmoniz.AI#readme)
    """)

# ============================================================================
# INICIALIZAÇÃO DE ESTADO
# ============================================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "modo_atual" not in st.session_state:
    st.session_state.modo_atual = modo

if "show_metrics" not in st.session_state:
    st.session_state.show_metrics = False

if "agent_executor" not in st.session_state:
    # Pre-carrega Agent pra evitar latência na primeira interação
    if "Agente" in modo:
        st.session_state.agent_executor = criar_sommelier_agent()

# ============================================================================
# HEADER
# ============================================================================

col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("# 🍷 Harmoniz.AI")
    st.markdown("**Sommelier Digital** — Seu guia de vinhos inteligente da Wine.com.br")

with col2:
    # Badge do modo
    if "Chat RAG" in modo:
        st.markdown(
            '<span class="mode-badge mode-chat">💨 RÁPIDO</span>',
            unsafe_allow_html=True,
        )
    elif "Agente" in modo:
        st.markdown(
            '<span class="mode-badge mode-agent">🤖 INTELIGENTE</span>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<span class="mode-badge mode-judge">🏆 PREMIUM</span>',
            unsafe_allow_html=True,
        )

_render_hero_banner()

st.divider()

# ============================================================================
# HISTÓRICO DE MENSAGENS
# ============================================================================

# Exibe mensagens anteriores
for message in st.session_state.messages:
    with st.chat_message(
        message["role"], avatar="🧑‍💼" if message["role"] == "user" else "🍷"
    ):
        st.markdown(message["content"])

        # Exibe metadata se disponível
        if "metadata" in message and message["metadata"]:
            with st.expander("📊 Detalhes"):
                for chave, valor in message["metadata"].items():
                    if isinstance(valor, list):
                        st.write(f"**{chave}:**")
                        for item in valor:
                            st.write(f"  • {item}")
                    else:
                        st.write(f"**{chave}:** {valor}")

# ============================================================================
# INPUT DO USUÁRIO
# ============================================================================

prompt = st.chat_input(
    placeholder="Como posso ajudar o seu paladar hoje? (ex: 'Vinho para churrasco')",
    key="chat_input",
)

if prompt:
    # Adiciona pergunta ao histórico
    st.session_state.messages.append(
        {"role": "user", "content": prompt, "metadata": None}
    )

    # Exibe pergunta
    with st.chat_message("user", avatar="🧑‍💼"):
        st.markdown(prompt)

    # Processamento e resposta
    with st.chat_message("assistant", avatar="🍷"):
        with st.spinner("🔄 Consultando adega..."):
            try:
                # ============================================================
                # MODO 1: CHAT RAG (RÁPIDO)
                # ============================================================
                if "Chat RAG" in modo:
                    resultado = perguntar_ao_sommelier(prompt)
                    resposta = resultado["result"]

                    # Exibe resposta
                    st.markdown(resposta)

                    # Metadados
                    metadata = {}

                    if resultado.get("filters_applied"):
                        st.info(
                            f"🔍 **Filtros aplicados:** {', '.join(resultado['filters_applied'])}"
                        )
                        metadata["Filtros"] = resultado["filters_applied"]

                    if resultado.get("source_documents"):
                        with st.expander(
                            f"📚 Fontes ({len(resultado['source_documents'])} documentos)"
                        ):
                            for doc in resultado["source_documents"]:
                                nome = doc.metadata.get("nome", "Desconhecido")
                                tipo = doc.metadata.get("tipo", "")
                                preco = doc.metadata.get("preco", "N/A")
                                pais = doc.metadata.get("pais", "")
                                st.write(f"**{nome}** ({tipo}) - {pais} - R$ {preco}")

                        metadata["Fontes"] = [
                            doc.metadata.get("nome")
                            for doc in resultado["source_documents"]
                        ]

                # ============================================================
                # MODO 2: AGENT (COMPLETO)
                # ============================================================
                elif "Agente" in modo:
                    # Cria ou recupera agent
                    if "agent_executor" not in st.session_state:
                        st.session_state.agent_executor = criar_sommelier_agent()

                    agent = st.session_state.agent_executor
                    resultado = agent.invoke({"input": prompt})
                    resposta = resultado["output"]

                    # Exibe resposta
                    st.markdown(resposta)

                    # Metadados
                    metadata = {
                        "Modo": "Agent",
                        "Ferramentas": "🔍 Busca, 💰 Promoção, 📦 Estoque, 🍴 Harmonização",
                    }

                # ============================================================
                # MODO 3: JUDGE (MULTI-LLM)
                # ============================================================
                else:  # Judge
                    resultado = ask_with_judge(prompt)
                    resposta = resultado.get("answer", resultado.get("output", ""))

                    # Exibe resposta
                    st.markdown(resposta)

                    # Informação do vencedor
                    winner = resultado.get("winner", "Unknown")
                    reason = resultado.get("reason", "")

                    st.success(f"🏆 **Modelo vencedor:** {winner}")
                    st.info(f"**Motivo:** {reason}")

                    # Scores dos modelos
                    if resultado.get("all_answers"):
                        with st.expander("📊 Comparação de modelos"):
                            cols = st.columns(len(resultado["all_answers"]))
                            for col, (model_name, response) in zip(
                                cols, resultado["all_answers"].items()
                            ):
                                with col:
                                    st.write(f"**{model_name}**")
                                    st.write(response[:150] + "...")

                    # Metadados
                    metadata = {
                        "Vencedor": winner,
                        "Razão": reason,
                        "Modelos": list(resultado.get("all_answers", {}).keys()),
                    }

                # Adiciona resposta ao histórico
                st.session_state.messages.append(
                    {"role": "assistant", "content": resposta, "metadata": metadata}
                )

            except Exception as e:
                st.error(f"❌ Erro ao processar: {str(e)}")
                st.info(
                    "**Dica:** Certifique-se que:\n"
                    "1. .env está configurado com as API keys\n"
                    "2. ChromaDB foi carregado (execute ingest.py)\n"
                    "3. O modo selecionado tem todos os modelos configurados"
                )

# ============================================================================
# FOOTER COM MÉTRICAS (Opcional)
# ============================================================================

if st.session_state.get("show_metrics") and st.session_state.messages:
    st.divider()
    st.markdown("### 📊 Estatísticas da Conversa")

    col1, col2, col3, col4 = st.columns(4)

    total_msgs = len(st.session_state.messages)
    user_msgs = sum(1 for m in st.session_state.messages if m["role"] == "user")
    assistant_msgs = total_msgs - user_msgs

    with col1:
        st.metric("Total de mensagens", total_msgs)
    with col2:
        st.metric("Perguntas", user_msgs)
    with col3:
        st.metric("Respostas", assistant_msgs)
    with col4:
        st.metric(
            "Modo atual",
            "RAG" if "Chat RAG" in modo else ("Agent" if "Agente" in modo else "Judge"),
        )
