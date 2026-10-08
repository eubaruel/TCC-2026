import unittest
from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import MagicMock

from flask import Flask

from api.controles.usuario_controle import Usuario_controle
from api.DAOs.usuario_dao import Usuario_dao
from api.middlewares.usuario_middleware import Usuario_middleware
from api.roteador.usuario_rotas import Usuario_rotas
from api.services.usuario_service import Usuario_service
from api.utils.resposta_erro_http import resposta_erro_http
from tests.fakes import FakeUsuarioDao


class SenhaDaoFake(FakeUsuarioDao):
    def alterar_senha(self, registro, senha_hash, deve_alterar_senha, senha_anterior):
        doc = self.documentos.get(registro)
        if not doc or not doc["ativo"] or doc["senha"] != senha_anterior:
            return False
        doc.update(senha=senha_hash, deve_alterar_senha=deve_alterar_senha)
        return True


class SenhaUsuarioTest(unittest.TestCase):
    def setUp(self):
        self.dao = SenhaDaoFake()
        self.service = Usuario_service(self.dao)
        self.professor = {"registro": 101, "nome": "Carlos Silva", "email": "carlos@example.com",
                          "senha": "Base123!", "role": "Professor"}
        self.service.criar(self.professor)
        self.service.criar({**self.professor, "registro": 200, "role": "Processo pedagógico"})
        app = Flask(__name__)
        app.config["TESTING"] = True
        app.register_blueprint(Usuario_rotas(Usuario_middleware(), Usuario_controle(self.service)).criar_rotas(),
                               url_prefix="/api/v1/usuarios")

        @app.errorhandler(resposta_erro_http)
        def erro(error):
            return {"mensagem": error.mensagem}, error.httpCode

        @app.errorhandler(ValueError)
        @app.errorhandler(TypeError)
        def invalido(error):
            return {"mensagem": str(error)}, 400

        self.http = app.test_client()

    def trocar(self, dados, registro=101):
        return self.http.patch(f"/api/v1/usuarios/{registro}/alterar-senha", json={"usuario": dados})

    def test_primeiro_login_troca_hash_e_preserva_cadastro(self):
        antes = deepcopy(self.dao.documentos[101])
        self.assertTrue(self.service.login({"registro": 101, "senha": "Base123!"})["usuario"]["deve_alterar_senha"])
        resposta = self.trocar({"senha_atual": "Base123!", "nova_senha": "Nova456!"})
        self.assertEqual(resposta.status_code, 200)
        self.assertFalse(resposta.json["data"]["usuario"]["deve_alterar_senha"])
        depois = self.dao.documentos[101]
        self.assertNotEqual(depois["senha"], antes["senha"])
        self.assertNotEqual(depois["senha"], "Nova456!")
        for campo in ("registro", "nome", "email", "role", "ativo"):
            self.assertEqual(depois[campo], antes[campo])
        with self.assertRaises(resposta_erro_http):
            self.service.login({"registro": 101, "senha": "Base123!"})
        login = self.service.login({"registro": 101, "senha": "Nova456!"})
        self.assertFalse(login["usuario"]["deve_alterar_senha"])
        self.assertNotIn("senha", login["usuario"])

    def test_redefinicao_exige_nova_troca(self):
        resposta = self.trocar({"nova_senha": "Temp789!", "solicitante": {"registro": 200, "senha": "Base123!"}})
        self.assertEqual(resposta.status_code, 200)
        self.assertTrue(resposta.json["data"]["usuario"]["deve_alterar_senha"])
        self.assertTrue(self.service.login({"registro": 101, "senha": "Temp789!"})["usuario"]["deve_alterar_senha"])
        self.assertEqual(self.trocar({"senha_atual": "Temp789!", "nova_senha": "Final789!"}).status_code, 200)

    def test_credenciais_incorretas_nao_alteram_banco(self):
        antes = deepcopy(self.dao.documentos)
        for dados in ({"senha_atual": "errada", "nova_senha": "Nova456!"},
                      {"nova_senha": "Nova456!", "solicitante": {"registro": 200, "senha": "errada"}}):
            self.assertEqual(self.trocar(dados).status_code, 401)
        self.assertEqual(self.dao.documentos, antes)

    def test_professor_nao_pode_redefinir_senha(self):
        self.assertEqual(self.trocar({"nova_senha": "Nova456!", "solicitante":
                                    {"registro": 101, "senha": "Base123!"}}).status_code, 403)

    def test_pedagogico_nao_redefine_outro_pedagogico(self):
        self.assertEqual(self.trocar({"nova_senha": "Nova456!", "solicitante":
                                    {"registro": 200, "senha": "Base123!"}}, registro=200).status_code, 403)

    def test_alvo_ausente_ou_inativo(self):
        dados = {"senha_atual": "Base123!", "nova_senha": "Nova456!"}
        self.assertEqual(self.trocar(dados, registro=999).status_code, 404)
        self.dao.documentos[101]["ativo"] = False
        self.assertEqual(self.trocar(dados).status_code, 404)

    def test_solicitante_inativo(self):
        self.dao.documentos[200]["ativo"] = False
        self.assertEqual(self.trocar({"nova_senha": "Nova456!", "solicitante":
                                    {"registro": 200, "senha": "Base123!"}}).status_code, 401)

    def test_corpos_invalidos_e_senha_igual(self):
        for dados in ({}, {"nova_senha": "Nova456!"},
                      {"nova_senha": "Nova456!", "senha_atual": "Base123!", "nome": "Outra Pessoa"},
                      {"nova_senha": "Nova456!", "senha_atual": "Base123!", "solicitante": {}},
                      {"nova_senha": "Base123!", "senha_atual": "Base123!"},
                      {"nova_senha": "curta", "senha_atual": "Base123!"},
                      {"nova_senha": "Nova456!", "solicitante": {"registro": True, "senha": "Base123!"}}):
            with self.subTest(dados=dados):
                self.assertEqual(self.trocar(dados).status_code, 400)
        self.assertEqual(self.http.patch("/api/v1/usuarios/101/alterar-senha", json=[]).status_code, 400)

    def test_conflito_concorrente(self):
        self.dao.alterar_senha = lambda *args: False
        self.assertEqual(self.trocar({"senha_atual": "Base123!", "nova_senha": "Nova456!"}).status_code, 409)

    def test_importacao_constroi_hash_e_indicador(self):
        doc = self.service._ler_linha({**self.professor, "registro": 300})
        self.assertTrue(doc["deve_alterar_senha"])
        self.assertTrue(doc["senha"].startswith("$2"))
        self.assertNotEqual(doc["senha"], "Base123!")

    def test_dao_atualiza_apenas_senha_e_indicador(self):
        colecao = MagicMock()
        colecao.update_one.return_value.matched_count = 1
        dao = Usuario_dao(SimpleNamespace(get_banco_de_dados=lambda: {"usuarios": colecao}))
        self.assertTrue(dao.alterar_senha(101, "hash-novo", False, "hash-antigo"))
        colecao.update_one.assert_called_once_with(
            {"registro": 101, "ativo": True, "senha": "hash-antigo"},
            {"$set": {"senha": "hash-novo", "deve_alterar_senha": False}}
        )

    def test_cadastro_real_marca_senha_temporaria(self):
        colecao = MagicMock()
        dao = Usuario_dao(SimpleNamespace(get_banco_de_dados=lambda: {"usuarios": colecao}))
        modelo = SimpleNamespace(nome="Carlos Silva", email="carlos@example.com", role="Professor",
                                 ativo=True, registro=101, senha="hash")
        dao.criar(modelo)
        self.assertTrue(colecao.insert_one.call_args.args[0]["deve_alterar_senha"])
