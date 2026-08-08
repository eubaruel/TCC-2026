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

    def test_prova_consulta_inclui_questoes_completas(self):
        colecao = ColecaoFake([{"_id": ObjectId(), "questoes": [{"alternativa_correta": "A"}]}])
        dao = Prova_dao(BancoFake("provas", colecao))
        dao.consulta({})
        self.assertNotIn("questoes.alternativa_correta", colecao.projecao)
        self.assertEqual(colecao.projecao["ativo"], 0)

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
