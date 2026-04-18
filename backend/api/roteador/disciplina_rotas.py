from flask import Blueprint, request
from functools import wraps

from api.middlewares.disciplina_middleware import Disciplina_middleware
from api.controles.disciplina_controle import Disciplina_controle


class Disciplina_rotas:
    #def __init__(self, jwt_middleware:Jwt_middleware):
    def __init__(self, disciplina_middleware:Disciplina_middleware, disciplina_controle:Disciplina_controle):
        print("⬆️  disciplina_rotas.__init__()")

        self.__disciplina_middleware = disciplina_middleware
        self.__disciplina_controle = disciplina_controle

        self.__blueprint = Blueprint('disciplinas',__name__)

    def criar_rotas(self):

        @self.__blueprint.route('/',methods=['POST'])
        @self.__disciplina_middleware.validar_body
        def cadastrar():
            return self.__disciplina_controle.cadastrar()
        
        @self.__blueprint.route('/',methods=['GET'])
        def ler():
            return self.__disciplina_controle.ler()
        
        @self.__blueprint.route('/',methods=['PUT'])
        @self.__disciplina_middleware.validar_body
        def alterar():
            return self.__disciplina_controle.alterar()
        
        @self.__blueprint.route('/<string:codigo_disciplina>',methods=['DELETE'])
        @self.__disciplina_middleware.validar_codigo_param
        def deletar(codigo_disciplina):
            return self.__disciplina_controle.deletar(codigo_disciplina)
        
        return self.__blueprint
        
        