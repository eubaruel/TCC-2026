from api.modelos.usuario import Usuario

class Usuario_dao:
    def __init__(self, banco_de_dados_dependency):
        print("⬆️  usuario_dao.__init__()")
        self.__banco_de_dados = banco_de_dados_dependency.get_banco_de_dados()
        self.__colecao = self.__banco_de_dados["usuarios"]


    def login(self,obj_usuario :Usuario):
        print("✅ usuario_dao.login()")

        filtro = {
            "registro":obj_usuario.registro,
            "ativo":True
        }

        usuario = self.__colecao.find_one(filtro,{"_id":0})

        if not usuario:
            print("❌ Credenciais inválidas")
            return None

        print("✅ Login realizado com sucesso")
        return usuario

    
    def criar(self, obj_usuario: Usuario) -> bool:
        print("✅ aluno_dao.criar()")
        doc = self.set_doc(obj_usuario)
        doc['senha'] = obj_usuario.senha
        doc['registro'] = obj_usuario.registro

        resultado = self.__colecao.insert_one(doc)

        if not resultado.inserted_id:
            raise Exception("Falha ao cadastrar usuário")
        
        return True
    
    
    def importar_excel(self, docs: list) -> bool:
        print("✅ usuario_dao.importar_excel()")
        self.__colecao.insert_many(docs)


    def consulta(self, filtro=None):
        print("✅ usuario_dao.consulta()")
        filtro = filtro or {}
        resultado = list(self.__colecao.find(filtro, {"_id":0, "senha":0}))
        return resultado
    
    
    def atualizar(self, obj_usuario: Usuario) -> bool:
        print("✅ usuario_dao.atualizar()")

        filtro = {"registro":obj_usuario.registro}
        doc = {
            "$set": self.set_doc(obj_usuario)
        }
        resultado = self.__colecao.update_one(filtro,doc)
        return resultado.matched_count > 0
    

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

    def set_doc(self, obj_usuario):
        return {
            "nome":obj_usuario.nome,
            "email":obj_usuario.email,
            "role":obj_usuario.role,
            "ativo":obj_usuario.ativo
        }