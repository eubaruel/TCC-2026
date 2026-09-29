import unittest

from servidor import Servidor


class ErrosServidorTest(unittest.TestCase):
    def setUp(self):
        servidor = Servidor(porta=0)
        servidor._Servidor__error_middleware()
        self.app = servidor._Servidor__app
        self.app.config["TESTING"] = False

        @self.app.get("/erro-validacao")
        def erro_validacao():
            raise ValueError("campo inválido")

        @self.app.get("/erro-interno")
        def erro_interno():
            raise RuntimeError("detalhe interno sigiloso")

        self.client = self.app.test_client()

    def test_value_error_retorna_400_padronizado(self):
        resposta = self.client.get("/erro-validacao")
        self.assertEqual(resposta.status_code, 400)
        corpo = resposta.get_json()
        self.assertFalse(corpo["sucesso"])
        self.assertEqual(corpo["mensagem"], "Dados inválidos")

    def test_erro_interno_nao_expoe_stack_ou_mensagem_original(self):
        resposta = self.client.get("/erro-interno")
        self.assertEqual(resposta.status_code, 500)
        corpo = resposta.get_json()
        serializado = str(corpo)
        self.assertNotIn("traceback", serializado.lower())
        self.assertNotIn("detalhe interno sigiloso", serializado)
        self.assertEqual(corpo["erro"]["codigo"], "INTERNAL_ERROR")


if __name__ == "__main__":
    unittest.main()
