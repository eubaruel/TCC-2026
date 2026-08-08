class Conversores:
    @staticmethod
    def booleano(valor: str) -> bool:
        normalizado = valor.strip().lower()

        if normalizado in {"true", "1"}:
            return True

        if normalizado in {"false", "0"}:
            return False

        raise ValueError(f"Booleano inválido: {valor}")
