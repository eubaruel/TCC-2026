@echo off
rem = r"""
setlocal
set "TCC_PYTHON="
if exist "%~dp0backend\.venv-correcao\Scripts\python.exe" set "TCC_PYTHON=%~dp0backend\.venv-correcao\Scripts\python.exe"
if not defined TCC_PYTHON where python.exe >nul 2>&1 && if not defined TCC_PYTHON set "TCC_PYTHON=python.exe"
if not defined TCC_PYTHON where py.exe >nul 2>&1 && if not defined TCC_PYTHON set "TCC_PYTHON=py.exe"
if not defined TCC_PYTHON if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" set "TCC_PYTHON=%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
if not defined TCC_PYTHON (
  echo Python nao encontrado. Instale o Python 3 e tente novamente.
  pause
  exit /b 1
)
"%TCC_PYTHON%" -x "%~f0" %*
set "TCC_INICIAR_EXIT=%errorlevel%"
if not "%TCC_INICIAR_EXIT%"=="0" pause
exit /b %TCC_INICIAR_EXIT%
"""

# Arquivo unico: o Windows executa o cabecalho e o Python ignora sua primeira linha (-x).
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import time
from datetime import datetime
from urllib.error import HTTPError, URLError
from urllib.request import ProxyHandler, Request, build_opener
import webbrowser


RAIZ = Path(__file__).resolve().parent
BACKEND = RAIZ / "backend"
FRONTEND = RAIZ / "frontend"
LEITOR = BACKEND / "sistema-correcao"
HTTP_LOCAL = build_opener(ProxyHandler({}))


def python_venv(pasta):
    return pasta / "Scripts" / "python.exe"


def executar(comando, pasta):
    subprocess.run([str(parte) for parte in comando], cwd=pasta, check=True)


def preparar_python(pasta, requisitos, reinstalar=False):
    interpretador = python_venv(pasta)
    if not interpretador.is_file():
        print(f"Preparando ambiente {pasta.name}...", flush=True)
        executar([sys.executable, "-m", "venv", pasta], BACKEND)
    marca = pasta / ".tcc-requisitos.sha256"
    assinatura = hashlib.sha256(requisitos.read_bytes()).hexdigest()
    if reinstalar or not marca.is_file() or marca.read_text() != assinatura:
        print(f"Instalando dependencias de {pasta.name}...", flush=True)
        executar([interpretador, "-m", "pip", "install", "-r", requisitos], BACKEND)
        executar([interpretador, "-m", "pip", "check"], BACKEND)
        marca.write_text(assinatura)
    return interpretador


def preparar_frontend(reinstalar=False):
    marca = FRONTEND / "node_modules" / ".tcc-dependencias.sha256"
    cli = FRONTEND / "node_modules" / "@vue" / "cli-service" / "bin" / "vue-cli-service.js"
    assinatura = hashlib.sha256((FRONTEND / "package-lock.json").read_bytes()
                               + (FRONTEND / "package.json").read_bytes()).hexdigest()
    if reinstalar or not cli.is_file() or not marca.is_file() or marca.read_text() != assinatura:
        print("Instalando dependencias do frontend (npm ci)...", flush=True)
        executar([os.environ.get("COMSPEC", "cmd.exe"), "/d", "/c", "npm.cmd", "ci"], FRONTEND)
        marca.write_text(assinatura)
    return cli


