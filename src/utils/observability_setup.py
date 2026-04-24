"""
Observability Setup com LangSmith
==================================

Demonstra como integrar LangSmith para monitoramento, debugging e otimizacao 
de chains e agents em producao.

Requisitos da vaga Wine:
- "Monitorar performance e otimizar modelos em producao"
- "MLOps como diferencial"

Este arquivo mostra o padrão profissional de observabilidade para IA em produção.
"""

import os
from typing import Any, Dict

from dotenv import load_dotenv
from langchain.callbacks.manager import trace_as_chain_group
from langchain_core.runnables import RunnableLambda
from langsmith import traceable

load_dotenv()

# ============================================================================
# CONFIGURACAO DE LANGSMITH
# ============================================================================

def setup_langsmith():
    """
    Configura LangSmith para rastreamento automático.
    
    Pré-requisito:
    1. Criar conta em https://smith.langchain.com
    2. Gerar API Key
    3. Adicionar ao .env:
       LANGCHAIN_TRACING_V2=true
       LANGCHAIN_API_KEY=your_api_key_here
       LANGCHAIN_PROJECT=harmoniz-ai-production
    """
    # Verificar se LangSmith está configurado
    if not os.getenv("LANGCHAIN_API_KEY"):
        print("\n⚠️  AVISO: LangSmith não configurado")
        print("   Para ativar observabilidade, configure:")
        print("   1. LANGCHAIN_TRACING_V2=true")
        print("   2. LANGCHAIN_API_KEY=<sua_chave>")
        print("   3. LANGCHAIN_PROJECT=harmoniz-ai-production\n")
        return False
    
    print("✓ LangSmith configurado com sucesso!")
    print(f"  Projeto: {os.getenv('LANGCHAIN_PROJECT', 'default')}")
    return True


# ============================================================================
# DECORADORES PARA RASTREAMENTO
# ============================================================================

@traceable(name="wine_recommendation_traced", run_type="chain")
def exemplo_recomendacao_tracida(pergunta: str) -> Dict[str, Any]:
    """
    Exemplo de funcao tracida com LangSmith.
    
    O decorator @traceable automaticamente:
    - Registra início e fim da execução
    - Captura latência (quanto tempo levou)
    - Registra entradas e saídas
    - Detecta erros e exceções
    - Permite debugging visual no dashboard LangSmith
    
    Isso é visível em: https://smith.langchain.com/projects/...
    """
    return {
        "pergunta": pergunta,
        "resposta": f"Recomendação para: {pergunta}",
        "latencia_ms": 250,
        "confianca": 0.95,
    }


# ============================================================================
# METRICAS DE MONITORAMENTO EM PRODUCAO
# ============================================================================

class SommelierMetrics:
    """
    Coleta e rastreia métricas de negócio do Harmoniz.AI em produção.
    """
    
    def __init__(self):
        self.total_recomendacoes = 0
        self.recomendacoes_aceitas = 0
        self.tempo_medio_resposta_ms = 0
        self.taxa_erro = 0.0
        self.alucinacoes_detectadas = 0
    
    @traceable(name="track_recommendation_metric", run_type="tool")
    def registrar_recomendacao(
        self,
        pergunta: str,
        resposta: str,
        latencia_ms: float,
        aceita: bool = False,
        alucinacao: bool = False,
    ) -> None:
        """
        Registra uma recomendação no LangSmith.
        
        Métricas capturadas:
        - Throughput: quantas recomendacoes por segundo
        - Latência: tempo de resposta
        - Taxa de aceitação: % que o usuário aceitou
        - Alucinações: quando a IA inventa um vinho que não existe
        """
        self.total_recomendacoes += 1
        
        if aceita:
            self.recomendacoes_aceitas += 1
        
        if alucinacao:
            self.alucinacoes_detectadas += 1
        
        # Log para visualização em LangSmith
        print(
            f"\n[METRICA] Recomendação #{self.total_recomendacoes}\n"
            f"  Pergunta: {pergunta[:50]}...\n"
            f"  Latência: {latencia_ms:.2f}ms\n"
            f"  Aceita: {'✓' if aceita else '✗'}\n"
            f"  Alucinação: {'⚠️' if alucinacao else '✓'}\n"
            f"  Taxa aceitação até agora: {self.taxa_aceitacao():.1%}"
        )
    
    def taxa_aceitacao(self) -> float:
        """Calcula a taxa de aceitação das recomendações."""
        if self.total_recomendacoes == 0:
            return 0.0
        return self.recomendacoes_aceitas / self.total_recomendacoes
    
    @traceable(name="get_observability_report", run_type="tool")
    def gerar_relatorio_observabilidade(self) -> Dict[str, Any]:
        """
        Gera relatório de observabilidade para o dashboard.
        
        Este é o tipo de métrica que aparece no LangSmith:
        - SLA (Service Level Agreement): latência < 500ms
        - Taxa de erro: % de falhas
        - Alucinações: quantidade de respostas inventadas
        """
        taxa_alucinacao = (
            self.alucinacoes_detectadas / self.total_recomendacoes
            if self.total_recomendacoes > 0
            else 0.0
        )
        
        return {
            "periodo": "últimos 24h (exemplo)",
            "total_recomendacoes": self.total_recomendacoes,
            "taxa_aceitacao": f"{self.taxa_aceitacao():.1%}",
            "alucinacoes": self.alucinacoes_detectadas,
            "taxa_alucinacao": f"{taxa_alucinacao:.2%}",
            "sla_latencia": "< 500ms",
            "status": "🟢 SAUDÁVEL" if taxa_alucinacao < 0.05 else "🔴 ALERTA",
        }


