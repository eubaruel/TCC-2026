from api.modelos.questao import Questao
from bson import ObjectId
import re

class Questao_dao:
    def __init__(self, banco_de_dados_dependency):
        print("⬆️  questao_dao.__init__()")
        self.__banco_de_dados = banco_de_dados_dependency.get_banco_de_dados()
        self.__colecao = self.__banco_de_dados["questoes"]

        self.__colecao.create_index(
            "enunciado",
            unique=True
        )


    def criar(self, obj_questao: Questao) -> str:
        print("✅ questao_dao.criar()")
        doc = self.set_doc(obj_questao)
        doc["ativo"] = True
        resultado = self.__colecao.insert_one(doc)
        if not resultado.inserted_id:
            raise Exception("Falha ao cadastrar questão")
        return str(resultado.inserted_id)

    
    def consulta(self, filtro=None) -> list:
        print("✅ questao_dao.consulta()")

        filtro = (filtro or {}).copy()
        filtro.setdefault("ativo", {"$ne": False})
        if "_id" in filtro:
            try:
                filtro["_id"] = ObjectId(filtro["_id"])
            except:
                return []

        if "enunciado" in filtro:
            texto = re.escape(filtro["enunciado"])
            filtro["enunciado"] = {
                "$regex": texto,
                "$options": "i"
            }

        resultado = list(self.__colecao.find(
            filtro,
            {"ativo": 0}
        ))
        for doc in resultado:
            doc["_id"] = str(doc["_id"])
        return resultado
    
    
    def atualizar(self, obj_questao: Questao) -> bool:
        print("✅ questao_dao.atualizar()")

        _id = obj_questao.id_hash

        try:
            filtro = {"_id": ObjectId(_id), "ativo": {"$ne": False}}
        except:
            return False

        doc = {
            "$set": self.set_doc(obj_questao)
        }

        resultado = self.__colecao.update_one(filtro, doc)

        return resultado.matched_count > 0
    
    
    def excluir(self, _id) -> bool:
        print("✅ questao_dao.excluir()")

        try:
            object_id = ObjectId(_id)
        except:
            return False
        resultado = self.__colecao.update_one(
            {"_id": object_id, "ativo": {"$ne": False}},
            {"$set": {"ativo": False}}
        )
        return resultado.modified_count > 0

    def campo_existe(self,campo,valor):
        print("✅ questao_dao.campo_existe()")
        filtro = {
            campo: {
                "$regex": f"^{re.escape(valor)}$",
                "$options": "i"
            }
        }
        resultado = self.__colecao.find_one(filtro, {"_id":1})

        return resultado is not None

    
    def set_doc(self,obj_questao):
        doc = {
            "assunto":obj_questao.assunto,
            "disciplina":obj_questao.disciplina,
            "tipo_questao": obj_questao.tipo_questao,
            "dificuldade":obj_questao.dificuldade,
            "autor":obj_questao.autor,
            "enunciado":obj_questao.enunciado,
            "professor":{
                "nome":obj_questao.professor.nome
            }
        }

        if doc["tipo_questao"] == "Objetiva":
            doc["alternativas"] = obj_questao.alternativas
            doc["alternativa_correta"] = obj_questao.alternativa_correta
        else:
            doc["numero_linhas"] = obj_questao.numero_linhas

        return doc
