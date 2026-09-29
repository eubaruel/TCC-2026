from flask import request,jsonify
from api.services.disciplina_service import Disciplina_service
from api.utils.resposta_json import Resposta_json

class Disciplina_controle:
    def __init__(self, disciplina_service:Disciplina_service):
        print("⬆️  Disciplina_controle.constructor()")
        self.__disciplina_service = disciplina_service

    def cadastrar(self):
        print("🔵 disciplina_controle.cadastrar()")

        json_disciplina = request.json.get("disciplina")
        cadastro = self.__disciplina_service.criar(json_disciplina)
        return Resposta_json.sucesso(
            mensagem = "Cadastro realizado com sucesso",
            data = {"disciplina":self._formatar_disciplina(json_disciplina)},
            codigo = 201
        )
    
    def ler(self):
        print("🔵 disciplina_controle.ler()")

        tipos = {
            "registro":int,
            "alunos":int
        }

        campos_permitidos = {"codigo_disciplina","nome_disciplina",
                            "registro","nome","turma","alunos"}
        
        filtro, erro = self._formatar_pesquisa(
            tipos = tipos,
            campos_permitidos = campos_permitidos,
            args = request.args.items()
        )

        if erro:
            return Resposta_json.erro(mensagem = erro, codigo = 400)
        
        consulta = self.__disciplina_service.consulta(filtro)

        return Resposta_json.sucesso(
            mensagem = "Executado com sucesso",
            data = {"disciplinas":consulta},
            codigo = 200
        )
    
    def alterar(self,codigo_disciplina):
        print("🔵 disciplina_controle.alterar()")

        json_disciplina = request.json.get("disciplina")
        sucesso = self.__disciplina_service.atualizar(json_disciplina, codigo_disciplina)

        if sucesso:
            return Resposta_json.sucesso(
                mensagem = "Atualizado com sucesso",
                data = {"disciplina":self._formatar_disciplina(json_disciplina)},
                codigo = 200
            )
        else:
            return Resposta_json.erro(
                mensagem = "Disciplina não encontrada",
                detalhes = f"Não foi possível atualizar a disciplina com o código {codigo_disciplina}",
                codigo = 404
            )
        
    def deletar(self, codigo_disciplina):
        print("🔵 disciplina_controle.deletar()")
        excluiu = self.__disciplina_service.excluir(codigo_disciplina)
        if excluiu:
            return Resposta_json.sucesso(
                mensagem = "Excluído com sucesso",
                codigo = 200
            )
        else:
            return Resposta_json.erro(
                mensagem = "Disciplina não encontrada",
                detalhes = f"Não existe disciplina com o código {codigo_disciplina}",
                codigo = 404
            )
    

    def _formatar_disciplina(self,disciplina):
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
    
    def _formatar_pesquisa(self,tipos,campos_permitidos,args):
        filtro = {}

        for key, value in args:
            if not value:
                continue

            if key not in campos_permitidos:
                return None, f"Parâmetro não permitido: {key}"

            conversor = tipos.get(key,str)

            try:
                if key == "registro":
                    filtro["professor.registro"] = conversor(value)
                elif key == "nome":
                    filtro["professor.nome"] = conversor(value)
                else:
                    filtro[key] = conversor(value)
            except ValueError:
                return None, f"{key} inválido: {value}"
            
        return filtro, None


