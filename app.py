"""
🍷 Harmoniz.AI — Streamlit Web Interface
========================================
Identidade visual fiel à marca: cores, tipografia e estética exatas.
"""

import os
from typing import Dict, Any

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────────────────────
# PRÉ-REQUISITO: garante base vetorial antes de qualquer import
# ─────────────────────────────────────────────────────────────
VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "data/processed/chroma_db")


def _ensure_vector_db_ready() -> None:
    if os.path.isdir(VECTOR_DB_PATH):
        try:
            with os.scandir(VECTOR_DB_PATH) as entries:
                if any(entries):
                    return
        except FileNotFoundError:
            pass
    with st.spinner("Preparando a adega digital pela primeira vez..."):
        try:
            from src.engine.ingest import ingest_data

            ingest_data()
        except Exception as exc:  # noqa: BLE001
            st.error("❌ Erro ao preparar a base vetorial. Confirme WINE_DATA_PATH e API Keys.")
            st.exception(exc)
            st.stop()


_ensure_vector_db_ready()

# ─────────────────────────────────────────────────────────────
# CACHE — carrega recursos pesados uma única vez
# ─────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def _load_sommelier():
    from src.engine.harmoniz_ai import perguntar_ao_sommelier

    return perguntar_ao_sommelier


@st.cache_resource(show_spinner=False)
def _load_agent():
    try:
        from src.engine.sommelier_agent import criar_sommelier_agent

        return criar_sommelier_agent(), None
    except Exception as exc:  # noqa: BLE001
        return None, str(exc)


@st.cache_resource(show_spinner=False)
def _load_judge():
    from src.engine.multi_llm_judge import ask_with_judge

    return ask_with_judge


def _load_engines() -> tuple[Any, Any, Any, Any]:
    try:
        sommelier = _load_sommelier()
        agent_executor, agent_error = _load_agent()
        judge = _load_judge()
    except ImportError as exc:  # pragma: no cover - erro fatal
        st.error(f"❌ Erro ao carregar módulos: {exc}")
        st.stop()

    return sommelier, agent_executor, agent_error, judge


perguntar_ao_sommelier, _agent_executor, _agent_error, ask_with_judge = _load_engines()

# ─────────────────────────────────────────────────────────────
# CONFIGURAÇÃO DA PÁGINA
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Harmoniz.AI — Sommelier Digital",
    page_icon="🍷",
    layout="wide",
    initial_sidebar_state="expanded",
)

DESIGN_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,900;1,700&family=Inter:wght@300;400;500;600&display=swap');

/* ── RESET & BASE ── */
*, *::before, *::after { box-sizing: border-box; }

.stApp {
    background-color: #1A0008;
    background-image:
        radial-gradient(ellipse 80% 60% at 50% -20%, rgba(124, 20, 40, 0.35) 0%, transparent 70%),
        radial-gradient(ellipse 40% 30% at 90% 80%, rgba(201, 168, 112, 0.08) 0%, transparent 60%);
    font-family: 'Inter', sans-serif;
}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #2D0010 0%, #1A0008 100%) !important;
    border-right: 1px solid rgba(201, 168, 112, 0.25) !important;
}
[data-testid="stSidebar"] > div { padding-top: 0 !important; }

/* ── TYPOGRAPHY OVERRIDE ── */
h1, h2, h3, h4, h5, h6,
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
    font-family: 'Playfair Display', serif !important;
    color: #C9A870 !important;
}
p, span, li, label, div {
    color: #F2E8D4;
    font-family: 'Inter', sans-serif;
}

