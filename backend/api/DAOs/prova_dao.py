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
        if str(filtro.get("tipo", "Objetiva")).strip().title() != "Objetiva":
            return []
        filtro["tipo"] = "Objetiva"
        filtro.setdefault("ativo", {"$ne": False})
        if "_id" in filtro:
            try:
                filtro["_id"] = ObjectId(filtro["_id"])
            except:
                return []

        resultado = list(self.__colecao.find(filtro, {"ativo": 0, "operacao_em_andamento": 0, "geracao_pendente": 0}))
        for doc in resultado:
            doc["_id"] = str(doc["_id"])
        return resultado

    def buscar_por_id(self, _id):
        print("✅ prova_dao.buscar_por_id()")

        try:
            object_id = ObjectId(_id)
        except:
            return None

        prova = self.__colecao.find_one(
            {"_id": object_id, "ativo": {"$ne": False}, "tipo": "Objetiva"},
            {"ativo": 0, "operacao_em_andamento": 0}
        )
        if prova:
            prova["_id"] = str(prova["_id"])

        return prova

    def reservar_operacao(self, _id, token) -> bool:
        try:
            object_id = ObjectId(_id)
        except:
            return False
        resultado = self.__colecao.update_one(
            {"_id": object_id, "ativo": {"$ne": False}, "tipo": "Objetiva",
             "operacao_em_andamento": {"$exists": False}},
            {"$set": {"operacao_em_andamento": token}}
        )
        return resultado.matched_count > 0

    def liberar_operacao(self, _id, token):
        self.__colecao.update_one(
            {"_id": ObjectId(_id), "operacao_em_andamento": token},
            {"$unset": {"operacao_em_andamento": ""}}
        )

    def concluir_geracao(self, _id, token) -> bool:
        resultado = self.__colecao.update_one(
            {"_id": ObjectId(_id), "ativo": {"$ne": False},
             "status": {"$in": list(Prova.STATUS_EDITAVEIS)}, "operacao_em_andamento": token},
            {"$unset": {"geracao_pendente": ""}}
        )
        return resultado.matched_count > 0

    def atualizar_questoes(self, _id, ids_questoes, token=None, geracao_pendente=False) -> bool:
        print("✅ prova_dao.atualizar_questoes()")

        try:
            object_id = ObjectId(_id)
        except:
            return False

        campos = {"questoes": ids_questoes, "status": "Em elaboração"}
        if geracao_pendente:
            campos["geracao_pendente"] = True
        resultado = self.__colecao.update_one(
            {"_id": object_id, "ativo": {"$ne": False}, "tipo": "Objetiva",
             "status": {"$in": list(Prova.STATUS_EDITAVEIS)},
             "operacao_em_andamento": token if token else {"$exists": False}},
            {"$set": campos}
        )
        return resultado.matched_count > 0

    def enviar(self, _id, ids_questoes, token=None) -> bool:
        resultado = self.__colecao.update_one(
            {"_id": ObjectId(_id), "ativo": {"$ne": False}, "tipo": "Objetiva",
             "status": {"$in": list(Prova.STATUS_EDITAVEIS)}, "questoes": ids_questoes,
             "geracao_pendente": {"$ne": True},
             "operacao_em_andamento": token if token else {"$exists": False}},
            {"$set": {"status": Prova.STATUS_ENVIADA}}
        )
        return resultado.matched_count > 0


    def atualizar(self, obj_prova: Prova, token=None) -> bool:
        print("✅ prova_dao.atualizar()")

        _id = obj_prova.id_hash
        try:
            filtro = {"_id": ObjectId(_id), "ativo": {"$ne": False},
                      "status": {"$in": list(Prova.STATUS_EDITAVEIS)},
                      "operacao_em_andamento": token if token else {"$exists": False}}
        except:
            return False

        doc = {
            "$set": self.set_doc(obj_prova)
        }

        resultado = self.__colecao.update_one(filtro, doc)
        return resultado.matched_count > 0


    def excluir(self, _id, token=None) -> bool:
        print("✅ prova_dao.excluir()")

        try:
            object_id = ObjectId(_id)
        except:
            return False

        resultado = self.__colecao.update_one(
            {"_id": object_id, "ativo": {"$ne": False},
             "status": {"$in": list(Prova.STATUS_EDITAVEIS)},
             "operacao_em_andamento": token if token else {"$exists": False}},
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
        professor = {
            "nome":obj_prova.professor.nome
        }
        if obj_prova.professor.registro is not None:
            professor["registro"] = obj_prova.professor.registro

        doc = {
            "id_turma":obj_prova.id_turma,
            "professor":professor,
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
