import unittest
from types import SimpleNamespace

from bson import ObjectId

from api.DAOs.aluno_dao import Aluno_dao
from api.DAOs.disciplina_dao import Disciplina_dao
from api.DAOs.prova_dao import Prova_dao
from api.DAOs.questao_dao import Questao_dao
from api.modelos.aluno import Aluno


class ColecaoFake:
    def __init__(self, documentos=None):
        self.documentos = documentos or []
        self.projecao = None
        self.filtro = None
        self.atualizacao = None
        self.indice = None

    def create_index(self, campo, unique=False):
        self.indice = (campo, unique)

    def find(self, filtro, projecao=None):
        self.filtro = filtro
        self.projecao = projecao
        return [dict(doc) for doc in self.documentos]

    def find_one(self, filtro, projecao=None):
        self.filtro = filtro
        self.projecao = projecao
        return dict(self.documentos[0]) if self.documentos else None

    def update_one(self, filtro, atualizacao):
        self.filtro = filtro
        self.atualizacao = atualizacao
        return SimpleNamespace(matched_count=1, modified_count=1)

    def bulk_write(self, operacoes, ordered=False):
        self.operacoes = operacoes
        self.ordered = ordered
        return SimpleNamespace(upserted_count=len(operacoes), modified_count=0)


class BancoFake:
    def __init__(self, nome, colecao):
        self.nome = nome
        self.colecao = colecao

    def get_banco_de_dados(self):
        return {self.nome: self.colecao}


