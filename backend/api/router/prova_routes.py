from flask import Blueprint, request
from functools import wraps

class Prova_routes:
    #def __init__(self, jwt_middleware:Jwt_middleware, prova_middleware:Prova_middleware, prova_controle:Prova_controle):
    def __init__(self):
        print("⬆️  prova_routes.__init__()")

        self.blueprint = Blueprint('provas',__name__)

    
    def create_routes(self):

        @self.blueprint.route('/',methods=['POST'])
        def cadastrar():
            return #self.prova_controle.cadastrar()
        
        @self.blueprint.route('/',methods=['GET'])
        def ler():
            return #self.prova_controle.ler()
        
        @self.blueprint.route('/',methods=['PUT'])
        def alterar():
            return #self.prova_controle.alterar()
        
        @self.blueprint.route('/',methods=['DELETE'])
        def deletar():
            return #self.prova_controle.deletar()