from functools import wraps
from flask import request
from api.utils.resposta_erro import resposta_erro

class Aluno_middleware:
    def validar_body(self,f):
        @wraps(f)
        def decorated_function(*args,**kwargs):
            print("🔷 aluno_middleware.validar_body()")
            body = request.get_json()

            if not body or 'aluno' not in body:
                raise resposta_erro(400, "Erro na validação de dados", {"mensagem": "O campo 'aluno' é obrigatório!"})
            
            aluno = body['aluno']

            campos_obrigatorios = ["matricula_aluno","nome_aluno","turma",
                                    "serie","situacao","email_aluno","ativo"]
            
            for campo in campos_obrigatorios:
                if campo not in aluno:
                    raise resposta_erro(400, "Erro na validação de dados", {"mensagem": f"O campo '{campo}' é obrigatório!"})
                
            return f(*args,**kwargs)
        return decorated_function
    
    def validar_matricula_param(self,f):
        @wraps(f)
        def decorated_function(*args,**kwargs):
            print("🔷 aluno_middleware.validar_matricula_param()")
            if 'matricula_aluno' not in kwargs:
                raise resposta_erro(400, "Erro na validação de dados", {"mensagem": "O parâmetro 'matricula_aluno' é obrigatório!"})
            return f(*args, **kwargs)
        return decorated_function
