from flask import request,jsonify
from api.services.aluno_service import Aluno_service
from api.utils.resposta_json import Resposta_json
from api.utils.verificar_arquivo import Verificar_arquivo as Arquivo
import pandas as pd

class Aluno_controle:
    def __init__(self, aluno_service:Aluno_service):
        print("⬆️  Aluno_controle.constructor()")
        self.__aluno_service = aluno_service

    def cadastrar(self):
        print("🔵 aluno_controle.cadastrar()")

        json_aluno = request.json.get("aluno")
        cadastro = self.__aluno_service.criar(json_aluno)
        return Resposta_json.sucesso(
            mensagem = "Cadastro realizado com sucesso",
            data = {"aluno":self._formatar_aluno(json_aluno)},
            codigo = 201
        )
    
    def importar(self):
        print("🔵 aluno_controle.importar()")

        arquivo = next(request.files.values(), None)

        erro = Arquivo.verificar_integridade(arquivo,".xlsx")

        if erro:
            return erro
        
        df = pd.read_excel(arquivo)
        resultado = self.__aluno_service.importar_excel(df)

        return Resposta_json.sucesso(
            mensagem = "Executado com sucesso",
            data = {"alunos inseridos": resultado},
            codigo = 200
        )
    
    
    def ler(self):
        print("🔵 aluno_controle.ler()")

        tipos = {
            "matricula_aluno": int,
            "serie":int,
            "ativo":bool
        }

        campos_permitidos = {"matricula_aluno", "nome_aluno",
                            "turma" ,"serie","situacao","ativo"}

        filtro, erro = self._formatar_pesquisa(
            tipos = tipos,
            campos_permitidos = campos_permitidos,
            args = request.args.items()
        )

        if erro:
            return Resposta_json.erro(mensagem = erro, codigo = 400)
        
        consulta = self.__aluno_service.consulta(filtro)
        
        return Resposta_json.sucesso(
            mensagem = "Executado com sucesso",
            data = {"alunos":consulta},
            codigo = 200
        )
    
    
    def alterar(self,matricula_aluno):
        print("🔵 aluno_controle.alterar()")

        json_aluno = request.json.get("aluno") 
        sucesso = self.__aluno_service.atualizar(json_aluno, matricula_aluno)
        
        if sucesso:
            return Resposta_json.sucesso(
                mensagem = "Atualizado com sucesso",
                data = {"aluno":self._formatar_aluno(json_aluno)},
                codigo = 200
            )
        else:
            return Resposta_json.erro(
                mensagem = "Aluno não encontrado",
                detalhes = f"Não foi possível atualizar o aluno com a matrícula {json_aluno.get('matricula_aluno')}",
                codigo = 404
            )
    
    def deletar(self, matricula_aluno):
        print("🔵 aluno_controle.deletar()")
        excluiu = self.__aluno_service.excluir(matricula_aluno)
        if excluiu:
            return Resposta_json.sucesso(
                mensagem = "Excluído com sucesso",
                codigo = 204
            )
        else:
            return Resposta_json.erro(
                mensagem = "Aluno não encontrado",
                detalhes = f"Não existe aluno com a matrícula {matricula_aluno}",
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
        
    def _formatar_aluno(self, aluno):
        return {
            "matricula_aluno": aluno.get("matricula_aluno"),
            "nome_aluno": aluno.get("nome_aluno"),
            "turma": aluno.get("turma"),
            "serie": aluno.get("serie"),
            "situacao": aluno.get("situacao"),
            "email_aluno": aluno.get("email_aluno"),
            "ativo":aluno.get("ativo")
        }
