![Harmoniz.AI](img/ChatGPT Image 24 de abr. de 2026, 21_52_30.png)

# Harmoniz.AI

Sommelier digital com arquitetura RAG para recomendacao de vinhos com base em catalogo real.

## Status da Aplicação

| Componente | Status | Notas |
|---|---|---|
| **Chat RAG** | ✅ Totalmente funcional | Self-querying + ChromaDB |
| **Agent** | ✅ Totalmente funcional | 4 ferramentas especializadas |
| **Judge (Multi-LLM)** | ⚠️ Parcial | Requer langchain-google-genai |
| **Streamlit Web UI** | ✅ Totalmente funcional | 3 modos selecionáveis |
| **FastAPI REST** | ✅ Totalmente funcional | 3 endpoints |
| **ChromaDB (VectorDB)** | ✅ Funcional | 570 vinhos indexados |
| **LangSmith (MLOps)** | ✅ Configurado | Observabilidade opcional |

## Visao Geral

O `Harmoniz.AI` foi projetado para responder perguntas sobre vinhos com maior precisao e menor risco de alucinacao, combinando:

- Recuperacao semantica de vinhos em base vetorial (RAG).
- Resposta conversacional orientada por contexto.
- Orquestracao multi-modelo (`GPT`, `Groq`, `Gemini`) com um juiz para selecionar a melhor resposta final.

Em vez de responder apenas com conhecimento generico, o sistema busca rotulos e descricoes no proprio dataset e usa esse contexto para fundamentar a recomendacao.

## Principais Recursos

### 🎯 3 Arquiteturas de Resposta

1. **💨 Chat RAG (Rápido < 500ms)**
   - Self-Querying com filtros automáticos (país, preço)
   - Recuperação de 4 documentos relevantes
   - Resposta fundamentada com source documents
   - ✅ Pronto para produção

2. **🤖 Agent Inteligente (1-3s)**
   - 4 ferramentas especializadas:
     - 🔍 Busca no catálogo (RAG)
     - 💰 Verifica preços e promoções
     - 📦 Consulta disponibilidade
     - 🍴 Recomendações por harmonização
   - Orquestração automática com LangChain AgentExecutor
   - Memória de conversação (ConversationBufferMemory)
   - ✅ Pronto para produção

3. **🏆 Judge Multi-LLM (3-5s, máxima qualidade)**
   - Consulta 3 modelos em paralelo:
     - OpenAI GPT-4o-mini
     - Groq Llama-3.3
     - Google Gemini-2.0
   - Juiz seleciona melhor resposta
   - ⚠️ Requer configuração de Google Gemini

### 💾 Dados e RAG

- Ingestão automática de `CSV`, `XLSX` e `XLS`
- 570+ vinhos com metadados: nome, tipo, país, preço
- ChromaDB para persistência de embeddings
- OpenAI `text-embedding-3-small` para semantização
- Self-Querying para filtros automáticos de país/preço

### 🌐 Interfaces