/* ── LOGO PRINCIPAL ── */
.hm-hero {
    text-align: center;
    padding: 48px 0 32px;
    position: relative;
}
.hm-hero::after {
    content: '';
    display: block;
    width: 120px;
    height: 1px;
    background: linear-gradient(90deg, transparent, #C9A870, transparent);
    margin: 20px auto 0;
}
.hm-logo {
    font-family: 'Playfair Display', serif;
    font-size: clamp(3rem, 8vw, 5.5rem);
    font-weight: 900;
    letter-spacing: -1px;
    line-height: 1;
    margin: 0;
    padding: 0;
}
.hm-logo-harmoniz { color: #C9A870; }
.hm-logo-dot      { color: #C9A870; opacity: 0.6; }
.hm-logo-ai       { color: #C41E52; }
.hm-tagline-main {
    font-family: 'Inter', sans-serif;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 6px;
    text-transform: uppercase;
    color: rgba(242, 232, 212, 0.55) !important;
    margin: 14px 0 4px;
}
.hm-tagline-sub {
    font-family: 'Playfair Display', serif;
    font-style: italic;
    font-size: 1rem;
    color: rgba(242, 232, 212, 0.65) !important;
    margin: 0;
}

/* ── BADGE DE MODO ── */
.hm-mode-wrap { text-align: center; margin: 0 0 32px; }
.hm-badge {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    padding: 5px 18px;
    border-radius: 999px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 2px;
    text-transform: uppercase;
}
.hm-badge-rag    { border: 1px solid rgba(201,168,112,0.5); color: #C9A870; background: rgba(201,168,112,0.08); }
.hm-badge-agent  { border: 1px solid rgba(196, 30, 82, 0.5); color: #C41E52; background: rgba(196,30,82,0.08); }
.hm-badge-judge  { border: 1px solid rgba(242,232,212,0.25); color: #F2E8D4; background: rgba(242,232,212,0.06); }

/* ── SIDEBAR LOGO ── */
.sb-logo {
    padding: 28px 20px 20px;
    border-bottom: 1px solid rgba(201, 168, 112, 0.15);
    margin-bottom: 8px;
}
.sb-logo-text {
    font-family: 'Playfair Display', serif;
    font-size: 1.6rem;
    font-weight: 900;
    line-height: 1;
}
.sb-logo-sub {
    font-size: 0.6rem;
    letter-spacing: 4px;
    text-transform: uppercase;
    color: rgba(242,232,212,0.4) !important;
    margin-top: 4px;
}

/* ── SIDEBAR LABELS & RADIO ── */
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stRadio label {
    color: rgba(242, 232, 212, 0.8) !important;
    font-size: 0.85rem;
}
[data-testid="stSidebar"] .stRadio [data-testid="stMarkdownContainer"] p {
    color: rgba(242, 232, 212, 0.9) !important;
}

/* ── CHAT MESSAGES ── */
[data-testid="stChatMessage"] {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(201, 168, 112, 0.15) !important;
    border-radius: 16px !important;
    backdrop-filter: blur(4px);
}
[data-testid="stChatMessage"][data-testid*="user"] {
    border-color: rgba(196, 30, 82, 0.2) !important;
}

/* ── CHAT INPUT ── */
[data-testid="stChatInput"] {
    background: rgba(61, 0, 16, 0.6) !important;
    border: 1px solid rgba(201, 168, 112, 0.3) !important;
    border-radius: 12px !important;
    color: #F2E8D4 !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: rgba(196, 30, 82, 0.6) !important;
    box-shadow: 0 0 0 3px rgba(196, 30, 82, 0.1) !important;
}
[data-testid="stChatInput"] textarea,
[data-testid="stChatInput"] input {
    color: #F2E8D4 !important;
    background: transparent !important;
}

/* ── BUTTONS ── */
.stButton > button {
    background: transparent !important;
    border: 1px solid rgba(201, 168, 112, 0.45) !important;
    color: #C9A870 !important;
    border-radius: 8px !important;
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.5px;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    background: rgba(201, 168, 112, 0.12) !important;
    border-color: #C9A870 !important;
}

/* ── ALERTS / CALLOUTS ── */
.stSuccess, [data-testid="stAlert"][kind="success"] {
    background: rgba(201, 168, 112, 0.1) !important;
    border-left: 3px solid #C9A870 !important;
    border-radius: 8px !important;
    color: #C9A870 !important;
}
.stInfo, [data-testid="stAlert"][kind="info"] {
    background: rgba(196, 30, 82, 0.08) !important;
    border-left: 3px solid rgba(196, 30, 82, 0.5) !important;
    border-radius: 8px !important;
    color: rgba(242,232,212,0.85) !important;
}
.stError, [data-testid="stAlert"][kind="error"] {
    background: rgba(196, 30, 82, 0.12) !important;
    border-left: 3px solid #C41E52 !important;
    border-radius: 8px !important;
}

/* ── EXPANDER ── */
details {
    background: rgba(61, 0, 16, 0.4) !important;
    border: 1px solid rgba(201, 168, 112, 0.18) !important;
    border-radius: 10px !important;
}
details summary {
    color: rgba(201, 168, 112, 0.8) !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
}

/* ── METRICS ── */
[data-testid="stMetric"] {
    background: rgba(61, 0, 16, 0.5) !important;
    border: 1px solid rgba(201, 168, 112, 0.15) !important;
    border-radius: 10px !important;
    padding: 12px 16px !important;
}
[data-testid="stMetric"] label {
    color: rgba(242, 232, 212, 0.5) !important;
    font-size: 0.72rem !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
}
[data-testid="stMetricValue"] {
    color: #C9A870 !important;
    font-family: 'Playfair Display', serif !important;
}

/* ── DIVIDER ── */
hr {
    border: none !important;
    height: 1px !important;
    background: linear-gradient(90deg, transparent, rgba(201,168,112,0.3), transparent) !important;
    margin: 16px 0 !important;
}

/* ── SPINNER ── */
[data-testid="stSpinner"] {
    color: #C9A870 !important;
}

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: #1A0008; }
::-webkit-scrollbar-thumb { background: rgba(201,168,112,0.3); border-radius: 99px; }
</style>
"""

st.markdown(DESIGN_CSS, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# ESTADO DA SESSÃO
# ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "show_metrics" not in st.session_state:
    st.session_state.show_metrics = False

# ─────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
    <div class=\"sb-logo\">
        <div class=\"sb-logo-text\">
            <span class=\"hm-logo-harmoniz\">Harmoniz</span><span class=\"hm-logo-ai\">.AI</span>
        </div>
        <div class=\"sb-logo-sub\">Sommelier Digital</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown("##### Modo de Operação")
    modo = st.radio(
        label="",
        options=["💨 Chat RAG — Rápido", "🤖 Agente — Inteligente", "🏆 Juiz — Multi-LLM"],
        help="Cada modo equilibra latência, custo e qualidade de forma diferente.",
        label_visibility="collapsed",
    )

    st.markdown("---")

    if "Chat RAG" in modo:
        st.markdown(
            """
        **⚡ Ultra-Rápido**  
        `< 500ms` · Custo mínimo  
        Self-Querying + ChromaDB + LCEL
        """
        )
    elif "Agente" in modo:
        st.markdown(
            """
        **🤖 Orquestração Inteligente**  
        `1 – 3s` · Custo médio  
        4 ferramentas automáticas:  
        🔍 Catálogo · 💰 Promoções  
        📦 Estoque · 🍴 Harmonização
        """
        )
    else:
        st.markdown(
            """
        **🏆 Máxima Qualidade**  
        `3 – 5s` · Custo 3× maior  
        GPT-4o-mini × Llama-3.3  
        × Gemini-2.0 + Juiz árbitro
        """
        )

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑 Limpar", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    with col2:
        if st.button("📊 Stats", use_container_width=True):
            st.session_state.show_metrics = not st.session_state.show_metrics
            st.rerun()

    st.markdown("---")
    st.markdown(
        """
    <p style=\"font-size:0.7rem; color:rgba(242,232,212,0.3); text-align:center; letter-spacing:1px;\">
    HARMONIZ.AI v1.0<br>
    <a href=\"https://github.com/vdfs89/Harmoniz.AI\" style=\"color:rgba(201,168,112,0.5);\">GitHub</a>
    </p>
    """,
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────────────────────
# HEADER PRINCIPAL
# ─────────────────────────────────────────────────────────────
st.markdown(
    """
<div class=\"hm-hero\">
    <h1 class=\"hm-logo\">
        <span class=\"hm-logo-harmoniz\">Harmoniz</span><span class=\"hm-logo-dot\">.</span><span class=\"hm-logo-ai\">AI</span>
    </h1>
    <p class=\"hm-tagline-main\">Sommelier Digital</p>
    <p class=\"hm-tagline-sub\">Seu sommelier com inteligência artificial.</p>
</div>
""",
    unsafe_allow_html=True,
)

if "Chat RAG" in modo:
    badge_html = '<span class="hm-badge hm-badge-rag">⚡ Modo Rápido</span>'
elif "Agente" in modo:
    badge_html = '<span class="hm-badge hm-badge-agent">🤖 Modo Agente</span>'
else:
    badge_html = '<span class="hm-badge hm-badge-judge">🏆 Modo Juiz</span>'

st.markdown(f'<div class="hm-mode-wrap">{badge_html}</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# HISTÓRICO DE MENSAGENS
# ─────────────────────────────────────────────────────────────
for message in st.session_state.messages:
    avatar = "🍷" if message["role"] == "assistant" else "🧑‍💼"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])
        if message.get("metadata"):
            with st.expander("📋 Detalhes"):
                for key, value in message["metadata"].items():
                    if isinstance(value, list):
                        st.write(f"**{key}:** {', '.join(str(item) for item in value)}")
                    else:
                        st.write(f"**{key}:** {value}")

# ─────────────────────────────────────────────────────────────
# INPUT & PROCESSAMENTO
# ─────────────────────────────────────────────────────────────
prompt = st.chat_input(
    placeholder="Como posso ajudar o seu paladar? (ex: vinho para risoto de cogumelos...)",
)

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt, "metadata": None})
    with st.chat_message("user", avatar="🧑‍💼"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🍷"):
        with st.spinner("Consultando adega..."):
            try:
                metadata: Dict[str, Any] = {}

                if "Chat RAG" in modo:
                    resultado = perguntar_ao_sommelier(prompt)
                    resposta = resultado["result"]
                    st.markdown(resposta)

                    if resultado.get("filters_applied"):
                        st.info(f"🔍 Filtros: {' · '.join(resultado['filters_applied'])}")
                        metadata["Filtros"] = resultado["filters_applied"]

                    if resultado.get("source_documents"):
                        with st.expander(
                            f"📚 {len(resultado['source_documents'])} rótulos analisados"
                        ):
                            for doc in resultado["source_documents"]:
                                nome = doc.metadata.get("nome", "—")
                                tipo = doc.metadata.get("tipo", "")
                                pais = doc.metadata.get("pais", "")
                                preco = doc.metadata.get("preco", "—")
                                st.write(f"**{nome}** · {tipo} · {pais} · R$ {preco}")
                        metadata["Fontes"] = [
                            doc.metadata.get("nome") for doc in resultado["source_documents"]
                        ]
                    metadata["Modo"] = "Chat RAG"

                elif "Agente" in modo:
                    if _agent_executor is None:
                        resposta = (
                            "❌ O Modo Agente não pôde ser carregado.\n\n"
                            f"Detalhe: `{_agent_error}`\n\n"
                            "Verifique as dependências do LangChain e o `VECTOR_DB_PATH`."
                        )
                        st.error(resposta)
                    else:
                        resultado = _agent_executor.invoke({"input": prompt})
                        resposta = resultado["output"]
                        st.markdown(resposta)
                    metadata["Modo"] = "Agente"
                    metadata["Ferramentas"] = "Busca · Promoção · Estoque · Harmonização"

                else:
                    resultado = ask_with_judge(prompt)
                    resposta = resultado.get("answer", resultado.get("output", ""))
                    st.markdown(resposta)

                    winner = resultado.get("winner", "—")
                    reason = resultado.get("reason", "")
                    st.success(f"🏆 Vencedor: **{winner}**")
                    if reason:
                        st.info(f"_{reason}_")

                    if resultado.get("all_answers"):
                        with st.expander("📊 Comparação de modelos"):
                            cols = st.columns(len(resultado["all_answers"]))
                            for col, (model_name, resposta_modelo) in zip(
                                cols, resultado["all_answers"].items()
                            ):
                                with col:
                                    st.markdown(f"**{model_name}**")
                                    st.caption(resposta_modelo[:200] + "…")

                    metadata = {
                        "Vencedor": winner,
                        "Razão": reason,
                        "Modelos": list(resultado.get("all_answers", {}).keys()),
                    }

                st.session_state.messages.append(
                    {"role": "assistant", "content": resposta, "metadata": metadata}
                )

            except Exception as exc:  # noqa: BLE001
                st.error(f"❌ {exc}")
                st.caption(
                    "Certifique-se de que o `.env` tem as API keys e o ChromaDB foi gerado "
                    "(`python src/engine/ingest.py`)."
                )

# ─────────────────────────────────────────────────────────────
# STATS (opcional)
# ─────────────────────────────────────────────────────────────
if st.session_state.show_metrics and st.session_state.messages:
    st.markdown("---")
    st.markdown("#### 📊 Estatísticas da Conversa")
    total_msgs = len(st.session_state.messages)
    user_msgs = sum(1 for msg in st.session_state.messages if msg["role"] == "user")
    assist_msgs = total_msgs - user_msgs
    modo_curto = "RAG" if "Chat RAG" in modo else ("Agente" if "Agente" in modo else "Juiz")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total", total_msgs)
    col2.metric("Perguntas", user_msgs)
    col3.metric("Respostas", assist_msgs)
    col4.metric("Modo", modo_curto)
