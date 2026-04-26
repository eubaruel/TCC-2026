from api.modelos.aluno import Aluno

class Aluno_dao:
    def __init__(self, banco_de_dados_dependency):
        print("⬆️  aluno_dao.__init__()")
        self.__banco_de_dados = banco_de_dados_dependency.get_banco_de_dados()
        self.__colecao = self.__banco_de_dados["alunos"]
        

    def criar(self, obj_aluno: Aluno) -> bool:
        print("✅ aluno_dao.criar()")
        doc = self.set_doc(obj_aluno)

        resultado = self.__colecao.insert_one(doc)

        if not resultado.inserted_id:
            raise Exception("Falha ao cadastrar aluno")
        
        return True
    
    def importar_excel(self, docs: list) -> bool:
        print("✅ aluno_dao.importar_excel()")
        self.__colecao.insert_many(docs)
    
    def consulta(self, filtro=None):
        print("✅ aluno_dao.consulta()")
        filtro = filtro or {}
        resultado = list(self.__colecao.find(filtro, {"_id": 0}))
        return resultado
    
    def atualizar(self, obj_aluno: Aluno, filtro=None) -> bool:
        print("✅ aluno_dao.atualizar()")
        doc = {
            "$set": self.set_doc(obj_aluno)
        }

        resultado = self.__colecao.update_one(filtro,doc)

        return resultado.matched_count > 0
    
    def excluir(self, matricula_aluno) -> bool:
        print("✅ aluno_dao.excluir()")

        filtro = {"matricula_aluno": int(matricula_aluno)}

        doc = {
            "$set": {
                "ativo": False
            }
        }

        resultado = self.__colecao.update_one(filtro, doc)

        if resultado.matched_count == 0:
            return False  # não encontrou

        return resultado.modified_count > 0  # alterou ou não
    
    def campo_existe(self,campo,valor):
        print("✅ aluno_dao.campo_existe()")
        filtro = {campo:valor}
        resultado = self.__colecao.find_one(filtro)

        return resultado is not None
    

    def set_doc(self, obj_aluno):
        return {
            "matricula_aluno": obj_aluno.matricula_aluno,
            "nome_aluno": obj_aluno.nome_aluno,
            "turma": obj_aluno.turma,
            "serie": obj_aluno.serie,
            "situacao": obj_aluno.situacao,
            "email_aluno": obj_aluno.email_aluno,
            "ativo":obj_aluno.ativo
        }

        

