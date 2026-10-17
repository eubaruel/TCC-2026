import unittest
import json
from io import BytesIO
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import requests
from bson import ObjectId
from flask import Flask

from api.clientes.correcao_cliente import Correcao_cliente
from api.DAOs.prova_x_aluno_dao import Prova_x_aluno_dao
from api.DAOs.aluno_dao import Aluno_dao
from api.DAOs.prova_dao import Prova_dao
from api.controles.prova_controle import Prova_controle
from api.services.correcao_service import Correcao_service
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
            {"matricula_aluno": 123}, {"_id": 0, "matricula_aluno": 1, "nome_aluno": 1, "turma": 1}
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

    def test_lote_com_base_invalida_retorna_erro_individual_e_preserva_resultado_valido(self):
        id_base, id_valida, id_orfa = (str(ObjectId()) for _ in range(3))
        registro = {"_id": id_valida, "id_prova": id_base, "matricula_aluno": 123,
                    "questoes": [{"posicao_alternativa_correta": 1}]}
        registros = {id_valida: registro, id_orfa: {**registro, "_id": id_orfa, "id_prova": str(ObjectId())}}
        cliente = SimpleNamespace(fechar=lambda: None, processar=lambda imagem: {
            "qrcode": id_orfa if imagem["arquivo"] == "orfa.png" else id_valida, "respostas": {"1": "A"}
        })
        correcoes = Correcao_service(
            cliente, SimpleNamespace(buscar_por_id=registros.get, salvar_correcao=lambda *_: True),
            SimpleNamespace(buscar_por_matricula=lambda _: {"nome_aluno": "Carlos Silva"}),
            SimpleNamespace(buscar_por_id=lambda id_: {"_id": id_base} if id_ == id_base else None)
        )
        self.addCleanup(correcoes.fechar)
        self.service.corrigir = correcoes.corrigir
        resposta = self.http.post("/api/v1/provas/corrigir-provas", data={
            "imagens": [(BytesIO(b"orfa"), "orfa.png"), (BytesIO(b"valida"), "valida.png")]
        })
        self.assertEqual(resposta.status_code, 200)
        dados = resposta.get_json()["data"]
        self.assertEqual([item["indice"] for item in dados["resultados"]], [1])
        self.assertEqual(dados["resultados"][0]["nota_prova"], 10)
        self.assertEqual(dados["erros"][0]["indice"], 0)
        self.assertEqual(dados["erros"][0]["codigo"], 404)
        self.assertEqual(dados["erros"][0]["mensagem"], "Prova-base não encontrada ou inativa")

    def test_ausente_vazia_e_excesso_de_arquivos(self):
        for data in ({}, {"imagens": (BytesIO(b""), "vazia.png")},
                     {"imagens": [(BytesIO(b"x"), f"{i}.png") for i in range(51)]}):
            resposta = self.http.post("/api/v1/provas/corrigir-provas", data=data)
            self.assertEqual(resposta.status_code, 400)
        self.service.corrigir.assert_not_called()

    def test_correcao_muda_status_da_base_impressa_sem_regenerar_versoes(self):
        id_base, id_aluno = ObjectId(), str(ObjectId())
        base = {"_id": id_base, "tipo": "Objetiva", "status": "Impressa", "ativo": True}
        colecao = MagicMock()
        colecao.find_one.side_effect = lambda filtro, projecao=None: dict(base) if filtro["_id"] == id_base else None

        def atualizar(filtro, alteracao):
            confere = all(base.get(campo) == valor for campo, valor in filtro.items() if not isinstance(valor, dict))
            if confere:
                base.update(alteracao["$set"])
            return SimpleNamespace(matched_count=int(confere))

        colecao.update_one.side_effect = atualizar
        registro = {"_id": id_aluno, "id_prova": str(id_base), "matricula_aluno": 123,
                    "questoes": [{"posicao_alternativa_correta": 1}]}
        versoes = SimpleNamespace(buscar_por_id=lambda id_: dict(registro) if id_ == id_aluno else None,
                                  salvar_correcao=lambda *_: True)
        correcoes = Correcao_service(
            SimpleNamespace(fechar=lambda: None, processar=lambda _: {"qrcode": id_aluno, "respostas": {"1": "A"}}),
            versoes, SimpleNamespace(buscar_por_matricula=lambda _: {"nome_aluno": "Carlos Silva"}),
            Prova_dao(SimpleNamespace(get_banco_de_dados=lambda: {"provas": colecao}))
        )
        self.addCleanup(correcoes.fechar)
        self.service.corrigir = correcoes.corrigir
        for _ in range(2):
            resposta = self.http.post("/api/v1/provas/corrigir-provas", data={"imagens": (BytesIO(b"cartao"), "cartao.png")})
            self.assertEqual(resposta.status_code, 200)
            self.assertEqual(resposta.json["data"]["erros"], [])
            self.assertEqual(resposta.json["data"]["resultados"][0]["nota_prova"], 10)
            self.assertEqual(base["status"], "Corrigida")
        colecao.update_one.assert_called_once()
        self.assertEqual(registro["questoes"], [{"posicao_alternativa_correta": 1}])

    def test_imagem_acima_do_limite(self):
        resposta = self.http.post("/api/v1/provas/corrigir-provas", data={
            "imagens": (BytesIO(b"x" * (5 * 1024 * 1024 + 1)), "grande.png")
        })
        self.assertEqual(resposta.status_code, 413)
        self.service.corrigir.assert_not_called()

    def test_ids_opcionais_correspondem_a_ordem_das_imagens(self):
        id_ = str(ObjectId())
        resposta = self.http.post("/api/v1/provas/corrigir-provas", data={
            "imagens": [(BytesIO(b"a"), "a.png"), (BytesIO(b"b"), "b.png")],
            "ids_provas_alunos": json.dumps([id_, None]),
        })
        self.assertEqual(resposta.status_code, 200)
        imagens = self.service.corrigir.call_args.args[0]
        self.assertEqual([i["id_prova_aluno"] for i in imagens], [id_, None])

    def test_ids_invalidos_ou_quantidade_incompativel_nao_corrigem_o_lote(self):
        for valor in ("nao-json", "null", "{}", "[]", '[123]', '["invalido"]', '[null, null]'):
            with self.subTest(valor=valor):
                resposta = self.http.post("/api/v1/provas/corrigir-provas", data={
                    "imagens": (BytesIO(b"x"), "a.png"), "ids_provas_alunos": valor,
                })
                self.assertEqual(resposta.status_code, 400)
        self.service.corrigir.assert_not_called()
