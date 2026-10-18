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
        @self.__blueprint.route('/lotes-correcao', methods=['POST'])
        def criar_lote_correcao():
            return self.__prova_controle.criar_lote_correcao()

        @self.__blueprint.route('/lotes-correcao/<string:_id>', methods=['GET'])
        def buscar_lote_correcao(_id):
            return self.__prova_controle.buscar_lote_correcao(_id)

        @self.__blueprint.route('/corrigir-provas', methods=['POST'])
        def corrigir_provas():
            return self.__prova_controle.corrigir_provas()

        @self.__blueprint.route('/criar-prova', methods=['POST'])
        @self.__prova_middleware.validar_criar_prova
        def criar_prova():
            return self.__prova_controle.criar_prova()

        @self.__blueprint.route('/<string:_id>/adicionar-questoes', methods=['PATCH'])
        @self.__prova_middleware.validar_id_prova
        @self.__prova_middleware.validar_adicionar_questoes
        def adicionar_questoes(_id):
            return self.__prova_controle.adicionar_questoes(_id)

        @self.__blueprint.route('/imprimir-provas/<string:_id>', methods=['GET'])
        @self.__prova_middleware.validar_id_prova
        def imprimir_provas(_id):
            return self.__prova_controle.imprimir_provas(_id)

        @self.__blueprint.route('/<string:_id>/enviar', methods=['PATCH'])
        @self.__prova_middleware.validar_id_prova
        def enviar(_id):
            return self.__prova_controle.enviar(_id)

        @self.__blueprint.route('/<string:_id>/confirmar-impressao', methods=['PATCH'])
        @self.__prova_middleware.validar_id_prova
        def confirmar_impressao(_id):
            return self.__prova_controle.confirmar_impressao(_id)

        @self.__blueprint.route('/',methods=['GET'])
        def ler():
            return self.__prova_controle.ler()
        
        @self.__blueprint.route('/<string:_id>', methods=['PUT'])
        @self.__prova_middleware.validar_id_prova
        def alterar(_id):
            return self.__prova_controle.alterar(_id)


        @self.__blueprint.route('/<string:_id>', methods=['DELETE'])
        @self.__prova_middleware.validar_id_prova
        def deletar(_id):
            return self.__prova_controle.deletar(_id)
        
        return self.__blueprint
