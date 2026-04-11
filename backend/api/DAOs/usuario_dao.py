from api.modelos.usuario import Usuario

class Usuario_dao:
    def __init__(self, banco_de_dados_dependency):
        print("⬆️  usuario_dao.__init__()")
        self.__banco_de_dados = banco_de_dados_dependency.get_banco_de_dados()
        self.__colecao = self.__banco_de_dados["usuarios"]

    
    def criar(self, obj_usuario: Usuario) -> bool:
        print("✅ aluno_dao.criar()")
        doc = self.set_doc(obj_usuario)

        resultado = self.__colecao.insert_one(doc)

        if not resultado.inserted_id:
            raise Exception("Falha ao cadastrar usuário")
        
        return True
    

    def consulta(self, filtro=None):
        print("✅ usuario_dao.consulta()")
        filtro = filtro or {}
        resultado = list(self.__colecao.find(filtro, {"_id":0, "senha":0}))
        return resultado
    
    def atualizar(self, obj_usuario: Usuario, filtro=None) -> bool:
        print("✅ usuario_dao.atualizar()")
        doc = {
            "$set": self.set_doc(obj_usuario)
        }

        resultado = self.__colecao.update_one(filtro,doc)

    def excluir(self, registro) -> bool:
        print("✅ usuario_dao.excluir()")

        filtro = {"registro":int(registro)}

        doc = {
            "$set":{
                "ativo":False
            }
        }

        resultado = self.__colecao.update_one(filtro, doc)

        if resultado.matched_count == 0:
            return False
        
        return resultado.modified_count > 0
    

    def campo_existe(self,campo,valor):
        print("✅ usuario_dao.campo_existe()")
        filtro = {campo:valor}
        resultado = self.__colecao.find_one(filtro)

        return resultado is not None

    def set_doc(obj_usuario):
        return {
            "registro": obj_usuario.registro,
            "nome":obj_usuario.nome,
            "email":obj_usuario.email,
            "senha":obj_usuario.senha,
            "role":obj_usuario.role,
            "ativo":obj_usuario.ativo
        }