from flask import request,jsonify
from api.services.usuario_service import Usuario_service
import pandas as pd

class Usuario_controle:
    def __init__(self, usuario_service:Usuario_service):
        print("⬆️  Usuario_controle.constructor()")
        self.__usuario_service = usuario_service

    def login(self):
        print("🔵 usuario_controle.login()")

        json_usuario = request.json.get("usuario")
        resultado = self.__usuario_service.login(json_usuario)
        return jsonify({
            "successo": True,
            "mensagem":"Login efetuado com sucesso!",
            "data": resultado
        }),200
    
    def cadastrar(self):
        print("🔵 usuario_controle.cadastrar()")

        json_usuario = request.json.get("usuario")
        cadastro = self.__usuario_service.criar(json_usuario)
        return jsonify({"success":True,
                        "message":"Cadastro realizado com sucesso",
                        "data":{
                            "aluno":self._formatar_usuario(json_usuario)
                            }
                        }),201
    
    def importar(self):
        print("🔵 aluno_controle.importar()")

        arquivo = next(request.files.values(), None)
        if not arquivo:
            return jsonify({
                "sucesso":False,
                "erro":{"mensagem": "Arquivo não enviado"}
            }),400
        
        if not arquivo.filename.endswith(".xlsx"):
            return jsonify({
                "sucesso":False,
                "erro":{"mensagem": "Formato inváldo"}
            }),400
        
        df = pd.read_excel(arquivo)
        resultado = self.__usuario_service.importar_excel(df)

        return jsonify({
            "sucesso":True,
            "mensagem":"Executado com sucesso",
            "data":{"usuarios inseridos":resultado}
        }),200
    
    
    def ler(self):
        print("🔵 usuario_controle.ler()")
        
        tipos = {
            "registro":int,
            "ativo":bool
        }

        campos_permitidos = {"registro","nome","email",
                            "role","ativo"}
        
        filtro = {}

        for key, value in request.args.items():
            if key not in campos_permitidos or not value:
                continue

            conversor = tipos.get(key, str)

            try:
                filtro[key] = conversor(value)
            except ValueError:
                return jsonify({
                    "success": False,
                    "error": {"message": f"{key} inválido: {value}"}
                }), 400
            
        consulta = self.__usuario_service.consulta(filtro)

        return jsonify({
            "sucesso":True,
            "mensagem":"Executado com sucesso",
            "data":{"usuários":consulta}
        }),200
    
    def alterar(self):
        print("🔵 usuario_controle.alterar()") 

        tipos = {
            "registro":int,
        }

        campos_permitidos = {"registro","nome"}

        filtro = {}

        for key, value in request.args.items():
            if key not in campos_permitidos or not value:
                continue

            conversor = tipos.get(key, str)

            try:
                filtro[key] = conversor(value)
            except ValueError:
                return jsonify({
                    "success": False,
                    "error": {"message": f"{key} inválido: {value}"}
                }), 400

        json_usuario = request.json.get("usuario")
        sucesso = self.__usuario_service.atualizar(json_usuario, filtro)

        if sucesso:
            return jsonify({
                "sucesso": True,
                "mensagem": "Atualizado com sucesso",
                "data": {
                    "usuario":self._formatar_usuario(json_usuario)               
                }
            }), 200
        else:
            return jsonify({
                "sucesso": False,
                "erro": {"message": f"Não foi possível atualizar o usuário com o registro {json_usuario.get("registro")}"},
            }), 404
        
    #def alterarSenha(self):
        #print("🔵 usuario_controle.alterarSenha()") 

        #USUÁRIO DEVE MANDAR SENHA ATUAL E SENHA NOVA
        
    def deletar(self, registro):
        print("🔵 usuario_controle.deletar()")
        excluiu = self.__usuario_service.excluir(registro)
        if excluiu:
            return jsonify({
            "sucesso": True,
            "mensagem": "Excluído com sucesso"
        }), 204
        else:
            return jsonify({
                "sucesso": False,
                "erro": {"message": f"Não existe usuario com o registro {registro}"}
            }), 404


    def _formatar_usuario(self,usuario):
        return{
            "registro":usuario.get("registro"),
            "nome":usuario.get("nome"),
            "email":usuario.get("email"),
            "role":usuario.get("role"),
            "ativo":usuario.get("ativo")
        }