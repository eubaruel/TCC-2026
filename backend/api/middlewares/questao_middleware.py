from functools import wraps
from flask import request
from api.utils.resposta_erro_http import resposta_erro_http

class Questao_middleware:
    def validar_body(self, f):
        @wraps(f)
        def decorated_function(*args,**kwargs):
            print("🔷 questao_middleware.validar_body()")
            body = request.get_json()

            if not body or 'questao' not in body:
                raise resposta_erro_http(400, "Erro na validação de dados", {"mensagem": "O campo 'questão' é obrigatório!"})
            
            questao = body['questao']
            campos_obrigatorios = ["professor","assunto","disciplina",
                                    "tipo_questao","dificuldade",
                                    "enunciado"]

            for campo in campos_obrigatorios:
                if campo not in questao:
                    raise resposta_erro_http(400, "Erro na validação de dados", {"mensagem":f"O campo '{campo}' é obrigatório!"})
                
            tipo = str(questao.get("tipo_questao", "")).strip().title()

            if tipo == "Objetiva" and not (
                "alternativas" in questao and "alternativa_correta" in questao
            ):
                raise resposta_erro_http(
                    400,
                    "Erro na validação de dados",
                    {"mensagem": "Questão objetiva exige alternativas e alternativa correta"}
                )

            if tipo == "Objetiva" and "numero_linhas" in questao:
                raise resposta_erro_http(
                    400,
                    "Erro na validação de dados",
                    {"mensagem": "Questão objetiva não deve possuir número de linhas"}
                )

            if tipo == "Dissertativa" and "numero_linhas" not in questao:
                raise resposta_erro_http(
                    400,
                    "Erro na validação de dados",
                    {"mensagem": "Questão dissertativa exige número de linhas"}
                )

            if tipo == "Dissertativa" and (
                "alternativas" in questao or "alternativa_correta" in questao
            ):
                raise resposta_erro_http(
                    400,
                    "Erro na validação de dados",
                    {"mensagem": "Questão dissertativa não deve possuir alternativas"}
                )
                                
            professor = questao["professor"]
            campos_obrigatorios_professor = ["nome"]

            for campo_professor in campos_obrigatorios_professor:
                if campo_professor not in professor:
                    raise resposta_erro_http(400, "Erro na validação de dados", {"mensagem": f"O campo '{campo_professor}' do professor é obrigatório!"})
                
            return f(*args, **kwargs)
        return decorated_function
    
    def validar_id_questao(self,f):
        @wraps(f)
        def decorated_function(*args,**kwargs):
            print("🔷 questao_middleware.validar_id()")
            if '_id' not in kwargs:
                raise resposta_erro_http(400, "Erro na validação de dados", {"mensagem": "O parâmetro '_id' é obrigatório!"})
            return f(*args, **kwargs)
        return decorated_function
