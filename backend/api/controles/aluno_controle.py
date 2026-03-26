from flask import request,jsonify
from backend.api.services.aluno_service import Aluno_service

class Aluno_controle:
    def __init__(self, aluno_service:Aluno_service):
        print("⬆️  Aluno_controle.constructor()")
        self.__aluno_service = aluno_service

    def cadastrar(self):
        print("🔵 aluno_controle.cadastrar()")

        json_aluno = request.json.get("aluno")
        cadastro = self.__aluno_service.criar(json_aluno)
        return jsonify({"success":True,
                        "message":"Cadastro realizado com sucesso",
                        "data":{
                            "aluno":self._formatar_aluno(json_aluno)
                            }
                        }),201
    
    
    def ler(self):
        print("🔵 aluno_controle.ler()")

        tipos = {
            "matricula_aluno": int,
            "serie":int
        }

        campos_permitidos = {"matricula_aluno", "nome_aluno",
                            "turma" ,"serie","situacao"}

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
    
        
        leitura = self.__aluno_service.consulta(**filtro)
        return jsonify({
            "success":True,
            "message":"Executado com sucesso",
            "data":{"alunos":leitura}
        }),200
    
    
    def alterar(self):
        print("🔵 aluno_controle.alterar()")

        json_aluno = request.json.get("aluno") 
        matricula_aluno = json_aluno.get("matricula_aluno")
        sucesso = self.__aluno_service.atualizar(json_aluno,matricula_aluno)
        
        if sucesso:
            return jsonify({
                "success": True,
                "message": "Atualizado com sucesso",
                "data": {
                    "aluno":self._formatar_aluno(json_aluno)               
                }
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": {"message": f"Não foi possível atualizar o aluno com a matricula {matricula_aluno}"},
            }), 404
    
    def deletar(self, matricula_aluno):
        print("🔵 aluno_controle.deletar()")
        excluiu = self.__aluno_service.delete(matricula_aluno)
        if excluiu:
            return jsonify({
            "success": True,
            "message": "Excluído com sucesso"
        }), 204
        else:
            return jsonify({
                "success": False,
                "error": {"message": f"Não existe aluno com a matrícula {matricula_aluno}"}
            }), 404
        
    def _formatar_aluno(self, aluno):
        return {
            "matricula_aluno": aluno.get("matricula_aluno"),
            "nome_aluno": aluno.get("nome_aluno"),
            "turma": aluno.get("turma"),
            "serie": aluno.get("serie"),
            "situacao": aluno.get("situacao"),
            "email_aluno": aluno.get("email_aluno")
        }
