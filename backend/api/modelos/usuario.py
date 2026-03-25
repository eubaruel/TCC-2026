import re
import bcrypt

class Usuario:
    def __init__(self):
        self.__id_hash = None
        self.__email = None
        self.__senha = None
        self.__role = None
        self.__ativo = None

    @property
    def id_hash(self):
        return self.__id_hash
    
    @id_hash.setter
    def id_hash(self,value):
        if value is None:
            raise ValueError("Id_hash nulo")
        
        if not isinstance(value, str):
            raise TypeError("Id_hash deve ser uma string")
        
        self.__id_hash = value

    
    @property
    def email(self):
        return self.__email
    
    @email.setter
    def email(self,value):
        if value is None:
            raise ValueError("Email nulo")
        
        if not isinstance(value, str):
            raise TypeError("Email deve ser uma string")
        
        value = value.strip()

        if len(value) < 5 or len(value) > 150:
            raise ValueError("Email deve ter entre 5 e 150 caracteres")
        pattern = r'^[a-zA-Z0-9][a-zA-Z0-9._%+-]{0,63}@[a-zA-Z0-9][a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern,value):
            raise ValueError("Email Inválido")
        
        self.__email = value.lower()

    
    @property
    def senha(self):
        return self.__senha
    
    @senha.setter
    def senha(self,value):
        if value is None:
            raise ValueError("Senha nula")
        
        if not isinstance(value,str):
            raise TypeError("Senha deve ser uma string")
        
        value = value.strip()

        if len(value) < 6:
            raise ValueError("Senha deve ter ao menos 6 caracteres")
        
        if not any(c.isupper() for c in value):
            raise ValueError("Senha deve conter ao menos uma letra maiúscula")
        
        if not any(c.isdigit() for c in value):
            raise ValueError("Senha deve conter ao menos um número")
        
        if not any(c in "!@#$%^&*(),.?\":{}|<>" for c in value):
            raise ValueError("Senha deve conter ao menos um caracter especial")
        
        self.__senha = value


    @property
    def role(self):
        return self.__role
    
    @role.setter
    def role(self, value):
        if value is None:
            raise ValueError("Role nulo")
    
        if not isinstance(value, str):
            raise TypeError("Role deve ser uma string")
    
        value = value.strip().lower()

        if len(value) == 0:
            raise ValueError("Role não pode ser vazio")

        roles_validos = {"admin", "professor", "aluno"}

        if value not in roles_validos:
            raise ValueError(f"Role inválido. Valores permitidos: {roles_validos}")

        self.__role = value

    
    @property
    def ativo(self):
        return self.__ativo
    
    @ativo.setter
    def ativo(self,value):
        if value is None:
            raise ValueError("Ativo nulo")
        
        if not isinstance(value,bool):
            raise TypeError("Ativo deve ser booleano")
        
        self.__ativo = value

    def to_dict(email,senha,role):
        return {
            "email":email,
            "senha":senha,
            "role":role
        }
    
    @staticmethod
    def from_dict(data):
        usuario = Usuario()
        usuario._Usuario__id_hash = data.get("id_hash")
        usuario._Usuario__email = data.get("email")
        usuario._Usuario__senha = data.get("senha")
        usuario._Usuario__role = data.get("role")