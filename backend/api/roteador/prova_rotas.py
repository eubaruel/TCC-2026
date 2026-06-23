from flask import Blueprint

from api.middlewares.prova_middleware import Prova_middleware
from api.controles.prova_controle import Prova_controle

class Prova_rotas:
    #def __init__(self, jwt_middleware:Jwt_middleware):
    def __init__(self, prova_middleware:Prova_middleware, prova_controle:Prova_controle):
        print("⬆️  prova_rotas.__init__()")

        self.__prova_middleware = prova_middleware
        self.__prova_controle = prova_controle
        
        self.__blueprint = Blueprint('provas',__name__)

    
    def criar_rotas(self):

        @self.__blueprint.route('/',methods=['POST'])
        @self.__prova_middleware.validar_body
        def cadastrar():
            return self.__prova_controle.cadastrar()
        
        @self.__blueprint.route('/',methods=['GET'])
        def ler():
            return self.__prova_controle.ler()
        
        @self.__blueprint.route('/<string:_id>', methods=['PUT'])
        @self.__prova_middleware.validar_id_prova
        @self.__prova_middleware.validar_body
        def alterar(_id):
            return self.__prova_controle.alterar(_id)


        @self.__blueprint.route('/<string:_id>', methods=['DELETE'])
        @self.__prova_middleware.validar_id_prova
        def deletar(_id):
            return self.__prova_controle.deletar(_id)
        
        return self.__blueprint