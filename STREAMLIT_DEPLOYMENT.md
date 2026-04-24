"""
🚀 GUIA DE DEPLOYMENT — Streamlit Cloud
========================================

Como deployar o Harmoniz.AI no Streamlit Cloud (gratuito)
e torná-lo acessível em: https://harmonizai.streamlit.app/
"""

# ============================================================================
# 1. PREPARAÇÃO LOCAL
# ============================================================================

"""
Antes de fazer push para GitHub:

1) Certifique-se que tem um arquivo secrets.toml com suas API keys:
   
   Arquivo: .streamlit/secrets.toml (NÃO commitar)
   
   Conteúdo:
   --------
   OPENAI_API_KEY = "sk_..."
   GROQ_API_KEY = "gsk_..."
   GEMINI_API_KEY = "AIzaSy..."
   LANGCHAIN_API_KEY = "ls_..."
   VECTOR_DB_PATH = "data/processed/chroma_db"
   LANGCHAIN_TRACING_V2 = "false"
   
   IMPORTANTE: Adicionar .streamlit/secrets.toml ao .gitignore

2) Teste localmente:
   streamlit run app.py

3) Se funcionou, está pronto pra cloud!
"""

# ============================================================================
# 2. SETUP NO STREAMLIT CLOUD
# ============================================================================

"""
**Passo 1: Criar conta**
   • Vá em https://streamlit.io/cloud
   • Clique em "Sign up"
   • Conecte com sua conta GitHub

**Passo 2: Deploy**
   • Em https://share.streamlit.io, clique "New app"
   • Selecione seu repositório: vdfs89/Harmoniz.AI
   • Branch: main
   • Main file path: app.py
   • Clique "Deploy"

**Passo 3: Configurar secrets (IMPORTANTE!)**
   • Após o deploy, clique em "..."
   • Vá em "Settings" → "Secrets"
   • Copie os mesmos secrets do seu .streamlit/secrets.toml:
   
   OPENAI_API_KEY = "sk_..."
   GROQ_API_KEY = "gsk_..."
   GEMINI_API_KEY = "AIzaSy..."
   LANGCHAIN_API_KEY = "ls_..."
   VECTOR_DB_PATH = "data/processed/chroma_db"
   LANGCHAIN_TRACING_V2 = "false"
   
   • Salve

**Passo 4: Aguarde o deploy**
   • Streamlit vai fazer build automaticamente
   • Pode levar 2-5 minutos
   • Seu app estará em: https://harmonizai.streamlit.app/
"""

# ============================================================================
# 3. TROUBLESHOOTING
# ============================================================================

"""
**Problema: "ModuleNotFoundError: No module named 'src'"**

Solução: Crie um arquivo `__init__.py` vazio em:
  src/__init__.py
  src/engine/__init__.py
  src/api/__init__.py
  src/utils/__init__.py

**Problema: "ChromaDB not found"**

Solução: Commit o diretório data/processed/chroma_db para GitHub
  (ou re-gere com ingest.py antes de fazer push)

**Problema: "API keys not found"**

Solução: Configure as secrets no painel do Streamlit Cloud
  Settings → Secrets → Cole seu secrets.toml

**Problema: App tá lento**

Solução: Use cache para não re-carregar ChromaDB/Agent
  @st.cache_resource
  def carregar_agent():
      return criar_sommelier_agent()
"""

# ============================================================================
# 4. MONITORAMENTO
# ============================================================================

"""
**Ver logs do app em produção:**
   • Clique em "..." no canto superior direito
   • "View logs" (mostra print statements e erros)

**Analytics:**
   • Dashboard do Streamlit Cloud mostra:
     - Número de usuários
     - Frequência de uso
     - Erros
     - Latência

**Performance:**
   • Se o app fica lento, Streamlit Cloud pode estar overcrowded
   • Use @st.cache_resource para cachear Agent e ChromaDB
"""

# ============================================================================
# 5. SHARING URL
# ============================================================================

"""
Após o deploy, compartilhe:

🔗 https://harmonizai.streamlit.app/

Durante a entrevista na Wine:
  1. Abra essa URL num navegador
  2. Mostre os 3 modos funcionando ao vivo
  3. Explique a arquitetura enquanto interage
  4. Prove que tem integração real de IA
"""

# ============================================================================
# 6. EXEMPLO DE SECRETS.TOML (LOCAL ONLY)
# ============================================================================

"""
Arquivo: .streamlit/secrets.toml
(NÃO COMMITAR — APENAS LOCAL)

---
OPENAI_API_KEY = "sk_test_..."
GROQ_API_KEY = "gsk_test_..."
GEMINI_API_KEY = "AIzaSyDx..."
LANGCHAIN_API_KEY = "ls_test_..."

VECTOR_DB_PATH = "data/processed/chroma_db"
LANGCHAIN_TRACING_V2 = "false"  # Ativar se quiser LangSmith em produção
LANGCHAIN_PROJECT = "harmoniz-ai-streamlit"
---

Depois adicione ao .gitignore:
.streamlit/secrets.toml
"""

# ============================================================================
# 7. OTIMIZAÇÕES PARA CLOUD
# ============================================================================

"""
Se o app ficar lento, use cache:

@st.cache_resource
def load_agent():
    from src.engine.sommelier_agent import criar_sommelier_agent
    return criar_sommelier_agent()

agent = load_agent()  # Carregado uma vez, reutilizado sempre

@st.cache_data
def load_vector_db():
    from langchain_community.vectorstores import Chroma
    from langchain_openai import OpenAIEmbeddings
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    return Chroma(
        persist_directory=os.getenv("VECTOR_DB_PATH"),
        embedding_function=embeddings,
    )

db = load_vector_db()
"""

# ============================================================================
# PRÓXIMOS PASSOS
# ============================================================================

"""
1. Configure .streamlit/secrets.toml localmente
2. Teste: streamlit run app.py
3. Faça commit e push: git add . && git commit && git push
4. Vá em https://share.streamlit.io
5. Clique "New app"
6. Selecione vdfs89/Harmoniz.AI, branch main, file app.py
7. Depois de deploy, configure secrets no painel
8. Acesse https://harmonizai.streamlit.app/
9. Compartilhe durante a entrevista! 🎉
"""

if __name__ == "__main__":
    print(__doc__)
