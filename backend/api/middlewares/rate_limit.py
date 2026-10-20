"""Limites da API, com cotas generosas para redes escolares com IP compartilhado."""
import hashlib
import math
import os
import re
import time

from flask import jsonify, request
from flask_limiter import Limiter
from limits.errors import StorageError
from limits.util import parse_many
from werkzeug.middleware.proxy_fix import ProxyFix


PADROES = {
    "RATE_LIMIT_GLOBAL": "1000 per minute;10000 per hour",
    "RATE_LIMIT_ROUTE": "600 per minute",
    "RATE_LIMIT_LOGIN_IP": "300 per minute",
    "RATE_LIMIT_LOGIN_REGISTRO": "10 per minute",
    "RATE_LIMIT_CORRECAO": "120 per minute",
    "RATE_LIMIT_IMPORTACAO": "30 per minute",
}


def chave_ip():
    # X-Forwarded-For só é considerado pelo ProxyFix quando explicitamente configurado.
    return request.remote_addr or "ip-desconhecido"


def chave_login():
    corpo = request.get_json(silent=True)
    usuario = corpo.get("usuario") if isinstance(corpo, dict) else None
    registro = usuario.get("registro") if isinstance(usuario, dict) else None
    texto = str(registro).strip() if type(registro) in (int, str) else ""
    normalizado = str(int(texto)) if re.fullmatch(r"[0-9]{1,10}", texto) else "invalido"
    # O registro e, principalmente, a senha não são gravados nos contadores.
    return hashlib.sha256(f"{chave_ip()}|{normalizado}".encode()).hexdigest()


def ignorar_requisicao():
    return request.method == "OPTIONS" or not request.path.startswith("/api/v1/")


def configurar_rate_limit(app):
    """Chamar após registrar os blueprints, antes da primeira requisição."""
    for nome, padrao in PADROES.items():
        app.config.setdefault(nome, os.getenv(nome) or padrao)
        try:
            limites = parse_many(app.config[nome])
            if not limites or any(limite.amount <= 0 for limite in limites):
                raise ValueError()
        except (TypeError, ValueError):
            raise ValueError(f"Configuracao invalida: {nome}") from None

    app.config.setdefault("RATELIMIT_STORAGE_URI", os.getenv("RATELIMIT_STORAGE_URI") or os.getenv("URI_BD"))
    armazenamento = app.config["RATELIMIT_STORAGE_URI"]
    if not armazenamento:
        raise ValueError("Configure URI_BD ou RATELIMIT_STORAGE_URI para os contadores de rate limit")
    opcoes = dict(app.config.get("RATELIMIT_STORAGE_OPTIONS") or {})
    if armazenamento.startswith(("mongodb://", "mongodb+srv://")):
        banco = os.getenv("NOME_BD")
        if not banco:
            raise ValueError("Configure NOME_BD para os contadores de rate limit")
        opcoes = {
            "database_name": banco,
            "counter_collection_name": "rate_limit_contadores",
            "window_collection_name": "rate_limit_janelas",
            "serverSelectionTimeoutMS": 5000,
            "connectTimeoutMS": 5000,
            **opcoes,
        }
    opcoes["wrap_exceptions"] = True
    app.config["RATELIMIT_STORAGE_OPTIONS"] = opcoes

    try:
        proxies = int(app.config.get("TRUSTED_PROXY_HOPS", os.getenv("TRUSTED_PROXY_HOPS") or "0"))
        if proxies < 0:
            raise ValueError()
    except (TypeError, ValueError):
        raise ValueError("TRUSTED_PROXY_HOPS deve ser um inteiro maior ou igual a zero") from None
    if proxies:
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=proxies, x_proto=0, x_host=0, x_port=0, x_prefix=0)

    limiter = Limiter(
        key_func=chave_ip,
        application_limits=app.config["RATE_LIMIT_GLOBAL"].split(";"),
        default_limits=app.config["RATE_LIMIT_ROUTE"].split(";"),
        headers_enabled=True,
        strategy="fixed-window",
        key_prefix="tcc-api-v1",
        retry_after="delta-seconds",
        swallow_errors=False,
        in_memory_fallback_enabled=False,
    )
    limiter.request_filter(ignorar_requisicao)
    limiter.init_app(app)

    configurados = set()
    for regra in app.url_map.iter_rules():
        if regra.endpoint in configurados or not regra.rule.startswith("/api/v1/"):
            continue
        configurados.add(regra.endpoint)
        funcao = app.view_functions[regra.endpoint]
        if regra.rule == "/api/v1/usuarios/login":
            funcao = limiter.limit(app.config["RATE_LIMIT_LOGIN_IP"])(funcao)
            funcao = limiter.limit(app.config["RATE_LIMIT_LOGIN_REGISTRO"],
                                   key_func=chave_login, override_defaults=False)(funcao)
        elif regra.rule == "/api/v1/provas/corrigir-provas":
            funcao = limiter.limit(app.config["RATE_LIMIT_CORRECAO"])(funcao)
        elif regra.rule.endswith("/excel"):
            funcao = limiter.limit(app.config["RATE_LIMIT_IMPORTACAO"])(funcao)
        app.view_functions[regra.endpoint] = funcao

    @app.errorhandler(429)
    def limite_excedido(_erro):
        atual = limiter.current_limit
        espera = max(1, math.ceil(atual.reset_at - time.time())) if atual else 60
        resposta = jsonify({
            "sucesso": False,
            "mensagem": f"Muitas requisições. Aguarde {espera} segundos e tente novamente.",
            "erro": {"codigo": 429, "tentar_novamente_em": espera},
        })
        resposta.status_code = 429
        resposta.headers["Retry-After"] = str(espera)
        return resposta

    @app.errorhandler(StorageError)
    def armazenamento_indisponivel(_erro):
        # Não desativa a proteção silenciosamente se o armazenamento falhar.
        resposta = jsonify({"sucesso": False, "mensagem": "Serviço temporariamente indisponível. Tente novamente em instantes.",
                            "erro": {"codigo": 503}})
        resposta.status_code = 503
        resposta.headers["Retry-After"] = "5"
        return resposta

    return limiter
