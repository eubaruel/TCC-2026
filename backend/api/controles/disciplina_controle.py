from flask import request,jsonify
from api.services.disciplina_service import Disciplina_service

class Disciplina_controle:
    def __init__(self, disciplina_service:Disciplina_service):
        print("⬆️  Disciplina_controle.constructor()")
        self.__disciplina_service = disciplina_service

    def cadastrar(self):
        print("🔵 disciplina_controle.cadastrar()")

        json_disciplina = request.json.get("disciplina")
        cadastro = self.__disciplina_service.criar(json_disciplina)
        return jsonify({"sucesso":True,
                        "mensagem":"Cadastro realizado com sucesso",
                        "data":{
                            "disciplina":self.formatar_disciplina(json_disciplina)
                            }
                        }),201
    
    def ler(self):
        print("🔵 disciplina_controle.ler()")

        tipos = {
            "registro":int,
            "alunos":int
        }

        campos_permitidos = {"codigo_disciplina","nome_disciplina",
                            "registro","nome","turma","alunos"}
        
        filtro = {}

        for key, value in request.args.items():
            if key not in campos_permitidos or not value:
                continue

            conversor = tipos.get(key, str)

            try:
                filtro[key] = conversor(value)
            except ValueError:
                return jsonify({
                    "sucesso": False,
                    "erro": {"mensagem": f"{key} inválido: {value}"}
                }), 400
        
        consulta = self.__disciplina_service.consulta(filtro)

        return jsonify({
            "sucesso":True,
            "mensagem":"Executado com sucesso",
            "data":{"disciplinas":consulta}
        }), 200
    
    def alterar(self):
        print("🔵 disciplina_controle.alterar()")

        campos_permitidos = {"codigo_disciplina"}

        filtro = {}

        for key, value in request.args.items():
            if key not in campos_permitidos or not value:
                return jsonify({
                "sucesso": False,
                "erro": {"mensagem": "Dado para filtragem inválido"}
            }), 404

            filtro = {"codigo_disciplina":value}
        
        json_disciplina = request.json.get("disciplina")
        sucesso = self.__disciplina_service.atualizar(json_disciplina, filtro)

        if sucesso:
            return jsonify({
                "sucesso": True,
                "mensagem": "Atualizado com sucesso",
                "data": {
                    "disciplina":self.formatar_disciplina(json_disciplina)
                }
            }), 200
        else:
            return jsonify({
                "sucesso": False,
                "erro": {"mensagem": f"Não foi atualizar a disciplina com o código {json_disciplina.get("codigo_disciplina")}"}
            }), 404
        
    def deletar(self, codigo_disciplina):
        print("🔵 disciplina_controle.deletar()")
        excluiu = self.__disciplina_service.excluir(codigo_disciplina)
        if excluiu:
            return jsonify({
                "sucesso": True,
                "mensagem": "Excluído com sucesso"
            }), 204
        else:
            return jsonify({
                "sucesso": False,
                "erro": {"mensagem": f"Não existe disciplina com o código {codigo_disciplina}"}
            }), 404
    

    #TÁ DANDO ERRADO AINDA, FALTA ARRUMAR

    def formatar_disciplina(self,disciplina):
        professor = disciplina.get("professor")
        
        formatado = {
            "codigo_disciplina":disciplina.get("codigo_disciplina"),
            "nome_disciplina":disciplina.get("nome_disciplina"),
            "turma":disciplina.get("turma"),
            "alunos":disciplina.get("alunos"),
            "professor": {
                "registro":professor.get("registro"),
                "nome":professor.get("nome")
            },
        }
        
        return formatado


