from flask import Blueprint, request
from functools import wraps
#from api.middlewares.jwt_middleware import Jwt_middleware
from api.middlewares.aluno_middleware import Aluno_middleware
from api.controles.aluno_controle import Aluno_controle


class Aluno_rotas:
    #def __init__(self, jwt_middleware:Jwt_middleware):
    def __init__(self, aluno_middleware:Aluno_middleware, aluno_controle:Aluno_controle):
        print("⬆️  aluno_rotas.__init__()")

        #self.jwt_middleware = jwt_middleware
        self.__aluno_middleware = aluno_middleware
        self.__aluno_controle = aluno_controle

        self.__blueprint = Blueprint('alunos',__name__)

    
    def criar_rotas(self):
        print("⬆️  aluno_rotas.criar_rotas()")
        
        @self.__blueprint.route('/',methods=['POST'])
        #@self.jwt_middleware.validar_token
        @self.__aluno_middleware.validar_body
        def cadastrar():
            return self.__aluno_controle.cadastrar()
        
        @self.__blueprint.route('/excel',methods=['POST'])
        #@self.jwt_middleware.validar_token
        def importar():
            return self.__aluno_controle.importar()
        
        @self.__blueprint.route('/',methods=['GET'])
        #@self.jwt_middleware.validar_token
        def ler():
            return self.__aluno_controle.ler()
        
        @self.__blueprint.route('/',methods=['PUT'])
        #@self.jwt_middleware.validar_token
        @self.__aluno_middleware.validar_body
        def alterar():
            return self.__aluno_controle.alterar()
        
        @self.__blueprint.route('/<int:matricula_aluno>',methods=['DELETE'])
        #@self.jwt_middleware.validar_token
        @self.__aluno_middleware.validar_matricula_param
        def deletar(matricula_aluno):
            return self.__aluno_controle.deletar(matricula_aluno)

        return self.__blueprint

    