- **Streamlit Web UI** — Chat interativo (app.py)
- **FastAPI REST API** — 3 endpoints HTTP
- **CLI** — Scripts diretos (initialize.py, src/engine/*.py)
- **LangSmith Dashboard** — Observabilidade em tempo real

### 🔒 Observabilidade & MLOps

- LangSmith integrado para rastreamento de chains
- Métricas automáticas: latência, custos, alucinações
- @traceable decorator para funções customizadas
- Logs estruturados com structured_logging

## Arquitetura

1. O arquivo de vinhos e carregado (`data/raw/...`).
2. Cada vinho vira um `Document` com perfil sensorial e harmonizacao.
3. Os documentos sao embedados (`text-embedding-3-small`) e persistidos no `Chroma`.
4. Em tempo de pergunta:
	 - `harmoniz_ai.py` usa retriever com `k=4`, aplica filtro por preco quando detecta "ate X" e responde com prompt especialista.
	 - `harmoniz_ai.py` tambem lista os rotulos analisados com nome e preco (`source_documents`).
	 - `multi_llm_judge.py` recupera contexto RAG, consulta os modelos e pede ao juiz a melhor resposta.

## Estrutura do Projeto

```text
.
|-- Docs/
|-- data/
|   |-- raw/
|   |-- processed/
|-- img/
|-- src/
|   |-- engine/
|   |   |-- ingest.py
|   |   |-- harmoniz_ai.py
|   |   |-- multi_llm_judge.py
|-- requirements.txt
|-- setup_project.py
|-- README.md
```

## Stack Tecnica

- Python 3.10+
- LangChain
- ChromaDB
- OpenAI Embeddings (`text-embedding-3-small`)
- OpenAI / Groq / Gemini
- Pandas + OpenPyXL

## ⚡ Início Rápido

### 1) Criar ambiente virtual

Windows (PowerShell):

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
python -m venv venv
source venv/bin/activate
```

### 2) Instalar dependências (Recomendado)

**Opção A: Com versões pinadas (RECOMENDADO - mais estável)**

```bash
pip install -r requirements-pinned.txt
```

Este arquivo contém versões específicas testadas de LangChain 0.1.20, que garante compatibilidade total com:
- ✅ Agent com `AgentExecutor`
- ✅ Chat RAG com `ChatPromptTemplate`
- ✅ ChromaDB persistente
- ⚠️ Judge (parcial - requer langchain-google-genai 0.0.9)

**Opção B: Com versões flexíveis**

```bash
pip install -r requirements.txt
```

### ⚠️ Resolva conflitos comuns de pydantic

Se receber erro como: `pydantic-core version (2.14.6) is incompatible with pydantic (2.11.7)`:

```bash
pip install --upgrade pydantic pydantic-core
```

Ou, para máxima estabilidade com LangChain 0.1.20:

```bash
pip install pydantic==2.11.7 pydantic-core==2.23.4 --force-reinstall --no-deps
```

### 3) Configurar `.env`

Crie ou ajuste o arquivo `.env` com as variáveis abaixo:

```env
# ====== CHAVES DE API (OBRIGATÓRIAS) ======
OPENAI_API_KEY=your_openai_api_key_here   # https://platform.openai.com/api-keys
GROQ_API_KEY=your_groq_api_key_here       # https://console.groq.com/keys
GEMINI_API_KEY=your_gemini_api_key_here   # https://aistudio.google.com/app/apikeys

# ====== MODELOS LLM ======
OPENAI_MODEL=gpt-4o-mini       # Recomendado: custo/qualidade
GROQ_MODEL=llama-3.3-70b-versatile
GEMINI_MODEL=gemini-2.0-flash
JUDGE_PROVIDER=openai
JUDGE_MODEL=gpt-4o-mini

# ====== DADOS E RAG ======
WINE_DATA_PATH=data/raw/wines_from_winecombr.xlsx
VECTOR_DB_PATH=data/processed/chroma_db
RAG_TOP_K=4

# ====== LANGSMITH (Opcional - Observabilidade) ======
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=ls_...
LANGCHAIN_PROJECT=harmoniz-ai-production
```

### 4) Teste inicial (Validar Instalação)

```bash
python initialize.py
```

Este script valida:
- ✅ Ambiente virtual ativado
- ✅ `.env` carregado com API keys
- ✅ ChromaDB acessível
- ✅ Todos os imports funcionam (Chat RAG, Agent, Judge)
- ✅ Streamlit configurado

Output esperado:
```
======================================================================
🍷 HARMONIZ.AI — Inicializador Streamlit
======================================================================

✓ Ambiente virtual ativado
✓ .env já existe
✓ ChromaDB encontrado
✓ Importações OK

========== PRONTO PARA RODAR ==========
```

**Se receber erro em Importações**, consulte [Troubleshooting](#troubleshooting)

## Web UI com Streamlit (Visual & Interativo)

### 🎨 Interface de Chat Profissional

Harmoniz.AI tem uma interface visual moderna construída com **Streamlit** — a ferramenta favorita dos Data Scientists.

**3 modos selecionáveis na barra lateral:**
- 💨 **Chat RAG** — Rápido (< 500ms) ✅ Totalmente funcional
- 🤖 **Agente** — Inteligente com 4 ferramentas ✅ Totalmente funcional
- 🏆 **Juiz** — Multi-LLM máxima qualidade ⚠️ Requer Google Gemini ativo

### 🚀 Rodar Localmente (2 Opções)

**Opção 1: Script Automático (RECOMENDADO)**

```bash
python initialize.py
```

Este script:
- ✅ Valida pré-requisitos (venv, .env, ChromaDB)
- ✅ Testa importações de todos os módulos
- ✅ Abre Streamlit automaticamente
- ✅ Mostra relatório de saúde do sistema

**Opção 2: Manualmente**

```bash
streamlit run app.py
```

**3. Abra no navegador:**

```
http://localhost:8501
```

### 🌍 Deploy no Streamlit Cloud (Grátis & Fácil)

Tornar seu app público em uma URL única como `https://harmonizai.streamlit.app/`:

**Passo 1: Prepare localmente**

```bash
# 1. Certifique-se que .env está configurado
# 2. Teste: python initialize.py
# 3. Verifique que tudo funciona
```

**Passo 2: Push para GitHub**

```bash
git add .
git commit -m "Ready for Streamlit Cloud deployment"
git push origin main
```

**Passo 3: Deploy no Streamlit Cloud**

- Vá em https://share.streamlit.io
- Clique "New app"
- **Repositório:** vdfs89/Harmoniz.AI
- **Branch:** main
- **Main file path:** `app.py` ⭐ (CRÍTICO: deve ser app.py, NÃO setup_project.py)
- Clique "Deploy"

**Passo 4: Configure Secrets (MUITO IMPORTANTE)**

Após o deploy:
1. Clique em "..." (três pontos, canto superior direito)
2. Selecione "Settings" → "Secrets"
3. Cole todo o conteúdo de `.streamlit/secrets.toml.example`
4. Substitua pelos seus valores reais
5. Clique "Save"

**Passo 5: Compartilhe!**

Seu app estará em: `https://harmonizai.streamlit.app/`

#### ⚠️ Se Receber Erro "Connection Refused"

Isso significa que o Streamlit Cloud está tentando rodar `setup_project.py` em vez de `app.py`:

1. No painel do Streamlit Cloud, clique em "..."
2. Vá em "Settings" → "Advanced settings"
3. Mude "Main file path" para: `app.py`
4. Clique "Save"
5. Streamlit vai fazer redeploy

Para mais detalhes: veja [STREAMLIT_DEPLOYMENT.md](STREAMLIT_DEPLOYMENT.md)

## REST API (FastAPI)

### 🚀 Início Rápido

**1) Instale dependências REST (se ainda não tiver):**

```bash
pip install fastapi uvicorn pydantic requests
```

Ou rode:
```bash
pip install -r requirements.txt
```

**2) Inicie o servidor:**

```bash
python run_api.py
```

ou com uvicorn direto:
```bash
uvicorn src.api.main:app --reload --port 8000
```

**3) Acesse a documentação interativa:**

```
http://localhost:8000/docs
```

Lá você pode:
- ✅ Testar todos os 3 endpoints
- 📖 Ver documentação detalhada
- 🔍 Inspecionar schemas Pydantic

### 📡 3 Endpoints — 3 Estratégias

| Endpoint | Latência | Custo | Melhor Para | URL |
|---|---|---|---|---|
| **`POST /v1/chat`** | ⚡ <500ms | 💰 Mínimo | Buscas simples, dia-a-dia | http://localhost:8000/docs#/Modes/chat_rag |
| **`POST /v1/agent`** | ⏱️ 1-3s | 💵 Médio | Múltiplas ferramentas, CRM | http://localhost:8000/docs#/Modes/agent_sommelier |
| **`POST /v1/judge`** | ⏲️ 3-5s | 💳 3x Custo | Máxima qualidade, crítico | http://localhost:8000/docs#/Modes/multi_llm_judge |

### 💡 Exemplos de Uso

#### Modo CHAT (Recomendado para MVP)

Busca rápida com Self-Querying automático:

```bash
curl -X POST "http://localhost:8000/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Qual vinho combina com frutos do mar e custa até R$100?",
    "user_id": "user_123"
  }'
```

Resposta:
```json
{
  "answer": "Para frutos do mar recomendo um Sauvignon Blanc francês...",
  "source_documents": [
    {
      "nome": "Sauvignon Blanc Loire Valley",
      "tipo": "Branco",
      "pais": "França",
      "preco": "R$ 85"
    }
  ],
  "filters_applied": ["preço_máximo: R$100", "tipo: Branco"],
  "mode": "chat"
}
```

#### Modo AGENT (Integração CRM/ERP)

Orquestração automática de ferramentas:

```bash
curl -X POST "http://localhost:8000/v1/agent" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Tem Malbec com promoção em estoque?",
    "user_id": "vendedor_456"
  }'
```

Resposta:
```json
{
  "answer": "✓ PROMOCAO ATIVA: 15% de desconto em Malbec Argentino. Temos 45 garrafas em estoque!",
  "tools_used": [
    "buscar_vinho_no_catalogo",
    "verificar_preco_promocional",
    "verificar_disponibilidade"
  ],
  "mode": "agent"
}
```

#### Modo JUDGE (Máxima Qualidade)

Compara respostas de 3 LLMs e escolhe a melhor:

```bash
curl -X POST "http://localhost:8000/v1/judge" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Qual é o melhor Pinot Noir para investimento?",
    "user_id": "sommelier_789"
  }'
```

Resposta:
```json
{
  "winner": "gpt-4o-mini",
  "reason": "Resposta mais completa com análise de potencial de envelhecimento",
  "answer": "Para investimento em Pinot Noir, recomendo foco em Borgonha...",
  "model_scores": {
    "gpt-4o-mini": 0.95,
    "groq-llama": 0.87,
    "gemini": 0.82
  },
  "mode": "judge"
}
```

### 🐳 Docker (Production Ready)

**Build da imagem:**

```bash
docker build -t harmoniz-api:1.0.0 .
```

**Rodar com docker-compose:**

```bash
# Cria variáveis em .env primeiro!
docker-compose up --build
```

**Rodar manualmente:**

```bash
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=your_openai_api_key_here \
  -e LANGCHAIN_API_KEY=your_langsmith_api_key_here \
  harmoniz-api:1.0.0
```

**Health check:**

```bash
curl http://localhost:8000/health
```

### 📊 Monitoramento em Tempo Real

Com LangSmith configurado, a API automaticamente rastreia:

- ⏱️ **Latência**: Quanto tempo cada request leva
- 💰 **Custos**: Tokens consumidos (GPT, Gemini, Llama)
- 🔍 **Debugging**: Inputs/outputs de cada ferramenta
- 📈 **Métricas**: Taxa de aceitação, alucinações

Acesse: https://smith.langchain.com/projects/harmoniz-ai

### 🏥 Health Check

```bash
curl http://localhost:8000/health
```

Resposta com status de tudo:
```json
{
  "status": "online",
  "system": "Harmoniz.AI",
  "environment": "production",
  "langsmith_enabled": true,
  "vector_db_ready": true,
  "models_configured": {
    "openai": true,
    "groq": true,
    "gemini": true
  }
}
```

## Observabilidade com LangSmith (MLOps)

### Setup LangSmith

LangSmith é a plataforma oficial de observabilidade para LangChain, permitindo rastrear, debugar e otimizar chains em produção.

**1) Criar conta e gerar API Key**

- Acesse https://smith.langchain.com
- Crie uma conta (gratuita)
- Gere uma API Key no dashboard
- Copie a chave

**2) Configurar `.env`**

Adicione ao seu `.env`:

```env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=<sua_api_key_aqui>
LANGCHAIN_PROJECT=harmoniz-ai-production
```

Use `.env.example` como referência.

**3) Rodar com observabilidade**

```bash
python src/utils/observability_setup.py
```

O script demonstra como rastrear:
- ⏱️ **Latência**: quanto tempo leva cada call ao LLM
- 📊 **Métricas**: taxa de aceitação, alucinações detectadas
- 🔍 **Debugging**: inputs/outputs de cada ferramenta
- 💰 **Custos**: tokens consumidos por modelo

**4) Visualizar no LangSmith**

Após configurar, acesse seu projeto em:
```
https://smith.langchain.com/projects/harmoniz-ai-production/
```

No dashboard você verá:
- Cada execução de chain tracida
- Latência de retriever, LLM, etc
- Erros e exceções em tempo real
- Taxa de alucinações
- Comparação de performance entre modelos

## Como Executar

### 1) Ingerir e indexar os vinhos

```bash
python src/engine/ingest.py
```

### 2) Rodar o chat RAG do sommelier

```bash
python src/engine/harmoniz_ai.py
```

Exemplos de pergunta no chat:

- `Quero um tinto para carne assada`
- `Me indica um vinho ate 100 reais para jantar romantico`

Quando houver contexto recuperado, o script imprime os rotulos analisados ao final da resposta.

### 3) Rodar o Agent com Ferramentas Especializadas

```bash
python src/engine/sommelier_agent.py
```

O Agent orquestra automaticamente múltiplas ferramentas:
- Busca no catálogo RAG
- Consulta de preços e promoções
- Verificação de disponibilidade
- Recomendações por prato/ocasião

Exemplos de perguntas para o Agent:
- `Que vinho você recomenda para um churrasco?`
- `Qual é o preço promocional do Malbec?`
- `Tem Cabernet em estoque?`
- `Que vinho harmoniza com frutos do mar?`

### 4) Rodar o modo multi-modelo com juiz

```bash
python src/engine/multi_llm_judge.py "Quero um vinho para massa com cogumelos"
```

## Scripts Principais

- `src/engine/ingest.py`
	- Le tabela de vinhos (`csv/xlsx/xls`).
	- Monta contexto rico por vinho.
	- Gera embeddings e persiste no Chroma.

- `src/engine/harmoniz_ai.py` — **Chat RAG Moderno**
	- Implementa LCEL (LangChain Expression Language) — padrão moderno do LangChain.
	- **Self-Querying RAG**: detecta automaticamente filtros por país e preço na pergunta.
	- Usa recuperacao com `k=4` e aplica filtros em metadados para maior precisão.
	- Retorna e imprime `source_documents` (nome, país, preco) para transparência RAG.
	- Disponibiliza chat interativo com tratamento robusto de excecoes.

- `src/engine/sommelier_agent.py` — **Agent com Ferramentas (Novo)**
	- Orquestra múltiplas ferramentas especializadas usando `AgentExecutor`.
	- **Tool 1**: buscar_vinho_no_catalogo (RAG + Chroma)
	- **Tool 2**: verificar_preco_promocional (simulacao de BD SQL)
	- **Tool 3**: verificar_disponibilidade (simulacao de inventário)
	- **Tool 4**: recomendar_harmonizacao (regras de sommelier)
	- Agent decide automaticamente qual ferramenta usar baseado na pergunta.
	- Mantém histórico de conversa com `ConversationBufferMemory`.
	- Demonstra padrão de produção para integração de IA em sistemas corporativos.

- `src/utils/observability_setup.py` — **Observabilidade com LangSmith (MLOps)**
\t- Demonstra como integrar LangSmith para rastreamento automático.
\t- `@traceable` decorator para rastrear functions customizadas.
\t- `SommelierMetrics` classe para coleta de métricas de negócio.
\t- Exemplos de monitoramento: latência, alucinações, taxa de aceitação.
\t- Relatórios enviados automaticamente para https://smith.langchain.com em tempo real.

## Troubleshooting & Erros Comuns

### ❌ "Erro ao carregar módulos: cannot import name 'AgentExecutor'"

**Causa:** Versão incorreta de LangChain (0.2+ descontinuou AgentExecutor).

**Solução:**
```bash
# Instale LangChain 0.1.20 com compatibilidade layer
pip install -r requirements-pinned.txt
# Ou manualmente:
pip install langchain==0.1.20 langchain-core==0.1.53
```

Se o erro persistir:
```bash
# Remova cache e reinstale
pip cache purge
pip install -r requirements-pinned.txt --force-reinstall
```

### ❌ "No module named 'langchain.memory'"

**Causa:** Versão moderna de LangChain moveu ConversationBufferMemory.

**Solução (já corrigida em sommelier_agent.py):**
```python
# ✓ Código já implementado com fallback:
try:
    from langchain.memory import ConversationBufferMemory
except ImportError:
    from langchain_community.memory import ConversationBufferMemory
```

### ❌ "pydantic-core version (2.14.6) incompatible with pydantic (2.11.7)"

**Causa:** Versões misturadas de pydantic e pydantic-core após múltiplas instalações.

**Solução (Recomendado):**
```bash
# Reinstale com versões compatíveis
pip install pydantic==2.11.7 pydantic-core==2.23.4 --force-reinstall --no-deps
```

Ou:
```bash
# Deixe pip resolver automaticamente
pip install --upgrade pydantic pydantic-core
```

### ❌ "No module named 'langchain.prompts'"

**Causa:** LangChain 0.1.20+ reorganizou módulos.

**Solução (já corrigida em harmoniz_ai.py e sommelier_agent.py):**
```python
# ✓ Código correto:
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
```

### ❌ "ChromaDB não encontrado" ao rodar initialize.py

**Causa:** Arquivo não foi gerado. Você precisa rodar ingest.py primeiro.

**Solução:**
```bash
# 1. Certifique-se que tem dados em data/raw/
# 2. Execute:
python src/engine/ingest.py
# 3. Depois teste:
python initialize.py
```

### ❌ "Connection refused" ao rodar Streamlit Cloud

**Causa:** Streamlit Cloud está tentando rodar `setup_project.py` em vez de `app.py`.

**Solução:**
1. Vá em https://share.streamlit.io → seu app
2. Clique "..." (três pontos) → "Settings"
3. Mude "Main file path" para: `app.py`
4. Clique "Save"
5. Streamlit fará redeploy automático

### ⚠️ "Gemini Judge Mode" com erro de import

**Status:** Requer `langchain-google-genai 0.0.9` (compatível com LangChain 0.1.20).

**Se receber erro:**
```bash
# Verifique a versão instalada
pip show langchain-google-genai

# Reinstale versão compatível
pip install langchain-google-genai==0.0.9 --force-reinstall
```

**Alternativa:** Use apenas Chat RAG e Agent (ambos totalmente funcionais).

### ✅ Validar instalação

```bash
# Use o script de inicialização
python initialize.py

# Resultado esperado:
# ✓ Ambiente virtual ativado
# ✓ .env já existe
# ✓ ChromaDB encontrado
# ✓ Importações OK
```

---

## Troubleshooting Rapido

- Erro de autenticacao: valide as chaves no `.env`.
- Modelo invalido/deprecado: ajuste `OPENAI_MODEL`, `GROQ_MODEL` ou `GEMINI_MODEL`.
- Sem contexto RAG: confira `VECTOR_DB_PATH` e execute novamente `ingest.py`.
- Erro de leitura de planilha: valide colunas obrigatorias no dataset (`Nome`, `Harmonização`, etc.).
- Resultado vazio com filtro de preco: tente reformular a pergunta ou aumentar o teto de preco (ex.: "ate 150").

## Roadmap

- **LangSmith Integration** (Monitoramento/MLOps) — rastrear latência, custos, alucinações.
- **Pydantic + Structured Extraction** — processar PDF de vinhos em JSON estruturado.
- **Tool.bind() com LangSmith Callbacks** — observabilidade de cada ferramenta do Agent.
- API REST FastAPI para exposição dos 3 modos (Chat RAG, Agent, Multi-LLM Judge).
- Avaliacao automatica de qualidade das respostas usando langchain evaluation framework.
- Dashboard de telemetria com métricas de negócio (recomendações aceitas, conversão, etc).

## Autor

Projeto desenvolvido por `vdfs89` como demonstracao tecnica de IA generativa aplicada a recomendacao de vinhos com dados reais.
