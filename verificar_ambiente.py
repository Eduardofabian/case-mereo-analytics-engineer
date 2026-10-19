"""
verificar_ambiente.py — Case Mereo (Grupo Aurora)
Checa se o ambiente tem o que falta pra rodar cada parte do projeto: o
pipeline SQL (etl/run_pipeline.py), o agente de IA (agente/) e o protótipo
de painel (painel/streamlit/prototipo_streamlit.py). Não instala nada sozinho (ODBC
driver é instalador do Windows, não pip; e instalar pacote sem perguntar é
ruim num ambiente que pode ser compartilhado) — só diz o que falta e o
comando exato pra resolver.

Uso:
    python verificar_ambiente.py

Sai com código 0 se o essencial pro pipeline SQL estiver ok, 1 se faltar
algo que bloqueia P1/P2/P3 (a entrega obrigatória, 30% da nota). Agente e
painel são checados, mas tratados como informativos — não derrubam o
código de saída, porque são opcionais dependendo do que o avaliador quer
rodar (ver requirements.txt, que tem os três blocos comentados).
"""
import importlib
import os
import sys
from pathlib import Path

PROJETO_ROOT = Path(__file__).resolve().parent
OK = "  [OK]"
FALTA = "  [FALTA]"
AVISO = "  [AVISO]"

bloqueante = False


def checa_python():
    print("== Python ==")
    v = sys.version_info
    if v >= (3, 9):
        print(f"{OK} Python {v.major}.{v.minor}.{v.micro}")
    else:
        print(f"{FALTA} Python {v.major}.{v.minor}.{v.micro} — use 3.9 ou mais novo")
        global bloqueante
        bloqueante = True


def checa_pacotes():
    print("\n== Pacotes Python — pipeline SQL (bloqueante) ==")
    faltando = []
    for pacote, modulo in [("pyodbc", "pyodbc"), ("pandas", "pandas"), ("numpy", "numpy")]:
        try:
            m = importlib.import_module(modulo)
            versao = getattr(m, "__version__", "?")
            print(f"{OK} {pacote} ({versao})")
        except ImportError:
            print(f"{FALTA} {pacote} — não instalado")
            faltando.append(pacote)
    if faltando:
        global bloqueante
        bloqueante = True
        print(f"\n    Resolve com: pip install {' '.join(faltando)}")
        print(f"    (ou: pip install -r requirements.txt)")


def checa_odbc_driver():
    print("\n== ODBC Driver 17 for SQL Server ==")
    try:
        import pyodbc
    except ImportError:
        print(f"{AVISO} não dá pra checar — pyodbc não está instalado (ver acima)")
        return
    drivers = pyodbc.drivers()
    alvo = "ODBC Driver 17 for SQL Server"
    if alvo in drivers:
        print(f"{OK} {alvo} encontrado")
    else:
        global bloqueante
        bloqueante = True
        print(f"{FALTA} {alvo} não encontrado")
        if drivers:
            print(f"    Drivers SQL Server instalados: {[d for d in drivers if 'SQL Server' in d]}")
        print("    Baixe em: https://learn.microsoft.com/sql/connect/odbc/download-odbc-driver-for-sql-server")


def checa_sql_server():
    print("\n== SQL Server (localhost) ==")
    try:
        import pyodbc
    except ImportError:
        print(f"{AVISO} não dá pra checar — pyodbc não está instalado (ver acima)")
        return
    conn_str = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=localhost;"
        "DATABASE=master;"
        "Trusted_Connection=yes;"
        "Connection Timeout=5;"
    )
    try:
        conn = pyodbc.connect(conn_str, autocommit=True, timeout=5)
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM sys.databases WHERE name = 'CaseMereo'")
        existe = cur.fetchone() is not None
        conn.close()
        print(f"{OK} conectou em localhost (autenticação do Windows)")
        print(f"{OK if existe else AVISO} banco CaseMereo {'já existe' if existe else 'ainda não existe (run_pipeline.py cria)'}")
    except Exception as e:
        global bloqueante
        bloqueante = True
        print(f"{FALTA} não conseguiu conectar em localhost: {e}")
        print("    Checa se o serviço do SQL Server está rodando (services.msc)")
        print("    e se o seu usuário do Windows tem acesso (autenticação integrada).")


def checa_dado_origem():
    print("\n== Dado de origem (material_original/) ==")
    alvo = PROJETO_ROOT / "material_original" / "dados" / "case_metas.db"
    if alvo.exists():
        print(f"{OK} {alvo.relative_to(PROJETO_ROOT)}")
    else:
        global bloqueante
        bloqueante = True
        print(f"{FALTA} {alvo.relative_to(PROJETO_ROOT)} não encontrado")
        print("    material_original/ não é versionado neste repo (ver .gitignore).")
        print("    Coloque os arquivos recebidos no case em material_original/dados/.")


def checa_agente():
    print("\n== Pacotes Python — agente de IA, agente/ (informativo) ==")
    faltando = []
    for pacote, modulo in [("pydantic-ai", "pydantic_ai"), ("duckdb", "duckdb")]:
        try:
            m = importlib.import_module(modulo)
            versao = getattr(m, "__version__", "?")
            print(f"{OK} {pacote} ({versao})")
        except ImportError:
            print(f"{AVISO} {pacote} — não instalado (só necessário pra rodar o agente)")
            faltando.append(pacote)
    if faltando:
        print(f"    Resolve com: pip install {' '.join(faltando)}")
    if os.environ.get("ANTHROPIC_API_KEY"):
        print(f"{OK} ANTHROPIC_API_KEY está definida")
    else:
        print(f"{AVISO} ANTHROPIC_API_KEY não está definida — necessária só pra rodar o agente")


def checa_painel():
    print("\n== Pacotes Python — painel, painel/streamlit/prototipo_streamlit.py (informativo) ==")
    try:
        m = importlib.import_module("streamlit")
        versao = getattr(m, "__version__", "?")
        print(f"{OK} streamlit ({versao})")
    except ImportError:
        print(f"{AVISO} streamlit — não instalado (só necessário pra rodar o protótipo Streamlit)")
        print("    Resolve com: pip install streamlit")


def main():
    checa_python()
    checa_pacotes()
    checa_odbc_driver()
    checa_sql_server()
    checa_dado_origem()
    checa_agente()
    checa_painel()

    print()
    if bloqueante:
        print("=== Falta item(ns) acima antes de rodar etl/run_pipeline.py. ===")
        sys.exit(1)
    else:
        print("=== Ambiente ok. Pode rodar: python etl/run_pipeline.py ===")
        sys.exit(0)


if __name__ == "__main__":
    main()
