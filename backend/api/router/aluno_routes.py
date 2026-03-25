from flask import Blueprint, request
from functools import wraps
#from backend.api.middlewares.jwt_middleware import Jwt_middleware
#from backend.api.middlewares.aluno_middleware import Aluno_middleware
#from backend.api.control.aluno_controle import Aluno_controle


class Aluno_routes:
    #def __init__(self, jwt_middleware:Jwt_middleware, aluno_middleware:Aluno_middleware, aluno_controle:Aluno_controle):
    def __init__(self):
        print("⬆️  aluno_routes.__init__()")

        #self.jwt_middleware = jwt_middleware
        #self.aluno_middleware = aluno_middleware
        #self.aluno_controle = aluno_controle

        self.blueprint = Blueprint('alunos',__name__)

    
    def create_routes(self):
        
        @self.blueprint.route('/',methods=['POST'])
        #@self.jwt_middleware.validar_token
        #@self.aluno_middleware.validar_body_criar
        def cadastrar():
            return #self.aluno_controle.cadastrar()
        
        @self.blueprint.route('/',methods=['GET'])
        def ler():
            return #self.aluno_controle.ler()
        
        @self.blueprint.route('/',methods=['PUT'])
        def alterar():
            return #self.aluno_controle.alterar()
        
        @self.blueprint.route('/',methods=['DELETE'])
        def deletar():
            return #self.aluno_controle.deletar()

    