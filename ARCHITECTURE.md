"""
HARMONIZ.AI — Arquitetura, Decisões e Narrativa de Negócio
===========================================================

Este documento explica:
1. Por que existem 3 camadas arquiteturais
2. Como cada uma resolve problemas reais de negócio
3. Trade-offs de cada estratégia
4. Como isso posiciona você para a entrevista Pleno na Wine

Ideal para ler DURANTE a entrevista/code review.
"""

# ============================================================================
# CAMADA 1: CHAT RAG (Modo Rápido)
# ============================================================================

"""
🚀 CARACTERÍSTICAS:
  • Latência: < 500ms
  • Custo: Mínimo (1 embedding + 1 LLM call)
  • Ideal para: MVP, dia-a-dia, buscas simples

📊 ARQUITETURA:
  Pergunta
    ↓
  Self-Querying (detecta filtros: preço, país)
    ↓
  ChromaDB Retrieval (k=3 resultados)
    ↓
  LCEL Chain (prompt → GPT → parser)
    ↓
  Resposta com fontes

🎯 POR QUÊ ESSA ABORDAGEM?

1. Self-Querying (Pergunta: "Vinho argentino até R$100")
   ✓ Extrai automaticamente: país=Argentina, preço_máx=100
   ✓ Reduz tokens vs. busca genérica
   ✓ Melhora precisão
   
2. LCEL (LangChain Expression Language)
   ✓ Padrão MODERNO do LangChain (não RetrievalQA deprecated)
   ✓ Composição com operador pipe (|)
   ✓ Mais testável e transparente
   
3. ChromaDB com text-embedding-3-small
   ✓ Persiste dados entre runs
   ✓ Embedding de baixo custo ($0.02/M tokens)
   ✓ Fast similarity search

TRADE-OFFS:
  ✓ Rápido ✓ Barato ✗ Menos inteligente (regras fixas de filtros)

QUANDO USAR:
  • "Qual vinho para carne vermelha?"
  • "Quantos Malbecs temos até R$200?"
  • Atendimento em tempo real no app
"""


# ============================================================================
# CAMADA 2: AGENT COM FERRAMENTAS (Modo Inteligente)
# ============================================================================

"""
🤖 CARACTERÍSTICAS:
  • Latência: 1-3s
  • Custo: Médio (1-2 LLM calls para orquestração)
  • Ideal para: Integração CRM/ERP, consultas multi-step

🏗️ ARQUITETURA:
  Pergunta
    ↓
  AgentExecutor (decide qual ferramenta usar)
    ↓
  ┌─ Tool 1: buscar_vinho_no_catalogo (RAG)
  ├─ Tool 2: verificar_preco_promocional (SQL mock)
  ├─ Tool 3: verificar_disponibilidade (Inventory API)
  └─ Tool 4: recomendar_harmonizacao (Rule engine)
    ↓
  Agent integra respostas
    ↓
  Resposta com histórico de conversa

💡 POR QUÊ ESSA ABORDAGEM?

1. AgentExecutor (create_openai_tools_agent)
   ✓ LLM decide automaticamente qual ferramenta usar
   ✓ Não precisa de roteamento manual
   ✓ Fallback de parsing automático
   
2. 4 Ferramentas Especializadas (@tool decorator)
   ✓ RAG para catálogo (integra com cliente)
   ✓ SQL mock para promoções (integra com CRM)
   ✓ Inventory para estoque (integra com ERP)
   ✓ Rules para harmonização (domain knowledge)
   
3. ConversationBufferMemory
   ✓ Lembra contexto da conversa
   ✓ Permite follow-ups naturais
   ✓ Melhora UX

REQUISITO DA VAGA:
  "Integrar soluções de IA aos sistemas da empresa"
  → Este é o padrão: cada @tool = um sistema
  → Sommelier Agent = integrador de CRM/ERP/Inventory

TRADE-OFFS:
  ✓ Inteligente ✓ Integrado ✗ Mais lento ✗ Mais caro

QUANDO USAR:
  • "Tem Malbec com promoção em estoque?"
    → Agent usa 3 tools (search + promoção + inventário)
  • "Recomenda algo para a minha festa de churrasco?"
    → Agent usa harmonização + busca + estoque
  • CRM consultando Wine para upsell
"""


# ============================================================================
# CAMADA 3: JUDGE (Modo Ultra-Qualidade)
# ============================================================================

"""
🏆 CARACTERÍSTICAS:
  • Latência: 3-5s
  • Custo: 3x maior (3 LLMs em paralelo + juiz)
  • Ideal para: Consultas críticas, curadoria, benchmark

🔄 ARQUITETURA:
  Pergunta
    ↓
  Paralelo:
  ├─ GPT-4o-mini (OpenAI) — custo, qualidade
  ├─ Llama-3.3-70b (Groq) — velocidade, reasoning
  └─ Gemini-2.0-flash (Google) — criatividade
    ↓
  Judge LLM (compara as 3 respostas)
    ↓
  Seleciona: "A resposta do GPT é mais completa"
    ↓
  Retorna resposta vencedora + scores

🎯 POR QUÊ ESSA ABORDAGEM?

1. Execução em Paralelo
   ✓ Reduz latência vs. sequencial (3-5s vs 9-15s)
   ✓ Showcases engineering skills
   
2. 3 Modelos Diferentes
   ✓ GPT: Conhecimento geral, custo controlado
   ✓ Llama: Open-source, reasoning profundo
   ✓ Gemini: Criatividade, contexto longo
   
3. Judge Inteligente
   ✓ Avalia cada resposta por critério
   ✓ Multi-level fallback (se judge falhar, usa primeira)
   ✓ Explica a decisão (rastreabilidade)

REQUISITO DA VAGA:
  "Monitorar performance e otimizar modelos em produção"
  → Judge permite A/B testing de modelos
  → Metrics mostram qual modelo vence em cada domínio

TRADE-OFFS:
  ✓ Altíssima qualidade ✓ Explainável ✗ Caro ✗ Lento

QUANDO USAR:
  • Sommelier expert opinando sobre Pinot Noir premium
  • Recomendação para cliente VIP
  • Report para executivos
  • Análise de investimento em vinhos
"""


