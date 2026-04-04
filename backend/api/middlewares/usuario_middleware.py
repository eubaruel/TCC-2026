from functools import wraps
from flask import request
from api.utils.resposta_erro import resposta_erro

class Usuario_middleware:
    def validar_body(self,f):
        @wraps(f)
        def decorated_function(*args,**kwargs):
            print("🔷 usuario_middleware.validar_body()")
            body = request.get_json()

            if not body or 'usuario' not in body:
                raise resposta_erro(400, "Erro na validação de dados", {"mensagem": "O campo 'usuario' é obrigatório!"})
            
            usuario = body['usuario']

            campos_obrigatorios = ["registro","nome","email",
                                "senha","role","ativo"]
            
            for campo in campos_obrigatorios:
                if campo not in usuario:
                    raise resposta_erro(400, "Erro na validação de dados", {"mensagem": f"O campo '{campo}' é obrigatório!"})
                
            return f(*args,**kwargs)
        return decorated_function
    
    def validar_login(self,f):
        @wraps(f)
        def decorated_function(*args,**kwargs):
            print("🔷 usuario_middleware.validar_login()")
            body = request.get_json()

            if not body or 'usuario' not in body:
                raise resposta_erro(400, "Erro na validação de dados", {"mensagem": "O campo 'usuario' é obrigatório!"})
            
            usuario = body['usuario']

            campos_obrigatorios = ["registro","senha"]

            for campo in campos_obrigatorios:
                if campo not in usuario:
                    raise resposta_erro(400, "Erro na validação de dados", {"mensagem": f"O campo '{campo}' é obrigatório!"})
                
            return f(*args,**kwargs)
        return decorated_function
    
    def validar_registro_param(self,f):
        @wraps(f)
        def decorated_function(*args,**kwargs):
            print("🔷 usuario_middleware.validar_registro_param()")
            if 'registro' not in kwargs:
                raise resposta_erro(400, "Erro na validação de dados", {"mensagem": "O parâmetro 'registro' é obrigatório!"})
            return f(*args,**kwargs)
        return decorated_function