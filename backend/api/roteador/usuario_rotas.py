from flask import Blueprint, request
from functools import wraps
from api.controles.usuario_controle import Usuario_controle
from api.middlewares.usuario_middleware import Usuario_middleware

class Usuario_rotas:
    def __init__(self,usuario_middleware:Usuario_middleware, usuario_controle:Usuario_controle):
        print("⬆️  usuario_rotas.__init__()")
        
        self.__usuario_middleware = usuario_middleware
        self.__usuario_controle = usuario_controle

        self.__blueprint = Blueprint('usuarios',__name__)

    
    def criar_rotas(self):

        @self.__blueprint.route('/login',methods=['POST'])
        @self.__usuario_middleware.validar_login
        def login():
            return self.__usuario_controle.login()

        @self.__blueprint.route('/',methods=['POST'])
        @self.__usuario_middleware.validar_body
        def cadastrar():
            return self.__usuario_controle.cadastrar()
        
        @self.__blueprint.route('/excel',methods=['POST'])
        #@self.jwt_middleware.validar_token
        def importar():
            return self.__aluno_controle.importar()
        
        @self.__blueprint.route('/',methods=['GET'])
        def ler():
            return self.__usuario_controle.ler()
        
        @self.__blueprint.route('/',methods=['PUT'])
        @self.__usuario_middleware.validar_body_alterar
        def alterar():
            return self.__usuario_controle.alterar()
        
        #@self.__blueprint.route('/senha',methods=['PUT'])
        #@self.__usuario_middleware.validar_body_alterar
        #def alterar():
            #return self.__usuario_controle.alterarSenha()
        
        @self.__blueprint.route('/<int:registro>',methods=['DELETE'])
        @self.__usuario_middleware.validar_registro_param
        def deletar(registro):
            return self.__usuario_controle.deletar(registro)
        
        return self.__blueprint