def configuracao(interpretador):
    # A venv interpreta o .env com o mesmo python-dotenv usado pela API.
    # Somente a porta e indicadores de configuracao saem deste subprocesso.
    codigo = """
import json, os
from pathlib import Path
from dotenv import load_dotenv, dotenv_values
load_dotenv(Path.cwd() / '.env')
faltantes = [campo for campo in ('URI_BD', 'NOME_BD') if not os.getenv(campo, '').strip()]
frontend = Path.cwd().parent / 'frontend'
api_explicita = 'VUE_APP_API_BASE_URL' in os.environ or any(
    'VUE_APP_API_BASE_URL' in dotenv_values(frontend / nome)
    for nome in ('.env', '.env.local', '.env.development', '.env.development.local')
    if (frontend / nome).is_file()
)
print(json.dumps({'porta': os.getenv('PORTA') or '8080', 'faltantes': faltantes, 'api_explicita': api_explicita}))
"""
    resultado = subprocess.run([str(interpretador), "-X", "utf8", "-c", codigo], cwd=BACKEND,
                               capture_output=True, text=True, encoding="utf-8")
    if resultado.returncode:
        raise RuntimeError("Nao foi possivel carregar a configuracao. Execute INICIAR.cmd --reinstalar para preparar os ambientes.")
    dados = json.loads(resultado.stdout)
    if dados["faltantes"]:
        raise RuntimeError("Configure " + ", ".join(dados["faltantes"]) + " em backend/.env ou nas variaveis de ambiente.")
    try:
        porta = int(dados["porta"])
    except (TypeError, ValueError):
        raise RuntimeError("PORTA deve ser um numero entre 1 e 65535.") from None
    if not 1 <= porta <= 65535 or porta in (5000, 8081):
        raise RuntimeError("PORTA deve estar entre 1 e 65535 e ser diferente de 5000 e 8081.")
    dados["porta"] = porta
    return dados


def exigir_porta_livre(porta):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as teste:
        try:
            # No Windows, evita compartilhar uma porta que ja esteja sendo usada.
            teste.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
            teste.bind(("127.0.0.1", porta))
        except OSError:
            raise RuntimeError(f"A porta {porta} ja esta em uso ou indisponivel. Encerre o servico existente antes de iniciar novamente.") from None


def iniciar_servico(nome, comando, pasta, ambiente, logs):
    caminho_log = logs / f"{nome}.log"
    with caminho_log.open("wb") as saida:
        processo = subprocess.Popen([str(parte) for parte in comando], cwd=pasta, env=ambiente,
                                    stdin=subprocess.DEVNULL, stdout=saida, stderr=subprocess.STDOUT,
                                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW)
    print(f"Iniciando {nome}... Log: {caminho_log}", flush=True)
    return {"nome": nome, "processo": processo, "log": caminho_log}


def aguardar_servico(servico, url, leitor=False, limite=90):
    fim = time.monotonic() + limite
    while time.monotonic() < fim:
        if servico["processo"].poll() is not None:
            raise RuntimeError(f"{servico['nome']} encerrou durante a inicializacao. Consulte {servico['log']}")
        try:
            with HTTP_LOCAL.open(Request(url), timeout=2) as resposta:
                if resposta.status == 200 and (not leitor or json.load(resposta).get("status") == "ok"):
                    print(f"[OK] {servico['nome']} pronto.", flush=True)
                    return
        except HTTPError as erro:
            # A raiz da API responde 404; a porta so abre depois da conexao com o banco.
            if erro.code == 404 and servico["nome"] == "api":
                print("[OK] api pronta.", flush=True)
                return
        except (OSError, URLError, ValueError):
            pass
        time.sleep(0.5)
    raise RuntimeError(f"Tempo esgotado aguardando {servico['nome']}. Consulte {servico['log']}")


