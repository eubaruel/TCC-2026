from flask import Blueprint, request
from functools import wraps

class Usuario_routes:
    def __init__(self):
        print("⬆️  usuario_routes.__init__()")

        self.blueprint = Blueprint('usuarios',__name__)

    
    def create_routes(self):

        @self.blueprint.route('/',methods=['POST'])
        def cadastrar():
            return #self.usuario_controle.cadastrar()
        
        @self.blueprint.route('/',methods=['GET'])
        def ler():
            return #self.usuario_controle.ler()
        
        @self.blueprint.route('/',methods=['PUT'])
        def alterar():
            return #self.aluno_controle.alterar()
        
        @self.blueprint.route('/',methods=['DELETE'])
        def deletar():
            return #self.aluno_controle.deletar()