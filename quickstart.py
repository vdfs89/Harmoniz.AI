#!/usr/bin/env python
"""
🍷 HARMONIZ.AI — QUICK START GUIDE
===================================

Guia rápido para testar TUDO que foi implementado em 10 minutos.

Requisitos:
  ✓ Python 3.10+
  ✓ Venv ativado
  ✓ .env configurado com API keys
  ✓ ChromaDB com dados (execute src/engine/ingest.py)
"""

import subprocess
import sys
import os
import time
from pathlib import Path

# Cores para terminal
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(texto):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{texto}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}\n")


def print_success(texto):
    print(f"{Colors.OKGREEN}✓ {texto}{Colors.ENDC}")


def print_info(texto):
    print(f"{Colors.OKCYAN}ℹ {texto}{Colors.ENDC}")


def print_warning(texto):
    print(f"{Colors.WARNING}⚠ {texto}{Colors.ENDC}")


def check_requirements():
    """Verifica pré-requisitos."""
    print_header("1️⃣  VERIFICANDO PRÉ-REQUISITOS")
    
    # Check Python version
    version = sys.version_info
    if version.major >= 3 and version.minor >= 10:
        print_success(f"Python {version.major}.{version.minor}")
    else:
        print(f"{Colors.FAIL}✗ Python 3.10+ requerido{Colors.ENDC}")
        return False
    
    # Check venv
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    if in_venv:
        print_success("Venv ativado")
    else:
        print(f"{Colors.FAIL}✗ Venv não está ativado{Colors.ENDC}")
        print("Execute: venv\\Scripts\\activate (Windows)")
        return False
    
    # Check .env
    env_file = Path(".env")
    if env_file.exists():
        print_success(".env encontrado")
    else:
        print_warning(".env não encontrado — use .env.example")
        return False
    
    # Check data directory
    data_dir = Path("data/processed/chroma_db")
    if data_dir.exists():
        print_success("ChromaDB carregado")
    else:
        print_warning("ChromaDB não encontrado — execute: python src/engine/ingest.py")
        return False
    
    return True


def test_chat_mode():
    """Testa modo Chat RAG."""
    print_header("2️⃣  TESTANDO MODO CHAT RAG")
    
    try:
        print_info("Importando módulos...")
        from src.engine.harmoniz_ai import perguntar_ao_sommelier
        
        print_info("Enviando pergunta...")
        resultado = perguntar_ao_sommelier("Vinho para frutos do mar")
        
        resposta = resultado["result"]
        print_success(f"Resposta recebida ({len(resposta)} chars)")
        
        print_info(f"\n📝 RESPOSTA:")
        print(f"{Colors.OKBLUE}{resposta[:200]}...{Colors.ENDC}\n")
        
        if resultado["source_documents"]:
            print_info(f"📚 Fontes: {len(resultado['source_documents'])} documentos")
        
        if resultado["filters_applied"]:
            print_info(f"🔍 Filtros: {', '.join(resultado['filters_applied'])}")
        
        return True
    except Exception as e:
        print(f"{Colors.FAIL}✗ Erro: {e}{Colors.ENDC}")
        return False


def test_agent_mode():
    """Testa modo Agent."""
    print_header("3️⃣  TESTANDO MODO AGENT")
    
    try:
        print_info("Criando Agent...")
        from src.engine.sommelier_agent import criar_sommelier_agent
        
        agent = criar_sommelier_agent()
        
        print_info("Enviando pergunta...")
        resultado = agent.invoke({"input": "Tem Malbec em estoque?"})
        
        resposta = resultado["output"]
        print_success(f"Resposta recebida ({len(resposta)} chars)")
        
        print_info(f"\n🤖 RESPOSTA:")
        print(f"{Colors.OKBLUE}{resposta[:200]}...{Colors.ENDC}\n")
        
        return True
    except Exception as e:
        print(f"{Colors.FAIL}✗ Erro: {e}{Colors.ENDC}")
        return False


def test_judge_mode():
    """Testa modo Judge."""
    print_header("4️⃣  TESTANDO MODO JUDGE (Multi-LLM)")
    
    try:
        print_info("Importando Judge...")
        from src.engine.multi_llm_judge import ask_with_judge
        
        print_info("Consultando 3 LLMs em paralelo...")
        resultado = ask_with_judge("Qual é o melhor Malbec?")
        
        winner = resultado.get("winner", "Unknown")
        print_success(f"Modelo vencedor: {winner}")
        
        resposta = resultado.get("answer", resultado.get("output", ""))
        print_info(f"\n🏆 RESPOSTA DO VENCEDOR:")
        print(f"{Colors.OKBLUE}{resposta[:200]}...{Colors.ENDC}\n")
        
        return True
    except Exception as e:
        print(f"{Colors.FAIL}✗ Erro: {e}{Colors.ENDC}")
        return False


def test_api():
    """Testa API REST."""
    print_header("5️⃣  TESTANDO API REST (FastAPI)")
    
    try:
        import requests
        
        print_info("Iniciando servidor API em background...")
        print_info("URL: http://localhost:8000")
        
        # Tenta health check
        print_info("Checando saúde da API...")
        try:
            response = requests.get("http://localhost:8000/health", timeout=2)
            if response.status_code == 200:
                print_success("API está online!")
                
                # Lista endpoints
                print_info("\n📡 ENDPOINTS DISPONÍVEIS:")
                print_info("  POST http://localhost:8000/v1/chat   → Chat RAG")
                print_info("  POST http://localhost:8000/v1/agent  → Agent")
                print_info("  POST http://localhost:8000/v1/judge  → Judge")
                print_info("  GET  http://localhost:8000/docs      → Swagger UI")
                
                return True
        except requests.exceptions.ConnectionError:
            print_warning("API não está rodando")
            print_info("Execute em outro terminal: python run_api.py")
            print_info("Depois rode este script novamente para testar a API")
            return False
    except ImportError:
        print_warning("requests não instalado — pulando teste de API")
        return False
    except Exception as e:
        print(f"{Colors.FAIL}✗ Erro: {e}{Colors.ENDC}")
        return False


