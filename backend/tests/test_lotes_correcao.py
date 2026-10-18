import unittest
from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import MagicMock

from bson import ObjectId
from flask import Flask

from api.DAOs.lote_correcao_dao import Lote_correcao_dao
from api.DAOs.prova_x_aluno_dao import Prova_x_aluno_dao
from api.services.correcao_service import Correcao_service
from api.controles.prova_controle import Prova_controle
from api.roteador.prova_rotas import Prova_rotas
from api.utils.resposta_erro_http import resposta_erro_http


class LoteCorrecaoTest(unittest.TestCase):
    def setUp(self):
        self.ids = [str(ObjectId()) for _ in range(2)]
        self.registros = [{"_id": id_, "correcao": {
            "id_correcao": f"correcao-{indice}", "id_prova_aluno": id_, "id_prova": str(ObjectId()),
            "matricula": indice + 1, "nome": nome, "turma": "1ºI - INFORMÁTICA", "nota_prova": nota,
        }} for indice, (id_, nome, nota) in enumerate(zip(self.ids, ["Zélia", "Ana"], [0, 6.67]))]
        self.versoes = SimpleNamespace(buscar_por_ids=MagicMock(return_value=self.registros))
        self.lotes = SimpleNamespace(criar=MagicMock(side_effect=lambda doc: {"_id": "lote", **deepcopy(doc)}),
                                     buscar_por_id=MagicMock(return_value=None))
        self.service = Correcao_service(SimpleNamespace(fechar=lambda: None), self.versoes, None, None, lote_dao=self.lotes)
        self.addCleanup(self.service.fechar)
        self.entradas = [{"arquivo": f"pagina-{i}.png", "id_prova_aluno": id_, "id_correcao": f"correcao-{i}"} for i, id_ in enumerate(self.ids)]

    def test_ordem_e_notas_sao_copiadas_do_banco_e_congeladas(self):
        lote = self.service.criar_lote(self.entradas)
        self.assertTrue(lote["imprimivel"])
        self.assertEqual([item["nome"] for item in lote["itens"]], ["Zélia", "Ana"])
        self.assertEqual([item["nota_prova"] for item in lote["itens"]], [0, 6.67])
        self.assertEqual([item["posicao"] for item in lote["itens"]], [1, 2])
        self.versoes.buscar_por_ids.assert_called_once_with(self.ids)
        self.registros[0]["correcao"]["nota_prova"] = 10
        self.assertEqual(lote["itens"][0]["nota_prova"], 0)

    def test_falha_nao_e_removida_e_bloqueia_impressao(self):
        lote = self.service.criar_lote([self.entradas[0], {"arquivo": "sem-qr.png", "erro": True}, self.entradas[1]])
        self.assertFalse(lote["imprimivel"])
        self.assertEqual([item["posicao"] for item in lote["itens"]], [1, 2, 3])
        self.assertFalse(lote["itens"][1]["corrigida"])
        self.assertNotIn("nota_prova", lote["itens"][1])

    def test_recusa_notas_do_frontend_duplicatas_e_correcao_antiga(self):
        invalidas = [[], None, [None], [{**self.entradas[0], "nota_prova": 10}],
                     [self.entradas[0], self.entradas[0]], [{**self.entradas[0], "id_prova_aluno": "invalido"}],
                     [{"arquivo": "erro.png", "erro": True, "nota_prova": 0}]]
        for entradas in invalidas:
            with self.subTest(entradas=entradas), self.assertRaises(resposta_erro_http):
                self.service.criar_lote(entradas)
        with self.assertRaises(resposta_erro_http) as contexto:
            self.service.criar_lote([{**self.entradas[0], "id_correcao": "desatualizada"}])
        self.assertEqual(contexto.exception.httpCode, 409)
        self.lotes.criar.assert_not_called()

    def test_cadastro_incompleto_impede_impressao_e_busca_inexistente_retorna_404(self):
        self.registros[0]["correcao"]["turma"] = ""
        with self.assertRaises(resposta_erro_http):
            self.service.criar_lote(self.entradas)
        with self.assertRaises(resposta_erro_http) as contexto:
            self.service.buscar_lote("inexistente")
        self.assertEqual(contexto.exception.httpCode, 404)

    def test_nota_invalida_no_banco_nao_gera_lote_imprimivel(self):
        for nota in (None, True, "10", -1, 11, float("nan")):
            self.registros[0]["correcao"]["nota_prova"] = nota
            with self.assertRaises(resposta_erro_http):
                self.service.criar_lote(self.entradas)

    def test_rotas_salvam_e_reabrem_o_lote_ordenado(self):
        app = Flask(__name__)
        middleware = SimpleNamespace(validar_criar_prova=lambda f: f, validar_id_prova=lambda f: f, validar_adicionar_questoes=lambda f: f)
        app.register_blueprint(Prova_rotas(middleware, Prova_controle(None, self.service)).criar_rotas(), url_prefix="/provas")

        @app.errorhandler(resposta_erro_http)
        def erro(error):
            return {"mensagem": error.mensagem}, error.httpCode

        http = app.test_client()
        for corpo in ({}, {"entradas": [], "nota": 10}):
            self.assertEqual(http.post("/provas/lotes-correcao", json=corpo).status_code, 400)
        resposta = http.post("/provas/lotes-correcao", json={"entradas": self.entradas})
        self.assertEqual(resposta.status_code, 201)
        lote = resposta.json["data"]["lote"]
        self.lotes.buscar_por_id.return_value = lote
        self.assertEqual(http.get("/provas/lotes-correcao/lote").json["data"]["lote"], lote)


class PersistenciaNotasTest(unittest.TestCase):
    def test_dao_grava_resultado_sem_alterar_questoes_e_busca_em_lote(self):
        colecao = MagicMock()
        colecao.update_one.return_value.matched_count = 1
        registro = {"_id": str(ObjectId()), "id_prova": str(ObjectId()), "questoes": [{"id_questao": "q", "posicao_alternativa_correta": 2}]}
        dao = Prova_x_aluno_dao(SimpleNamespace(get_banco_de_dados=lambda: {"provas_x_alunos": colecao}))
        resultado = {"nota_prova": 0, "id_correcao": "teste"}
        self.assertTrue(dao.salvar_correcao(registro, resultado))
        filtro, alteracao = colecao.update_one.call_args.args
        self.assertEqual(filtro["questoes"], registro["questoes"])
        self.assertEqual(alteracao, {"$set": {"correcao": resultado}})
        colecao.find.return_value = [{"_id": ObjectId(registro["_id"]), "correcao": resultado}]
        self.assertEqual(dao.buscar_por_ids([registro["_id"]])[0]["_id"], registro["_id"])

    def test_dao_lote_salva_e_busca_sem_criar_nova_correcao(self):
        colecao = MagicMock()
        id_ = ObjectId()
        colecao.insert_one.return_value.inserted_id = id_
        dao = Lote_correcao_dao(SimpleNamespace(get_banco_de_dados=lambda: {"lotes_correcao": colecao}))
        self.assertEqual(dao.criar({"itens": []})["_id"], str(id_))
        colecao.find_one.return_value = {"_id": id_, "itens": []}
        self.assertEqual(dao.buscar_por_id(str(id_))["_id"], str(id_))
        self.assertIsNone(dao.buscar_por_id("invalido"))
        colecao.update_one.assert_not_called()


if __name__ == "__main__":
    unittest.main()