class DaoTest(unittest.TestCase):
    def test_busca_da_base_exige_prova_ativa_e_objetiva(self):
        colecao = ColecaoFake()
        dao = Prova_dao(BancoFake("provas", colecao))
        id_prova = str(ObjectId())
        self.assertIsNone(dao.buscar_por_id(id_prova))
        self.assertEqual(colecao.filtro, {"_id": ObjectId(id_prova), "ativo": {"$ne": False}, "tipo": "Objetiva"})
        colecao.filtro = None
        self.assertIsNone(dao.buscar_por_id("invalido"))
        self.assertIsNone(colecao.filtro)

    def test_reserva_e_liberacao_condicionam_ausencia_e_dono_da_operacao(self):
        colecao = ColecaoFake()
        dao = Prova_dao(BancoFake("provas", colecao))
        id_prova = str(ObjectId())
        self.assertTrue(dao.reservar_operacao(id_prova, "token-1"))
        self.assertEqual(colecao.filtro["operacao_em_andamento"], {"$exists": False})
        self.assertEqual(colecao.filtro["ativo"], {"$ne": False})
        self.assertEqual(colecao.atualizacao, {"$set": {"operacao_em_andamento": "token-1"}})
        dao.liberar_operacao(id_prova, "token-1")
        self.assertEqual(colecao.filtro["operacao_em_andamento"], "token-1")
        self.assertEqual(colecao.atualizacao, {"$unset": {"operacao_em_andamento": ""}})
        colecao.update_one = lambda *args: SimpleNamespace(matched_count=0)
        self.assertFalse(dao.reservar_operacao(id_prova, "token-2"))

    def test_geracao_pendente_so_e_finalizada_pelo_dono_da_reserva(self):
        colecao = ColecaoFake()
        dao = Prova_dao(BancoFake("provas", colecao))
        id_prova = str(ObjectId())
        self.assertTrue(dao.atualizar_questoes(id_prova, ["q1"], token="token-1", geracao_pendente=True))
        self.assertEqual(colecao.filtro["operacao_em_andamento"], "token-1")
        self.assertTrue(colecao.atualizacao["$set"]["geracao_pendente"])
        self.assertTrue(dao.concluir_geracao(id_prova, "token-1"))
        self.assertEqual(colecao.filtro["operacao_em_andamento"], "token-1")
        self.assertEqual(colecao.atualizacao, {"$unset": {"geracao_pendente": ""}})
        self.assertTrue(dao.enviar(id_prova, ["q1"], token="token-1"))
        self.assertEqual(colecao.filtro["geracao_pendente"], {"$ne": True})
        self.assertEqual(colecao.filtro["operacao_em_andamento"], "token-1")

    def test_escritas_sem_token_nao_alteram_uma_prova_reservada(self):
        colecao = ColecaoFake()
        dao = Prova_dao(BancoFake("provas", colecao))
        id_prova = str(ObjectId())
        for operacao in (lambda: dao.enviar(id_prova, ["q1"]),
                         lambda: dao.atualizar_questoes(id_prova, ["q1"]),
                         lambda: dao.excluir(id_prova)):
            operacao()
            self.assertEqual(colecao.filtro["operacao_em_andamento"], {"$exists": False})

    def test_envio_prova_condiciona_status_e_selecao_antes_de_bloquear(self):
        colecao = ColecaoFake()
        dao = Prova_dao(BancoFake("provas", colecao))
        ids = ["64b000000000000000000001"]
        self.assertTrue(dao.enviar(str(ObjectId()), ids))
        self.assertEqual(colecao.filtro["status"], {"$in": ["Aguardando questões", "Em elaboração"]})
        self.assertEqual(colecao.filtro["questoes"], ids)
        self.assertEqual(colecao.atualizacao, {"$set": {"status": "Enviada ao pedagógico"}})

    def test_selecao_prova_so_atualiza_status_editaveis(self):
        colecao = ColecaoFake()
        dao = Prova_dao(BancoFake("provas", colecao))
        ids = ["64b000000000000000000001"]
        self.assertTrue(dao.atualizar_questoes(str(ObjectId()), ids))
        self.assertEqual(colecao.filtro["status"], {"$in": ["Aguardando questões", "Em elaboração"]})
        self.assertEqual(colecao.atualizacao, {"$set": {"questoes": ids, "status": "Em elaboração"}})

    def test_questao_verifica_referencias_em_provas_concluidas(self):
        provas = ColecaoFake([{"_id": ObjectId()}])
        banco = SimpleNamespace(get_banco_de_dados=lambda: {"questoes": ColecaoFake(), "provas": provas})
        dao = Questao_dao(banco)
        id_questao = str(ObjectId())
        self.assertTrue(dao.usada_em_prova_concluida(id_questao))
        self.assertEqual(provas.filtro["questoes"], id_questao)
        self.assertEqual(provas.filtro["status"], {"$nin": ["Aguardando questões", "Em elaboração"]})

    def test_aluno_set_doc_inclui_matricula(self):
        aluno = Aluno()
        aluno.matricula_aluno = 12345678
        aluno.nome_aluno = "Carlos Silva"
        aluno.turma = "Turma 2026 A"
        aluno.serie = 3
        aluno.situacao = "Pre-Mat"
        aluno.email_aluno = "carlos@example.com"
        aluno.ativo = True

        dao = Aluno_dao(BancoFake("alunos", ColecaoFake()))
        self.assertEqual(dao.set_doc(aluno)["matricula_aluno"], 12345678)

    def test_questao_consulta_inclui_gabarito(self):
        colecao = ColecaoFake([{"_id": ObjectId(), "enunciado": "Teste"}])
        dao = Questao_dao(BancoFake("questoes", colecao))
        dao.consulta({})
        self.assertNotIn("alternativa_correta", colecao.projecao)
        self.assertEqual(colecao.projecao["ativo"], 0)
        self.assertEqual(colecao.filtro["tipo_questao"], "Objetiva")

    def test_prova_consulta_mantem_vetor_de_ids(self):
        colecao = ColecaoFake([{
            "_id": ObjectId(),
            "questoes": ["64b000000000000000000001"]
        }])
        dao = Prova_dao(BancoFake("provas", colecao))
        resultado = dao.consulta({})
        self.assertEqual(
            resultado[0]["questoes"],
            ["64b000000000000000000001"]
        )
        self.assertEqual(colecao.projecao["ativo"], 0)
        self.assertEqual(colecao.filtro["tipo"], "Objetiva")
        self.assertEqual(colecao.projecao["operacao_em_andamento"], 0)
        self.assertEqual(colecao.projecao["geracao_pendente"], 0)

    def test_consultas_nao_retornam_tipos_nao_objetivos(self):
        for classe, nome, campo in [
            (Questao_dao, "questoes", "tipo_questao"),
            (Prova_dao, "provas", "tipo"),
        ]:
            with self.subTest(colecao=nome):
                colecao = ColecaoFake([{"_id": ObjectId()}])
                dao = classe(BancoFake(nome, colecao))
                self.assertEqual(dao.consulta({campo: "Outro"}), [])
                self.assertIsNone(colecao.filtro)
                filtro = {campo: " objetiva "}
                dao.consulta(filtro)
                self.assertEqual(colecao.filtro[campo], "Objetiva")
                self.assertEqual(filtro[campo], " objetiva ")

    def test_questao_dao_busca_ids_ativos_em_lote(self):
        id_questao = ObjectId()
        colecao = ColecaoFake([{
            "_id": id_questao,
            "tipo_questao": "Objetiva"
        }])
        dao = Questao_dao(BancoFake("questoes", colecao))

        resultado = dao.buscar_por_ids([str(id_questao)])

        self.assertEqual(resultado[0]["_id"], str(id_questao))
        self.assertEqual(colecao.filtro["_id"], {"$in": [id_questao]})
        self.assertEqual(colecao.filtro["ativo"], {"$ne": False})
        self.assertEqual(colecao.filtro["tipo_questao"], "Objetiva")

    def test_exclusoes_de_questao_disciplina_e_prova_sao_logicas(self):
        id_valido = str(ObjectId())

        colecao_questao = ColecaoFake()
        self.assertTrue(Questao_dao(BancoFake("questoes", colecao_questao)).excluir(id_valido))
        self.assertEqual(colecao_questao.atualizacao, {"$set": {"ativo": False}})

        colecao_disciplina = ColecaoFake()
        self.assertTrue(Disciplina_dao(BancoFake("disciplinas", colecao_disciplina)).excluir("MAT"))
        self.assertEqual(colecao_disciplina.atualizacao, {"$set": {"ativo": False}})

        colecao_prova = ColecaoFake()
        self.assertTrue(Prova_dao(BancoFake("provas", colecao_prova)).excluir(id_valido))
        self.assertEqual(colecao_prova.atualizacao, {"$set": {"ativo": False}})


if __name__ == "__main__":
    unittest.main()
