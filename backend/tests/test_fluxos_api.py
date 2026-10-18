import unittest
from copy import deepcopy
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from threading import Event
from unittest.mock import patch

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

    def test_middleware_exige_alternativas_e_gabarito(self):
        payload = payload_questao(2)
        payload["questao"].pop("alternativas")
        payload["questao"].pop("alternativa_correta")
        self.assertEqual(self.questao_client.post("/api/v1/questoes/", json=payload).status_code, 400)

    def test_cadastro_e_atualizacao_rejeitam_tipo_nao_objetivo(self):
        payload = payload_questao(90)
        questao = self.questao_client.post(
            "/api/v1/questoes/", json=payload
        ).get_json()["data"]["questao"]
        payload["questao"]["tipo_questao"] = "Outro"
        for metodo, rota in [
            (self.questao_client.post, "/api/v1/questoes/"),
            (self.questao_client.put, f"/api/v1/questoes/{questao['_id']}"),
        ]:
            with self.subTest(rota=rota):
                self.assertEqual(metodo(rota, json=payload).status_code, 400)
        self.assertEqual(self.questao_dao.documentos[questao["_id"]]["tipo_questao"], "Objetiva")

    def test_prova_rejeita_tipo_nao_objetivo_na_criacao_e_atualizacao(self):
        prova_dao = FakeProvaDao()
        service = Prova_service(prova_dao, self.questao_dao, self.prova_x_aluno_service)
        client = criar_app(
            Prova_rotas(Prova_middleware(), Prova_controle(service)).criar_rotas(),
            "/api/v1/provas"
        ).test_client()
        dados = {"id_turma": "Turma 2026 A", "professor": {"registro": 101, "nome": "Carlos Silva"}, "disciplina": {"codigo_disciplina": "MAT", "nome_disciplina": "Matemática"}, "tipo": "Objetiva", "serie": 3, "periodo_letivo": "1º período letivo", "data_de_aplicacao": "2026-08-20", "quantidade_questoes": 3}
        prova = client.post("/api/v1/provas/criar-prova", json={"prova": dados}).get_json()["data"]["prova"]
        dados["tipo"] = "Outro"
        self.assertEqual(client.post("/api/v1/provas/criar-prova", json={"prova": dados}).status_code, 400)
        dados.update(status="Aguardando questões", questoes=[])
        self.assertEqual(client.put(f"/api/v1/provas/{prova['_id']}", json={"prova": dados}).status_code, 400)
        self.assertEqual(len(prova_dao.documentos), 1)
        self.assertEqual(prova_dao.documentos[prova["_id"]]["tipo"], "Objetiva")

    def test_modelos_aceitam_apenas_tipo_objetivo(self):
        from api.modelos.prova import Prova
        from api.modelos.questao import Questao

        for modelo, campo in [(Prova(), "tipo"), (Questao(), "tipo_questao")]:
            with self.subTest(modelo=type(modelo).__name__):
                setattr(modelo, campo, " objetiva ")
                self.assertEqual(getattr(modelo, campo), "Objetiva")
                with self.assertRaises(ValueError):
                    setattr(modelo, campo, "Outro")

    def test_prova_objetiva_rejeita_questao_legada_de_outro_tipo(self):
        questao = self.questao_client.post(
            "/api/v1/questoes/", json=payload_questao(91)
        ).get_json()["data"]["questao"]
        self.questao_dao.documentos[questao["_id"]]["tipo_questao"] = "Outro"
        segunda_questao = self.questao_client.post(
            "/api/v1/questoes/", json=payload_questao(92)
        ).get_json()["data"]["questao"]
        prova_dao = FakeProvaDao()
        service = Prova_service(prova_dao, self.questao_dao, self.prova_x_aluno_service)
        with self.assertRaises(resposta_erro_http) as resultado:
            service._validar_ids_questoes(
                [questao["_id"], segunda_questao["_id"]], "Objetiva",
                {"codigo_disciplina": "MAT", "nome_disciplina": "Matemática"}
            )
        self.assertEqual(resultado.exception.httpCode, 400)
        self.assertEqual(resultado.exception.mensagem, "Tipo de questão incompatível")

    def test_criacao_da_prova_base_sem_questoes(self):
        prova_dao = FakeProvaDao()
        service = Prova_service(prova_dao, self.questao_dao, self.prova_x_aluno_service)
        controle = Prova_controle(service)
        client = criar_app(Prova_rotas(Prova_middleware(), controle).criar_rotas(), "/api/v1/provas").test_client()

        payload = {"prova": {"id_turma": "Turma 2026 A", "professor": {"registro": 101, "nome": "Carlos Silva"}, "disciplina": {"codigo_disciplina": "MAT", "nome_disciplina": "Matemática"}, "tipo": "Objetiva", "serie": 3, "periodo_letivo": "1º período letivo", "data_de_aplicacao": "2026-08-20", "quantidade_questoes": 3}}
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
        self.assertEqual(self.prova_x_aluno_dao.documentos, {})

        # Mesmo nome, registros diferentes: a atribuição depende do registro.
        payload["prova"]["professor"]["registro"] = 202
        client.post("/api/v1/provas/criar-prova", json=payload)
        consulta = client.get("/api/v1/provas/?registro=101")
        self.assertEqual(consulta.status_code, 200)
        self.assertEqual(consulta.get_json()["data"]["provas"], [prova_retornada])
        consulta_por_id = client.get(f"/api/v1/provas/?registro=101&id={prova_retornada['_id']}")
        self.assertEqual(consulta_por_id.get_json()["data"]["provas"], [prova_retornada])
        self.assertEqual(client.get("/api/v1/provas/?registro=303").get_json()["data"]["provas"], [])

    def test_consulta_provas_rejeita_registro_nao_inteiro(self):
        controle = Prova_controle(Prova_service(FakeProvaDao(), self.questao_dao, self.prova_x_aluno_service))
        client = criar_app(Prova_rotas(Prova_middleware(), controle).criar_rotas(), "/api/v1/provas").test_client()

        resposta = client.get("/api/v1/provas/?registro=abc")

        self.assertEqual(resposta.status_code, 400)
        self.assertIn("registro inválido", resposta.get_json()["mensagem"])

    def test_criacao_da_prova_base_rejeita_campos_gerenciados_pela_api(self):
        prova_dao = FakeProvaDao()
        service = Prova_service(prova_dao, self.questao_dao, self.prova_x_aluno_service)
        controle = Prova_controle(service)
        client = criar_app(Prova_rotas(Prova_middleware(), controle).criar_rotas(), "/api/v1/provas").test_client()

        payload = {"prova": {"id_turma": "Turma 2026 A", "professor": {"registro": 101, "nome": "Carlos Silva"}, "disciplina": {"codigo_disciplina": "MAT", "nome_disciplina": "Matemática"}, "tipo": "Objetiva", "serie": 3, "periodo_letivo": "1º período letivo", "data_de_aplicacao": "2026-08-20", "quantidade_questoes": 3, "questoes": []}}
        resposta = client.post("/api/v1/provas/criar-prova", json=payload)

        self.assertEqual(resposta.status_code, 400)
        self.assertIn("questoes", resposta.get_json()["erro"]["mensagem"])
        self.assertEqual(prova_dao.documentos, {})

    def test_criacao_da_prova_base_exige_registro_do_professor(self):
        prova_dao = FakeProvaDao()
        service = Prova_service(prova_dao, self.questao_dao, self.prova_x_aluno_service)
        controle = Prova_controle(service)
        client = criar_app(Prova_rotas(Prova_middleware(), controle).criar_rotas(), "/api/v1/provas").test_client()

        payload = {"prova": {"id_turma": "Turma 2026 A", "professor": {"nome": "Carlos Silva"}, "disciplina": {"codigo_disciplina": "MAT", "nome_disciplina": "Matemática"}, "tipo": "Objetiva", "serie": 3, "periodo_letivo": "1º período letivo", "data_de_aplicacao": "2026-08-20", "quantidade_questoes": 3}}
        resposta = client.post("/api/v1/provas/criar-prova", json=payload)

        self.assertEqual(resposta.status_code, 400)
        self.assertIn("registro", resposta.get_json()["erro"]["mensagem"])

    def test_adiciona_duas_questoes_e_substitui_o_vetor_sem_duplicar(self):
        questao = self.questao_client.post(
            "/api/v1/questoes/",
            json=payload_questao(30)
        ).get_json()["data"]["questao"]

        segunda_questao = self.questao_client.post(
            "/api/v1/questoes/", json=payload_questao(31)
        ).get_json()["data"]["questao"]

        prova_dao = FakeProvaDao()
        service = Prova_service(prova_dao, self.questao_dao, self.prova_x_aluno_service)
        controle = Prova_controle(service)
        client = criar_app(
            Prova_rotas(Prova_middleware(), controle).criar_rotas(),
            "/api/v1/provas"
        ).test_client()

        payload_prova = {"prova": {"id_turma": "Turma 2026 A", "professor": {"registro": 101, "nome": "Carlos Silva"}, "disciplina": {"codigo_disciplina": "MAT", "nome_disciplina": "Matemática"}, "tipo": "Objetiva", "serie": 3, "periodo_letivo": "1º período letivo", "data_de_aplicacao": "2026-08-20", "quantidade_questoes": 3}}
        prova = client.post(
            "/api/v1/provas/criar-prova",
            json=payload_prova
        ).get_json()["data"]["prova"]

        rota = f"/api/v1/provas/{prova['_id']}/adicionar-questoes"
        payload = {"prova": {"questoes": [questao["_id"], segunda_questao["_id"]]}}

        primeira_resposta = client.patch(rota, json=payload)
        segunda_resposta = client.patch(rota, json=payload)

        self.assertEqual(primeira_resposta.status_code, 200)
        self.assertEqual(segunda_resposta.status_code, 200)
        self.assertEqual(
            primeira_resposta.get_json()["data"]["prova"]["questoes"],
            [questao["_id"], segunda_questao["_id"]]
        )
        self.assertEqual(
            prova_dao.documentos[prova["_id"]]["questoes"],
            [questao["_id"], segunda_questao["_id"]]
        )
        self.assertEqual(
            prova_dao.documentos[prova["_id"]]["status"],
            "Em elaboração"
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
                "periodo_letivo": "1º período letivo",
                "data_de_aplicacao": "2026-08-20",
                "quantidade_questoes": 3
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

        self.assertEqual(client.patch(f"/api/v1/provas/{prova['_id']}/enviar").status_code, 200)
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

        # Uma base válida sem versões continua retornando uma lista vazia.
        prova_dao.documentos["000000000000000000000099"] = {
            "_id": "000000000000000000000099", "ativo": True, "tipo": "Objetiva", "questoes": [],
            "status": "Enviada ao pedagógico"
        }
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
        prova_dao.documentos[id_prova] = {
            "_id": id_prova, "ativo": True, "tipo": "Objetiva", "questoes": ["000000000000000000000099"],
            "status": "Enviada ao pedagógico"
        }
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

        payload_prova = {"prova": {"id_turma": "Turma 2026 A", "professor": {"registro": 101, "nome": "Carlos Silva"}, "disciplina": {"codigo_disciplina": "MAT", "nome_disciplina": "Matemática"}, "tipo": "Objetiva", "serie": 3, "periodo_letivo": "1º período letivo", "data_de_aplicacao": "2026-08-20", "quantidade_questoes": 3}}
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

        payload_prova = {"prova": {"id_turma": "Turma 2026 A", "professor": {"registro": 101, "nome": "Carlos Silva"}, "disciplina": {"codigo_disciplina": "MAT", "nome_disciplina": "Matemática"}, "tipo": "Objetiva", "serie": 3, "periodo_letivo": "1º período letivo", "data_de_aplicacao": "2026-08-20", "quantidade_questoes": 3}}
        prova = client.post(
            "/api/v1/provas/criar-prova",
            json=payload_prova
        ).get_json()["data"]["prova"]
        # Simula um registro antigo de tipo não suportado, sem permitir seu cadastro.
        prova_dao.documentos[prova["_id"]]["tipo"] = "Outro"
        incompativel = client.patch(
            f"/api/v1/provas/{prova['_id']}/adicionar-questoes",
            json={"prova": {"questoes": [questao["_id"]]}}
        )

        self.assertEqual(inexistente.status_code, 404)
        self.assertEqual(incompativel.status_code, 400)
        self.assertIn("Tipo", incompativel.get_json()["mensagem"])
        self.assertEqual(prova_dao.documentos[prova["_id"]]["questoes"], [])


class FluxoSelecaoEEnvioTest(unittest.TestCase):
    def setUp(self):
        FluxoQuestaoEProvaTest.setUp(self)
        self.prova_dao = FakeProvaDao()
        self.questao_dao.provas = self.prova_dao.documentos
        self.service = Prova_service(self.prova_dao, self.questao_dao, self.prova_x_aluno_service)
        self.client = criar_app(
            Prova_rotas(Prova_middleware(), Prova_controle(self.service)).criar_rotas(), "/api/v1/provas"
        ).test_client()
        self.metadados = {"id_turma": "Turma 2026 A", "professor": {"registro": 101, "nome": "Carlos Silva"},
                          "disciplina": {"codigo_disciplina": "MAT", "nome_disciplina": "Matemática"},
                          "tipo": "Objetiva", "serie": 3, "periodo_letivo": "1º período letivo", "data_de_aplicacao": "2026-08-20", "quantidade_questoes": 3}
        self.prova = self.client.post("/api/v1/provas/criar-prova", json={"prova": self.metadados}).get_json()["data"]["prova"]
        self.id = self.prova["_id"]
        self.ids = [self.questao_client.post("/api/v1/questoes/", json=payload_questao(numero)).get_json()["data"]["questao"]["_id"]
                    for numero in range(200, 203)]
        self.aluno_dao.documentos = {numero: {"matricula_aluno": numero, "turma": "Turma 2026 A", "ativo": True}
                                     for numero in (20260001, 20260002)}

    def salvar(self, ids=None):
        return self.client.patch(f"/api/v1/provas/{self.id}/adicionar-questoes",
                                 json={"prova": {"questoes": self.ids if ids is None else ids}})

    def enviar(self):
        return self.client.patch(f"/api/v1/provas/{self.id}/enviar")

    def test_impressao_rejeita_base_excluida_ou_inexistente_sem_apagar_versoes(self):
        self.salvar()
        versoes = deepcopy(self.prova_x_aluno_dao.documentos)
        self.assertEqual(self.client.get(f"/api/v1/provas/imprimir-provas/{self.id}").status_code, 409)
        self.assertEqual(self.client.delete(f"/api/v1/provas/{self.id}").status_code, 200)
        for id_prova in (self.id, "invalido"):
            resposta = self.client.get(f"/api/v1/provas/imprimir-provas/{id_prova}")
            self.assertEqual(resposta.status_code, 404)
            self.assertEqual(resposta.get_json()["mensagem"], "Prova não encontrada")
        self.prova_dao.documentos.pop(self.id)
        with patch.object(self.prova_x_aluno_service, "montar_para_impressao") as montar:
            self.assertEqual(self.client.get(f"/api/v1/provas/imprimir-provas/{self.id}").status_code, 404)
            montar.assert_not_called()
        self.assertEqual(self.prova_x_aluno_dao.documentos, versoes)

    def test_impressao_concluida_e_estavel_e_nao_reabre_edicao(self):
        self.salvar()
        self.enviar()
        versoes = deepcopy(self.prova_x_aluno_dao.documentos)
        rota = f"/api/v1/provas/imprimir-provas/{self.id}"
        primeira = self.client.get(rota)
        segunda = self.client.get(rota)
        self.assertEqual(primeira.status_code, 200)
        self.assertEqual(primeira.get_json()["data"], segunda.get_json()["data"])
        self.assertEqual(len(primeira.get_json()["data"]["provas_alunos"]), 2)
        self.assertEqual(self.salvar(self.ids[::-1]).status_code, 409)
        self.assertEqual(self.client.delete(f"/api/v1/provas/{self.id}").status_code, 409)
        self.assertEqual(self.prova_x_aluno_dao.documentos, versoes)

    def test_confirmacao_de_impressao_e_idempotente_sem_regenerar_versoes(self):
        rota = f"/api/v1/provas/{self.id}/confirmar-impressao"
        self.assertEqual(self.client.patch(rota).status_code, 409)
        self.salvar()
        self.assertEqual(self.client.patch(rota).status_code, 409)
        self.enviar()
        versoes = deepcopy(self.prova_x_aluno_dao.documentos)
        self.assertEqual(self.client.get(f"/api/v1/provas/imprimir-provas/{self.id}").status_code, 200)
        self.assertEqual(self.prova_dao.documentos[self.id]["status"], "Enviada ao pedagógico")
        for _ in range(2):
            resposta = self.client.patch(rota)
            self.assertEqual(resposta.status_code, 200)
            self.assertEqual(resposta.get_json()["data"]["prova"]["status"], "Impressa")
        self.assertEqual(self.prova_dao.documentos[self.id]["status"], "Impressa")
        self.assertEqual(self.client.get(f"/api/v1/provas/imprimir-provas/{self.id}").status_code, 200)
        self.assertEqual(self.salvar().status_code, 409)
        self.assertEqual(self.enviar().status_code, 409)
        self.assertEqual(self.prova_x_aluno_dao.documentos, versoes)

    def test_periodo_letivo_e_obrigatorio_na_criacao_e_persistido(self):
        self.assertEqual(self.prova["periodo_letivo"], "1º período letivo")
        self.assertEqual(self.prova_dao.documentos[self.id]["periodo_letivo"], "1º período letivo")
        dados = {chave: valor for chave, valor in self.metadados.items() if chave != "periodo_letivo"}
        resposta = self.client.post("/api/v1/provas/criar-prova", json={"prova": dados})
        self.assertEqual(resposta.status_code, 400)
        self.assertIn("periodo_letivo", resposta.get_json()["erro"]["mensagem"])
        for valor in (None, 3):
            self.assertEqual(self.client.post("/api/v1/provas/criar-prova", json={"prova": {**self.metadados, "periodo_letivo": valor}}).status_code, 400)

    def test_periodo_letivo_na_consulta_no_put_e_na_imutabilidade(self):
        dados = {**self.metadados, "periodo_letivo": " 2º período letivo "}
        criada = self.client.post("/api/v1/provas/criar-prova", json={"prova": dados})
        self.assertEqual(criada.get_json()["data"]["prova"]["periodo_letivo"], "2º período letivo")
        consulta = self.client.get("/api/v1/provas/", query_string={"periodo_letivo": "1º período letivo"})
        self.assertEqual([item["_id"] for item in consulta.get_json()["data"]["provas"]], [self.id])
        dados.update(status="Aguardando questões", questoes=[])
        resposta = self.client.put(f"/api/v1/provas/{self.id}", json={"prova": dados})
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.get_json()["data"]["prova"]["periodo_letivo"].strip(), "2º período letivo")
        self.assertEqual(self.prova_dao.documentos[self.id]["periodo_letivo"], "2º período letivo")
        self.salvar()
        dados.update(status="Em elaboração", questoes=self.ids, periodo_letivo="3º período letivo")
        self.assertEqual(self.client.put(f"/api/v1/provas/{self.id}", json={"prova": dados}).status_code, 409)

    def test_criacao_exige_quantidade_inteira_entre_dois_e_dez(self):
        for valor in (None, True, False, 0, 1, 11, 2.5, "3"):
            with self.subTest(valor=valor):
                resposta = self.client.post("/api/v1/provas/criar-prova", json={"prova": {**self.metadados, "quantidade_questoes": valor}})
                self.assertEqual(resposta.status_code, 400)
        dados = {chave: valor for chave, valor in self.metadados.items() if chave != "quantidade_questoes"}
        self.assertEqual(self.client.post("/api/v1/provas/criar-prova", json={"prova": dados}).status_code, 400)
        self.assertEqual(len(self.prova_dao.documentos), 1)
        self.assertEqual(self.prova["quantidade_questoes"], 3)
        consulta = self.client.get(f"/api/v1/provas/?id={self.id}").get_json()["data"]["provas"][0]
        self.assertEqual(consulta["quantidade_questoes"], 3)

    def test_selecao_parcial_salva_mas_so_envia_com_a_quantidade_definida(self):
        self.assertEqual(self.salvar(self.ids[:2]).status_code, 200)
        base = deepcopy(self.prova_dao.documentos[self.id])
        versoes = deepcopy(self.prova_x_aluno_dao.documentos)
        self.assertEqual(self.enviar().status_code, 400)
        self.assertEqual(self.prova_dao.documentos[self.id], base)
        self.assertEqual(self.prova_x_aluno_dao.documentos, versoes)
        excedentes = self.ids_para_limite()[:4]
        self.assertEqual(self.salvar(excedentes).status_code, 400)
        self.assertEqual(self.prova_dao.documentos[self.id], base)
        self.assertEqual(self.prova_x_aluno_dao.documentos, versoes)
        self.assertEqual(self.salvar().status_code, 200)
        self.assertEqual(self.enviar().status_code, 200)

    def test_quantidade_pode_mudar_antes_de_selecionar_e_depois_fica_bloqueada(self):
        payload = {**self.metadados, "quantidade_questoes": 4, "status": "Aguardando questões", "questoes": []}
        resposta = self.client.put(f"/api/v1/provas/{self.id}", json={"prova": payload})
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.get_json()["data"]["prova"]["quantidade_questoes"], 4)
        self.assertEqual(self.prova_dao.documentos[self.id]["quantidade_questoes"], 4)
        self.salvar()
        payload.update(quantidade_questoes=3, status="Em elaboração", questoes=self.ids)
        self.assertEqual(self.client.put(f"/api/v1/provas/{self.id}", json={"prova": payload}).status_code, 409)
        payload.pop("quantidade_questoes")
        resposta = self.client.put(f"/api/v1/provas/{self.id}", json={"prova": payload})
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.get_json()["data"]["prova"]["quantidade_questoes"], 4)
        self.assertEqual(self.prova_dao.documentos[self.id]["quantidade_questoes"], 4)

    def test_bases_antigas_sem_quantidade_continuam_com_limites_anteriores(self):
        self.prova_dao.documentos[self.id].pop("quantidade_questoes")
        self.assertEqual(self.salvar(self.ids[:2]).status_code, 200)
        self.assertEqual(self.enviar().status_code, 200)
        self.assertEqual(self.client.get(f"/api/v1/provas/imprimir-provas/{self.id}").status_code, 200)

    def test_impressao_e_confirmacao_rejeitam_quantidade_inconsistente(self):
        self.salvar(); self.enviar()
        self.prova_dao.documentos[self.id]["quantidade_questoes"] = 4
        self.assertEqual(self.client.get(f"/api/v1/provas/imprimir-provas/{self.id}").status_code, 400)
        self.assertEqual(self.client.patch(f"/api/v1/provas/{self.id}/confirmar-impressao").status_code, 400)
        self.prova_dao.documentos[self.id]["quantidade_questoes"] = 3
        registro = next(iter(self.prova_x_aluno_dao.documentos.values()))
        registro["questoes"].pop()
        self.assertEqual(self.client.get(f"/api/v1/provas/imprimir-provas/{self.id}").status_code, 400)

    def test_confirmacao_rejeita_base_invalida_sem_versoes_e_corrigida(self):
        rota = f"/api/v1/provas/{self.id}/confirmar-impressao"
        self.salvar()
        self.enviar()
        with patch.object(self.prova_x_aluno_service, "quantidade_versoes", return_value=0):
            self.assertEqual(self.client.patch(rota).status_code, 409)
        self.assertEqual(self.prova_dao.documentos[self.id]["status"], "Enviada ao pedagógico")
        self.prova_dao.documentos[self.id]["status"] = "Corrigida"
        self.assertEqual(self.client.patch(rota).status_code, 409)
        self.assertEqual(self.prova_dao.documentos[self.id]["status"], "Corrigida")
        self.prova_dao.documentos[self.id]["ativo"] = False
        self.assertEqual(self.client.patch(rota).status_code, 404)

    def _preparar_correcao_parcial(self, total=4, processadas=3):
        self.salvar()
        self.enviar()
        self.client.patch(f"/api/v1/provas/{self.id}/confirmar-impressao")
        documentos = self.prova_x_aluno_dao.documentos
        modelo = deepcopy(next(iter(documentos.values())))
        documentos.clear()
        for indice in range(total):
            versao = {**deepcopy(modelo), "_id": f"{indice + 10000:024x}", "matricula_aluno": indice + 9000}
            if indice < processadas:
                versao["tentativa_correcao"] = {"sucesso": indice % 2 == 0, "concluida_em": "2026-10-18T22:00:00+00:00"}
            documentos[(self.id, versao["matricula_aluno"])] = versao

    def test_consulta_impressas_retorna_contador_com_falhas_sem_alterar_documentos(self):
        self._preparar_correcao_parcial()
        versoes = deepcopy(self.prova_x_aluno_dao.documentos)
        resposta = self.client.get("/api/v1/provas/", query_string={"status": "Impressa"})
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json["data"]["provas"][0]["progresso_correcao"], {"total": 4, "processadas": 3})
        self.assertEqual(self.prova_x_aluno_dao.documentos, versoes)
        self.assertEqual(self.prova_dao.documentos[self.id]["status"], "Impressa")

    def test_ignorar_acima_da_metade_altera_so_o_status_e_preserva_versoes(self):
        self._preparar_correcao_parcial()
        versoes = deepcopy(self.prova_x_aluno_dao.documentos)
        resposta = self.client.patch(f"/api/v1/provas/{self.id}/ignorar-provas-nao-corrigidas")
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json["data"]["prova"]["status"], "Corrigida")
        self.assertEqual(resposta.json["data"]["prova"]["progresso_correcao"], {"total": 4, "processadas": 3})
        self.assertEqual(self.prova_x_aluno_dao.documentos, versoes)
        self.assertNotIn("operacao_em_andamento", self.prova_dao.documentos[self.id])
        self.assertEqual(self.client.patch(f"/api/v1/provas/{self.id}/ignorar-provas-nao-corrigidas").status_code, 409)

    def test_ignorar_nao_aceita_metade_ou_menos_e_reconsulta_contagem_na_confirmacao(self):
        self._preparar_correcao_parcial()
        rota = f"/api/v1/provas/{self.id}/ignorar-provas-nao-corrigidas"
        # A lista informa 3/4, mas uma versão muda antes da confirmação.
        self.assertEqual(self.client.get(f"/api/v1/provas/?id={self.id}").json["data"]["provas"][0]["progresso_correcao"]["processadas"], 3)
        list(self.prova_x_aluno_dao.documentos.values())[2].pop("tentativa_correcao")
        for tentativas in (2, 1, 0):
            if tentativas < 2:
                list(self.prova_x_aluno_dao.documentos.values())[tentativas].pop("tentativa_correcao")
            # Números enviados pelo navegador não podem contornar a contagem do banco.
            self.assertEqual(self.client.patch(rota, json={"processadas": 4, "total": 4}).status_code, 409)
            self.assertEqual(self.prova_dao.documentos[self.id]["status"], "Impressa")
            self.assertNotIn("operacao_em_andamento", self.prova_dao.documentos[self.id])
        self.prova_x_aluno_dao.documentos.clear()
        self.assertEqual(self.client.patch(rota).status_code, 409)

    def test_ignorar_rejeita_status_diferente_de_impressa_e_base_inexistente(self):
        self._preparar_correcao_parcial()
        for status in ("Aguardando questões", "Em elaboração", "Enviada ao pedagógico", "Corrigida"):
            self.prova_dao.documentos[self.id]["status"] = status
            self.assertEqual(self.client.patch(f"/api/v1/provas/{self.id}/ignorar-provas-nao-corrigidas").status_code, 409)
        self.assertEqual(self.client.patch(f"/api/v1/provas/{'f' * 24}/ignorar-provas-nao-corrigidas").status_code, 404)

    def test_ignorar_conta_maioria_estrita_com_total_impar_e_respeita_reserva(self):
        self._preparar_correcao_parcial(total=3, processadas=2)
        self.assertTrue(self.prova_dao.reservar_operacao(self.id, "outra-operacao"))
        rota = f"/api/v1/provas/{self.id}/ignorar-provas-nao-corrigidas"
        self.assertEqual(self.client.patch(rota).status_code, 409)
        self.prova_dao.liberar_operacao(self.id, "outra-operacao")
        self.assertEqual(self.client.patch(rota).status_code, 200)

    def test_impressao_inclui_nome_por_matricula_em_uma_consulta_sem_alterar_versoes(self):
        nomes = {20260001: "Ana Maria da Silva", 20260002: "João Pereira"}
        for matricula, nome in nomes.items():
            self.aluno_dao.documentos[matricula]["nome_aluno"] = nome
        self.salvar()
        self.enviar()
        versoes = deepcopy(self.prova_x_aluno_dao.documentos)
        with patch.object(self.aluno_dao, "consulta", wraps=self.aluno_dao.consulta) as consulta:
            resposta = self.client.get(f"/api/v1/provas/imprimir-provas/{self.id}")
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(consulta.call_count, 1)
        self.assertEqual({item["matricula_aluno"]: item["nome_aluno"]
                          for item in resposta.get_json()["data"]["provas_alunos"]}, nomes)
        self.assertEqual({item["matricula_aluno"]: item["turma_aluno"]
                          for item in resposta.get_json()["data"]["provas_alunos"]},
                         {matricula: self.aluno_dao.documentos[matricula]["turma"] for matricula in nomes})
        self.assertEqual(self.prova_x_aluno_dao.documentos, versoes)

    def test_impressao_sem_cadastro_do_aluno_nao_inventa_nome(self):
        self.salvar()
        self.enviar()
        self.aluno_dao.documentos = {}
        resposta = self.client.get(f"/api/v1/provas/imprimir-provas/{self.id}")
        self.assertEqual(resposta.status_code, 200)
        self.assertTrue(all(item["nome_aluno"] == "" for item in resposta.get_json()["data"]["provas_alunos"]))
        self.assertTrue(all(item["turma_aluno"] == "" for item in resposta.get_json()["data"]["provas_alunos"]))

    def test_geracao_bloqueia_conclusao_e_outras_escritas_da_mesma_prova(self):
        self.salvar()
        versoes_anteriores = deepcopy(self.prova_x_aluno_dao.documentos)
        iniciada, liberar = Event(), Event()
        gerar = self.prova_x_aluno_service.gerar
        outro_service = Prova_service(self.prova_dao, self.questao_dao, self.prova_x_aluno_service)

        def gerar_pausado(id_prova, turmas, ids):
            if id_prova == self.id:
                iniciada.set()
                if not liberar.wait(5):
                    raise RuntimeError("Teste de geração excedeu o tempo")
            return gerar(id_prova, turmas, ids)

        with patch.object(self.prova_x_aluno_service, "gerar", side_effect=gerar_pausado):
            with ThreadPoolExecutor(max_workers=1) as executor:
                futuro = executor.submit(self.service.adicionar_questoes, self.id, self.ids[::-1])
                try:
                    self.assertTrue(iniciada.wait(3))
                    self.assertEqual(self.enviar().status_code, 409)
                    with self.assertRaises(resposta_erro_http) as erro:
                        outro_service.adicionar_questoes(self.id, self.ids)
                    self.assertEqual(erro.exception.httpCode, 409)
                    self.assertEqual(self.client.delete(f"/api/v1/provas/{self.id}").status_code, 409)
                    dados = {**self.metadados, "questoes": self.ids[::-1], "status": "Em elaboração"}
                    self.assertEqual(self.client.put(f"/api/v1/provas/{self.id}", json={"prova": dados}).status_code, 409)
                    self.assertEqual(self.prova_x_aluno_dao.documentos, versoes_anteriores)
                    consulta = self.client.get("/api/v1/provas/").get_json()["data"]["provas"][0]
                    self.assertNotIn("operacao_em_andamento", consulta)
                    self.assertNotIn("geracao_pendente", consulta)
                    # A reserva é por prova, não um bloqueio global do servidor.
                    outra = self.client.post("/api/v1/provas/criar-prova", json={"prova": self.metadados}) \
                        .get_json()["data"]["prova"]
                    resultado = outro_service.adicionar_questoes(outra["_id"], self.ids)
                    self.assertEqual(resultado["provas_alunos_geradas"], 2)
                finally:
                    liberar.set()
                resultado = futuro.result(timeout=5)
        self.assertEqual(resultado["prova"]["status"], "Em elaboração")
        self.assertNotIn("operacao_em_andamento", self.prova_dao.documentos[self.id])
        self.assertNotIn("geracao_pendente", self.prova_dao.documentos[self.id])
        versoes_prontas = deepcopy(self.prova_x_aluno_dao.documentos)
        self.assertEqual(self.enviar().status_code, 200)
        self.assertEqual(self.salvar().status_code, 409)
        self.assertEqual(self.prova_x_aluno_dao.documentos, versoes_prontas)

    def test_conclusao_bloqueia_nova_geracao_em_outro_service(self):
        self.salvar()
        versoes = deepcopy(self.prova_x_aluno_dao.documentos)
        iniciada, liberar = Event(), Event()
        enviar = self.prova_dao.enviar
        outro_service = Prova_service(self.prova_dao, self.questao_dao, self.prova_x_aluno_service)

        def enviar_pausado(id_prova, ids, token=None):
            iniciada.set()
            if not liberar.wait(5):
                raise RuntimeError("Teste de envio excedeu o tempo")
            return enviar(id_prova, ids, token=token)

        with patch.object(self.prova_dao, "enviar", side_effect=enviar_pausado):
            with ThreadPoolExecutor(max_workers=1) as executor:
                futuro = executor.submit(self.service.enviar, self.id)
                try:
                    self.assertTrue(iniciada.wait(3))
                    with self.assertRaises(resposta_erro_http) as erro:
                        outro_service.adicionar_questoes(self.id, self.ids[::-1])
                    self.assertEqual(erro.exception.httpCode, 409)
                finally:
                    liberar.set()
                self.assertEqual(futuro.result(timeout=5)["prova"]["status"], "Enviada ao pedagógico")
        self.assertEqual(self.prova_x_aluno_dao.documentos, versoes)
        self.assertEqual(self.enviar().status_code, 200)
        self.assertEqual(self.salvar().status_code, 409)

    def test_falha_na_geracao_libera_reserva_mas_exige_recuperacao_antes_de_enviar(self):
        self.salvar()
        gerar = self.prova_x_aluno_service.gerar
        invertidas = self.ids[::-1]

        def gerar_e_falhar(*args):
            gerar(*args)
            raise RuntimeError("Falha ao finalizar a sincronização")

        with patch.object(self.prova_x_aluno_service, "gerar", side_effect=gerar_e_falhar):
            with self.assertRaises(RuntimeError):
                self.salvar(invertidas)
        doc = self.prova_dao.documentos[self.id]
        self.assertNotIn("operacao_em_andamento", doc)
        self.assertTrue(doc["geracao_pendente"])
        self.assertEqual(self.prova_x_aluno_service.quantidade_versoes(self.id, invertidas, doc["id_turma"]), 2)
        self.assertEqual(self.enviar().status_code, 409)
        self.assertEqual(doc["status"], "Em elaboração")
        with patch.object(self.prova_x_aluno_service, "gerar", wraps=gerar) as recuperacao:
            resposta = self.salvar(invertidas)
            recuperacao.assert_called_once()
        self.assertEqual(resposta.status_code, 200)
        self.assertTrue(resposta.get_json()["data"]["versoes_regeneradas"])
        self.assertNotIn("geracao_pendente", doc)
        self.assertNotIn("operacao_em_andamento", resposta.get_json()["data"]["prova"])
        self.assertEqual(self.enviar().status_code, 200)

    def ids_para_limite(self):
        return self.ids + [self.questao_client.post("/api/v1/questoes/", json=payload_questao(numero))
                           .get_json()["data"]["questao"]["_id"] for numero in range(300, 308)]

    def test_aceita_duas_e_dez_questoes_na_selecao_e_no_envio(self):
        ids = self.ids_para_limite()
        for quantidade in (2, 10):
            with self.subTest(quantidade=quantidade):
                self.metadados["quantidade_questoes"] = quantidade
                self.id = self.client.post("/api/v1/provas/criar-prova", json={"prova": self.metadados}) \
                    .get_json()["data"]["prova"]["_id"]
                resposta = self.salvar(ids[:quantidade])
                self.assertEqual(resposta.status_code, 200)
                self.assertEqual(resposta.get_json()["data"]["provas_alunos_geradas"], 2)
                self.assertEqual(self.enviar().status_code, 200)
                self.assertEqual(self.prova_dao.documentos[self.id]["questoes"], ids[:quantidade])

    def test_onze_questoes_nao_alteram_base_nem_versoes(self):
        ids = self.ids_para_limite()
        self.salvar()
        base = deepcopy(self.prova_dao.documentos[self.id])
        versoes = deepcopy(self.prova_x_aluno_dao.documentos)
        resposta = self.salvar(ids)
        self.assertEqual(resposta.status_code, 400)
        self.assertEqual(resposta.get_json()["mensagem"], "Limite de questões excedido")
        self.assertEqual(self.prova_dao.documentos[self.id], base)
        self.assertEqual(self.prova_x_aluno_dao.documentos, versoes)

    def test_prova_antiga_acima_do_limite_nao_pode_ser_enviada(self):
        ids = self.ids_para_limite()
        self.salvar()
        self.prova_dao.documentos[self.id]["questoes"] = ids
        base = deepcopy(self.prova_dao.documentos[self.id])
        versoes = deepcopy(self.prova_x_aluno_dao.documentos)
        resposta = self.enviar()
        self.assertEqual(resposta.status_code, 400)
        self.assertEqual(resposta.get_json()["mensagem"], "Limite de questões excedido")
        self.assertEqual(self.prova_dao.documentos[self.id], base)
        self.assertEqual(self.prova_x_aluno_dao.documentos, versoes)

    def test_lista_vazia_nao_pode_ser_salva(self):
        self.assertEqual(self.salvar([]).status_code, 400)
        self.assertEqual(self.prova_dao.documentos[self.id]["questoes"], [])
        self.assertEqual(self.prova_x_aluno_dao.documentos, {})

    def test_uma_questao_nao_altera_base_nem_versoes(self):
        self.salvar()
        base = deepcopy(self.prova_dao.documentos[self.id])
        versoes = deepcopy(self.prova_x_aluno_dao.documentos)
        resposta = self.salvar(self.ids[:1])
        self.assertEqual(resposta.status_code, 400)
        self.assertEqual(resposta.get_json()["erro"]["mensagem"], "Informe ao menos duas questões")
        self.assertEqual(self.prova_dao.documentos[self.id], base)
        self.assertEqual(self.prova_x_aluno_dao.documentos, versoes)

    def test_salvar_sem_mudanca_preserva_gabaritos_e_id_da_base(self):
        primeira = self.salvar()
        versoes = deepcopy(self.prova_x_aluno_dao.documentos)
        segunda = self.salvar()
        self.assertEqual(primeira.status_code, 200)
        self.assertEqual(segunda.status_code, 200)
        self.assertEqual(segunda.get_json()["data"]["provas_alunos_geradas"], 2)
        self.assertFalse(segunda.get_json()["data"]["versoes_regeneradas"])
        self.assertEqual(self.prova_x_aluno_dao.documentos, versoes)
        self.assertEqual(len(self.prova_dao.documentos), 1)
        self.assertEqual(segunda.get_json()["data"]["prova"]["_id"], self.id)
        self.assertEqual(self.prova_dao.documentos[self.id]["questoes"], self.ids)
        self.assertEqual(self.prova_dao.documentos[self.id]["status"], "Em elaboração")

    def test_zero_alunos_impede_envio_e_permite_recuperacao(self):
        alunos = self.aluno_dao.documentos
        self.aluno_dao.documentos = {}
        self.assertEqual(self.salvar().get_json()["data"]["provas_alunos_geradas"], 0)
        self.assertEqual(self.enviar().status_code, 409)
        self.assertEqual(self.prova_dao.documentos[self.id]["status"], "Em elaboração")
        self.aluno_dao.documentos = alunos
        self.assertEqual(self.salvar().get_json()["data"]["provas_alunos_geradas"], 2)
        self.assertEqual(self.enviar().status_code, 200)

    def test_reordenar_salva_a_ordem_e_atualiza_versoes_antes_da_conclusao(self):
        self.salvar()
        invertidas = self.ids[::-1]
        resposta = self.salvar(invertidas)
        self.assertTrue(resposta.get_json()["data"]["versoes_regeneradas"])
        self.assertEqual(self.prova_dao.documentos[self.id]["questoes"], invertidas)

    def test_rejeita_objetos_e_metadados_na_selecao(self):
        self.assertEqual(self.salvar([{"_id": self.ids[0]}]).status_code, 400)
        resposta = self.client.patch(f"/api/v1/provas/{self.id}/adicionar-questoes",
                                    json={"prova": {"questoes": self.ids, "professor": self.metadados["professor"]}})
        self.assertEqual(resposta.status_code, 400)
        self.assertEqual(self.prova_dao.documentos[self.id]["questoes"], [])

    def test_envio_e_reenvio_nao_regeneram_e_bloqueiam_edicao(self):
        self.salvar()
        versoes = deepcopy(self.prova_x_aluno_dao.documentos)
        for _ in range(2):
            resposta = self.enviar()
            self.assertEqual(resposta.status_code, 200)
            self.assertEqual(resposta.get_json()["data"]["prova"]["status"], "Enviada ao pedagógico")
        self.assertEqual(self.prova_x_aluno_dao.documentos, versoes)
        self.assertEqual(self.salvar().status_code, 409)
        self.assertEqual(self.salvar(self.ids[::-1]).status_code, 409)
        dados = {**self.metadados, "questoes": self.ids, "status": "Aguardando questões"}
        self.assertEqual(self.client.put(f"/api/v1/provas/{self.id}", json={"prova": dados}).status_code, 409)
        self.assertEqual(self.client.delete(f"/api/v1/provas/{self.id}").status_code, 409)
        self.assertEqual(self.prova_x_aluno_dao.documentos, versoes)

    def test_bloqueia_alteracao_e_exclusao_de_questao_em_prova_concluida(self):
        self.salvar()
        self.enviar()
        questao = deepcopy(self.questao_dao.documentos[self.ids[0]])
        rota = f"/api/v1/questoes/{self.ids[0]}"
        self.assertEqual(self.questao_client.put(rota, json=payload_questao(200)).status_code, 409)
        self.assertEqual(self.questao_client.delete(rota).status_code, 409)
        self.assertEqual(self.questao_dao.documentos[self.ids[0]], questao)

    def test_sem_questoes_ou_questao_incompleta_nao_conclui(self):
        self.assertEqual(self.enviar().status_code, 400)
        original = deepcopy(self.questao_dao.documentos[self.ids[0]])
        for campo, valor in [("enunciado", "<p><br></p>"), ("alternativa_correta", "inexistente"), ("alternativas", [])]:
            with self.subTest(campo=campo):
                self.questao_dao.documentos[self.ids[0]] = {**original, campo: valor}
                self.assertEqual(self.salvar().status_code, 400)
                self.assertEqual(self.prova_dao.documentos[self.id]["questoes"], [])
        self.questao_dao.documentos[self.ids[0]] = original
        self.salvar()
        self.questao_dao.documentos[self.ids[0]]["alternativa_correta"] = "inexistente"
        self.assertEqual(self.enviar().status_code, 400)

    def test_put_nao_contorna_rotas_de_selecao_e_envio(self):
        dados = {**self.metadados, "questoes": self.ids, "status": "Enviada ao pedagógico"}
        self.assertEqual(self.client.put(f"/api/v1/provas/{self.id}", json={"prova": dados}).status_code, 400)
        self.salvar()
        dados.update(questoes=self.ids, status="Em elaboração", id_turma="Turma 2026 B")
        self.assertEqual(self.client.put(f"/api/v1/provas/{self.id}", json={"prova": dados}).status_code, 409)


if __name__ == "__main__":
    unittest.main()
