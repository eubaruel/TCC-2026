import unittest
from concurrent.futures import ThreadPoolExecutor
from threading import Lock, Event
from types import SimpleNamespace
from unittest.mock import MagicMock

from api.services.correcao_service import Correcao_service


class CorrecaoTest(unittest.TestCase):
    def setUp(self):
        self.registro = {
            "_id": "000000000000000000000001", "matricula_aluno": 50280715,
            "id_prova": "000000000000000000000002",
            "questoes": [{"posicao_alternativa_correta": p} for p in (1, 4, 5)]
        }
        self.prova = {"_id": self.registro["id_prova"], "ativo": True, "tipo": "Objetiva"}
        self.provas = SimpleNamespace(buscar_por_id=MagicMock(side_effect=lambda id_: self.prova
            if self.prova and id_ == self.prova["_id"] and self.prova["ativo"] and self.prova["tipo"] == "Objetiva" else None))
        self.dados = {"qrcode": self.registro["_id"], "respostas": {
            "1": "A", "2": "D", "3": None, "4": "E"
        }}
        self.cliente = SimpleNamespace(processar=lambda imagem: self.dados, fechar=lambda: None)
        self.dao = SimpleNamespace(buscar_por_id=lambda id_: self.registro if id_ == self.registro["_id"] else None)
        self.alunos = SimpleNamespace(buscar_por_matricula=lambda _: {"nome_aluno": "Carlos Silva"})
        self.service = Correcao_service(self.cliente, self.dao, self.alunos, self.provas, concorrencia=2)
        self.addCleanup(self.service.fechar)

    @staticmethod
    def imagem(nome="cartao.png"):
        return {"arquivo": nome, "bytes": b"imagem", "content_type": "image/png"}

    def test_nota_ordem_individual_null_e_posicoes_extras(self):
        retorno = self.service.corrigir([self.imagem()])
        resultado = retorno["resultados"][0]
        self.assertEqual(resultado["nota_prova"], 6.67)
        self.assertEqual(resultado["gabarito_correto"], {"1": "A", "2": "D", "3": "E"})
        self.assertEqual(resultado["gabarito_aluno"], {"1": "A", "2": "D", "3": None})
        self.assertEqual(retorno["erros"], [])
        self.provas.buscar_por_id.assert_called_once_with(self.registro["id_prova"])

    def test_base_inexistente_inativa_ou_nao_objetiva_impede_correcao(self):
        for prova in (None, {**self.prova, "ativo": False}, {**self.prova, "tipo": "Outro"}):
            with self.subTest(prova=prova):
                self.prova = prova
                retorno = self.service.corrigir([self.imagem()])
                self.assertEqual(retorno["resultados"], [])
                self.assertEqual(retorno["erros"][0]["codigo"], 404)
                self.assertEqual(retorno["erros"][0]["mensagem"], "Prova-base não encontrada ou inativa")

    def test_registro_individual_sem_vinculo_valido_nao_e_corrigido(self):
        for id_prova in (None, "", "  ", 123, "inexistente"):
            with self.subTest(id_prova=id_prova):
                self.registro["id_prova"] = id_prova
                retorno = self.service.corrigir([self.imagem()])
                self.assertEqual(retorno["resultados"], [])
                self.assertEqual(retorno["erros"][0]["codigo"], 404)
        self.registro.pop("id_prova")
        self.assertEqual(self.service.corrigir([self.imagem()])["erros"][0]["codigo"], 404)

    def test_base_invalida_nao_interrompe_correcao_dos_outros_alunos(self):
        orfa = {**self.registro, "_id": "000000000000000000000003", "id_prova": "inexistente"}
        self.dao.buscar_por_id = lambda id_: orfa if id_ == orfa["_id"] else self.registro
        self.cliente.processar = lambda imagem: {**self.dados,
            "qrcode": orfa["_id"] if imagem["arquivo"] == "orfa.png" else self.registro["_id"]}
        retorno = self.service.corrigir([self.imagem("orfa.png"), self.imagem("valida.png")])
        self.assertEqual([resultado["indice"] for resultado in retorno["resultados"]], [1])
        self.assertEqual(retorno["resultados"][0]["nota_prova"], 6.67)
        self.assertEqual(retorno["erros"][0]["indice"], 0)
        self.assertEqual(retorno["erros"][0]["codigo"], 404)

    def test_erro_individual_nao_interrompe_lote(self):
        self.cliente.processar = lambda imagem: self.dados if imagem["arquivo"] == "ok.png" else {"qrcode": "NÃO ENCONTRADO"}
        retorno = self.service.corrigir([self.imagem("ruim.png"), self.imagem("ok.png")])
        self.assertEqual(retorno["resultados"][0]["indice"], 1)
        self.assertEqual(retorno["erros"][0]["codigo"], 422)

    def test_resposta_omitida_nao_e_tratada_como_branco(self):
        del self.dados["respostas"]["2"]
        retorno = self.service.corrigir([self.imagem()])
        self.assertEqual(retorno["resultados"], [])
        self.assertEqual(retorno["erros"][0]["codigo"], 502)

    def test_prova_com_mais_de_dez_questoes(self):
        self.registro["questoes"] = [{"posicao_alternativa_correta": 1}] * 11
        self.assertEqual(self.service.corrigir([self.imagem()])["erros"][0]["codigo"], 422)

    def test_limites_uma_e_dez_questoes(self):
        for quantidade in (1, 10):
            with self.subTest(quantidade=quantidade):
                self.registro["questoes"] = [{"posicao_alternativa_correta": 1}] * quantidade
                self.dados["respostas"] = {str(numero): "A" for numero in range(1, 11)}
                retorno = self.service.corrigir([self.imagem()])
                self.assertEqual(retorno["erros"], [])
                self.assertEqual(retorno["resultados"][0]["nota_prova"], 10)
                self.assertEqual(len(retorno["resultados"][0]["gabarito_correto"]), quantidade)

    def test_id_desconhecido(self):
        self.dados["qrcode"] = "inexistente"
        self.assertEqual(self.service.corrigir([self.imagem()])["erros"][0]["codigo"], 404)

    def test_concorrencia_compartilhada_entre_lotes(self):
        lock = Lock()
        duas_em_execucao = Event()
        liberar = Event()
        estado = {"ativos": 0, "maximo": 0}

        def processar(imagem):
            with lock:
                estado["ativos"] += 1
                estado["maximo"] = max(estado["maximo"], estado["ativos"])
                if estado["ativos"] == 2:
                    duas_em_execucao.set()
            try:
                if not liberar.wait(5):
                    raise RuntimeError("Teste de concorrência excedeu o tempo")
                return self.dados
            finally:
                with lock:
                    estado["ativos"] -= 1

        self.cliente.processar = processar
        with ThreadPoolExecutor(max_workers=2) as executor:
            lotes = [executor.submit(self.service.corrigir, [self.imagem()] * 2) for _ in range(2)]
            try:
                self.assertTrue(duas_em_execucao.wait(3))
            finally:
                liberar.set()
            retornos = [lote.result(timeout=5) for lote in lotes]
        self.assertEqual(estado["maximo"], 2)
        self.assertEqual(sum(len(r["resultados"]) for r in retornos), 4)


if __name__ == "__main__":
    unittest.main()