# ============================================================================
# INTEGRACAO COM CHAINS (Exemplo)
# ============================================================================

@traceable(name="rag_chain_with_monitoring", run_type="chain")
def rag_chain_monitorado(
    pergunta: str,
    retriever: Any,
    llm: Any,
) -> str:
    """
    Exemplo de RAG chain integrada com LangSmith.
    
    O LangSmith automaticamente traça:
    1. Retriever execution
    2. LLM call
    3. Prompt formatting
    4. Latência total
    5. Tokens consumidos
    
    Visível no dashboard: https://smith.langchain.com/
    """
    # Simulacao de retrieval
    contexto = f"[Contexto recuperado para: {pergunta}]"
    
    # Simulacao de LLM call
    resposta = f"Resposta gerada para: {pergunta}"
    
    return resposta


# ============================================================================
# EXEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🔍 HARMONIZ.AI — Observability Setup com LangSmith")
    print("=" * 70)
    
    # 1. Setup LangSmith
    setup_langsmith()
    
    # 2. Instancia métricas
    metricas = SommelierMetrics()
    
    # 3. Exemplo de rastreamento
    print("\n📊 Simulando recomendações monitoradas...\n")
    
    # Recomendação 1: Sucesso
    metricas.registrar_recomendacao(
        pergunta="Vinho para churrasco",
        resposta="Malbec Argentino",
        latencia_ms=245.3,
        aceita=True,
        alucinacao=False,
    )
    
    # Recomendação 2: Alucinação detectada
    metricas.registrar_recomendacao(
        pergunta="Vinho misterioso para fantasmas",
        resposta="Vinho inexistente no catálogo",
        latencia_ms=189.2,
        aceita=False,
        alucinacao=True,
    )
    
    # Recomendação 3: Sucesso
    metricas.registrar_recomendacao(
        pergunta="Vinho para frutos do mar",
        resposta="Sauvignon Blanc Francês",
        latencia_ms=267.8,
        aceita=True,
        alucinacao=False,
    )
    
    # 4. Relatório
    print("\n" + "=" * 70)
    print("📈 RELATORIO DE OBSERVABILIDADE")
    print("=" * 70)
    relatorio = metricas.gerar_relatorio_observabilidade()
    for chave, valor in relatorio.items():
        print(f"{chave.upper():.<30} {valor}")
    
    print("\n" + "=" * 70)
    print("💡 PROXIMO PASSO:")
    print("   1. Configure LangSmith (veja setup_langsmith())")
    print("   2. Visite: https://smith.langchain.com/projects/")
    print("   3. Veja dashboards em TEMPO REAL de:")
    print("      - Latência de cada call")
    print("      - Taxa de erro")
    print("      - Alucinações detectadas")
    print("      - Custos de tokens (GPT, Gemini, etc)")
    print("=" * 70 + "\n")
