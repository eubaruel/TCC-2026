import unittest
from copy import deepcopy
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
from api.services.prova_x_aluno_service import Prova_x_aluno_service
from api.services.questao_service import Questao_service
from api.services.usuario_service import Usuario_service
from api.utils.conversores import Conversores
from api.utils.resposta_erro_http import resposta_erro_http
from tests.fakes import FakeAlunoDao, FakeDisciplinaDao, FakeProvaDao, FakeProvaXAlunoDao, FakeQuestaoDao, FakeUsuarioDao


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
        self.aluno_dao = FakeAlunoDao()
        self.prova_x_aluno_dao = FakeProvaXAlunoDao()
        self.prova_x_aluno_service = Prova_x_aluno_service(
            self.aluno_dao,
            self.prova_x_aluno_dao,
            self.questao_dao
        )
        service = Questao_service(self.questao_dao)
        controle = Questao_controle(service)
        self.questao_client = criar_app(Questao_rotas(Questao_middleware(), controle).criar_rotas(), "/api/v1/questoes").test_client()

    def test_listagem_de_questoes_retorna_gabarito(self):
        resposta_criacao = self.questao_client.post(
            "/api/v1/questoes/",
            json=payload_questao(1)
        )
        self.assertEqual(resposta_criacao.status_code, 201)

        questao_criada = resposta_criacao.get_json()["data"]["questao"]
        ids = [alternativa["id"] for alternativa in questao_criada["alternativas"]]
        self.assertEqual(len(ids), 5)
        self.assertEqual(len(set(ids)), 5)
        self.assertEqual(
            [alternativa["texto"] for alternativa in questao_criada["alternativas"]],
            ["A", "B", "C", "D", "E"]
        )
        self.assertEqual(
            questao_criada["alternativa_correta"],
            questao_criada["alternativas"][0]["id"]
        )

        questao = self.questao_client.get("/api/v1/questoes/").get_json()["data"]["questoes"][0]
        self.assertIn("alternativas", questao)
        self.assertIn(
            questao["alternativa_correta"],
            [alternativa["id"] for alternativa in questao["alternativas"]]
        )

    def test_rejeita_texto_correto_ausente_das_alternativas(self):
        payload = payload_questao(20)
        payload["questao"]["alternativa_correta"] = "Alternativa inexistente"
        resposta = self.questao_client.post("/api/v1/questoes/", json=payload)
        self.assertEqual(resposta.status_code, 400)

    def test_middleware_rejeita_campos_do_tipo_errado(self):
        payload = payload_questao(2)
        payload["questao"].pop("alternativas")
        payload["questao"].pop("alternativa_correta")
        payload["questao"]["numero_linhas"] = 5
        self.assertEqual(self.questao_client.post("/api/v1/questoes/", json=payload).status_code, 400)

    def test_criacao_da_prova_base_sem_questoes(self):
        prova_dao = FakeProvaDao()
        service = Prova_service(prova_dao, self.questao_dao, self.prova_x_aluno_service)
        controle = Prova_controle(service)
        client = criar_app(Prova_rotas(Prova_middleware(), controle).criar_rotas(), "/api/v1/provas").test_client()

        payload = {"prova": {"id_turma": "Turma 2026 A", "professor": {"registro": 101, "nome": "Carlos Silva"}, "disciplina": {"codigo_disciplina": "MAT", "nome_disciplina": "Matemática"}, "tipo": "Objetiva", "serie": 3, "bimestre": "1° bimestre", "data_de_aplicacao": "2026-08-20"}}
        criacao = client.post("/api/v1/provas/criar-prova", json=payload)

        self.assertEqual(criacao.status_code, 201)
        persistida = next(iter(prova_dao.documentos.values()))
        self.assertEqual(persistida["professor"]["registro"], 101)
        self.assertEqual(persistida["questoes"], [])
        self.assertEqual(persistida["status"], "Aguardando questões")

        prova_retornada = criacao.get_json()["data"]["prova"]
        self.assertEqual(prova_retornada["_id"], persistida["_id"])
        self.assertEqual(prova_retornada["questoes"], [])
        self.assertEqual(prova_retornada["status"], "Aguardando questões")

    def test_criacao_da_prova_base_rejeita_campos_gerenciados_pela_api(self):
        prova_dao = FakeProvaDao()
        service = Prova_service(prova_dao, self.questao_dao, self.prova_x_aluno_service)
        controle = Prova_controle(service)
        client = criar_app(Prova_rotas(Prova_middleware(), controle).criar_rotas(), "/api/v1/provas").test_client()

        payload = {"prova": {"id_turma": "Turma 2026 A", "professor": {"registro": 101, "nome": "Carlos Silva"}, "disciplina": {"codigo_disciplina": "MAT", "nome_disciplina": "Matemática"}, "tipo": "Objetiva", "serie": 3, "bimestre": "1° bimestre", "data_de_aplicacao": "2026-08-20", "questoes": []}}
        resposta = client.post("/api/v1/provas/criar-prova", json=payload)

        self.assertEqual(resposta.status_code, 400)
        self.assertIn("questoes", resposta.get_json()["erro"]["mensagem"])
        self.assertEqual(prova_dao.documentos, {})

    def test_criacao_da_prova_base_exige_registro_do_professor(self):
        prova_dao = FakeProvaDao()
        service = Prova_service(prova_dao, self.questao_dao, self.prova_x_aluno_service)
        controle = Prova_controle(service)
        client = criar_app(Prova_rotas(Prova_middleware(), controle).criar_rotas(), "/api/v1/provas").test_client()

        payload = {"prova": {"id_turma": "Turma 2026 A", "professor": {"nome": "Carlos Silva"}, "disciplina": {"codigo_disciplina": "MAT", "nome_disciplina": "Matemática"}, "tipo": "Objetiva", "serie": 3, "bimestre": "1° bimestre", "data_de_aplicacao": "2026-08-20"}}
        resposta = client.post("/api/v1/provas/criar-prova", json=payload)

        self.assertEqual(resposta.status_code, 400)
        self.assertIn("registro", resposta.get_json()["erro"]["mensagem"])

    def test_adiciona_uma_questao_e_substitui_o_vetor_sem_duplicar(self):
        questao = self.questao_client.post(
            "/api/v1/questoes/",
            json=payload_questao(30)
        ).get_json()["data"]["questao"]

        prova_dao = FakeProvaDao()
        service = Prova_service(prova_dao, self.questao_dao, self.prova_x_aluno_service)
        controle = Prova_controle(service)
        client = criar_app(
            Prova_rotas(Prova_middleware(), controle).criar_rotas(),
            "/api/v1/provas"
        ).test_client()

        payload_prova = {"prova": {"id_turma": "Turma 2026 A", "professor": {"registro": 101, "nome": "Carlos Silva"}, "disciplina": {"codigo_disciplina": "MAT", "nome_disciplina": "Matemática"}, "tipo": "Objetiva", "serie": 3, "bimestre": "1° bimestre", "data_de_aplicacao": "2026-08-20"}}
        prova = client.post(
            "/api/v1/provas/criar-prova",
            json=payload_prova
        ).get_json()["data"]["prova"]

        rota = f"/api/v1/provas/{prova['_id']}/adicionar-questoes"
        payload = {"prova": {"questoes": [questao["_id"]]}}

        primeira_resposta = client.patch(rota, json=payload)
        segunda_resposta = client.patch(rota, json=payload)

        self.assertEqual(primeira_resposta.status_code, 200)
        self.assertEqual(segunda_resposta.status_code, 200)
        self.assertEqual(
            primeira_resposta.get_json()["data"]["prova"]["questoes"],
            [questao["_id"]]
        )
        self.assertEqual(
            prova_dao.documentos[prova["_id"]]["questoes"],
            [questao["_id"]]
        )
        self.assertEqual(
            prova_dao.documentos[prova["_id"]]["status"],
            "Aguardando questões"
        )

    def test_prova_objetiva_gera_uma_versao_embaralhada_por_aluno(self):
        ids_questoes = []
        for numero in range(40, 43):
            questao = self.questao_client.post(
                "/api/v1/questoes/",
                json=payload_questao(numero)
            ).get_json()["data"]["questao"]
            ids_questoes.append(questao["_id"])

        self.aluno_dao.documentos = {
            12345678: {
                "matricula_aluno": 12345678,
                "turma": "Turma 2026 A",
                "ativo": True
            },
            87654321: {
                "matricula_aluno": 87654321,
                "turma": "Turma 2026 B",
                "ativo": True
            },
            11111111: {
                "matricula_aluno": 11111111,
                "turma": "Turma 2026 A",
                "ativo": False
            },
            22222222: {
                "matricula_aluno": 22222222,
                "turma": "Turma 2026 C",
                "ativo": True
            }
        }

        prova_dao = FakeProvaDao()
        service = Prova_service(
            prova_dao,
            self.questao_dao,
            self.prova_x_aluno_service
        )
        controle = Prova_controle(service)
        client = criar_app(
            Prova_rotas(Prova_middleware(), controle).criar_rotas(),
            "/api/v1/provas"
        ).test_client()

        payload_prova = {
            "prova": {
                "id_turma": ["Turma 2026 A", "Turma 2026 B"],
                "professor": {"registro": 101, "nome": "Carlos Silva"},
                "disciplina": {
                    "codigo_disciplina": "MAT",
                    "nome_disciplina": "Matemática"
                },
                "tipo": "Objetiva",
                "serie": 3,
                "bimestre": "1° bimestre",
                "data_de_aplicacao": "2026-08-20"
            }
        }
        prova = client.post(
            "/api/v1/provas/criar-prova",
            json=payload_prova
        ).get_json()["data"]["prova"]

        rota = f"/api/v1/provas/{prova['_id']}/adicionar-questoes"
        resposta = client.patch(
            rota,
            json={"prova": {"questoes": ids_questoes}}
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(
            resposta.get_json()["data"]["provas_alunos_geradas"],
            2
        )
        self.assertEqual(len(self.prova_x_aluno_dao.documentos), 2)

        for documento in self.prova_x_aluno_dao.documentos.values():
            questoes_aluno = documento["questoes"]
            ids_aluno = [questao["id_questao"] for questao in questoes_aluno]

            self.assertCountEqual(ids_aluno, ids_questoes)
            self.assertNotEqual(ids_aluno, ids_questoes)
            self.assertTrue(all(
                set(questao) == {
                    "id_questao",
                    "posicao_alternativa_correta"
                }
                for questao in questoes_aluno
            ))
            self.assertTrue(all(
                1 <= questao["posicao_alternativa_correta"] <= 5
                for questao in questoes_aluno
            ))

        segunda_resposta = client.patch(
            rota,
            json={"prova": {"questoes": ids_questoes}}
        )
        self.assertEqual(segunda_resposta.status_code, 200)
        self.assertEqual(len(self.prova_x_aluno_dao.documentos), 2)

        questoes_persistidas = deepcopy(self.questao_dao.documentos)
        self.prova_x_aluno_dao.documentos[("outra-prova", 99999999)] = {
            "matricula_aluno": 99999999,
            "id_prova": "outra-prova",
            "questoes": []
        }

        impressao = client.get(
            f"/api/v1/provas/imprimir-provas/{prova['_id']}"
        )
        self.assertEqual(impressao.status_code, 200)

        dados_impressao = impressao.get_json()["data"]
        self.assertEqual(dados_impressao["id_prova"], prova["_id"])
        self.assertEqual(len(dados_impressao["provas_alunos"]), 2)
        self.assertNotIn(
            99999999,
            [
                prova_aluno["matricula_aluno"]
                for prova_aluno in dados_impressao["provas_alunos"]
            ]
        )

        for prova_aluno in dados_impressao["provas_alunos"]:
            matricula = prova_aluno["matricula_aluno"]
            configuracoes = self.prova_x_aluno_dao.documentos[
                (prova["_id"], matricula)
            ]["questoes"]
            questoes_impressao = prova_aluno["questoes"]

            self.assertEqual(
                [questao["_id"] for questao in questoes_impressao],
                [configuracao["id_questao"] for configuracao in configuracoes]
            )

            for questao, configuracao in zip(
                questoes_impressao,
                configuracoes
            ):
                indice_correto = (
                    configuracao["posicao_alternativa_correta"] - 1
                )
                self.assertEqual(
                    questao["alternativas"][indice_correto]["id"],
                    questao["alternativa_correta"]
                )

        self.assertEqual(self.questao_dao.documentos, questoes_persistidas)

    def test_imprimir_provas_sem_alunos_retorna_lista_vazia(self):
        prova_dao = FakeProvaDao()
        service = Prova_service(
            prova_dao,
            self.questao_dao,
            self.prova_x_aluno_service
        )
        controle = Prova_controle(service)
        client = criar_app(
            Prova_rotas(Prova_middleware(), controle).criar_rotas(),
            "/api/v1/provas"
        ).test_client()

        resposta = client.get(
            "/api/v1/provas/imprimir-provas/000000000000000000000099"
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(
            resposta.get_json()["data"]["provas_alunos"],
            []
        )

    def test_imprimir_provas_rejeita_questao_ausente(self):
        id_prova = "000000000000000000000088"
        self.prova_x_aluno_dao.documentos[(id_prova, 12345678)] = {
            "matricula_aluno": 12345678,
            "id_prova": id_prova,
            "questoes": [{
                "id_questao": "000000000000000000000099",
                "posicao_alternativa_correta": 1
            }]
        }

        prova_dao = FakeProvaDao()
        service = Prova_service(
            prova_dao,
            self.questao_dao,
            self.prova_x_aluno_service
        )
        controle = Prova_controle(service)
        client = criar_app(
            Prova_rotas(Prova_middleware(), controle).criar_rotas(),
            "/api/v1/provas"
        ).test_client()

        resposta = client.get(
            f"/api/v1/provas/imprimir-provas/{id_prova}"
        )

        self.assertEqual(resposta.status_code, 404)
        self.assertEqual(
            resposta.get_json()["mensagem"],
            "Questão não encontrada"
        )

    def test_adicionar_questoes_rejeita_vetor_vazio_e_ids_repetidos(self):
        questao = self.questao_client.post(
            "/api/v1/questoes/",
            json=payload_questao(31)
        ).get_json()["data"]["questao"]

        prova_dao = FakeProvaDao()
        service = Prova_service(prova_dao, self.questao_dao, self.prova_x_aluno_service)
        controle = Prova_controle(service)
        client = criar_app(
            Prova_rotas(Prova_middleware(), controle).criar_rotas(),
            "/api/v1/provas"
        ).test_client()

        payload_prova = {"prova": {"id_turma": "Turma 2026 A", "professor": {"registro": 101, "nome": "Carlos Silva"}, "disciplina": {"codigo_disciplina": "MAT", "nome_disciplina": "Matemática"}, "tipo": "Objetiva", "serie": 3, "bimestre": "1° bimestre", "data_de_aplicacao": "2026-08-20"}}
        prova = client.post(
            "/api/v1/provas/criar-prova",
            json=payload_prova
        ).get_json()["data"]["prova"]
        rota = f"/api/v1/provas/{prova['_id']}/adicionar-questoes"

        resposta_vazia = client.patch(
            rota,
            json={"prova": {"questoes": []}}
        )
        resposta_repetida = client.patch(
            rota,
            json={"prova": {"questoes": [questao["_id"], questao["_id"]]}}
        )

        self.assertEqual(resposta_vazia.status_code, 400)
        self.assertEqual(resposta_repetida.status_code, 400)
        self.assertEqual(prova_dao.documentos[prova["_id"]]["questoes"], [])

    def test_adicionar_questoes_rejeita_prova_inexistente_e_tipo_incompativel(self):
        questao = self.questao_client.post(
            "/api/v1/questoes/",
            json=payload_questao(32)
        ).get_json()["data"]["questao"]

        prova_dao = FakeProvaDao()
        service = Prova_service(prova_dao, self.questao_dao, self.prova_x_aluno_service)
        controle = Prova_controle(service)
        client = criar_app(
            Prova_rotas(Prova_middleware(), controle).criar_rotas(),
            "/api/v1/provas"
        ).test_client()

        inexistente = client.patch(
            "/api/v1/provas/000000000000000000000099/adicionar-questoes",
            json={"prova": {"questoes": [questao["_id"]]}}
        )

        payload_prova = {"prova": {"id_turma": "Turma 2026 A", "professor": {"registro": 101, "nome": "Carlos Silva"}, "disciplina": {"codigo_disciplina": "MAT", "nome_disciplina": "Matemática"}, "tipo": "Dissertativa", "serie": 3, "bimestre": "1° bimestre", "data_de_aplicacao": "2026-08-20"}}
        prova = client.post(
            "/api/v1/provas/criar-prova",
            json=payload_prova
        ).get_json()["data"]["prova"]
        incompativel = client.patch(
            f"/api/v1/provas/{prova['_id']}/adicionar-questoes",
            json={"prova": {"questoes": [questao["_id"]]}}
        )

        self.assertEqual(inexistente.status_code, 404)
        self.assertEqual(incompativel.status_code, 400)
        self.assertIn("Tipo", incompativel.get_json()["mensagem"])


if __name__ == "__main__":
    unittest.main()
