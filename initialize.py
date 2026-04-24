#!/usr/bin/env python3
"""
🚀 Inicializador de Harmoniz.AI — Streamlit Edition
====================================================

Script que prepara o ambiente e inicia a aplicação Streamlit.
Executa validações antes de rodar.

Uso:
    python initialize.py

Windows:
    python initialize.py
    # ou
    py initialize.py
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    """Print formatted header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}\n")


def print_success(text):
    """Print success message."""
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")


def print_warning(text):
    """Print warning message."""
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")


def print_error(text):
    """Print error message."""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")


def check_venv():
    """Verifica se estamos em um venv."""
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    
    if not in_venv:
        print_warning("Não está em um ambiente virtual ativo")
        print("   Execute: venv\\Scripts\\activate (Windows)")
        print("            source venv/bin/activate (Unix)")
        return False
    
    print_success("Ambiente virtual ativado")
    return True


def check_env_file():
    """Verifica se .env existe e cria exemplo se não existir."""
    if Path(".env").exists():
        print_success(".env já existe")
        return True
    
    # Cria .env baseado em .env.example se existir
    if Path(".env.example").exists():
        shutil.copy(".env.example", ".env")
        print_warning(".env criado baseado em .env.example")
        print("   ⚠️ Configure as API keys em .env antes de continuar!")
        return True
    
    print_warning(".env não encontrado")
    return False


def check_streamlit_secrets():
    """Verifica e prepara .streamlit/secrets.toml."""
    streamlit_dir = Path(".streamlit")
    streamlit_dir.mkdir(exist_ok=True)
    
    secrets_file = streamlit_dir / "secrets.toml"
    secrets_example = streamlit_dir / "secrets.toml.example"
    
    if secrets_file.exists():
        print_success(".streamlit/secrets.toml já existe")
        return True
    
    if secrets_example.exists():
        print_warning(".streamlit/secrets.toml não encontrado")
        print("   Copie .streamlit/secrets.toml.example → .streamlit/secrets.toml")
        print("   e configure seus valores antes de rodar a app")
        return False
    
    print_error("Nenhum arquivo de secrets encontrado")
    return False


def check_data_structure():
    """Verifica se existe ChromaDB."""
    chroma_path = Path("data/processed/chroma_db")
    
    if chroma_path.exists():
        print_success("ChromaDB encontrado")
        return True
    
    print_warning("ChromaDB não encontrado")
    print("   Execute: python src/engine/ingest.py")
    return False


def check_imports():
    """Tenta importar os módulos principais."""
    print("\nVerificando importações...")
    
    try:
        from src.engine.harmoniz_ai import perguntar_ao_sommelier
        print_success("src.engine.harmoniz_ai importado")
    except ImportError as e:
        print_error(f"Falha ao importar harmoniz_ai: {e}")
        return False
    
    try:
        from src.engine.sommelier_agent import criar_sommelier_agent
        print_success("src.engine.sommelier_agent importado")
    except ImportError as e:
        print_error(f"Falha ao importar sommelier_agent: {e}")
        return False
    
    try:
        from src.engine.multi_llm_judge import ask_with_judge
        print_success("src.engine.multi_llm_judge importado")
    except ImportError as e:
        print_error(f"Falha ao importar multi_llm_judge: {e}")
        return False
    
    return True


def main():
    """Executa o inicializador."""
    print_header("🍷 HARMONIZ.AI — Inicializador Streamlit")
    
    # Checklist
    checks = [
        ("Ambiente virtual", check_venv),
        ("Arquivo .env", check_env_file),
        ("Secrets Streamlit", check_streamlit_secrets),
        ("ChromaDB", check_data_structure),
        ("Importações", check_imports),
    ]
    
    results = {}
    for name, check_func in checks:
        print(f"\n🔍 Verificando: {name}")
        try:
            results[name] = check_func()
        except Exception as e:
            print_error(f"Erro em {name}: {e}")
            results[name] = False
    
    # Sumário
    print_header("📊 SUMÁRIO")
    all_ok = True
    for name, passed in results.items():
        status = f"{Colors.OKGREEN}✓ OK{Colors.ENDC}" if passed else f"{Colors.WARNING}⚠ INCOMPLETO{Colors.ENDC}"
        print(f"{name:.<40} {status}")
        if not passed:
            all_ok = False
    
    if not all_ok:
        print_warning("\n⚠️ Alguns pré-requisitos não estão atendidos")
        print("   Resolva os problemas acima e tente novamente")
        print("   Ou execute: python src/engine/ingest.py (para gerar ChromaDB)")
        sys.exit(1)
    
    # Tudo OK — inicia Streamlit
    print_header("🚀 INICIANDO HARMONIZ.AI")
    print("\nStreamlit vai abrir em seu navegador em breve...")
    print("URL: http://localhost:8501\n")
    
    # Executa streamlit
    try:
        subprocess.run(
            [sys.executable, "-m", "streamlit", "run", "app.py"],
            check=False
        )
    except KeyboardInterrupt:
        print_warning("\nAplicação encerrada pelo usuário")
        sys.exit(0)
    except Exception as e:
        print_error(f"Erro ao iniciar Streamlit: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
