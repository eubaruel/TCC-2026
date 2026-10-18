from flask import request,jsonify
from api.services.questao_service import Questao_service
from api.utils.resposta_json import Resposta_json

class Questao_controle:
    def __init__(self, questao_service:Questao_service):
        print("⬆️  Questao_controle.constructor()")
        self.__questao_service = questao_service

    def cadastrar(self):
        print("🔵 questao_controle.cadastrar()")

        json_questao = request.json.get("questao")
        questao_criada = self.__questao_service.criar(json_questao)

        return Resposta_json.sucesso(
            mensagem = "Cadastro realizado com sucesso",
            data = {"questao": questao_criada},
            codigo = 201
        )
    
    def ler(self):
        print("🔵 questao_controle.ler()")

        tipos = {"registro":int}
        
        campos_permitidos = ["id","nome",
                            "assunto","disciplina","tipo_questao",
                            "dificuldade","autor","enunciado"]

        filtro, erro = self._formatar_pesquisa(
                    tipos = tipos,
                    campos_permitidos = campos_permitidos,
                    args = request.args.items() 
                    )
        
        if erro:
            return Resposta_json.erro(mensagem = erro, codigo = 400)
        
        consulta = self.__questao_service.consulta(filtro)

        return Resposta_json.sucesso(
            mensagem = "Executado com sucesso",
            data = {"questoes":consulta},
            codigo = 200
        )
    
    def alterar(self,_id):
        print("🔵 questao_controle.alterar()")

        json_questao = request.json.get("questao")
        questao_atualizada = self.__questao_service.atualizar(json_questao, _id)

        if questao_atualizada:
            return Resposta_json.sucesso(
                mensagem = "Atualizado com sucesso",
                data = {"questao": questao_atualizada},
                codigo = 200
            )
        else:
            return Resposta_json.erro(
                mensagem = f"Não foi possível atualizar a questão",
                codigo = 400
            )
        
    def deletar(self, _id):
        print("🔵 questao_controle.deletar()")
        
        excluiu = self.__questao_service.excluir(_id)
        if excluiu:
            return Resposta_json.sucesso(
                mensagem = "Excluído com sucesso",
                data = None,
                codigo = 200
            )
        else:
            return Resposta_json.erro(
                mensagem = f"Não existe questão com o id {_id}",
                codigo =  404
            )

        

    def _formatar_pesquisa(self,tipos,campos_permitidos,args):
        filtro = {}

        for key, value in args:
            if not value:
                continue

            if key not in campos_permitidos:
                return None, f"Parâmetro não permitido: {key}"

            conversor = tipos.get(key,str)

            try:
                if key == "id":
                    filtro["_id"] = value
                elif key == "nome":
                    filtro["professor.nome"] = conversor(value)
                else:
                    filtro[key] = conversor(value)
            except ValueError:
                return None, f"{key} inválido: {value}"
            
        return filtro, None
