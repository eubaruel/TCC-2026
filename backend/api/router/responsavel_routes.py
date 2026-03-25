from flask import Blueprint, request
from functools import wraps

class Responsavel_routes:

    def __init__(self):
        print("⬆️  responsavel_routes.__init__()")

        self.blueprint = Blueprint('responsaveis',__name__)

    def create_routes(self):

        @self.blueprint.route('/',methods=['POST'])
        def cadastrar():
            return #self.responsavel_controle.cadastrar()
        
        @self.blueprint.route('/',methods=['GET'])
        def ler():
            return #self.responsavel_controle.ler()
        
        @self.blueprint.route('/',methods=['PUT'])
        def alterar():
            return #self.responsavel_controle.alterar()
        
        @self.blueprint.route('/',methods=['DELETE'])
        def deletar():
            return #self.responsavel_controle.deletar()