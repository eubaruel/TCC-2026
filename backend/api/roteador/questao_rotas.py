from flask import Blueprint, request
from functools import wraps
#from backend.api.middlewares.jwt_middleware import Jwt_middleware
from api.middlewares.questao_middleware import Questao_middleware
from api.controles.questao_controle import Questao_controle

class Questao_rotas:
    #def __init__(self, jwt_middleware:Jwt_middleware):
    def __init__(self, questao_middleware:Questao_middleware, questao_controle:Questao_controle):
        print("⬆️  questao_rotas.__init__()")

        #self.jwt_middleware = jwt_middleware
        self.__questao_middleware = questao_middleware
        self.__questao_controle = questao_controle

        self.__blueprint = Blueprint('questoes',__name__)

    def criar_rotas(self):
        
        @self.__blueprint.route('/',methods=['POST'])
        #@self.jwt_middleware.validar_token
        @self.__questao_middleware.validar_body
        def cadastrar():
            return self.__questao_controle.cadastrar()
        
        @self.__blueprint.route('/',methods=['GET'])
        def ler():
            return self.__questao_controle.ler()
        
        @self.__blueprint.route('/<string:_id>',methods=['PUT'])
        @self.__questao_middleware.validar_id_questao
        @self.__questao_middleware.validar_body
        def alterar(_id):
            return self.__questao_controle.alterar(_id)
        
        @self.__blueprint.route('/<string:_id>',methods=['DELETE'])
        @self.__questao_middleware.validar_id_questao
        def deletar(_id):
            return self.__questao_controle.deletar(_id)
        
        return self.__blueprint