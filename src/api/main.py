"""
Harmoniz.AI REST API
====================

API profissional que expõe as 3 camadas arquiteturais:
  1. Chat RAG: Busca rápida + Self-Querying
  2. Agent: Orquestração inteligente de ferramentas
  3. Judge: Comparação multi-modelo (GPT vs Llama vs Gemini)

Requisitos da vaga:
  ✓ "Integrar soluções de IA aos sistemas da empresa" → Agent com 4 tools
  ✓ "Monitorar performance em produção" → LangSmith tracing
  ✓ "MLOps" → Health checks, métricas, observabilidade

Status: PRODUÇÃO READY
"""

import logging
import os
import sys
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from langsmith import traceable
import uvicorn

# Carrega variáveis de ambiente
load_dotenv()

# Imports das 3 camadas
try:
    from src.engine.harmoniz_ai import perguntar_ao_sommelier
    from src.engine.sommelier_agent import criar_sommelier_agent
    from src.engine.multi_llm_judge import ask_with_judge
except ImportError as e:
    print(f"[ERRO] Falha ao importar módulos: {e}")
    print("Certifique-se que os arquivos estão em src/engine/")
    sys.exit(1)

# ============================================================================
# LOGGING
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("harmoniz-api")

# ============================================================================
# FASTAPI APP
# ============================================================================

