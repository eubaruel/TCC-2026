from flask import Blueprint, request
from functools import wraps
#from backend.api.middlewares.jwt_middleware import Jwt_middleware
from backend.api.middlewares.aluno_middleware import Aluno_middleware
from backend.api.controles.aluno_controle import Aluno_controle


class Aluno_rotas:
    #def __init__(self, jwt_middleware:Jwt_middleware):
    def __init__(self, aluno_middleware:Aluno_middleware, aluno_controle:Aluno_controle):
        print("⬆️  aluno_rotas.__init__()")

        #self.jwt_middleware = jwt_middleware
        self.aluno_middleware = aluno_middleware
        self.aluno_controle = Aluno_controle

        self.blueprint = Blueprint('alunos',__name__)

    
    def criar_rotas(self):
        
        @self.blueprint.route('/',methods=['POST'])
        #@self.jwt_middleware.validar_token
        @self.aluno_middleware.validar_body
        def cadastrar():
            return self.aluno_controle.cadastrar()
        
        @self.blueprint.route('/',methods=['GET'])
        #@self.jwt_middleware.validar_token
        def ler():
            return self.aluno_controle.ler()
        
        @self.blueprint.route('/',methods=['PUT'])
        #@self.jwt_middleware.validar_token
        @self.aluno_middleware.validar_body
        def alterar():
            return self.aluno_controle.alterar()
        
        @self.blueprint.route('/<int:matricula_aluno>',methods=['DELETE'])
        #@self.jwt_middleware.validar_token
        @self.aluno_middleware.validar_matricula_param
        def deletar(matricula_aluno):
            return self.aluno_controle.deletar(matricula_aluno)

    