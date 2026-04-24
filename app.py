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
import sys
from typing import Dict, Any

import streamlit as st
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

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

# Custom CSS
st.markdown("""
    <style>
    .main { padding-top: 2rem; }
    .stChatMessage { border-radius: 10px; }
    .sommelier-message { background-color: #f0f8ff; }
    h1 { color: #722f37; font-family: 'Georgia', serif; }
    .mode-badge { 
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    .mode-chat { background-color: #d4edda; color: #155724; }
    .mode-agent { background-color: #d1ecf1; color: #0c5460; }
    .mode-judge { background-color: #fff3cd; color: #856404; }
    </style>
    """, unsafe_allow_html=True)

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
        options=[
            "💨 Chat RAG (Rápido)",
            "🤖 Agente (Completo)",
            "🏆 Juiz (Multi-LLM)"
        ],
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
            st.session_state.show_metrics = not st.session_state.get("show_metrics", False)
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
        st.markdown('<span class="mode-badge mode-chat">💨 RÁPIDO</span>', unsafe_allow_html=True)
    elif "Agente" in modo:
        st.markdown('<span class="mode-badge mode-agent">🤖 INTELIGENTE</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="mode-badge mode-judge">🏆 PREMIUM</span>', unsafe_allow_html=True)

st.divider()

# ============================================================================
# HISTÓRICO DE MENSAGENS
# ============================================================================

# Exibe mensagens anteriores
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="🧑‍💼" if message["role"] == "user" else "🍷"):
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
    key="chat_input"
)

if prompt:
    # Adiciona pergunta ao histórico
    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
        "metadata": None
    })
    
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
                        with st.expander(f"📚 Fontes ({len(resultado['source_documents'])} documentos)"):
                            for doc in resultado["source_documents"]:
                                nome = doc.metadata.get("nome", "Desconhecido")
                                tipo = doc.metadata.get("tipo", "")
                                preco = doc.metadata.get("preco", "N/A")
                                pais = doc.metadata.get("pais", "")
                                st.write(f"**{nome}** ({tipo}) - {pais} - R$ {preco}")
                        
                        metadata["Fontes"] = [doc.metadata.get("nome") for doc in resultado["source_documents"]]
                
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
                        "Ferramentas": "🔍 Busca, 💰 Promoção, 📦 Estoque, 🍴 Harmonização"
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
                        "Modelos": list(resultado.get("all_answers", {}).keys())
                    }
                
                # Adiciona resposta ao histórico
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": resposta,
                    "metadata": metadata
                })
            
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
        st.metric("Modo atual", "RAG" if "Chat RAG" in modo else ("Agent" if "Agente" in modo else "Judge"))
