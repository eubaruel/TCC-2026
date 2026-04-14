from api.modelos.usuario import Usuario
from api.DAOs.usuario_dao import Usuario_dao

from api.utils.resposta_erro import resposta_erro

class Usuario_service:
    def __init__(self, usuario_dao_dependency: Usuario_dao):
        print("⬆️ usuario_service.__init__()")
        self.__usuario_dao = usuario_dao_dependency

    def login (self, json_usuario: dict) -> dict:
        print("🟣 usuario_service.login()")

        obj_usuario = Usuario()
        obj_usuario.registro = json_usuario.get("registro")
        senha_digitada = json_usuario.get("senha")

        usuario_db = self.__usuario_dao.login(obj_usuario)

        if not usuario_db or usuario_db is None:
            raise resposta_erro(
                401,
                "Usuário ou senha inválidos",
                {"mensagem": "Não foi possível realizar autenticação"}
            )
        
        obj_usuario.set_senha_hash(usuario_db["senha"])

        if not obj_usuario.verificar_senha(senha_digitada):
            raise resposta_erro(
                401,
                "Usuário ou senha inválidos",
                {"mensagem": "Não foi possível realizar autenticação"}
            )
        
        #FALTA A CRIAÇÃO DO TOKEN JWT
        return{
            'usuario': {
                'registro': usuario_db["registro"],
                'nome': usuario_db["nome"],
                'email':usuario_db["email"],
                'role':usuario_db["role"]
                #"token": jwt.gerarToken(usuario["usuario"])
            }
        }
        
    
    
    def criar(self, json_usuario: dict) -> bool:
        print("🟣 usuario_service.criar()")

        obj_usuario = Usuario()
        self.setar_modelo_usuario(obj_usuario, json_usuario)
        obj_usuario.senha = json_usuario.get("senha")
        obj_usuario.gerar_hash_senha()

        registro_existe = self.__usuario_dao.campo_existe("registro",obj_usuario.registro)
        if registro_existe:
            raise resposta_erro(
                400,
                "Registro repitido",
                {'mensagem':f'O funcionário com o registro {obj_usuario.registro} já está cadastrado'}
            )
        return self.__usuario_dao.criar(obj_usuario)
    
    
    def consulta(self, filtro) -> list[dict]:
        print("🟣 usuario_service.consulta()")
        return self.__usuario_dao.consulta(filtro)
    
    
    def atualizar(self, json_aluno: dict, filtro) -> bool:
        print("🟣 usuario_service.atualizar()")

        obj_usuario = Usuario()
        self.setar_modelo_usuario(obj_usuario, json_aluno)
        return self.__usuario_dao.atualizar(obj_usuario,filtro)
    
    
    def excluir(self, registro: int) -> bool:
        print("🟣 usuario_service.excluir()")
        obj_usuario = Usuario()
        obj_usuario.registro = registro
        return self.__usuario_dao.excluir(obj_usuario.registro)

    
    def setar_modelo_usuario(self, obj_usuario, json_usuario):
        obj_usuario.registro = json_usuario.get("registro")
        obj_usuario.nome = json_usuario.get("nome")
        obj_usuario.email = json_usuario.get("email")
        obj_usuario.role = json_usuario.get("role")
        obj_usuario.ativo = True