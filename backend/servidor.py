import os
from dotenv import load_dotenv

load_dotenv()

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from werkzeug.exceptions import HTTPException, NotFound

from api.banco_de_dados.banco_de_dados import Banco_de_dados
from api.utils.resposta_erro import resposta_erro

from api.middlewares.aluno_middleware import Aluno_middleware
from api.controles.aluno_controle import Aluno_controle
from api.services.aluno_service import Aluno_service
from api.DAOs.aluno_dao import Aluno_dao
from api.roteador.aluno_rotas import Aluno_rotas

from api.middlewares.usuario_middleware import Usuario_middleware
from api.controles.usuario_controle import Usuario_controle
from api.services.usuario_service import Usuario_service
from api.DAOs.usuario_dao import Usuario_dao
from api.roteador.usuario_rotas import Usuario_rotas

from api.middlewares.disciplina_middleware import Disciplina_middleware
from api.controles.disciplina_controle import Disciplina_controle
from api.services.disciplina_service import Disciplina_service
from api.DAOs.disciplina_dao import Disciplina_dao
from api.roteador.disciplina_rotas import Disciplina_rotas

import traceback

class Servidor:
    """
    Classe principal do servidor Flask.

    Responsável por inicializar middlewares, roteadores e gerenciar a aplicação.
    """

    def __init__(self, porta):
        # 🔹 Porta em que o servidor irá rodar
        self.__porta = porta

        self.__app = Flask(__name__, static_folder= "static", static_url_path="")

        # 🔹 Configuração de CORS (Cross-Origin Resource Sharing)
        #    Permite que clientes de outros domínios/portas acessem sua API
        #    Exemplo: permitir todos os domínios (somente para desenvolvimento)
        CORS(self.__app, resources={r"/*": {"origins": "*"}})

        # 🔹 Middlewares

        self.__aluno_middleware = Aluno_middleware()
        self.__aluno_dao = None
        self.__aluno_service = None
        self.__aluno_controle = None

        self.__usuario_middleware = Usuario_middleware()
        self.__usuario_dao = None
        self.__usuario_service = None
        self.__usuario_controle = None

        self.__disciplina_middleware = Disciplina_middleware()
        self.__disciplina_dao = None
        self.__disciplina_service = None
        self.__disciplina_controle = None

        self.__conexao_db = None

    def init(self):
        """
        Inicializa a aplicação:
        - Conexão com o banco
        - Middlewares
        - Roteadores
        """

        self.__conexao_db =  Banco_de_dados(uri=os.getenv("URI_BD"),
                                            nome_bd=os.getenv("NOME_BD"))


        self.__conexao_db.conectar()

        self.__error_middleware()

        self.__setup_aluno()

        self.__setup_usuario()

        self.__setup_disciplina()


    def __setup_aluno(self):
        """Configura o módulo Aluno (DAO, Service, Controle, Rotas)"""
        print("⬆️  Setup Aluno")

        # DAO recebe conexão global com o banco (injeção de dependência)
        self.__aluno_dao = Aluno_dao(self.__conexao_db)

        # Service recebe DAO (injeção de dependência)
        self.__aluno_service = Aluno_service(self.__aluno_dao)

        # Controle recebe Service (injeção de dependência)
        self.__aluno_controle = Aluno_controle(self.__aluno_service)

        # Router recebe Controle + Middlewares
        aluno_roteador = Aluno_rotas(
            self.__aluno_middleware,
            self.__aluno_controle
        )

        # Registra rotas da entidade Aluno
        self.__app.register_blueprint(aluno_roteador.criar_rotas(), url_prefix="/api/v1/alunos")
        print("⬆️  Rotas registradas")

    def __setup_usuario(self):
        """Configura o módulo Usuário (DAO, Service, Controle, Rotas)"""
        print("⬆️  Setup usuário")

        # DAO recebe conexão global com o banco (injeção de dependência
        self.__usuario_dao = Usuario_dao(self.__conexao_db)

        # Service recebe DAO (injeção de dependência)
        self.__usuario_service = Usuario_service(self.__usuario_dao)

        # Controle recebe Service (injeção de dependência)
        self.__usuario_controle = Usuario_controle(self.__usuario_service)

        # Router recebe Controle + Middlewares
        usuario_roteador = Usuario_rotas(
            self.__usuario_middleware,
            self.__usuario_controle
        )

        # Registra rotas da entidade Usuário
        self.__app.register_blueprint(usuario_roteador.criar_rotas(), url_prefix="/api/v1/usuarios")
        print("⬆️  Rotas registradas")


    def __setup_disciplina(self):
        """Configura o módulo Usuário (DAO, Service, Controle, Rotas)"""
        print("⬆️  Setup disciplina")

        self.__disciplina_dao = Disciplina_dao(self.__conexao_db)
        self.__disciplina_service = Disciplina_service(self.__disciplina_dao)
        self.__disciplina_controle = Disciplina_controle(self.__disciplina_service)

        disciplina_roteador = Disciplina_rotas(
            self.__disciplina_middleware,
            self.__disciplina_controle
        )

        self.__app.register_blueprint(disciplina_roteador.criar_rotas(), url_prefix="/api/v1/disciplinas")
        print("⬆️  Rotas registradas")
        

    def __error_middleware(self):
        """Middleware global de tratamento de erros"""
        @self.__app.errorhandler(Exception)
        def handle_error(error):

            # 🔹 404 - Rota ou arquivo não encontrado
            if isinstance(error, NotFound):
                return error, 404

            # 🔹 Captura ErrorResponse customizado
            if isinstance(error, resposta_erro):
                print("🟡 Server.error_middleware()")
                # Extrai stack trace como string
                stack_str = ''.join(traceback.format_exception(type(error), error, error.__traceback__))

                resposta = {
                    "success": False,
                    "error": {
                        "message": str(error),
                        "code": getattr(error, "code", None),
                        "details": getattr(error, "error", None)
                    },
                    "data": {
                        "message": "Erro tratado pela aplicação",
                        "stack": stack_str
                    }
                }
                return jsonify(resposta), error.httpCode

            # 🔹 Outros erros internos (não tratados)
            stack_str = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
            print("🟡 Server.error_middleware()")
            resposta = {
                "success": False,
                "error": {
                    "message": str(error),
                    "code": getattr(error, "code", None)
                },
                "data": {
                    "message": "Ocorreu um erro interno no servidor",
                    "stack": stack_str
                }
            }

            return jsonify(resposta), 500
        
    def run(self):
        """Inicia o servidor Flask na porta configurada"""
        print("✅ Servidor iniciado com sucesso")
        print(f"🚀 Servidor rodando em: http://127.0.0.1:{self.__porta}")
        # ⚠️ debug=False é necessário para que o errorhandler global capture exceções
        self.__app.run(port=self.__porta, debug=False)

    def close(self):
        print("❌ Conexão com o servidor encerrada")
        self.__conexao_db.fechar_conexao()