from flask import request,jsonify
from api.services.prova_service import Prova_service
from api.utils.resposta_json import Resposta_json

class Prova_controle:
    def __init__(self, prova_service:Prova_service):
        print("⬆️  Prova_controle.constructor()")
        self.__prova_service = prova_service

    def criar_prova(self):
        print("🔵 prova_controle.criar_prova()")
        json_prova = request.json.get("prova")
        prova_criada = self.__prova_service.criar_prova(json_prova)

        return Resposta_json.sucesso(
            mensagem = "Prova criada com sucesso",
            data = {"prova": prova_criada},
            codigo = 201
        )

    def adicionar_questoes(self, _id):
        print("🔵 prova_controle.adicionar_questoes()")

        json_prova = request.json.get("prova")
        resultado = self.__prova_service.adicionar_questoes(
            _id,
            json_prova.get("questoes")
        )

        return Resposta_json.sucesso(
            mensagem = "Questões adicionadas com sucesso",
            data = resultado,
            codigo = 200
        )

    def imprimir_provas(self, _id):
        print("🔵 prova_controle.imprimir_provas()")

        provas_alunos = self.__prova_service.imprimir_provas(_id)
        return Resposta_json.sucesso(
            mensagem = "Provas montadas com sucesso",
            data = {
                "id_prova": _id,
                "provas_alunos": provas_alunos
            },
            codigo = 200
        )
    
    
    def ler(self):
        print("🔵 prova_controle.ler()")

        tipos = {
            "serie":int,
        }

        campos_permitidos = ["id","id_turma","codigo_disciplina",
                            "nome_disciplina","nome",
                            "status","tipo","serie","bimestre",
                            "data_de_aplicacao"
                            ]
        
        filtro, erro = self._formatar_pesquisa(
            tipos = tipos,
            campos_permitidos = campos_permitidos,
            args = request.args.items()
        )

        if erro:
            return Resposta_json.erro(mensagem = erro, codigo = 400)
        
        consulta = self.__prova_service.consulta(filtro)

        return Resposta_json.sucesso(
            mensagem = "Executado com sucesso",
            data = {"provas":consulta},
            codigo = 200
        )
    
    
    def alterar(self,_id):
        print("🔵 prova_controle.alterar()")

        json_prova = request.json.get("prova")
        sucesso = self.__prova_service.atualizar(json_prova, _id)
        if sucesso:
            return Resposta_json.sucesso(
                mensagem = "Atualizado com sucesso",
                data = {"prova":self._formatar_prova(json_prova, _id)},
                codigo = 200
            )
        else:
            return Resposta_json.erro(
                mensagem = "Não foi possível atualizar a prova",
                codigo = 400
            )
        
    
    def deletar(self, _id):
        print("🔵 prova_controle.deletar()")

        excluiu = self.__prova_service.excluir(_id)
        if excluiu:
            return Resposta_json.sucesso(
                mensagem = "Excluído com sucesso",
                data = None,
                codigo = 200
            )
        else:
            return Resposta_json.erro(
                mensagem = f"Não existe prova com o id {_id}",
                codigo = 404
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

                elif key == "codigo_disciplina":
                    filtro["disciplina.codigo_disciplina"] = conversor(value)

                elif key == "nome_disciplina":
                    filtro["disciplina.nome_disciplina"] = conversor(value)

                else:
                    filtro[key] = conversor(value)
            except ValueError:
                return None, f"{key} inválido: {value}"
            
        return filtro, None
    
    def _formatar_prova(self,prova, id_hash):
        professor = prova.get("professor")
        disciplina = prova.get("disciplina")

        formatado = {
            "_id":id_hash,
            "id_turma":prova.get("id_turma"),
            "professor":{
                "nome":professor.get("nome")
            },
            "disciplina":{
                "codigo_disciplina":disciplina.get("codigo_disciplina"),
                "nome_disciplina":disciplina.get("nome_disciplina")
            },
            "status":prova.get("status"),
            "tipo":prova.get("tipo"),
            "serie":prova.get("serie"),
            "bimestre":prova.get("bimestre"),
            "data_de_aplicacao":prova.get("data_de_aplicacao"),
            "questoes":prova.get("questoes")
        }

        return formatado
