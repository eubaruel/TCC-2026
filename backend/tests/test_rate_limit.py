import os
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import MagicMock, patch

from flask import Flask
from api.middlewares.rate_limit import PADROES, configurar_rate_limit


def criar_app(**config):
    app = Flask(__name__)
    app.config.update(TESTING=True, RATELIMIT_STORAGE_URI="memory://",
                      **{chave: "1000 per minute" for chave in PADROES})
    app.config.update(config)

    @app.route("/api/v1/usuarios/login", methods=["POST"])
    def login():
        return {"sucesso": True}

    @app.route("/api/v1/provas/corrigir-provas", methods=["POST"])
    def corrigir():
        return {"sucesso": True}

    @app.route("/api/v1/alunos/excel", methods=["POST"])
    def importar():
        return {"sucesso": True}

    @app.route("/api/v1/questoes/", methods=["GET", "POST"])
    def questoes():
        return {"sucesso": True}

    @app.get("/api/v1/provas/<id_prova>")
    def prova(id_prova):
        return {"sucesso": True}

    @app.get("/fora-da-api")
    def arquivo():
        return "arquivo"

    limiter = configurar_rate_limit(app)
    return app, limiter


class RateLimitTest(unittest.TestCase):
    def test_limite_por_rota_429_json_headers_e_outro_ip_livre(self):
        app, _ = criar_app(RATE_LIMIT_ROUTE="2 per minute")
        http = app.test_client()
        self.assertEqual(http.get("/api/v1/questoes/").status_code, 200)
        self.assertEqual(http.post("/api/v1/questoes/").status_code, 200)
        bloqueada = http.get("/api/v1/questoes/")
        self.assertEqual(bloqueada.status_code, 429)
        self.assertFalse(bloqueada.json["sucesso"])
        self.assertEqual(bloqueada.json["erro"]["codigo"], 429)
        self.assertGreater(int(bloqueada.headers["Retry-After"]), 0)
        self.assertEqual(bloqueada.headers["X-RateLimit-Remaining"], "0")
        self.assertEqual(http.get("/api/v1/questoes/", environ_overrides={"REMOTE_ADDR": "192.0.2.2"}).status_code, 200)

    def test_teto_global_conta_rotas_diferentes(self):
        app, _ = criar_app(RATE_LIMIT_GLOBAL="2 per minute;10 per hour")
        http = app.test_client()
        self.assertEqual(http.get("/api/v1/questoes/").status_code, 200)
        self.assertEqual(http.get("/api/v1/provas/a").status_code, 200)
        self.assertEqual(http.post("/api/v1/alunos/excel").status_code, 429)

    def test_ids_diferentes_na_mesma_rota_nao_renovam_cota(self):
        app, _ = criar_app(RATE_LIMIT_ROUTE="1 per minute")
        http = app.test_client()
        self.assertEqual(http.get("/api/v1/provas/a").status_code, 200)
        self.assertEqual(http.get("/api/v1/provas/b").status_code, 429)

    def test_login_separa_registros_do_mesmo_ip_e_normaliza_zeros(self):
        app, _ = criar_app(RATE_LIMIT_LOGIN_REGISTRO="2 per minute")
        http = app.test_client()
        def entrar(registro):
            return http.post("/api/v1/usuarios/login", json={"usuario": {"registro": registro, "senha": "teste"}})
        self.assertEqual(entrar(1).status_code, 200)
        self.assertEqual(entrar("001").status_code, 200)
        self.assertEqual(entrar("1").status_code, 429)
        for registro in range(2, 102):
            self.assertEqual(entrar(registro).status_code, 200)
        self.assertEqual(http.get("/api/v1/questoes/").status_code, 200)

    def test_login_por_ip_impede_contornar_trocando_registro(self):
        app, _ = criar_app(RATE_LIMIT_LOGIN_IP="2 per minute")
        http = app.test_client()
        for registro, status in [(1, 200), (2, 200), (3, 429)]:
            self.assertEqual(http.post("/api/v1/usuarios/login", json={"usuario": {"registro": registro}}).status_code, status)

    def test_json_invalido_nao_derruba_a_protecao(self):
        app, _ = criar_app(RATE_LIMIT_LOGIN_REGISTRO="1 per minute")
        http = app.test_client()
        for corpo, status in [([], 200), ({"usuario": []}, 429)]:
            self.assertEqual(http.post("/api/v1/usuarios/login", json=corpo).status_code, status)

    def test_correcao_e_importacao_tem_cotas_proprias_sem_afetar_consultas(self):
        app, _ = criar_app(RATE_LIMIT_CORRECAO="2 per minute", RATE_LIMIT_IMPORTACAO="1 per minute")
        http = app.test_client()
        for status in (200, 200, 429):
            self.assertEqual(http.post("/api/v1/provas/corrigir-provas").status_code, status)
        self.assertEqual(http.post("/api/v1/alunos/excel").status_code, 200)
        self.assertEqual(http.post("/api/v1/alunos/excel").status_code, 429)
        self.assertEqual(http.get("/api/v1/questoes/").status_code, 200)

    def test_preflight_e_arquivos_nao_consumem_cotas(self):
        app, _ = criar_app(RATE_LIMIT_GLOBAL="1 per minute", RATE_LIMIT_ROUTE="1 per minute")
        http = app.test_client()
        for _ in range(5):
            self.assertEqual(http.options("/api/v1/questoes/").status_code, 200)
            self.assertEqual(http.get("/fora-da-api").status_code, 200)
        self.assertEqual(http.get("/api/v1/questoes/").status_code, 200)
        self.assertEqual(http.get("/api/v1/questoes/").status_code, 429)

    def test_x_forwarded_for_nao_contorna_limite_por_padrao(self):
        app, _ = criar_app(RATE_LIMIT_ROUTE="1 per minute")
        http = app.test_client()
        self.assertEqual(http.get("/api/v1/questoes/", headers={"X-Forwarded-For": "192.0.2.1"}).status_code, 200)
        self.assertEqual(http.get("/api/v1/questoes/", headers={"X-Forwarded-For": "192.0.2.2"}).status_code, 429)

    def test_proxy_confiavel_configurado_distingue_ips_reais(self):
        app, _ = criar_app(RATE_LIMIT_ROUTE="1 per minute", TRUSTED_PROXY_HOPS=1)
        http = app.test_client()
        for ip in ("192.0.2.1", "192.0.2.2"):
            self.assertEqual(http.get("/api/v1/questoes/", headers={"X-Forwarded-For": ip}).status_code, 200)

    def test_expiracao_da_janela_libera_nova_tentativa(self):
        app, _ = criar_app(RATE_LIMIT_ROUTE="1 per minute")
        http = app.test_client()
        agora = time.time()
        with patch("time.time", return_value=agora):
            self.assertEqual(http.get("/api/v1/questoes/").status_code, 200)
            self.assertEqual(http.get("/api/v1/questoes/").status_code, 429)
        with patch("time.time", return_value=agora + 61):
            self.assertEqual(http.get("/api/v1/questoes/").status_code, 200)

    def test_requisicoes_simultaneas_respeitam_contador_atomico(self):
        app, _ = criar_app(RATE_LIMIT_ROUTE="5 per minute")
        def requisitar(_):
            with app.test_client() as http:
                return http.get("/api/v1/questoes/").status_code
        with ThreadPoolExecutor(max_workers=12) as executor:
            codigos = list(executor.map(requisitar, range(20)))
        self.assertEqual(codigos.count(200), 5)
        self.assertEqual(codigos.count(429), 15)

    def test_configuracao_mongodb_usa_banco_do_projeto_e_colecoes_separadas(self):
        app = Flask(__name__)
        app.config.update(RATELIMIT_STORAGE_URI="mongodb://localhost:27017")
        cliente = MagicMock()
        with patch.dict(os.environ, {"NOME_BD": "escola_teste"}), patch(
                "limits.storage.mongodb.MongoDBStorage._init_mongo_client", return_value=cliente):
            limiter = configurar_rate_limit(app)
            self.assertIs(limiter.storage.storage, cliente)
        self.assertEqual(type(limiter.storage).__name__, "MongoDBStorage")
        opcoes = app.config["RATELIMIT_STORAGE_OPTIONS"]
        self.assertEqual(opcoes["database_name"], "escola_teste")
        self.assertEqual(opcoes["counter_collection_name"], "rate_limit_contadores")
        self.assertFalse(limiter._in_memory_fallback_enabled)

    def test_falha_no_armazenamento_nao_libera_requisicoes_sem_protecao(self):
        from limits.errors import StorageError
        app, limiter = criar_app()
        with patch.object(limiter.limiter, "hit", side_effect=StorageError(RuntimeError("detalhe interno"))):
            resposta = app.test_client().get("/api/v1/questoes/")
        self.assertEqual(resposta.status_code, 503)
        self.assertFalse(resposta.json["sucesso"])
        self.assertNotIn("detalhe interno", str(resposta.json))

    def test_servidor_preserva_resposta_429_e_expoe_headers_cors(self):
        from servidor import Servidor
        servidor = Servidor(porta=0)
        servidor._Servidor__error_middleware()
        app = servidor._Servidor__app
        app.config.update(RATELIMIT_STORAGE_URI="memory://", RATE_LIMIT_ROUTE="1 per minute")
        app.add_url_rule("/api/v1/teste", "teste", lambda: {"sucesso": True})
        configurar_rate_limit(app)
        http = app.test_client()
        http.get("/api/v1/teste")
        resposta = http.get("/api/v1/teste", headers={"Origin": "http://localhost:8081"})
        self.assertEqual(resposta.status_code, 429)
        self.assertEqual(resposta.json["erro"]["codigo"], 429)
        self.assertIn("Retry-After", resposta.headers["Access-Control-Expose-Headers"])

    def test_configuracao_invalida_e_rejeitada(self):
        for limite in ("invalido", "0 per minute", ""):
            with self.subTest(limite=limite), self.assertRaises(ValueError):
                criar_app(RATE_LIMIT_ROUTE=limite)


if __name__ == "__main__":
    unittest.main()
