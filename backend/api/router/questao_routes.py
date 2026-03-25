from flask import Blueprint, request
from functools import wraps
#from backend.api.middlewares.jwt_middleware import Jwt_middleware
#from backend.api.middlewares.questao_middleware import Questao_middleware
#from backend.api.control.questao_controle import Questao_controle

class Questao_routes:
    #def __init__(self, jwt_middleware:Jwt_middleware, questao_middleware:Questao_middleware, questao_controle:Questao_controle):
    def __init__(self):

        #self.jwt_middleware = jwt_middleware
        #self.questao_middleware = questao_middleware
        #self.questao_controle = questao_controle

        self.blueprint = Blueprint('questoes',__name__)

    def create_routes(self):
        
        @self.blueprint.route('/',methods=['POST'])
        #@self.jwt_middleware.validar_token
        #@self.jwt_middleware.validar_body_criar
        def cadastrar():
            return #self.questao_controle.cadastrar()
        
        @self.blueprint.route('/',methods=['GET'])
        def ler():
            return #self.questao_controle.cadastrar()
        
        @self.blueprint.route('/',methods=['PUT'])
        def alterar():
            return #self.questao_controle.alterar()
        
        @self.blueprint.route('/',methods=['DELETE'])
        def deletar():
            return #self.questao_controle.deletar()