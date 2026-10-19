import unittest
from copy import deepcopy
from concurrent.futures import ThreadPoolExecutor
from threading import Lock, Event
from types import SimpleNamespace
from unittest.mock import MagicMock

from api.services.correcao_service import Correcao_service
from api.utils.resposta_erro_http import resposta_erro_http


class CorrecaoTest(unittest.TestCase):
    def setUp(self):
        self.registro = {
            "_id": "000000000000000000000001", "matricula_aluno": 50280715,
            "id_prova": "000000000000000000000002",
            "questoes": [{"posicao_alternativa_correta": p} for p in (1, 4, 5)]
        }
        self.prova = {"_id": self.registro["id_prova"], "ativo": True, "tipo": "Objetiva"}
        self.provas = SimpleNamespace(marcar_corrigida=MagicMock(side_effect=self._marcar_corrigida), buscar_por_id=MagicMock(side_effect=lambda id_: self.prova
            if self.prova and id_ == self.prova["_id"] and self.prova["ativo"] and self.prova["tipo"] == "Objetiva" else None))
        self.dados = {"qrcode": self.registro["_id"], "respostas": {
            "1": "A", "2": "D", "3": None, "4": "E"
        }}
        self.cliente = SimpleNamespace(processar=lambda imagem: self.dados, fechar=lambda: None)
        self.registros = {self.registro["_id"]: self.registro}
        self.dao = SimpleNamespace(buscar_por_id=lambda id_: deepcopy(self.registros.get(id_)),
                                   salvar_correcao=MagicMock(side_effect=self._salvar_correcao),
                                   registrar_tentativa_correcao=MagicMock(side_effect=self._registrar_tentativa),
                                   contar_correcoes=self._contar_correcoes)
        self.alunos = SimpleNamespace(buscar_por_matricula=lambda _: {"nome_aluno": "Carlos Silva", "turma": "3A"})
        self.service = Correcao_service(self.cliente, self.dao, self.alunos, self.provas, concorrencia=2)
        self.addCleanup(self.service.fechar)

    def _marcar_corrigida(self, id_prova):
        if self.prova["_id"] == id_prova and self.prova.get("status") == "Impressa":
            self.prova["status"] = "Corrigida"
            return True
        return False

    def _registrar_tentativa(self, registro, tentativa):
        atual = self.registros.get(registro["_id"])
        if not atual or atual["id_prova"] != registro["id_prova"] or atual["questoes"] != registro["questoes"]:
            return False
        atual["tentativa_correcao"] = deepcopy(tentativa)
        return True

    def _salvar_correcao(self, registro, correcao):
        if not self._registrar_tentativa(registro, {"sucesso": True, "concluida_em": correcao["corrigida_em"]}):
            return False
        self.registros[registro["_id"]]["correcao"] = deepcopy(correcao)
        return True

    def _contar_correcoes(self, id_prova):
        versoes = [r for r in self.registros.values() if r["id_prova"] == id_prova]
        return {"total": len(versoes), "processadas": sum("tentativa_correcao" in r or "correcao" in r for r in versoes)}

    @staticmethod
    def imagem(nome="cartao.png"):
        return {"arquivo": nome, "bytes": b"imagem", "content_type": "image/png"}

    def test_quantidade_da_base_deve_corresponder_a_versao_do_aluno(self):
        self.prova.update(quantidade_questoes=3, questoes=["q1", "q2", "q3"])
        self.assertEqual(len(self.service.corrigir([self.imagem()])["resultados"]), 1)
        self.prova["quantidade_questoes"] = 4
        retorno = self.service.corrigir([self.imagem()])
        self.assertEqual(retorno["resultados"], [])
        self.assertEqual(retorno["erros"][0]["codigo"], 422)
        self.prova["quantidade_questoes"] = 3
        self.prova["questoes"].pop()
        self.assertEqual(self.service.corrigir([self.imagem()])["erros"][0]["codigo"], 422)

    def test_correcao_bem_sucedida_marca_somente_a_base_impressa(self):
        self.prova["status"] = "Impressa"
        retorno = self.service.corrigir([self.imagem()])
        self.assertEqual(len(retorno["resultados"]), 1)
        self.assertEqual(retorno["erros"], [])
        self.provas.marcar_corrigida.assert_called_once_with(self.registro["id_prova"])

    def _adicionar_versao(self, numero=3, id_prova=None):
        versao = {**deepcopy(self.registro), "_id": f"{numero:024x}", "matricula_aluno": numero,
                  "id_prova": id_prova or self.registro["id_prova"]}
        versao.pop("correcao", None)
        versao.pop("tentativa_correcao", None)
        self.registros[versao["_id"]] = versao
        return versao

    def test_status_aguarda_todas_as_versoes_entre_envios_e_instancias(self):
        self.prova["status"] = "Impressa"
        segunda = self._adicionar_versao()
        self.service.corrigir([self.imagem()])
        self.assertEqual(self._contar_correcoes(self.registro["id_prova"]), {"total": 2, "processadas": 1})
        self.assertEqual(self.prova["status"], "Impressa")
        self.provas.marcar_corrigida.assert_not_called()
        # Outro processo/serviço consulta a contagem persistida, em vez de um contador em memória.
        outro = Correcao_service(self.cliente, self.dao, self.alunos, self.provas)
        self.addCleanup(outro.fechar)
        self.dados["qrcode"] = segunda["_id"]
        self.dados["respostas"] = {}
        retorno = outro.corrigir([self.imagem()])
        self.assertEqual(len(retorno["erros"]), 1)
        self.assertEqual(self.prova["status"], "Corrigida")
        self.assertFalse(segunda["tentativa_correcao"]["sucesso"])
        self.provas.marcar_corrigida.assert_called_once_with(self.registro["id_prova"])

    def test_reenvios_da_mesma_versao_nao_completam_o_total(self):
        self.prova["status"] = "Impressa"
        self._adicionar_versao()
        for _ in range(3):
            self.service.corrigir([self.imagem()])
        self.dados["respostas"] = {}
        self.service.corrigir([self.imagem()])
        self.assertEqual(self._contar_correcoes(self.registro["id_prova"]), {"total": 2, "processadas": 1})
        self.assertEqual(self.prova["status"], "Impressa")
        self.provas.marcar_corrigida.assert_not_called()

    def test_todas_as_tentativas_com_falha_tambem_completam_a_base(self):
        self.prova["status"] = "Impressa"
        segunda = self._adicionar_versao()
        self.cliente.processar = MagicMock(side_effect=resposta_erro_http(502, "Leitor indisponível"))
        for registro in (self.registro, segunda):
            self.service.corrigir([{**self.imagem(), "id_prova_aluno": registro["_id"]}])
        self.assertEqual(self.prova["status"], "Corrigida")
        self.assertTrue(all(r["tentativa_correcao"]["sucesso"] is False for r in self.registros.values()))
        self.assertTrue(all("correcao" not in r for r in self.registros.values()))

    def test_falha_sem_identificacao_nao_conta_por_associacao_ao_lote(self):
        self.prova["status"] = "Impressa"
        self._adicionar_versao()
        self.cliente.processar = lambda imagem: self.dados if imagem["arquivo"] == "ok.png" else {"qrcode": "NÃO ENCONTRADO"}
        self.service.corrigir([self.imagem("ok.png"), self.imagem("sem-qr.png")])
        self.assertEqual(self.prova["status"], "Impressa")
        self.assertEqual(self._contar_correcoes(self.registro["id_prova"])["processadas"], 1)

    def test_versoes_de_outra_base_nao_entram_na_contagem(self):
        self.prova["status"] = "Impressa"
        outra = self._adicionar_versao(id_prova="000000000000000000000099")
        self.service.corrigir([self.imagem()])
        self.assertEqual(self.prova["status"], "Corrigida")
        self.assertNotIn("tentativa_correcao", outra)

    def test_correcao_anterior_sem_marcador_continua_contando(self):
        self.prova["status"] = "Impressa"
        anterior = self._adicionar_versao()
        anterior["correcao"] = {"id_correcao": "anterior"}
        self.service.corrigir([self.imagem()])
        self.assertEqual(self.prova["status"], "Corrigida")

    def test_falha_na_persistencia_da_tentativa_nao_completa_a_base(self):
        self.prova["status"] = "Impressa"
        self.dados["respostas"] = {}
        self.dao.registrar_tentativa_correcao.side_effect = RuntimeError("Banco indisponível")
        with self.assertLogs(level="ERROR"):
            self.service.corrigir([self.imagem()])
        self.assertEqual(self.prova["status"], "Impressa")
        self.assertNotIn("tentativa_correcao", self.registro)

    def test_versao_alterada_durante_falha_nao_recebe_tentativa_antiga(self):
        self.prova["status"] = "Impressa"

        def buscar_aluno(_):
            self.registro["questoes"] = [{"posicao_alternativa_correta": 2}]
            return None

        self.alunos.buscar_por_matricula = buscar_aluno
        self.service.corrigir([self.imagem()])
        self.assertEqual(self.prova["status"], "Impressa")
        self.assertNotIn("tentativa_correcao", self.registro)

    def test_fila_ocupada_nao_registra_tentativa_que_nao_foi_processada(self):
        self.prova["status"] = "Impressa"
        self.service._vagas = MagicMock()
        self.service._vagas.acquire.return_value = False
        retorno = self.service.corrigir([{**self.imagem(), "id_prova_aluno": self.registro["_id"]}])
        self.assertEqual(retorno["erros"][0]["codigo"], 503)
        self.dao.registrar_tentativa_correcao.assert_not_called()
        self.provas.marcar_corrigida.assert_not_called()

    def test_base_sem_versoes_nao_e_marcada_por_contagem_zero(self):
        self.prova["status"] = "Impressa"
        self.dao.contar_correcoes = lambda _: {"total": 0, "processadas": 0}
        self.service.corrigir([self.imagem()])
        self.provas.marcar_corrigida.assert_not_called()

    def test_conclusoes_concorrentes_contam_cada_registro_uma_vez(self):
        self.prova["status"] = "Impressa"
        segunda = self._adicionar_versao()
        self.cliente.processar = lambda imagem: {**self.dados, "qrcode": imagem["id_prova_aluno"]}
        imagens = [{**self.imagem(), "id_prova_aluno": registro["_id"]} for registro in (self.registro, segunda)]
        with ThreadPoolExecutor(max_workers=2) as executor:
            retornos = list(executor.map(lambda imagem: self.service.corrigir([imagem]), imagens))
        self.assertTrue(all(not r["erros"] for r in retornos))
        self.assertEqual(self._contar_correcoes(self.registro["id_prova"]), {"total": 2, "processadas": 2})
        self.assertEqual(self.prova["status"], "Corrigida")

    def test_outros_status_nao_sao_alterados_e_falha_identificada_conta_como_tentativa(self):
        for status in ("Aguardando questões", "Em elaboração", "Enviada ao pedagógico", "Corrigida"):
            self.prova["status"] = status
            self.assertEqual(len(self.service.corrigir([self.imagem()])["resultados"]), 1)
        self.provas.marcar_corrigida.assert_not_called()
        self.prova["status"] = "Impressa"
        self.dados["respostas"] = {}
        self.assertEqual(len(self.service.corrigir([self.imagem()])["erros"]), 1)
        self.provas.marcar_corrigida.assert_called_once_with(self.registro["id_prova"])
        self.assertFalse(self.registro["tentativa_correcao"]["sucesso"])

    def test_lote_parcial_muda_base_impressa_apos_sucesso_sem_ocultar_falhas(self):
        self.prova["status"] = "Impressa"
        self.cliente.processar = lambda imagem: self.dados if imagem["arquivo"] == "ok.png" else {"qrcode": "NÃO ENCONTRADO"}
        retorno = self.service.corrigir([self.imagem("ruim.png"), self.imagem("ok.png")])
        self.assertEqual([item["indice"] for item in retorno["resultados"]], [1])
        self.assertEqual([item["indice"] for item in retorno["erros"]], [0])
        self.provas.marcar_corrigida.assert_called_once_with(self.registro["id_prova"])

    def test_falha_ao_salvar_status_nao_anuncia_correcao_confirmada(self):
        self.prova["status"] = "Impressa"
        self.provas.marcar_corrigida.side_effect = RuntimeError("Banco indisponível")
        with self.assertLogs(level="ERROR"):
            retorno = self.service.corrigir([self.imagem()])
        self.assertEqual(retorno["resultados"], [])
        self.assertEqual(retorno["erros"][0]["codigo"], 500)

    def test_nota_ordem_individual_null_e_posicoes_extras(self):
        retorno = self.service.corrigir([self.imagem()])
        resultado = retorno["resultados"][0]
        self.assertEqual(resultado["nota_prova"], 6.67)
        self.assertEqual(resultado["gabarito_correto"], {"1": "A", "2": "D", "3": "E"})
        self.assertEqual(resultado["gabarito_aluno"], {"1": "A", "2": "D", "3": None})
        self.assertEqual(retorno["erros"], [])
        self.provas.buscar_por_id.assert_called_once_with(self.registro["id_prova"])
        self.dao.salvar_correcao.assert_called_once()
        salvo = {chave: valor for chave, valor in resultado.items() if chave not in ("indice", "arquivo")}
        self.assertEqual(self.dao.salvar_correcao.call_args.args[1], salvo)

    def test_falha_ao_persistir_resultado_nao_retorna_nota_nem_muda_status(self):
        self.prova["status"] = "Impressa"
        self.dao.salvar_correcao.side_effect = None
        self.dao.salvar_correcao.return_value = False
        retorno = self.service.corrigir([self.imagem()])
        self.assertEqual(retorno["resultados"], [])
        self.assertEqual(retorno["erros"][0]["codigo"], 409)
        self.provas.marcar_corrigida.assert_not_called()

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

    def test_falha_apos_ler_qr_identifica_aluno_sem_retornar_nota(self):
        self.dados["respostas"] = {}
        retorno = self.service.corrigir([self.imagem()])
        erro = retorno["erros"][0]
        self.assertEqual(retorno["resultados"], [])
        self.assertEqual((erro["matricula"], erro["nome"], erro["turma"]), (50280715, "Carlos Silva", "3A"))
        self.assertNotIn("nota_prova", erro)

    def test_qr_do_frontend_identifica_falha_do_leitor_sem_ser_usado_para_corrigir(self):
        self.cliente.processar = MagicMock(side_effect=resposta_erro_http(502, "Leitor indisponível"))
        imagem = {**self.imagem(), "id_prova_aluno": self.registro["_id"]}
        retorno = self.service.corrigir([imagem])
        self.assertEqual(retorno["resultados"], [])
        self.assertEqual(retorno["erros"][0]["nome"], "Carlos Silva")
        self.assertEqual(retorno["erros"][0]["turma"], "3A")

    def test_qr_do_leitor_prevalece_sobre_a_identificacao_enviada(self):
        self.dados["respostas"] = {}
        imagem = {**self.imagem(), "id_prova_aluno": "000000000000000000000099"}
        erro = self.service.corrigir([imagem])["erros"][0]
        self.assertEqual(erro["nome"], "Carlos Silva")
        self.assertEqual(imagem["id_prova_aluno"], self.registro["_id"])

    def test_sem_qr_ou_com_id_desconhecido_nao_inventa_identificacao(self):
        self.dados["qrcode"] = None
        for id_ in (None, "invalido", "000000000000000000000099"):
            erro = self.service.corrigir([{**self.imagem(), "id_prova_aluno": id_}])["erros"][0]
            self.assertIsNone(erro["matricula"])
            self.assertIsNone(erro["nome"])
            self.assertIsNone(erro["turma"])

    def test_cadastro_ausente_preserva_somente_matricula_e_consulta_falha_nao_interrompe(self):
        self.dados["respostas"] = {}
        self.alunos.buscar_por_matricula = lambda _: None
        erro = self.service.corrigir([self.imagem()])["erros"][0]
        self.assertEqual(erro["matricula"], 50280715)
        self.assertIsNone(erro["nome"])
        self.assertIsNone(erro["turma"])
        self.dao.buscar_por_id = MagicMock(side_effect=RuntimeError("Banco indisponível"))
        with self.assertLogs(level="ERROR"):
            retorno = self.service.corrigir([self.imagem(), self.imagem()])
        self.assertEqual(len(retorno["erros"]), 2)

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
