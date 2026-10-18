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

        if not usuario_db or not usuario_db.get("senha"):
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
                'role':usuario_db["role"],
                'deve_alterar_senha': usuario_db.get("deve_alterar_senha", True)
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

    def alterar_senha(self, registro, dados):
        alvo = Usuario()
        alvo.registro = registro
        usuario_db = self.__usuario_dao.login(alvo)
        if not usuario_db:
            raise resposta_erro_http(404, "Usuário ativo não encontrado")
        if not usuario_db.get("senha"):
            raise resposta_erro_http(409, "Usuário sem senha cadastrada; corrija o cadastro")

        redefinicao = "solicitante" in dados
        if redefinicao:
            credenciais = dados["solicitante"]
            solicitante = self.login(credenciais)["usuario"]
            if solicitante["role"] != "Processo pedagógico" or usuario_db["role"] != "Professor":
                raise resposta_erro_http(403, "Somente o processo pedagógico pode redefinir a senha de um professor")
        else:
            alvo.set_senha_hash(usuario_db["senha"])
            if not alvo.verificar_senha(dados["senha_atual"]):
                raise resposta_erro_http(401, "Senha atual inválida")

        nova_senha = Usuario()
        nova_senha.senha = dados["nova_senha"]
        alvo.set_senha_hash(usuario_db["senha"])
        if alvo.verificar_senha(nova_senha.senha):
            raise resposta_erro_http(400, "A nova senha deve ser diferente da senha atual")
        nova_senha.gerar_hash_senha()
        if not self.__usuario_dao.alterar_senha(
            registro, nova_senha.senha, redefinicao, usuario_db["senha"]
        ):
            raise resposta_erro_http(409, "O usuário foi alterado durante a operação; tente novamente")
        return {"registro": registro, "deve_alterar_senha": redefinicao}
    
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
        doc["senha"] = obj_usuario.senha
        doc["deve_alterar_senha"] = True

        return doc
