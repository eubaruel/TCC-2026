from api.modelos.prova import Prova
from bson import ObjectId
import re

class Prova_dao:
    def __init__(self, banco_de_dados_dependency):
        print("⬆️ prova_dao.init()")
        self.__banco_de_dados = banco_de_dados_dependency.get_banco_de_dados()
        self.__colecao = self.__banco_de_dados["provas"]


    def criar(self, obj_prova: Prova) -> str:
        print("✅ prova_dao.criar()")
        doc = self.set_doc(obj_prova)
        doc["ativo"] = True
        resultado = self.__colecao.insert_one(doc)
        if not resultado.inserted_id:
            raise Exception("Falha ao cadastrar prova")
        return str(resultado.inserted_id)


    def consulta(self, filtro=None) -> list:
        print("✅ prova_dao.consulta()")

        filtro = (filtro or {}).copy()
        filtro.setdefault("ativo", {"$ne": False})
        if "_id" in filtro:
            try:
                filtro["_id"] = ObjectId(filtro["_id"])
            except:
                return []

        resultado = list(self.__colecao.find(filtro, {"ativo": 0}))
        for doc in resultado:
            doc["_id"] = str(doc["_id"])
        return resultado


    def atualizar(self, obj_prova: Prova) -> bool:
        print("✅ prova_dao.atualizar()")

        _id = obj_prova.id_hash
        try:
            filtro = {"_id": ObjectId(_id), "ativo": {"$ne": False}}
        except:
            return False

        doc = {
            "$set": self.set_doc(obj_prova)
        }

        resultado = self.__colecao.update_one(filtro, doc)
        return resultado.matched_count > 0


    def excluir(self, _id) -> bool:
        print("✅ prova_dao.excluir()")

        try:
            object_id = ObjectId(_id)
        except:
            return False

        resultado = self.__colecao.update_one(
            {"_id": object_id, "ativo": {"$ne": False}},
            {"$set": {"ativo": False}}
        )

        return resultado.modified_count > 0


    def campo_existe(self, campo, valor):
        print("✅ prova_dao.campo_existe()")

        if campo == "_id":
            try:
                resultado = self.__colecao.find_one(
                    {"_id": ObjectId(valor)},
                    {"_id": 1}
                )
                return resultado is not None
            except:
                return False

        filtro = {
            campo: {
                "$regex": f"^{re.escape(valor)}$",
                "$options": "i"
            }
        }

        resultado = self.__colecao.find_one(filtro, {"_id": 1})

        return resultado is not None

    def set_doc(self, obj_prova):
        doc = {
            "id_turma":obj_prova.id_turma,
            "professor":{
                "nome":obj_prova.professor.nome
            },
            "disciplina":{
                "codigo_disciplina":obj_prova.disciplina.codigo_disciplina,
                "nome_disciplina":obj_prova.disciplina.nome_disciplina
            },
            "status":obj_prova.status,
            "tipo":obj_prova.tipo,
            "serie":obj_prova.serie,
            "bimestre":obj_prova.bimestre,
            "data_de_aplicacao":obj_prova.data_de_aplicacao,
            "questoes":obj_prova.questoes
        }

        return doc
