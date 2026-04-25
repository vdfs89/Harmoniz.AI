"""
🚀 GUIA DE DEPLOYMENT — Streamlit Cloud
========================================

Como deployar o Harmoniz.AI no Streamlit Cloud (gratuito)
e torná-lo acessível em: https://harmonizai.streamlit.app/

⚠️ IMPORTANTE: O ficheiro principal DEVE ser app.py, NÃO setup_project.py
"""

# ============================================================================
# 1. PREPARAÇÃO LOCAL (PRÉ-REQUISITO)
# ============================================================================

"""
Antes de fazer push para GitHub:

**PASSO 1: Criar arquivo secrets.toml (LOCAL ONLY)**

   Local: .streamlit/secrets.toml (NÃO commitar ao GitHub!)
   
   Copie o conteúdo de .streamlit/secrets.toml.example:
   - Substitua cada placeholder pelos seus valores reais
   - Etc.
   
   Exemplo completo:
   --------
   OPENAI_API_KEY = "your_openai_api_key_here"
   GROQ_API_KEY = "your_groq_api_key_here"
   GEMINI_API_KEY = "your_gemini_api_key_here"
   OPENAI_MODEL = "gpt-4o-mini"
   GROQ_MODEL = "llama-3.3-70b-versatile"
   GEMINI_MODEL = "gemini-2.0-flash"
   JUDGE_PROVIDER = "openai"
   JUDGE_MODEL = "gpt-4o-mini"
   WINE_DATA_PATH = "data/raw/wines_from_winecombr.xlsx"
   VECTOR_DB_PATH = "data/processed/chroma_db"
   LANGCHAIN_TRACING_V2 = "false"
   --------
   
   ✅ O .gitignore já tem .streamlit/secrets.toml listado (não será commitado)

**PASSO 2: Testar localmente**

   Certifique-se que tudo funciona:
   
   # Terminal
   streamlit run app.py
   
   # Browser
   http://localhost:8501
   
   # Teste os 3 modos (Chat, Agent, Judge)
   # Se tudo funcionar, está pronto para cloud!

**PASSO 3: Fazer push para GitHub**

   git add .
   git commit -m "Deploy-ready: all secrets configured locally"
   git push origin main
"""

# ============================================================================
# 2. SETUP NO STREAMLIT CLOUD (Passo-a-Passo)
# ============================================================================

"""
**⚠️ AVISO CRÍTICO:**

Você DEVE usar o ficheiro **app.py** como "Main module" no Streamlit Cloud.
NÃO use setup_project.py (esse é um script de inicialização que termina logo).

---

**PASSO 1: Acessar Streamlit Cloud**

   • Vá em https://share.streamlit.io
   • Clique em "Sign up" (se não tiver conta)
   • Conecte sua conta GitHub

---

**PASSO 2: Deploy Novo App**

   • Clique em "New app"
   
   Preencha:
   --------
   Repository: vdfs89/Harmoniz.AI
   Branch: main
   Main file path: app.py  ← ⭐ CRÍTICO: Deve ser app.py, NÃO setup_project.py
   --------
   
   • Clique "Deploy"
   • Aguarde 2-5 minutos (Streamlit vai fazer build)

---

**PASSO 3: Adicionar Secrets (MUITO IMPORTANTE)**

   Seu app vai ficar com erro "connection refused" se não fizer isto!
   
   1. Após o deploy, verá seu app em: https://harmonizai.streamlit.app/
   2. Se aparecer erro, clique em "..." (três pontos, canto superior direito)
   3. Selecione "Settings"
   4. Abra a aba "Secrets"
   5. Cole TODO o conteúdo de .streamlit/secrets.toml.example:
   
      OPENAI_API_KEY = "your_openai_api_key_here"
      GROQ_API_KEY = "your_groq_api_key_here"
      GEMINI_API_KEY = "your_gemini_api_key_here"
      OPENAI_MODEL = "gpt-4o-mini"
      ...etc...
   
   6. Substitua os valores pelos seus valores REAIS
   7. Clique "Save"
   8. Streamlit vai fazer redeploy automaticamente

---

**PASSO 4: Verificar Se Está Online**

   • Abra https://harmonizai.streamlit.app/
   • Deve ver a interface do Harmoniz.AI carregada
   • Teste os 3 modos (Chat, Agent, Judge)
   • Se funcionar, pronto! 🎉

---

**Se Ainda Tiver Erro "Connection Refused":**

   1. Verifique se escolheu **app.py** como Main file (não setup_project.py)
   2. Verifique se adicionou TODOS os secrets obrigatórios
   3. Verifique se os valores dos secrets estão corretos (sem aspas extras)
   4. Clique em "Rerun" para forçar reinicialização
   5. Se persistir, clique em "..." → "Advanced settings" → "Restart app"
"""

