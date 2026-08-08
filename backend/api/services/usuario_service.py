from api.modelos.usuario import Usuario
from api.DAOs.usuario_dao import Usuario_dao

from api.utils.resposta_erro_http import resposta_erro_http
import pandas as pd

class Usuario_service:
    def __init__(self, usuario_dao_dependency: Usuario_dao):
        print("⬆️ usuario_service.__init__()")
        self.__usuario_dao = usuario_dao_dependency

    _CAMPOS_USUARIO = [
        "nome",
        "email",
        "role"
    ]

    def login (self, json_usuario: dict) -> dict:
        print("🟣 usuario_service.login()")

        obj_usuario = Usuario()
        obj_usuario.registro = json_usuario.get("registro")
        senha_digitada = json_usuario.get("senha")

        usuario_db = self.__usuario_dao.login(obj_usuario)

        if not usuario_db or usuario_db is None:
            raise resposta_erro_http(
                401,
                "Usuário ou senha inválidos",
                {"mensagem": "Não foi possível realizar autenticação"}
            )
        
        obj_usuario.set_senha_hash(usuario_db["senha"])

        if not obj_usuario.verificar_senha(senha_digitada):
            raise resposta_erro_http(
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
        
    def importar_excel(self, df) ->int:
        print("🟣 usuario_service.importar_excel()")

        docs = []
        
        inseridos = 0

        for _, linha in df.iterrows():
            if linha.isnull().any():
                print("❌ Linha com valor nulo:", linha)
                continue
            try:
                doc = self._ler_linha(linha)

                if doc:
                    docs.append(doc)
                    inseridos += 1
                else:
                    continue

            except Exception as e:
                print(f"Erro na linha: {linha} → {e}")
                continue

        if docs:
            self.__usuario_dao.importar_excel(docs)

        return inseridos
    
    def criar(self, json_usuario: dict) -> bool:
        print("🟣 usuario_service.criar()")

        obj_usuario = Usuario()
        self._setar_modelo_usuario(obj_usuario, json_usuario)
        obj_usuario.registro = json_usuario.get("registro")
        obj_usuario.senha = json_usuario.get("senha")
        obj_usuario.gerar_hash_senha()

        registro_existe = self.__usuario_dao.campo_existe("registro",obj_usuario.registro)
        if registro_existe:
            raise resposta_erro_http(
                400,
                "Registro repetido",
                {'mensagem':f'O funcionário com o registro {obj_usuario.registro} já está cadastrado'}
            )
        return self.__usuario_dao.criar(obj_usuario)
    
    
    def consulta(self, filtro) -> list[dict]:
        print("🟣 usuario_service.consulta()")
        return self.__usuario_dao.consulta(filtro)
    
    
    def atualizar(self, json_usuario: dict, registro: int) -> bool:
        print("🟣 usuario_service.atualizar()")

        obj_usuario = Usuario()
        self._setar_modelo_usuario(obj_usuario, json_usuario, incluir_ativo=True)
        obj_usuario.registro = registro

        registro_existe = self.__usuario_dao.campo_existe("registro",obj_usuario.registro)
        if not registro_existe:
            raise resposta_erro_http(
                400,
                "Usuário não encontrado",
                {"mensagem":f"O usuário com o registro {obj_usuario.registro} não está cadastrado"}
            )
        return self.__usuario_dao.atualizar(obj_usuario)
    
    
    def excluir(self, registro: int) -> bool:
        print("🟣 usuario_service.excluir()")
        obj_usuario = Usuario()
        obj_usuario.registro = registro
        return self.__usuario_dao.excluir(obj_usuario.registro)

    
    def _setar_modelo_usuario(self, obj_usuario, json_usuario, incluir_ativo=False):
        for campo in self._CAMPOS_USUARIO:
            setattr(obj_usuario, campo, json_usuario.get(campo))
        obj_usuario.ativo = json_usuario.get("ativo") if incluir_ativo else True


    def _ler_linha(self, linha):

        obj_usuario = Usuario()

        obj_usuario.registro = int(linha["registro"])
        obj_usuario.nome = linha["nome"]
        obj_usuario.email = linha["email"]
        obj_usuario.senha = linha["senha"]
        obj_usuario.gerar_hash_senha()
        obj_usuario.role = linha["role"]
        obj_usuario.ativo = True

        if self.__usuario_dao.campo_existe("registro",obj_usuario.registro):
            return None

        doc = self.__usuario_dao.set_doc(obj_usuario)
        doc["registro"] = obj_usuario.registro

        return doc