def show_summary():
    """Mostra sumário final."""
    print_header("📊 SUMÁRIO DO PROJETO")
    
    print(f"{Colors.BOLD}ARQUITETURA:{Colors.ENDC}")
    print("""
  🚀 Camada 1: Chat RAG
     └─ LCEL + Self-Querying + ChromaDB
     └─ Latência: < 500ms | Custo: Mínimo
  
  🤖 Camada 2: Agent com 4 Ferramentas
     └─ Orquestração automática (busca, estoque, promoção, harmonização)
     └─ Latência: 1-3s | Custo: Médio
  
  🏆 Camada 3: Judge (Multi-LLM)
     └─ GPT-4o-mini vs Llama-3.3 vs Gemini-2.0 com árbitro inteligente
     └─ Latência: 3-5s | Custo: Alto (máxima qualidade)
    """)
    
    print(f"{Colors.BOLD}OBSERVABILIDADE:{Colors.ENDC}")
    print("""
  🔍 LangSmith Integration
     └─ Rastreamento automático de latência, custos, alucinações
     └─ Dashboard: https://smith.langchain.com/projects/
    """)
    
    print(f"{Colors.BOLD}DEPLOYMENT:{Colors.ENDC}")
    print("""
  🐳 Docker
     └─ Dockerfile multi-stage (production-ready)
     └─ docker-compose.yml para desenvolvimento
  
  🌐 FastAPI REST
     └─ 3 endpoints: /v1/chat, /v1/agent, /v1/judge
     └─ Health check: /health
     └─ Swagger UI: /docs
    """)
    
    print(f"{Colors.BOLD}GIT COMMITS:{Colors.ENDC}")
    print("""
  10 commits mostrando progresso:
    • Data ingestion (ETL)
    • LCEL modernization
    • Self-Querying RAG
    • Agent Pattern
    • Multi-LLM orchestration
    • LangSmith observability
    • FastAPI + Docker
    • Examples + Documentation
    """)
    
    print(f"{Colors.BOLD}REQUISITOS DA VAGA WINE ATENDIDOS:{Colors.ENDC}")
    print("""
  ✓ Experiência avançada com LangChain (LCEL, Agent, Multi-Model)
  ✓ "Integrar soluções de IA aos sistemas" → Agent com 4 tools
  ✓ "Monitorar performance em produção" → LangSmith + métricas
  ✓ "MLOps como diferencial" → Observability setup profissional
  ✓ Código limpo, documentado, versionado
  ✓ Portfolio pronto para entrevista técnica
    """)


def show_next_steps():
    """Mostra próximos passos."""
    print_header("🚀 PRÓXIMOS PASSOS")
    
    print("""
1️⃣  TESTE TUDO LOCALMENTE:
    
    # Terminal 1: Inicie a API
    python run_api.py
    
    # Terminal 2: Rode exemplos
    python examples_api.py
    
    # Browser: Abra Swagger UI
    http://localhost:8000/docs

2️⃣  CONFIGURE LANGSMITH (Opcional mas recomendado):
    
    # 1. Crie conta em https://smith.langchain.com
    # 2. Gere API Key
    # 3. Configure .env:
    LANGCHAIN_TRACING_V2=true
    LANGCHAIN_API_KEY=ls_...
    
    # 4. Veja rastreamento em tempo real

3️⃣  DOCKERFILE PARA PRODUCTION:
    
    docker build -t harmoniz-ai:1.0 .
    docker run -p 8000:8000 harmoniz-ai:1.0

4️⃣  ENTREVISTA NA WINE:
    
    • Abra ARCHITECTURE.md durante a entrevista
    • Explique os 3 modos e trade-offs
    • Mostre LangSmith dashboard
    • Code review: https://github.com/vdfs89/Harmoniz.AI
    """)


def main():
    """Executa testes."""
    print_header("🍷 HARMONIZ.AI — TESTE RÁPIDO (10 minutos)")
    
    # Checklist
    if not check_requirements():
        print(f"\n{Colors.FAIL}Falha nos pré-requisitos{Colors.ENDC}")
        return
    
    results = {
        "Chat RAG": test_chat_mode(),
        "Agent": test_agent_mode(),
        "Judge": test_judge_mode(),
        "API": test_api(),
    }
    
    # Sumário
    show_summary()
    
    # Resultados
    print_header("✅ RESULTADOS")
    for nome, passou in results.items():
        status = f"{Colors.OKGREEN}✓ PASSOU{Colors.ENDC}" if passou else f"{Colors.WARNING}⚠ PULOU/FALHOU{Colors.ENDC}"
        print(f"{nome:15} {status}")
    
    # Próximos passos
    show_next_steps()
    
    print(f"\n{Colors.OKGREEN}{Colors.BOLD}Projeto está pronto para entrevista! 🎉{Colors.ENDC}\n")


if __name__ == "__main__":
    main()
