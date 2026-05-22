from flask import request,jsonify
from api.services.usuario_service import Usuario_service
from api.utils.resposta_json import Resposta_json
from api.utils.verificar_arquivo import Verificar_arquivo as Arquivo
import pandas as pd

class Usuario_controle:
    def __init__(self, usuario_service:Usuario_service):
        print("⬆️  Usuario_controle.constructor()")
        self.__usuario_service = usuario_service

    def login(self):
        print("🔵 usuario_controle.login()")

        json_usuario = request.json.get("usuario")
        resultado = self.__usuario_service.login(json_usuario)
        return Resposta_json.sucesso(
            mensagem = "Login efetuado com sucesso!",
            data = resultado,
            codigo = 200
        )
    
    def cadastrar(self):
        print("🔵 usuario_controle.cadastrar()")

        json_usuario = request.json.get("usuario")
        cadastro = self.__usuario_service.criar(json_usuario)
        return Resposta_json.sucesso(
            mensagem = "Cadastro realizado com sucesso",
            data = {"usuario":self._formatar_usuario(json_usuario)},
            codigo = 201
        )
    
    def importar(self):
        print("🔵 aluno_controle.importar()")

        arquivo = next(request.files.values(), None)
        erro = Arquivo.verificar_integridade(arquivo,".xlsx")

        if erro:
            return erro
        
        df = pd.read_excel(arquivo)
        resultado = self.__usuario_service.importar_excel(df)

        return Resposta_json.sucesso(
            mensagem = "Executado com sucesso",
            data = {"usuarios inseridos": resultado},
            codigo = 200
        )
    
    
    def ler(self):
        print("🔵 usuario_controle.ler()")
        
        tipos = {
            "registro":int,
            "ativo":bool
        }

        campos_permitidos = {"registro","nome","email",
                            "role","ativo"}
        
        filtro, erro = self._formatar_pesquisa(
            tipos = tipos,
            campos_permitidos = campos_permitidos,
            args = request.args.items()
        )

        if erro:
            return Resposta_json.erro(
                mensagem = "Parâmetro de pesquisa inválido",
                detalhes = erro,
                codigo = 400)
            
        consulta = self.__usuario_service.consulta(filtro)

        return Resposta_json.sucesso(
            mensagem = "Executado com sucesso",
            data = {"usuarios" : consulta},
            codigo = 200
        )
    
    
    def alterar(self, registro):
        print("🔵 usuario_controle.alterar()") 

        json_usuario = request.json.get("usuario")
        sucesso = self.__usuario_service.atualizar(json_usuario, registro)

        if sucesso:
            return Resposta_json.sucesso(
                mensagem = "Atualizado com sucesso",
                data = {"usuario":self._formatar_usuario(json_usuario)},
                codigo = 200
            )
        else:
            return Resposta_json.erro(
                mensagem = "Alteração de dados falhou",
                detalhes = f"Não foi possível atualizar o usuário com o registro {json_usuario.get('registro')}",
                codigo = 404
            )

        
    #def alterarSenha(self):
        #print("🔵 usuario_controle.alterarSenha()") 

        #USUÁRIO DEVE MANDAR SENHA ATUAL E SENHA NOVA
        
    def deletar(self, registro):
        print("🔵 usuario_controle.deletar()")
        excluiu = self.__usuario_service.excluir(registro)
        if excluiu:
            return Resposta_json.sucesso(
                mensagem = "Excluído com sucesso",
                codigo = 204
            )
        else:
            return Resposta_json.erro(
                mensagem = "Não foi possível desativar o usuário",
                detalhes = f"Não existe usuario com o registro {registro}",
                codigo = 404
            )
        

    def _formatar_pesquisa(self,tipos,campos_permitidos,args):
        filtro = {}

        for key, value in args:
            if key not in campos_permitidos or not value:
                continue

            conversor = tipos.get(key,str)

            try:
                filtro[key] = conversor(value)
            except ValueError:
                return None, f"{key} inválido: {value}"
            
        return filtro, None
    


    def _formatar_usuario(self,usuario):
        return{
            "registro":usuario.get("registro"),
            "nome":usuario.get("nome"),
            "email":usuario.get("email"),
            "role":usuario.get("role"),
            "ativo":usuario.get("ativo")
        }