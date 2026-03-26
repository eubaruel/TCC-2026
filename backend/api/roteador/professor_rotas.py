from flask import Blueprint, request
from functools import wraps

class Professor_rotas:
    #def __init__(self, jwt_middleware:Jwt_middleware, professor_middleware:Professor_middleware, professor_controle:Professor_controle):
    def __init__(self):
        print("⬆️  professor_rotas.__init__()")

        #self.jwt_middleware = jwt_middleware
        #self.professor_middleware = professor_middleware
        #self.professor_controle = professor_controle

        self.blueprint = Blueprint('professores',__name__)


    def criar_rotas(self):

        @self.blueprint.route('/',methods=['POST'])
        def cadastrar():
            return #self.professor_controle.cadastrar()
        
        @self.blueprint.route('/',methods=['GET'])
        def ler():
            return #self.professor_controle.ler()
        
        @self.blueprint.route('/',methods=['PUT'])
        def alterar():
            return #self.professor_controle.alterar()
        
        @self.blueprint.route('/',methods=['DELETE'])
        def deletar():
            return #self.professor_controle.deletar()
        