#!/usr/bin/env python
"""
Launcher para Harmoniz.AI API
============================

Script de conveniência que:
1. Valida .env
2. Instala dependências se necessário
3. Inicia o servidor FastAPI com recarregamento automático

Uso:
    python run_api.py          # Inicia em desenvolvimento (com reload)
    python run_api.py --prod   # Inicia em produção (sem reload)
"""

import os
import subprocess
import sys
from pathlib import Path

def check_env():
    """Valida variáveis críticas do .env"""
    from dotenv import load_dotenv
    
    load_dotenv()
    
    critical_keys = ["OPENAI_API_KEY", "VECTOR_DB_PATH"]
    missing = []
    
    for key in critical_keys:
        if not os.getenv(key):
            missing.append(key)
    
    if missing:
        print(f"⚠️  AVISO: Variáveis .env faltando: {', '.join(missing)}")
        print("   Configure seu .env antes de continuar.")
        return False
    
    return True


def check_venv():
    """Valida que estamos em um venv"""
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    
    if not in_venv:
        print("⚠️  AVISO: Não está em um venv ativo!")
        print("   Execute: venv\\Scripts\\activate (Windows)")
        print("            source venv/bin/activate (Unix)")
        return False
    
    return True


def main():
    """Inicia a API"""
    prod_mode = "--prod" in sys.argv
    
    # Validações
    if not check_venv():
        sys.exit(1)
    
    if not check_env():
        sys.exit(1)
    
    # Calcula working directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Constrói comando uvicorn
    host = "0.0.0.0"
    port = int(os.getenv("PORT", 8000))
    reload_arg = "" if prod_mode else "--reload"
    
    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "src.api.main:app",
        "--host", host,
        "--port", str(port),
        "--log-level", "info",
    ]
    
    if not prod_mode:
        cmd.append("--reload")
    
    print("\n" + "=" * 70)
    print("🍷 Harmoniz.AI API — Inicializando")
    print("=" * 70)
    print(f"\n📡 URL: http://localhost:{port}")
    print(f"📚 Swagger: http://localhost:{port}/docs")
    print(f"🏥 Health: http://localhost:{port}/health")
    print(f"\n🔧 Modo: {'PRODUÇÃO' if prod_mode else 'DESENVOLVIMENTO (com reload)'}")
    print("\n" + "=" * 70 + "\n")
    
    # Executa uvicorn
    subprocess.run(cmd)


if __name__ == "__main__":
    main()
