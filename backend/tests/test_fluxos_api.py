import unittest
from pathlib import Path

import pandas as pd
from flask import Flask

from api.controles.aluno_controle import Aluno_controle
from api.controles.disciplina_controle import Disciplina_controle
from api.controles.prova_controle import Prova_controle
from api.controles.questao_controle import Questao_controle
from api.controles.usuario_controle import Usuario_controle
from api.middlewares.aluno_middleware import Aluno_middleware
from api.middlewares.disciplina_middleware import Disciplina_middleware
from api.middlewares.prova_middleware import Prova_middleware
from api.middlewares.questao_middleware import Questao_middleware
from api.middlewares.usuario_middleware import Usuario_middleware
from api.roteador.aluno_rotas import Aluno_rotas
from api.roteador.disciplina_rotas import Disciplina_rotas
from api.roteador.prova_rotas import Prova_rotas
from api.roteador.questao_rotas import Questao_rotas
from api.roteador.usuario_rotas import Usuario_rotas
from api.services.aluno_service import Aluno_service
from api.services.disciplina_service import Disciplina_service
from api.services.prova_service import Prova_service
from api.services.questao_service import Questao_service
from api.services.usuario_service import Usuario_service
from api.utils.conversores import Conversores
from api.utils.resposta_erro_http import resposta_erro_http
from tests.fakes import FakeAlunoDao, FakeDisciplinaDao, FakeProvaDao, FakeQuestaoDao, FakeUsuarioDao


def criar_app(blueprint, prefixo):
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.register_blueprint(blueprint, url_prefix=prefixo)

    @app.errorhandler(resposta_erro_http)
    def tratar_erro(error):
        return {"sucesso": False, "mensagem": error.mensagem, "erro": error.erro}, error.httpCode

    @app.errorhandler(ValueError)
    @app.errorhandler(TypeError)
    def tratar_validacao(error):
        return {"sucesso": False, "mensagem": "Dados inválidos", "erro": {"detalhes": str(error)}}, 400

    return app


def payload_questao(numero):
    return {"questao": {
        "professor": {"nome": "Carlos Silva"},
        "assunto": "Álgebra",
        "disciplina": ["mat", "matemática"],
        "tipo_questao": "Objetiva",
        "dificuldade": "Médio",
        "autor": "Carlos Silva",
        "enunciado": f"Quanto vale a expressão número {numero}?",
        "alternativas": ["A", "B", "C", "D", "E"],
        "alternativa_correta": "A",
    }}


class FluxoAlunoTest(unittest.TestCase):
    def setUp(self):
        self.dao = FakeAlunoDao()
        service = Aluno_service(self.dao)
        controle = Aluno_controle(service)
        rotas = Aluno_rotas(Aluno_middleware(), controle)
        self.client = criar_app(rotas.criar_rotas(), "/api/v1/alunos").test_client()

    def test_crud_preserva_matricula_e_oculta_email_na_listagem(self):
        payload = {"aluno": {
            "matricula_aluno": 12345678, "nome_aluno": "Carlos Silva",
            "turma": "Turma 2026 A", "serie": 3, "situacao": "Pre-Mat",
            "email_aluno": "carlos@example.com",
        }}
        resposta = self.client.post("/api/v1/alunos/", json=payload)
        self.assertEqual(resposta.status_code, 201)
        self.assertEqual(self.dao.documentos[12345678]["matricula_aluno"], 12345678)
        aluno = self.client.get("/api/v1/alunos/?ativo=true").get_json()["data"]["alunos"][0]
        self.assertNotIn("email_aluno", aluno)
        resposta = self.client.delete("/api/v1/alunos/12345678")
        self.assertEqual(resposta.status_code, 200)
        self.assertFalse(self.dao.documentos[12345678]["ativo"])

    def test_filtro_false_e_parametro_desconhecido(self):
        controle = Aluno_controle(Aluno_service(self.dao))
        filtro, erro = controle._formatar_pesquisa({"ativo": Conversores.booleano}, {"ativo"}, [("ativo", "false")])
        self.assertIsNone(erro)
        self.assertIs(filtro["ativo"], False)
        filtro, erro = controle._formatar_pesquisa({}, {"ativo"}, [("senha", "x")])
        self.assertIsNone(filtro)
        self.assertIn("não permitido", erro)

    def test_importacao_valida_tudo_antes_do_upsert(self):
        service = Aluno_service(self.dao)
        df = pd.DataFrame([{"matrícula": 12345678, "nome": "Carlos Silva", "turma": "Turma 2026 A", "série": 3, "situação": "Pre-Mat", "email": "carlos@example.com"}])
        resultado = service.importar_excel(df)
        self.assertEqual(resultado["processados"], 1)
        invalido = df.rename(columns={"matrícula": "ALUNO"})
        with self.assertRaises(resposta_erro_http):
            service.importar_excel(invalido)
        self.assertEqual(len(self.dao.importacoes), 1)

    def test_planilha_modelo_e_compativel_com_o_importador(self):
        caminho = Path(__file__).parents[1] / "api" / "docs" / "jsons" / "alunos" / "planilha_modelo.xlsx"
        df = pd.read_excel(caminho)
        resultado = Aluno_service(self.dao).importar_excel(df)
        self.assertEqual(resultado["processados"], 1)
        self.assertIn(50280715, self.dao.documentos)


