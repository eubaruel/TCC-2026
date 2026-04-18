from functools import wraps
from flask import request
from api.utils.resposta_erro import resposta_erro

class Disciplina_middleware:
    def validar_body(self,f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            print("🔷 disciplina_middleware.validar_body()")
            body = request.get_json()

            if not body or 'disciplina' not in body:
                raise resposta_erro(400, "Erro na validação de dados", {"mensagem": "O campo 'disciplina' é obrigatório!"})
            
            disciplina = body['disciplina']
            campos_obrigatorios = ["codigo_disciplina","nome_disciplina",
                                "professor","turma","alunos"]
            
            professor = disciplina['professor']
            campos_obrigatorios_professor = ["registro", "nome"]

            for campo in campos_obrigatorios:
                if campo not in disciplina:
                    raise resposta_erro(400, "Erro na validação de dados", {"mensagem": f"O campo '{campo}' é obrigatório!"})
            
            for campo_professor in campos_obrigatorios_professor:
                if campo_professor not in professor:
                    raise resposta_erro(400, "Erro na validação de dados", {"mensagem": f"O campo '{campo_professor}' do professor é obrigatório!"})
            
            return f(*args, **kwargs)
        return decorated_function
    
    def validar_codigo_param(self,f):
        @wraps(f)
        def decorated_function(*args,**kwargs):
            print("🔷 aluno_middleware.validar_matricula_param()")
            if 'codigo_disciplina' not in kwargs:
                raise resposta_erro(400, "Erro na validação de dados", {"mensagem": "O parâmetro 'codigo_matricula' é obrigatório!"})
            return f(*args, **kwargs)
        return decorated_function