import unittest
from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import MagicMock

from api.DAOs.usuario_dao import Usuario_dao
from api.modelos.usuario import Usuario
from api.utils.usuarios_teste import inserir_usuarios_teste


class DaoTeste:
    def __init__(self):
        self.documentos = {}

    def campo_existe(self, campo, valor):
        return valor in self.documentos

    def criar_se_ausente(self, usuario):
        if usuario.registro in self.documentos:
            return False
        self.documentos[usuario.registro] = {
            "nome": usuario.nome, "email": usuario.email, "senha": usuario.senha,
            "role": usuario.role, "ativo": usuario.ativo, "deve_alterar_senha": True
        }
        return True


class UsuariosTesteTest(unittest.TestCase):
    def test_insere_dois_roles_com_hash_e_nao_duplica(self):
        dao = DaoTeste()
        self.assertEqual(inserir_usuarios_teste(dao), 2)
        self.assertEqual(dao.documentos[1]["role"], "Professor")
        self.assertEqual(dao.documentos[2]["role"], "Processo pedagógico")
        for doc in dao.documentos.values():
            modelo = Usuario()
            modelo.set_senha_hash(doc["senha"])
            self.assertTrue(modelo.verificar_senha("Teste123!"))
            self.assertNotEqual(doc["senha"], "Teste123!")
        antes = deepcopy(dao.documentos)
        self.assertEqual(inserir_usuarios_teste(dao), 0)
        self.assertEqual(dao.documentos, antes)

    def test_preserva_usuario_existente_inclusive_inativo(self):
        dao = DaoTeste()
        existente = {"nome": "Outro Usuario", "senha": "outro-hash", "ativo": False}
        dao.documentos[1] = deepcopy(existente)
        self.assertEqual(inserir_usuarios_teste(dao), 1)
        self.assertEqual(dao.documentos[1], existente)
        self.assertIn(2, dao.documentos)

    def test_dao_utiliza_set_on_insert(self):
        colecao = MagicMock()
        colecao.update_one.return_value.upserted_id = "id"
        dao = Usuario_dao(SimpleNamespace(get_banco_de_dados=lambda: {"usuarios": colecao}))
        usuario = SimpleNamespace(registro=1, nome="Professor Teste", email="p@example.com",
                                  role="Professor", ativo=True, senha="hash")
        self.assertTrue(dao.criar_se_ausente(usuario))
        args, kwargs = colecao.update_one.call_args
        self.assertEqual(args[0], {"registro": 1})
        self.assertEqual(set(args[1]), {"$setOnInsert"})
        self.assertEqual(args[1]["$setOnInsert"]["senha"], "hash")
        self.assertTrue(kwargs["upsert"])
        colecao.update_one.return_value.upserted_id = None
        self.assertFalse(dao.criar_se_ausente(usuario))
