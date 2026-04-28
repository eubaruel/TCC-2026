from api.modelos.disciplina import Disciplina

class Disciplina_dao:
    def __init__(self, banco_de_dados_dependency):
        print("⬆️  disciplina_dao.__init__()")
        self.__banco_de_dados = banco_de_dados_dependency.get_banco_de_dados()
        self.__colecao = self.__banco_de_dados["disciplinas"]

    def criar(self, obj_disciplina: Disciplina) -> bool:
        print("✅ disciplina_dao.criar()")
        doc = self.set_doc(obj_disciplina)

        resultado = self.__colecao.insert_one(doc)

        if not resultado.inserted_id:
            raise Exception("Falha ao cadastrar disciplina")
        
        return True
    

    def consulta(self, filtro=None):
        print("✅ disciplina_dao.consulta()")
        filtro = filtro or {}
        resultado = list(self.__colecao.find(filtro, {"_id": 0}))
        return resultado
    

    def atualizar(self, obj_disciplina: Disciplina, filtro=None) -> bool:
        print("✅ disciplina_dao.atualizar()")
        doc = {
            "$set": self.set_doc(obj_disciplina)
        }

        resultado = self.__colecao.update_one(filtro,doc)

        return resultado.matched_count > 0
    

    def excluir(self, codigo_disciplina) -> bool:
        print("✅ disciplina_dao.excluir()")

        filtro = {"codigo_disciplina": codigo_disciplina}

        resultado = self.__colecao.delete_one(filtro)

        return resultado.deleted_count > 0
    
    def campo_existe(self, campo, valor):
        print("✅ disciplina_dao.campo_existe()")
        filtro = {campo:valor}
        resultado = self.__colecao.find_one(filtro)

        return resultado is not None

    def set_doc(self, obj_disciplina):
        return {
            "codigo_disciplina":obj_disciplina.codigo_disciplina,
            "nome_disciplina":obj_disciplina.nome_disciplina,
            "professor":{
                "registro":obj_disciplina.professor.registro,
                "nome":obj_disciplina.professor.nome
            },
            "turma":obj_disciplina.turma,
            "alunos":obj_disciplina.alunos
        }