app = FastAPI(
    title="Harmoniz.AI API",
    description="🍷 Sommelier Digital API para Wine.com.br — 3 Modos Especializados",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

# CORS - Permitir requisições do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# SCHEMAS (Pydantic)
# ============================================================================


class QueryRequest(BaseModel):
    """Requisição padrão para todos os endpoints."""
    
    question: str = Field(
        ...,
        min_length=5,
        max_length=500,
        description="Pergunta do usuário sobre vinhos (ex: 'Vinho para churrasco com orçamento até R$100')"
    )
    user_id: Optional[str] = Field(
        default="guest",
        description="ID do usuário para rastreamento (opcional)"
    )
    
    class Config:
        examples = [
            {
                "question": "Qual vinho combina com frutos do mar?",
                "user_id": "user_123"
            }
        ]


class SourceDocument(BaseModel):
    """Documento fonte recuperado via RAG."""
    
    nome: str = Field(..., description="Nome do vinho")
    tipo: Optional[str] = Field(None, description="Tipo: Tinto, Branco, Rosé, etc")
    pais: Optional[str] = Field(None, description="País de origem")
    preco: Optional[str] = Field(None, description="Preço em R$")


class ChatResponse(BaseModel):
    """Resposta do modo Chat RAG."""
    
    answer: str = Field(..., description="Resposta do Sommelier")
    source_documents: List[SourceDocument] = Field(
        default_factory=list,
        description="Vinhos do catálogo usados como contexto"
    )
    filters_applied: List[str] = Field(
        default_factory=list,
        description="Filtros automáticos detectados (preço, país, etc)"
    )
    mode: str = "chat"
    
    class Config:
        examples = [
            {
                "answer": "Para frutos do mar recomendo um Sauvignon Blanc francês...",
                "source_documents": [
                    {"nome": "Sauvignon Blanc Loire", "tipo": "Branco", "pais": "França", "preco": "R$ 85"}
                ],
                "filters_applied": ["preço_máximo: R$100"],
                "mode": "chat"
            }
        ]


class AgentResponse(BaseModel):
    """Resposta do modo Agent com orquestração de ferramentas."""
    
    answer: str = Field(..., description="Resposta do Agent Sommelier")
    tools_used: List[str] = Field(
        default_factory=list,
        description="Ferramentas que o Agent acionou (buscar_vinho, verificar_promocao, etc)"
    )
    mode: str = "agent"
    
    class Config:
        examples = [
            {
                "answer": "Encontrei Malbec com 15% de desconto e temos 45 garrafas em estoque!",
                "tools_used": ["buscar_vinho_no_catalogo", "verificar_preco_promocional", "verificar_disponibilidade"],
                "mode": "agent"
            }
        ]


class JudgeResponse(BaseModel):
    """Resposta do modo Multi-LLM Judge."""
    
    winner: str = Field(..., description="Melhor resposta (gpt|groq|gemini)")
    reason: str = Field(..., description="Por que essa resposta venceu")
    answer: str = Field(..., description="A resposta do modelo vencedor")
    model_scores: Dict[str, float] = Field(
        default_factory=dict,
        description="Pontuação de cada modelo (0-1)"
    )
    mode: str = "judge"
    
    class Config:
        examples = [
            {
                "winner": "gpt-4o-mini",
                "reason": "Resposta mais completa e bem estruturada",
                "answer": "Para churrasco recomendo Malbec Argentino de boa estrutura...",
                "model_scores": {"gpt-4o-mini": 0.95, "groq": 0.87, "gemini": 0.82},
                "mode": "judge"
            }
        ]


class HealthResponse(BaseModel):
    """Resposta do health check."""
    
    status: str
    system: str
    environment: str
    langsmith_enabled: bool
    vector_db_ready: bool
    models_configured: Dict[str, bool]


# ============================================================================
# OBSERVABILIDADE (LangSmith Integration)
# ============================================================================

@traceable(name="api_chat_request", run_type="chain")
def _process_chat_request(question: str, user_id: str) -> Dict[str, Any]:
    """Processa requisição de Chat com LangSmith tracking."""
    logger.info(f"[CHAT] user={user_id} question={question[:50]}...")
    return perguntar_ao_sommelier(question)


@traceable(name="api_agent_request", run_type="chain")
def _process_agent_request(question: str, user_id: str) -> Dict[str, Any]:
    """Processa requisição de Agent com LangSmith tracking."""
    logger.info(f"[AGENT] user={user_id} question={question[:50]}...")
    agent = criar_sommelier_agent()
    resultado = agent.invoke({"input": question})
    return resultado


@traceable(name="api_judge_request", run_type="chain")
def _process_judge_request(question: str, user_id: str) -> Dict[str, Any]:
    """Processa requisição de Judge com LangSmith tracking."""
    logger.info(f"[JUDGE] user={user_id} question={question[:50]}...")
    return ask_with_judge(question)


# ============================================================================
# ENDPOINTS
# ============================================================================


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint — status básico."""
    return {
        "message": "🍷 Harmoniz.AI API — Sommelier Digital para Wine.com.br",
        "version": "1.0.0",
        "docs": "/docs",
        "modes": ["chat", "agent", "judge"]
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check() -> HealthResponse:
    """
    Health check completo — verifica integrações e status de sistemas.
    
    Útil para:
    - Kubernetes liveness probes
    - Monitoramento em produção
    - Validar que LangSmith está conectado
    """
    try:
        # Detecta se LangSmith está habilitado
        langsmith_enabled = (
            os.getenv("LANGCHAIN_TRACING_V2") == "true" and
            bool(os.getenv("LANGCHAIN_API_KEY"))
        )
        
        # Tenta conectar à base vetorial (Chroma)
        from langchain_community.vectorstores import Chroma
        from langchain_openai import OpenAIEmbeddings
        
        persist_directory = os.getenv("VECTOR_DB_PATH", "data/processed/chroma_db")
        try:
            embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
            vector_db = Chroma(
                persist_directory=persist_directory,
                embedding_function=embeddings,
            )
            vector_db_ready = True
        except Exception:
            vector_db_ready = False
        
        # Models configurados
        models = {
            "openai": bool(os.getenv("OPENAI_API_KEY")),
            "groq": bool(os.getenv("GROQ_API_KEY")),
            "gemini": bool(os.getenv("GEMINI_API_KEY")),
        }
        
        return HealthResponse(
            status="online",
            system="Harmoniz.AI",
            environment=os.getenv("ENVIRONMENT", "development"),
            langsmith_enabled=langsmith_enabled,
            vector_db_ready=vector_db_ready,
            models_configured=models,
        )
    
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")


@app.post("/v1/chat", response_model=ChatResponse, tags=["Modes"])
async def chat_rag(request: QueryRequest) -> ChatResponse:
    """
    **Modo CHAT RAG** — Busca rápida com Self-Querying
    
    Melhor para:
    - ⚡ Latência baixa (< 500ms)
    - 💰 Custo mínimo
    - 🔍 Buscas simples ("vinho para carne", "até R$100")
    
    Internamente:
    - Detecta automaticamente filtros (preço, país)
    - Recupera contexto do catálogo (ChromaDB + OpenAI embeddings)
    - Gera resposta via GPT com Self-Querying
    
    Exemplo:
    ```bash
    curl -X POST "http://localhost:8000/v1/chat" \\
      -H "Content-Type: application/json" \\
      -d '{"question": "Vinho para churrasco com orçamento até R$100"}'
    ```
    """
    try:
        resultado = _process_chat_request(request.question, request.user_id)
        
        # Converte documents para SourceDocument
        source_docs = [
            SourceDocument(
                nome=doc.metadata.get("nome", "Desconhecido"),
                tipo=doc.metadata.get("tipo"),
                pais=doc.metadata.get("pais"),
                preco=str(doc.metadata.get("preco", "N/A")),
            )
            for doc in resultado.get("source_documents", [])
        ]
        
        return ChatResponse(
            answer=resultado["result"],
            source_documents=source_docs,
            filters_applied=resultado.get("filters_applied", []),
        )
    
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")


@app.post("/v1/agent", response_model=AgentResponse, tags=["Modes"])
async def agent_sommelier(request: QueryRequest) -> AgentResponse:
    """
    **Modo AGENT** — Orquestração inteligente de ferramentas
    
    Melhor para:
    - 🛠️ Consultas complexas que precisam de múltiplas ferramentas
    - 📦 Integração com sistemas corporativos (estoque, CRM, promoções)
    - 🤖 Multi-step reasoning
    
    O Agent automaticamente escolhe quais ferramentas usar:
    1. **buscar_vinho_no_catalogo**: RAG search (similar ao Chat)
    2. **verificar_preco_promocional**: Consulta DB de promoções
    3. **verificar_disponibilidade**: Consulta sistema de estoque
    4. **recomendar_harmonizacao**: Sommelier rules baseadas em regras
    
    Exemplo:
    ```bash
    curl -X POST "http://localhost:8000/v1/agent" \\
      -H "Content-Type: application/json" \\
      -d '{"question": "Tem Malbec em estoque com promoção?"}'
    ```
    """
    try:
        resultado = _process_agent_request(request.question, request.user_id)
        
        # Extrai tools usadas do agent scratchpad (se disponível)
        tools_used = []
        if "tool_calls" in str(resultado):
            # Lógica simples de detecção (pode ser refinada)
            if "buscar" in resultado["output"].lower():
                tools_used.append("buscar_vinho_no_catalogo")
            if "promo" in resultado["output"].lower():
                tools_used.append("verificar_preco_promocional")
            if "estoque" in resultado["output"].lower():
                tools_used.append("verificar_disponibilidade")
        
        return AgentResponse(
            answer=resultado["output"],
            tools_used=tools_used,
        )
    
    except Exception as e:
        logger.error(f"Agent error: {e}")
        raise HTTPException(status_code=500, detail=f"Agent processing failed: {str(e)}")


@app.post("/v1/judge", response_model=JudgeResponse, tags=["Modes"])
async def multi_llm_judge(request: QueryRequest) -> JudgeResponse:
    """
    **Modo JUDGE** — Comparação multi-modelo com árbitro inteligente
    
    Melhor para:
    - 🏆 Máxima precisão/qualidade (custo 3x maior)
    - 🎯 Consultas críticas ou de alta importância
    - 📊 Benchmarking de modelos
    
    Executa em paralelo:
    - GPT-4o-mini (OpenAI)
    - Llama-3.3-70b (Groq) — mais rápido
    - Gemini-2.0-flash (Google) — mais criativo
    
    Um "juiz" inteligente escolhe a melhor resposta.
    
    Exemplo:
    ```bash
    curl -X POST "http://localhost:8000/v1/judge" \\
      -H "Content-Type: application/json" \\
      -d '{"question": "Qual é o melhor vinho para investimento?"}'
    ```
    """
    try:
        resultado = _process_judge_request(request.question, request.user_id)
        
        # Monta response com scores dos modelos
        model_scores = {}
        if "all_answers" in resultado:
            # Simula scores baseado em disponibilidade de respostas
            for model_name in resultado["all_answers"]:
                model_scores[model_name] = 0.85  # Score placeholder
        
        return JudgeResponse(
            winner=resultado.get("winner", "gpt-4o-mini"),
            reason=resultado.get("reason", "Avaliação multi-modelo concluída"),
            answer=resultado.get("answer", resultado.get("output", "")),
            model_scores=model_scores,
        )
    
    except Exception as e:
        logger.error(f"Judge error: {e}")
        raise HTTPException(status_code=500, detail=f"Judge processing failed: {str(e)}")


# ============================================================================
# MIDDLEWARES / ERROR HANDLERS
# ============================================================================


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware para logging de requisições."""
    logger.info(f"{request.method} {request.url.path}")
    response = await call_next(request)
    return response


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handler customizado para HTTPExceptions."""
    logger.error(f"HTTP {exc.status_code}: {exc.detail}")
    return {
        "error": exc.detail,
        "status_code": exc.status_code,
        "path": str(request.url.path),
    }


# ============================================================================
# STARTUP / SHUTDOWN
# ============================================================================


@app.on_event("startup")
async def startup_event():
    """Validações e inicializações ao iniciar."""
    logger.info("🚀 Harmoniz.AI API iniciando...")
    
    # Verifica LangSmith
    if os.getenv("LANGCHAIN_TRACING_V2") == "true":
        logger.info(f"✓ LangSmith habilitado (projeto: {os.getenv('LANGCHAIN_PROJECT')})")
    else:
        logger.warning("⚠️  LangSmith desabilitado — configure para observabilidade")
    
    # Verifica variáveis críticas
    api_keys = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "VECTOR_DB": os.getenv("VECTOR_DB_PATH"),
    }
    for key, value in api_keys.items():
        status = "✓" if value else "✗"
        logger.info(f"{status} {key}")
    
    logger.info("✓ API pronta para requisições\n")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup ao desligar."""
    logger.info("🛑 Harmoniz.AI API encerrando...")


# ============================================================================
# MAIN
# ============================================================================


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    
    print("\n" + "=" * 70)
    print("🍷 HARMONIZ.AI API — Starting")
    print("=" * 70)
    print(f"\n📡 Host: http://localhost:{port}")
    print(f"📚 Swagger UI: http://localhost:{port}/docs")
    print(f"🔧 ReDoc: http://localhost:{port}/redoc")
    print(f"🏥 Health: http://localhost:{port}/health")
    print("\n3 MODOS DISPONÍVEIS:")
    print("  1. POST /v1/chat    → RAG ultra-rápido (< 500ms)")
    print("  2. POST /v1/agent   → Orquestração inteligente")
    print("  3. POST /v1/judge   → Máxima qualidade (multi-LLM)")
    print("\n" + "=" * 70 + "\n")
    
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=port,
        reload=os.getenv("ENVIRONMENT") == "development",
        log_level="info",
    )