class FluxoUsuarioTest(unittest.TestCase):
    def test_cadastro_login_listagem_e_atualizacao(self):
        dao = FakeUsuarioDao()
        service = Usuario_service(dao)
        controle = Usuario_controle(service)
        client = criar_app(Usuario_rotas(Usuario_middleware(), controle).criar_rotas(), "/api/v1/usuarios").test_client()
        payload = {"usuario": {"registro": 101, "nome": "Carlos Silva", "email": "carlos@example.com", "senha": "Senha@123", "role": "Professor"}}
        self.assertEqual(client.post("/api/v1/usuarios/", json=payload).status_code, 201)
        login = client.post("/api/v1/usuarios/login", json={"usuario": {"registro": 101, "senha": "Senha@123"}})
        self.assertEqual(login.status_code, 200)
        listagem = client.get("/api/v1/usuarios/").get_json()["data"]["usuarios"]
        self.assertNotIn("senha", listagem[0])
        alterado = {"usuario": {"nome": "Carlos Souza", "email": "souza@example.com", "role": "Professor", "ativo": False}}
        self.assertEqual(client.put("/api/v1/usuarios/101", json=alterado).status_code, 200)
        self.assertFalse(dao.documentos[101]["ativo"])


class FluxoDisciplinaTest(unittest.TestCase):
    def test_listagem_troca_matriculas_por_quantidade(self):
        dao = FakeDisciplinaDao()
        service = Disciplina_service(dao)
        controle = Disciplina_controle(service)
        client = criar_app(Disciplina_rotas(Disciplina_middleware(), controle).criar_rotas(), "/api/v1/disciplinas").test_client()
        payload = {"disciplina": {"codigo_disciplina": "MAT", "nome_disciplina": "Matemática", "professor": {"registro": 101, "nome": "Carlos Silva"}, "turma": "Turma 2026 A", "alunos": [12345678, 87654321]}}
        self.assertEqual(client.post("/api/v1/disciplinas/", json=payload).status_code, 201)
        disciplina = client.get("/api/v1/disciplinas/").get_json()["data"]["disciplinas"][0]
        self.assertNotIn("alunos", disciplina)
        self.assertEqual(disciplina["quantidade_alunos"], 2)
        filtro, erro = controle._formatar_pesquisa({"registro": int}, {"registro", "nome"}, [("registro", "101"), ("nome", "Carlos Silva")])
        self.assertIsNone(erro)
        self.assertEqual(filtro["professor.registro"], 101)
        self.assertEqual(filtro["professor.nome"], "Carlos Silva")


class FluxoQuestaoEProvaTest(unittest.TestCase):
    def setUp(self):
        self.questao_dao = FakeQuestaoDao()
        service = Questao_service(self.questao_dao)
        controle = Questao_controle(service)
        self.questao_client = criar_app(Questao_rotas(Questao_middleware(), controle).criar_rotas(), "/api/v1/questoes").test_client()

    def test_listagem_de_questoes_retorna_gabarito(self):
        self.assertEqual(self.questao_client.post("/api/v1/questoes/", json=payload_questao(1)).status_code, 201)
        questao = self.questao_client.get("/api/v1/questoes/").get_json()["data"]["questoes"][0]
        self.assertIn("alternativas", questao)
        self.assertEqual(questao["alternativa_correta"], "A")

    def test_middleware_rejeita_campos_do_tipo_errado(self):
        payload = payload_questao(2)
        payload["questao"].pop("alternativas")
        payload["questao"].pop("alternativa_correta")
        payload["questao"]["numero_linhas"] = 5
        self.assertEqual(self.questao_client.post("/api/v1/questoes/", json=payload).status_code, 400)

    def test_prova_armazena_questoes_completas_sem_ids(self):
        for numero in range(1, 6):
            self.questao_client.post("/api/v1/questoes/", json=payload_questao(numero))

        questoes = self.questao_client.get("/api/v1/questoes/").get_json()["data"]["questoes"]
        prova_dao = FakeProvaDao()
        service = Prova_service(prova_dao)
        controle = Prova_controle(service)
        client = criar_app(Prova_rotas(Prova_middleware(), controle).criar_rotas(), "/api/v1/provas").test_client()
        payload = {"prova": {"id_turma": "Turma 2026 A", "professor": {"nome": "Carlos Silva"}, "disciplina": {"codigo_disciplina": "MAT", "nome_disciplina": "Matemática"}, "status": "Não Corrigida", "tipo": "Objetiva", "serie": 3, "bimestre": "1° bimestre", "data_de_aplicacao": "2026-08-20", "questoes": questoes}}
        criacao = client.post("/api/v1/provas/", json=payload)
        self.assertEqual(criacao.status_code, 201)
        persistida = next(iter(prova_dao.documentos.values()))
        self.assertEqual(len(persistida["questoes"]), 5)
        self.assertEqual(persistida["questoes"][0]["alternativa_correta"], "A")
        self.assertNotIn("_id", persistida["questoes"][0])
        self.assertIn("enunciado", persistida["questoes"][0])

        retornada = client.get("/api/v1/provas/").get_json()["data"]["provas"][0]
        self.assertEqual(retornada["questoes"][0]["alternativa_correta"], "A")
        self.assertNotIn("_id", retornada["questoes"][0])

        payload["prova"]["questoes"] = [questoes[0]] * 5
        self.assertEqual(client.post("/api/v1/provas/", json=payload).status_code, 400)

        payload["prova"]["questoes"] = ["id-invalido"] * 5
        self.assertEqual(client.post("/api/v1/provas/", json=payload).status_code, 400)


if __name__ == "__main__":
    unittest.main()
