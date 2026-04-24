"""
Exemplos de uso da Harmoniz.AI REST API
========================================

Copia e cola esses exemplos para testar a API rapidamente.
"""

# ============================================================================
# SETUP INICIAL
# ============================================================================

import requests
import json

# URL base (ajuste conforme seu ambiente)
BASE_URL = "http://localhost:8000"

# Headers padrão
HEADERS = {"Content-Type": "application/json"}


# ============================================================================
# 1. HEALTH CHECK
# ============================================================================

def check_health():
    """Verifica se a API está online e pronta."""
    response = requests.get(f"{BASE_URL}/health")
    print("Status:", response.status_code)
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))


# ============================================================================
# 2. MODO CHAT (RAG Ultra-Rápido)
# ============================================================================

def exemplo_chat_simples():
    """Busca simples com Self-Querying."""
    payload = {
        "question": "Qual vinho combina com frutos do mar?",
        "user_id": "user_123"
    }
    response = requests.post(f"{BASE_URL}/v1/chat", json=payload, headers=HEADERS)
    print("Chat Response:", response.status_code)
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))


def exemplo_chat_com_filtro():
    """Busca com filtros automáticos (preço, país)."""
    payload = {
        "question": "Vinho argentino para churrasco, até R$150",
        "user_id": "user_456"
    }
    response = requests.post(f"{BASE_URL}/v1/chat", json=payload, headers=HEADERS)
    resultado = response.json()
    
    print("🍷 RESPOSTA:")
    print(resultado["answer"])
    
    print("\n📍 FONTES:")
    for doc in resultado["source_documents"]:
        print(f"  • {doc['nome']} ({doc['tipo']}) - R$ {doc['preco']}")
    
    print("\n🔍 FILTROS DETECTADOS:")
    for filtro in resultado["filters_applied"]:
        print(f"  • {filtro}")


# ============================================================================
# 3. MODO AGENT (Orquestração com Ferramentas)
# ============================================================================

def exemplo_agent_consulta_estoque():
    """Agent consulta estoque automaticamente."""
    payload = {
        "question": "Tem Malbec em estoque com promoção ativa?",
        "user_id": "vendedor_789"
    }
    response = requests.post(f"{BASE_URL}/v1/agent", json=payload, headers=HEADERS)
    resultado = response.json()
    
    print("🤖 AGENT RESPONSE:")
    print(resultado["answer"])
    
    print("\n🔧 FERRAMENTAS USADAS:")
    for tool in resultado["tools_used"]:
        print(f"  • {tool}")


def exemplo_agent_recomendacao():
    """Agent recomenda baseado em ocasião."""
    payload = {
        "question": "Vou fazer uma festa com comida italiana, o que você recomenda?",
        "user_id": "user_999"
    }
    response = requests.post(f"{BASE_URL}/v1/agent", json=payload, headers=HEADERS)
    resultado = response.json()
    print(resultado["answer"])


# ============================================================================
# 4. MODO JUDGE (Multi-LLM com Árbitro)
# ============================================================================

def exemplo_judge():
    """Compara respostas de 3 LLMs (GPT + Llama + Gemini)."""
    payload = {
        "question": "Qual é o melhor Pinot Noir para investimento a longo prazo?",
        "user_id": "sommelier_expert"
    }
    response = requests.post(f"{BASE_URL}/v1/judge", json=payload, headers=HEADERS)
    resultado = response.json()
    
    print(f"🏆 MODELO VENCEDOR: {resultado['winner']}")
    print(f"📊 RAZÃO: {resultado['reason']}")
    print(f"\n💡 RESPOSTA SELECIONADA:\n{resultado['answer']}")
    
    print("\n📈 SCORES:")
    for modelo, score in resultado["model_scores"].items():
        stars = "⭐" * int(score * 5)
        print(f"  {modelo:20} {stars} ({score:.2f})")


# ============================================================================
# 5. COMPARAÇÃO DE PERFORMANCE
# ============================================================================

def comparar_performance():
    """Compara latência dos 3 modos."""
    import time
    
    pergunta = "Vinho para pizza com cerveja gelada"
    
    modos = {
        "chat": f"{BASE_URL}/v1/chat",
        "agent": f"{BASE_URL}/v1/agent",
        "judge": f"{BASE_URL}/v1/judge",
    }
    
    payload = {"question": pergunta, "user_id": "perf_test"}
    
    print("⏱️  TESTE DE LATÊNCIA\n")
    
    for modo, url in modos.items():
        inicio = time.time()
        response = requests.post(url, json=payload, headers=HEADERS)
        latencia_ms = (time.time() - inicio) * 1000
        
        status = "✓" if response.status_code == 200 else "✗"
        print(f"{status} {modo.upper():10} {latencia_ms:7.2f}ms")


# ============================================================================
# MAIN — Execute os exemplos
# ============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🍷 EXEMPLOS DE USO — Harmoniz.AI REST API")
    print("=" * 70)
    
    # 1. Health Check
    print("\n[1] HEALTH CHECK")
    print("-" * 70)
    try:
        check_health()
    except Exception as e:
        print(f"Erro: {e}")
        print("   ⚠️  API não está rodando!")
        print("   Execute: python run_api.py")
    
    # 2. Chat Simples
    print("\n\n[2] CHAT SIMPLES")
    print("-" * 70)
    try:
        exemplo_chat_simples()
    except Exception as e:
        print(f"Erro: {e}")
    
    # 3. Chat com Filtros
    print("\n\n[3] CHAT COM FILTROS AUTOMÁTICOS")
    print("-" * 70)
    try:
        exemplo_chat_com_filtro()
    except Exception as e:
        print(f"Erro: {e}")
    
    # 4. Agent
    print("\n\n[4] AGENT (Orquestração com Ferramentas)")
    print("-" * 70)
    try:
        exemplo_agent_consulta_estoque()
    except Exception as e:
        print(f"Erro: {e}")
    
    # 5. Agent Recomendação
    print("\n\n[5] AGENT (Recomendação por Ocasião)")
    print("-" * 70)
    try:
        exemplo_agent_recomendacao()
    except Exception as e:
        print(f"Erro: {e}")
    
    # 6. Judge
    print("\n\n[6] JUDGE (Multi-LLM com Árbitro)")
    print("-" * 70)
    try:
        exemplo_judge()
    except Exception as e:
        print(f"Erro: {e}")
    
    # 7. Performance
    print("\n\n[7] COMPARAÇÃO DE LATÊNCIA")
    print("-" * 70)
    try:
        comparar_performance()
    except Exception as e:
        print(f"Erro: {e}")
    
    print("\n" + "=" * 70 + "\n")
