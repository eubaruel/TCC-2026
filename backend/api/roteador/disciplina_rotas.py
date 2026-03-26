from flask import Blueprint, request
from functools import wraps


class Disciplina_rotas:
    #def __init__(self, jwt_middleware:Jwt_middleware, aluno_middleware:Aluno_middleware, aluno_controle:Aluno_controle):
    def __init__(self):
        print("⬆️  disciplina_rotas.__init__()")

        self.blueprint = Blueprint('disciplinas',__name__)

    def criar_rotas(self):

        @self.blueprint.route('/',methods=['POST'])
        #
        #@self.disciplina_middleware.validar_body_criar
        def cadastrar():
            return #self.disciplina_controle.cadastrar()
        
        @self.blueprint.route('/',methods=['GET'])
        def ler():
            return #self.disciplina_controle.ler()
        
        @self.blueprint.route('/',methods=['PUT'])
        def alterar():
            return #self.aluno_controle.alterar()
        
        @self.blueprint.route('/',methods=['DELETE'])
        def deletar():
            return #self.aluno_controle.delete()
        
        