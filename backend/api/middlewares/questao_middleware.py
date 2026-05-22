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
                
            tem_alternativas = (
                "alternativas" in questao and
                "alternativa_correta" in questao
            )

            tem_numero_linhas = "numero_linhas" in questao

            if not (tem_alternativas or tem_numero_linhas):
                raise resposta_erro_http(
                    400,
                    "Erro na validação de dados",
                    {"mensagem": "É necessário ter alternativas ou número de linhas"}
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