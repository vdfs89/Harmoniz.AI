![Harmoniz.AI](img/Gemini_Generated_Image_xazn0vxazn0vxazn.png)

# Harmoniz.AI

Sommelier digital com arquitetura RAG para recomendacao de vinhos com base em catalogo real.

## Visao Geral

O `Harmoniz.AI` foi projetado para responder perguntas sobre vinhos com maior precisao e menor risco de alucinacao, combinando:

- Recuperacao semantica de vinhos em base vetorial (RAG).
- Resposta conversacional orientada por contexto.
- Orquestracao multi-modelo (`GPT`, `Groq`, `Gemini`) com um juiz para selecionar a melhor resposta final.

Em vez de responder apenas com conhecimento generico, o sistema busca rotulos e descricoes no proprio dataset e usa esse contexto para fundamentar a recomendacao.

## Principais Recursos

- Ingestao de dados em `CSV`, `XLSX` e `XLS`.
- Conversao do catalogo em documentos semanticos com metadados (`nome`, `tipo`, `pais`, `preco`).
- Armazenamento vetorial persistente com `ChromaDB`.
- Chat RAG com persona de sommelier.
- Modo de avaliacao com multiplos modelos e juiz.
- Fallback resiliente quando algum provedor falha.

## Arquitetura

1. O arquivo de vinhos e carregado (`data/raw/...`).
2. Cada vinho vira um `Document` com perfil sensorial e harmonizacao.
3. Os documentos sao embedados (`text-embedding-3-small`) e persistidos no `Chroma`.
4. Em tempo de pergunta:
	 - `harmoniz_ai.py` usa retriever + prompt especialista para responder.
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

## Configuracao do Ambiente

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

### 2) Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3) Configurar `.env`

Crie ou ajuste o arquivo `.env` com as variaveis abaixo:

```env
# Chaves
OPENAI_API_KEY=...
GROQ_API_KEY=...
GEMINI_API_KEY=...

# Modelos
OPENAI_MODEL=gpt-4o-mini
GROQ_MODEL=llama-3.1-70b-versatile
GEMINI_MODEL=gemini-1.5-flash
JUDGE_PROVIDER=openai
JUDGE_MODEL=gpt-4o-mini

# Dados e RAG
WINE_DATA_PATH=data/raw/wines_from_winecombr.xlsx
VECTOR_DB_PATH=data/processed/chroma_db
RAG_TOP_K=6
```

Observacao:
- `WINE_CSV_PATH` ainda pode ser usado como retrocompatibilidade no `ingest.py`.

## Como Executar

### 1) Ingerir e indexar os vinhos

```bash
python src/engine/ingest.py
```

### 2) Rodar o chat RAG do sommelier

```bash
python src/engine/harmoniz_ai.py
```

### 3) Rodar o modo multi-modelo com juiz

```bash
python src/engine/multi_llm_judge.py "Quero um vinho para massa com cogumelos"
```

## Scripts Principais

- `src/engine/ingest.py`
	- Le tabela de vinhos (`csv/xlsx/xls`).
	- Monta contexto rico por vinho.
	- Gera embeddings e persiste no Chroma.

- `src/engine/harmoniz_ai.py`
	- Carrega base vetorial.
	- Executa `RetrievalQA` com prompt de sommelier.
	- Disponibiliza chat interativo no terminal.

- `src/engine/multi_llm_judge.py`
	- Recupera contexto via RAG.
	- Consulta GPT, Groq e Gemini (quando configurados).
	- Escolhe resposta final com juiz (`openai`, `groq` ou `gemini`).
	- Aplica fallback se algum modelo/juiz falhar.

## Troubleshooting Rapido

- Erro de autenticacao: valide as chaves no `.env`.
- Modelo invalido/deprecado: ajuste `OPENAI_MODEL`, `GROQ_MODEL` ou `GEMINI_MODEL`.
- Sem contexto RAG: confira `VECTOR_DB_PATH` e execute novamente `ingest.py`.
- Erro de leitura de planilha: valide colunas obrigatorias no dataset (`Nome`, `Harmonização`, etc.).

## Roadmap

- Filtros por faixa de preco/tipo/pais no retriever.
- API REST para integracao com front-end.
- Avaliacao automatica de qualidade das respostas.
- Observabilidade e telemetria de prompts.

## Autor

Projeto desenvolvido por `vdfs89` como demonstracao tecnica de IA generativa aplicada a recomendacao de vinhos com dados reais.