# ============================================================================
# 3. TROUBLESHOOTING (Resolvendo Erros)
# ============================================================================

"""
**❌ ERRO: "Connection refused" ou "ConnectionError"**

Causa: O Streamlit Cloud está tentando correr um script que termina (setup_project.py)
Solução:
  1. Verifique que escolheu **app.py** como "Main file path"
  2. Se escolheu errado, clique em "..." → "Settings" → "Advanced settings"
  3. Mude "Main file" de setup_project.py para app.py
  4. Clique "Save"
  5. Streamlit vai fazer redeploy
  
---

**❌ ERRO: "ModuleNotFoundError: No module named 'src'"**

Causa: Streamlit Cloud não consegue importar os módulos
Solução:
  1. Certifique-se que os ficheiros __init__.py existem:
     - src/__init__.py ✓
     - src/engine/__init__.py ✓
     - src/api/__init__.py ✓
     - src/utils/__init__.py ✓
  2. Faça git push
  3. Redeploy no Streamlit Cloud

---

**❌ ERRO: "No such file or directory: 'data/processed/chroma_db'"**

Causa: ChromaDB não foi commitado ou VECTOR_DB_PATH está errado
Solução:
  1. Localmente, regenere o ChromaDB:
     python src/engine/ingest.py
  2. Faça commit e push:
     git add data/processed/chroma_db/
     git commit -m "Include ChromaDB"
     git push origin main
  3. Ou, configure VECTOR_DB_PATH nos Secrets para "data/processed/chroma_db"

---

**❌ ERRO: "ImportError" ao criar o Agent (linha 253)**

Causa: Dependências do LangChain Agent não instaladas (ex.: langchain-chroma) OU o diretório da base vetorial não existe no servidor.
Solução:
  1. Garanta que o `requirements.txt` contém:
     - langchain>=0.3.0
     - langchain-community>=0.3.0
     - langchain-openai>=0.2.0
     - langchain-google-genai
     - langchain-chroma
  2. No Streamlit Cloud, rode `pip install -r requirements.txt` automaticamente ao redeploy.
  3. Em **Settings → Secrets**, defina `VECTOR_DB_PATH` = "data/processed/chroma_db" e `GEMINI_API_KEY` (obrigatório para o Agent usar ferramentas Google).
  4. Faça push da pasta `data/processed/chroma_db/` ou execute `python src/engine/ingest.py` antes do deploy para que o caminho exista.

---

**❌ ERRO: "OPENAI_API_KEY is not set" ou "OpenAIError: Incorrect API key"**

Causa: Secret não foi configurado ou valor está errado
Solução:
  1. No Streamlit Cloud, vá em "Settings" → "Secrets"
  2. Verifique que OPENAI_API_KEY está lá
  3. Copie exatamente o valor (sem "sk_" duplicado, sem espaços)
  4. Salve
  5. Clique em "Rerun" para testar

---

**❌ ERRO: "TimeoutError" ou "App is running behind schedule"**

Causa: Tempo de resposta muito longo (> 30s)
Solução:
  1. Está em Free tier do Streamlit Cloud? Pode ser mais lento.
  2. Ou use cache para não recarregar Agent/ChromaDB cada vez:
     
     @st.cache_resource
     def load_agent():
         from src.engine.sommelier_agent import criar_sommelier_agent
         return criar_sommelier_agent()
     
     agent = load_agent()

---

**❌ ERRO: "KeyError: 'WINE_DATA_PATH'" ou variáveis de ambiente não encontradas**

Causa: Faltam secrets no Streamlit Cloud
Solução:
  1. Configure TODAS estas variáveis nos Secrets:
     - OPENAI_API_KEY
     - GROQ_API_KEY
     - GEMINI_API_KEY
     - OPENAI_MODEL
     - GROQ_MODEL
     - GEMINI_MODEL
     - WINE_DATA_PATH
     - VECTOR_DB_PATH
  2. Use .streamlit/secrets.toml.example como guia

---

**⚠️ COMO VERIFICAR SE ESTÁ TUDO CERTO:**

   1. No Streamlit Cloud, clique em "..." → "View logs"
   2. Procure por mensagens de erro
   3. Verifique se os imports funcionam
   4. Se vir "ModuleNotFoundError", problema é com __init__.py
   5. Se vir "OPENAI_API_KEY", problema é com secrets
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
OPENAI_API_KEY = "your_openai_api_key_here"
GROQ_API_KEY = "your_groq_api_key_here"
GEMINI_API_KEY = "your_gemini_api_key_here"
LANGCHAIN_API_KEY = "your_langsmith_api_key_here"

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