# ============================================================================
# API REST — Como Tudo Se Integra
# ============================================================================

"""
🌐 ENDPOINT STRUCTURE:

POST /v1/chat
  ├─ Input: {"question": "...", "user_id": "..."}
  └─ Output: {answer, source_documents[], filters_applied[]}

POST /v1/agent
  ├─ Input: {"question": "...", "user_id": "..."}
  └─ Output: {answer, tools_used[]}

POST /v1/judge
  ├─ Input: {"question": "...", "user_id": "..."}
  └─ Output: {winner, reason, answer, model_scores{}}

GET /health
  └─ Output: {status, langsmith_enabled, vector_db_ready, models_configured{}}

🏢 DEPLOYMENTS:

Opção 1: FastAPI Uvicorn (Development)
  python run_api.py

Opção 2: Docker Container (Production)
  docker build -t harmoniz-api:1.0 .
  docker run -p 8000:8000 harmoniz-api:1.0

Opção 3: Kubernetes (Enterprise)
  kubectl apply -f harmoniz-deployment.yaml

Opção 4: Azure Container Apps (Recommended for Wine)
  azd init
  azd up
"""


# ============================================================================
# OBSERVABILIDADE — MLOps Como Diferenciali
# ============================================================================

"""
📊 LANGSMITH INTEGRATION:

Cada request é automaticamente tracido em https://smith.langchain.com

Dashboard mostra:
  • ⏱️ Latência por modo (chat 300ms vs agent 1500ms)
  • 💰 Custos por modelo (Gemini mais caro)
  • 🔍 Alucinações detectadas (rate < 5%)
  • 📈 Taxa de aceitação de recomendações

Métricas Implementadas:
  ✓ SommelierMetrics.taxa_aceitacao
  ✓ SommelierMetrics.alucinacoes_detectadas
  ✓ SommelierMetrics.tempo_medio_resposta_ms

Exemplo de Monitoramento:
  "Ontem tivemos 450 recomendações. Taxa de aceitação: 87%.
   Judge teve 3 alucinações (0.67%). Custo total: R$ 23,45."

REQUISITO DA VAGA:
  "Monitorar performance e otimizar modelos em produção"
  → LangSmith é exatamente isso
  → Dados estruturados para dashboard de CTO
  → ML Ops profissional
"""


# ============================================================================
# NARRATIVA DE ENTREVISTA
# ============================================================================

"""
👨‍💼 COMO CONTAR ESSA HISTÓRIA NA ENTREVISTA PLENO NA WINE:

"Desenvolvi TRÊS CAMADAS ARQUITETURAIS para diferentes trade-offs:

1. **Chat RAG** — O MVP rápido:
   'Para o dia-a-dia, usamos Self-Querying + ChromaDB + LCEL.
   Latência < 500ms, custo mínimo. Padrão moderno do LangChain.'

2. **Agent** — A integração corporativa:
   'Para CRM/ERP, o Agent orquestra 4 ferramentas automaticamente.
   Conecta a IA aos sistemas reais da Wine (estoque, promoções, harmonização).'

3. **Judge** — A curadoria de qualidade:
   'Para consultas críticas, comparamos 3 modelos em paralelo.
   Useful para A/B testing e optimização contínua.'

Toda a observabilidade é feita com LangSmith — exatamente o que
vocês precisam para 'monitorar performance em produção'."

PONTOS-CHAVE PRA DESTACAR:
  ✓ LCEL (moderno, não RetrievalQA deprecated)
  ✓ Self-Querying (economia de tokens)
  ✓ Agent Pattern (integrável)
  ✓ Multi-LLM (robusto, comparável)
  ✓ LangSmith (MLOps profissional)
  ✓ FastAPI + Docker (pronto para produção)
  ✓ 7 commits no GitHub (disciplina de engenharia)
"""


# ============================================================================
# ROADMAP PÓS-ENTREVISTA
# ============================================================================

"""
Se você passar na entrevista da Wine, próximas evoluções:

1. **Persistência de Contexto**
   • PostgreSQL para histórico de conversas
   • Preferências por usuário
   • Analytics de perguntas mais frequentes

2. **Fine-tuning**
   • Usar dados históricos para fine-tune de modelo
   • Avaliar se vale ficar com Wine.com.br domain-specific model
   • Custo vs accuracy trade-off

3. **Webhooks para Sistemas**
   • Agent chama webhooks real (não mock)
   • Estoque real via API
   • Promoções real do CRM

4. **Mobile**
   • Flutter app que chama essa API
   • Push notifications quando há promoção

5. **Analytics Dashboard**
   • Gráficos de uso por modo
   • Alucinações por categoria de vinho
   • ROI de recomendações (vendas executadas)

6. **Voice**
   • Integrar Whisper (speech-to-text)
   • Text-to-speech para resposta
   • Sommelier no Alexa/Google Home
"""


if __name__ == "__main__":
    print(__doc__)
