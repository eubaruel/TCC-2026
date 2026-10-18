from functools import wraps
from flask import request
from api.utils.resposta_erro_http import resposta_erro_http

class Usuario_middleware:
    def validar_alterar_senha(self, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            body = request.get_json(silent=True)
            usuario = body.get("usuario") if isinstance(body, dict) else None
            if not isinstance(usuario, dict):
                raise resposta_erro_http(400, "O campo 'usuario' deve ser um objeto")
            permitidos = {"nova_senha", "senha_atual", "solicitante"}
            if set(usuario) - permitidos:
                raise resposta_erro_http(400, "Esta rota aceita apenas dados de alteração de senha")
            if not isinstance(usuario.get("nova_senha"), str):
                raise resposta_erro_http(400, "Informe 'nova_senha' como string")
            if ("senha_atual" in usuario) == ("solicitante" in usuario):
                raise resposta_erro_http(400, "Informe 'senha_atual' ou 'solicitante', exclusivamente")
            if "solicitante" in usuario:
                solicitante = usuario["solicitante"]
                if (not isinstance(solicitante, dict) or set(solicitante) != {"registro", "senha"}
                        or type(solicitante.get("registro")) is not int
                        or not isinstance(solicitante.get("senha"), str)):
                    raise resposta_erro_http(400, "Informe registro inteiro e senha string do solicitante")
            elif not isinstance(usuario["senha_atual"], str):
                raise resposta_erro_http(400, "Informe 'senha_atual' como string")
            return f(*args, **kwargs)
        return decorated_function

    def validar_body(self,f):
        @wraps(f)
        def decorated_function(*args,**kwargs):
            print("🔷 usuario_middleware.validar_body()")
            body = request.get_json()

            if not body or 'usuario' not in body:
                raise resposta_erro_http(400, "Erro na validação de dados", {"mensagem": "O campo 'usuario' é obrigatório!"})
            
            usuario = body['usuario']

            campos_obrigatorios = ["registro","nome","email",
                                "senha","role"]
            
            for campo in campos_obrigatorios:
                if campo not in usuario:
                    raise resposta_erro_http(400, "Erro na validação de dados", {"mensagem": f"O campo '{campo}' é obrigatório!"})
                
            return f(*args,**kwargs)
        return decorated_function
    
    def validar_body_alterar(self,f):
        @wraps(f)
        def decorated_function(*args,**kwargs):
            print("🔷 usuario_middleware.validar_body()")
            body = request.get_json()

            if not body or 'usuario' not in body:
                raise resposta_erro_http(400, "Erro na validação de dados", {"mensagem": "O campo 'usuario' é obrigatório!"})
            
            usuario = body['usuario']

            campos_obrigatorios = ["nome","email",
                                "role","ativo"]
            
            for campo in campos_obrigatorios:
                if campo not in usuario:
                    raise resposta_erro_http(400, "Erro na validação de dados", {"mensagem": f"O campo '{campo}' é obrigatório!"})
                
            return f(*args,**kwargs)
        return decorated_function
    
    def validar_login(self,f):
        @wraps(f)
        def decorated_function(*args,**kwargs):
            print("🔷 usuario_middleware.validar_login()")
            body = request.get_json()

            if not body or 'usuario' not in body:
                raise resposta_erro_http(400, "Erro na validação de dados", {"mensagem": "O campo 'usuario' é obrigatório!"})
            
            usuario = body['usuario']

            campos_obrigatorios = ["registro","senha"]

            for campo in campos_obrigatorios:
                if campo not in usuario:
                    raise resposta_erro_http(400, "Erro na validação de dados", {"mensagem": f"O campo '{campo}' é obrigatório!"})
                
            return f(*args,**kwargs)
        return decorated_function
    
    def validar_registro_param(self,f):
        @wraps(f)
        def decorated_function(*args,**kwargs):
            print("🔷 usuario_middleware.validar_registro_param()")
            if 'registro' not in kwargs:
                raise resposta_erro_http(400, "Erro na validação de dados", {"mensagem": "O parâmetro 'registro' é obrigatório!"})
            return f(*args,**kwargs)
        return decorated_function
