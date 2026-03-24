class error_response(Exception):
    def __init__(self, httpCode: int, message: str, error: any = None):

        super().__init__(message)
        self.__httpCode = httpCode
        self.__error = error

    @property
    def httpCode(self) -> int:
        return self.__httpCode

    @property
    def error(self):
        return self.__error

    def __str__(self) -> str:
        return f"[{self.__httpCode}] {self.args[0]} | Detalhes: {self.__error}"