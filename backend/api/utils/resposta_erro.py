class resposta_erro(Exception):
    def __init__(self, httpCode: int, mensagem: str, erro: any = None):

        super().__init__(mensagem)
        self.__httpCode = httpCode
        self.__erro = erro

    @property
    def httpCode(self) -> int:
        return self.__httpCode

    @property
    def erro(self):
        return self.__error

    def __str__(self) -> str:
        return f"[{self.__httpCode}] {self.args[0]} | Detalhes: {self.__erro}"