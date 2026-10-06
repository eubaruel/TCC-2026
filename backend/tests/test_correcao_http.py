import unittest
from io import BytesIO
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import requests
from bson import ObjectId
from flask import Flask

from api.clientes.correcao_cliente import Correcao_cliente
from api.DAOs.prova_x_aluno_dao import Prova_x_aluno_dao
from api.DAOs.aluno_dao import Aluno_dao
from api.controles.prova_controle import Prova_controle
from api.roteador.prova_rotas import Prova_rotas
from api.utils.resposta_erro_http import resposta_erro_http


class ConsultaCorrecaoTest(unittest.TestCase):
    def test_busca_identificador_individual_sem_mudar_colecao(self):
        colecao = MagicMock()
        identificador = ObjectId()
        colecao.find_one.return_value = {"_id": identificador, "matricula_aluno": 123}
        banco = SimpleNamespace(get_banco_de_dados=lambda: {"provas_x_alunos": colecao})
        dao = Prova_x_aluno_dao(banco)
        self.assertEqual(dao.buscar_por_id(str(identificador))["_id"], str(identificador))
        colecao.find_one.assert_called_once_with({"_id": identificador})
        self.assertIsNone(dao.buscar_por_id("invalido"))
        self.assertEqual(colecao.find_one.call_count, 1)
        colecao.update_one.assert_not_called()

    def test_busca_nome_pela_matricula(self):
        colecao = MagicMock()
        banco = SimpleNamespace(get_banco_de_dados=lambda: {"alunos": colecao})
        dao = Aluno_dao(banco)
        dao.buscar_por_matricula(123)
        colecao.find_one.assert_called_once_with(
            {"matricula_aluno": 123}, {"_id": 0, "matricula_aluno": 1, "nome_aluno": 1}
        )


class ClienteCorrecaoTest(unittest.TestCase):
    def setUp(self):
        self.cliente = Correcao_cliente("http://leitor:5000/", timeout=12)
        self.sessao = MagicMock()
        self.patch = patch("api.clientes.correcao_cliente.requests.Session", return_value=self.sessao)
        self.criar_sessao = self.patch.start()
        self.addCleanup(self.patch.stop)
        self.addCleanup(self.cliente.fechar)
        self.imagem = {"arquivo": "cartao.png", "bytes": b"png", "content_type": "image/png"}

    def test_multipart_timeout_e_reuso_de_conexao(self):
        resposta = self.sessao.post.return_value.__enter__.return_value
        resposta.json.return_value = {"qrcode": "id", "respostas": {"1": "A"}}
        for _ in range(2):
            self.assertEqual(self.cliente.processar(self.imagem)["qrcode"], "id")
        self.sessao.post.assert_called_with(
            "http://leitor:5000/processar",
            files={"imagem": ("cartao.png", b"png", "image/png")}, timeout=(5, 12)
        )
        self.assertEqual(self.sessao.post.call_count, 2)
        self.criar_sessao.assert_called_once()

    def test_timeout_e_indisponibilidade(self):
        for erro, codigo in [(requests.Timeout(), 504), (requests.ConnectionError(), 502)]:
            self.sessao.post.side_effect = erro
            with self.assertRaises(resposta_erro_http) as contexto:
                self.cliente.processar(self.imagem)
            self.assertEqual(contexto.exception.httpCode, codigo)

    def test_json_invalido(self):
        self.sessao.post.return_value.__enter__.return_value.json.side_effect = ValueError()
        with self.assertRaises(resposta_erro_http) as contexto:
            self.cliente.processar(self.imagem)
        self.assertEqual(contexto.exception.httpCode, 502)


class RotaCorrecaoTest(unittest.TestCase):
    def setUp(self):
        self.service = SimpleNamespace(corrigir=MagicMock(return_value={"resultados": [], "erros": []}))
        controle = Prova_controle(None, self.service)
        middleware = SimpleNamespace(
            validar_criar_prova=lambda f: f, validar_id_prova=lambda f: f,
            validar_adicionar_questoes=lambda f: f
        )
        app = Flask(__name__)
        app.config.update(TESTING=True, MAX_CONTENT_LENGTH=50 * 1024 * 1024)
        app.register_blueprint(Prova_rotas(middleware, controle).criar_rotas(), url_prefix="/api/v1/provas")

        @app.errorhandler(resposta_erro_http)
        def erro(error):
            return {"mensagem": error.mensagem}, error.httpCode

        self.http = app.test_client()

    def test_varias_imagens_e_resposta(self):
        resposta = self.http.post("/api/v1/provas/corrigir-provas", data={
            "imagens": [(BytesIO(b"primeira"), "a.png"), (BytesIO(b"segunda"), "b.png")]
        })
        self.assertEqual(resposta.status_code, 200)
        imagens = self.service.corrigir.call_args.args[0]
        self.assertEqual([i["arquivo"] for i in imagens], ["a.png", "b.png"])
        self.assertEqual(imagens[1]["bytes"], b"segunda")
        self.assertTrue(resposta.json["sucesso"])

    def test_ausente_vazia_e_excesso_de_arquivos(self):
        for data in ({}, {"imagens": (BytesIO(b""), "vazia.png")},
                     {"imagens": [(BytesIO(b"x"), f"{i}.png") for i in range(51)]}):
            resposta = self.http.post("/api/v1/provas/corrigir-provas", data=data)
            self.assertEqual(resposta.status_code, 400)
        self.service.corrigir.assert_not_called()

    def test_imagem_acima_do_limite(self):
        resposta = self.http.post("/api/v1/provas/corrigir-provas", data={
            "imagens": (BytesIO(b"x" * (5 * 1024 * 1024 + 1)), "grande.png")
        })
        self.assertEqual(resposta.status_code, 413)
        self.service.corrigir.assert_not_called()
