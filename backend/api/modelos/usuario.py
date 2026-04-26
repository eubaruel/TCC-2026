import re
import bcrypt

class Usuario:
    def __init__(self):
        self.__registro = None
        self.__nome = None
        self.__email = None
        self.__senha = None
        self.__role = None
        self.__ativo = None

    @property
    def registro(self):
        return self.__registro

    @registro.setter
    def registro(self, value):
        if value is None:
            raise ValueError("Registro do funcionário nulo")

        if not isinstance(value, int):
            raise TypeError("Registro do funcionário deve ser um int")

        self.__registro = value

    @property
    def nome(self):
        return self.__nome

    @nome.setter
    def nome(self, value):
        if value is None:
            raise ValueError("Nome do funcionário nulo")

        if not isinstance(value, str):
            raise TypeError("Nome do funcionário deve ser uma string")

        value = value.strip().title()
        
        if len(value) < 5:
            raise ValueError("Nome do funcionário deve ter ao menos 5 caracteres")

        if len(value.split()) < 2:
            raise ValueError("Nome do funcionário deve ter ao menos um sobrenome")
        
        for n in value.split(): 
            if len(n) < 3:
                raise ValueError("Cada parte do nome deve conter ao menos 3 caracteres")

        self.__nome = value

    
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

    def set_senha_hash(self, hash_senha: str):
        self.__senha = hash_senha


    @property
    def role(self):
        return self.__role
    
    @role.setter
    def role(self, value):
        if value is None:
            raise ValueError("Role nulo")
    
        if not isinstance(value, str):
            raise TypeError("Role deve ser uma string")
    
        value = value.strip().capitalize()

        if len(value) == 0:
            raise ValueError("Role não pode ser vazio")

        roles_validos = {"Professor", "Processo pedagógico"}

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

    def gerar_hash_senha(self):
        if self.__senha is None:
            raise ValueError("Senha não definida")
        
        self.__senha = bcrypt.hashpw(
            self.__senha.encode(),
            bcrypt.gensalt()
        ).decode()

    def verificar_senha(self, senha_digitada: str) -> bool:
        if self.__senha is None:
            return False

        return bcrypt.checkpw(
            senha_digitada.encode(),
            self.__senha.encode()
        )