def encerrar_servicos(servicos):
    for servico in reversed(servicos):
        processo = servico["processo"]
        if processo.poll() is None:
            # Apenas processos criados nesta execucao e seus descendentes.
            subprocess.run(["taskkill.exe", "/PID", str(processo.pid), "/T", "/F"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                           creationflags=subprocess.CREATE_NO_WINDOW)
            try:
                processo.wait(timeout=10)
            except subprocess.TimeoutExpired:
                processo.kill()
    if servicos:
        print("Servicos desta execucao encerrados.", flush=True)


def main():
    parser = argparse.ArgumentParser(description="Inicia API, leitor de gabaritos e frontend do TCC.")
    parser.add_argument("--verificar", action="store_true", help="Confere configuracao e portas sem instalar ou iniciar servicos.")
    parser.add_argument("--reinstalar", action="store_true", help="Instala novamente as dependencias dos tres servicos.")
    parser.add_argument("--sem-navegador", action="store_true", help="Inicia os servicos sem abrir o navegador.")
    opcoes = parser.parse_args()
    servicos = []
    try:
        if os.name != "nt":
            raise RuntimeError("Este inicializador foi preparado para Windows.")
        if sys.version_info < (3, 10):
            raise RuntimeError("Use Python 3.10 ou superior; o guia desta maquina utiliza Python 3.13.")
        node = shutil.which("node.exe")
        if not node or not shutil.which("npm.cmd"):
            raise RuntimeError("Instale Node.js com npm e abra novamente o terminal.")
        for arquivo in (BACKEND / "app.py", BACKEND / "requirements.txt", LEITOR / "app.py",
                        LEITOR / "requirements.txt", FRONTEND / "package-lock.json", FRONTEND / "package.json"):
            if not arquivo.is_file():
                raise RuntimeError(f"Arquivo necessario nao encontrado: {arquivo}")
        print("TCC - inicializacao local", flush=True)
        api_python = python_venv(BACKEND / ".venv-correcao")
        leitor_python = python_venv(BACKEND / ".venv-leitor")
        if not opcoes.verificar:
            api_python = preparar_python(BACKEND / ".venv-correcao", BACKEND / "requirements.txt", opcoes.reinstalar)
            leitor_python = preparar_python(BACKEND / ".venv-leitor", LEITOR / "requirements.txt", opcoes.reinstalar)
            cli = preparar_frontend(opcoes.reinstalar)
        elif not api_python.is_file() or not leitor_python.is_file():
            raise RuntimeError("Execute INICIAR.cmd sem --verificar para criar os ambientes e instalar as dependencias.")
        dados = configuracao(api_python)
        for porta in (dados["porta"], 5000, 8081):
            exigir_porta_livre(porta)
        if opcoes.verificar:
            print("[OK] Python, Node.js, caminhos, configuracao do banco e portas conferidos.")
            print("Esta verificacao nao testa a conexao de rede com o MongoDB nem instala dependencias.")
            return 0
        logs = BACKEND / ".venv-correcao" / "logs-inicializacao" / datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        logs.mkdir(parents=True)
        ambiente = {**os.environ, "PYTHONUNBUFFERED": "1", "PYTHONUTF8": "1", "PORTA": str(dados["porta"])}
        leitor = iniciar_servico("leitor", [leitor_python, "-m", "flask", "--app", "app", "--no-debug", "run",
                                  "--host", "127.0.0.1", "--port", "5000", "--no-reload"], LEITOR, ambiente, logs)
        servicos.append(leitor)
        aguardar_servico(leitor, "http://127.0.0.1:5000/health", leitor=True)
        api = iniciar_servico("api", [api_python, "-u", "app.py"], BACKEND, ambiente, logs)
        servicos.append(api)
        aguardar_servico(api, f"http://127.0.0.1:{dados['porta']}/")
        if not dados["api_explicita"]:
            ambiente["VUE_APP_API_BASE_URL"] = f"http://localhost:{dados['porta']}/api/v1"
        frontend = iniciar_servico("frontend", [node, cli, "serve", "--host", "127.0.0.1", "--port", "8081"],
                                   FRONTEND, ambiente, logs)
        servicos.append(frontend)
        aguardar_servico(frontend, "http://127.0.0.1:8081/", limite=180)
        print("\nTudo pronto: http://localhost:8081\nMantenha esta janela aberta. Pressione Ctrl+C para encerrar tudo.", flush=True)
        if not opcoes.sem_navegador:
            webbrowser.open("http://localhost:8081")
        while True:
            for servico in servicos:
                if servico["processo"].poll() is not None:
                    raise RuntimeError(f"{servico['nome']} encerrou. Consulte {servico['log']}")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nEncerrando...", flush=True)
        return 0
    except (OSError, RuntimeError, subprocess.CalledProcessError) as erro:
        print(f"\n[ERRO] {erro}", file=sys.stderr, flush=True)
        return 1
    finally:
        encerrar_servicos(servicos)


if __name__ == "__main__":
    sys.exit(main())
