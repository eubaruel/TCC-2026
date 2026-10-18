import unittest
from copy import deepcopy

from api.controles.questao_controle import Questao_controle
from api.middlewares.questao_middleware import Questao_middleware
from api.roteador.questao_rotas import Questao_rotas
from api.services.questao_service import Questao_service
from api.utils.texto_questao import contar_caracteres
from tests.fakes import FakeQuestaoDao
from tests.test_fluxos_api import criar_app, payload_questao


class ContagemTextoTest(unittest.TestCase):
    def test_texto_entidades_espacos_pontuacao_e_unicode(self):
        for html, texto in [
            ("  a  \n b! ", "  a  \n b! "),
            ("<p> A&nbsp; &amp; 😀! </p>", " A\u00a0 & 😀! "),
            ("<p>um</p><p>dois<br> três</p>", "umdois três"),
            ("<strong>ação</strong>&#33;&#x1F600;", "ação!😀"),
            ("<p>a\r\nb\rc</p>", "a\nb\nc"),
        ]:
            with self.subTest(html=html):
                self.assertEqual(contar_caracteres(html), len(texto))

    def test_ignora_imagem_atributos_comentarios_script_e_style(self):
        imagem = f'<img src="data:image/png;base64,{"a" * 100000}" alt="Texto alternativo">'
        self.assertEqual(contar_caracteres(imagem), 0)
        self.assertEqual(contar_caracteres(f"<p><strong>Olá!</strong>{imagem}</p><!-- comentário -->"), 4)
        self.assertEqual(contar_caracteres("<script>ignorar</script><style>ignorar</style><p>A</p>"), 1)
        self.assertEqual(contar_caracteres("<p><br></p>"), 0)


class LimitesQuestaoHttpTest(unittest.TestCase):
    def setUp(self):
        self.dao = FakeQuestaoDao()
        controle = Questao_controle(Questao_service(self.dao))
        rotas = Questao_rotas(Questao_middleware(), controle)
        self.client = criar_app(rotas.criar_rotas(), "/api/v1/questoes").test_client()

    def test_aceita_limites_exatos_sem_limite_total_e_preserva_html(self):
        payload = payload_questao(1)
        dados = payload["questao"]
        dados["enunciado"] = f'<p>{"á" * 7000}<img src="data:image/png;base64,{"a" * 20000}"></p>'
        dados["alternativas"] = [f'<p><strong>{"&amp;" * 2000}</strong></p>'] * 5
        dados["alternativa_correta"] = dados["alternativas"][0]
        resposta = self.client.post("/api/v1/questoes/", json=payload)
        self.assertEqual(resposta.status_code, 201, resposta.get_json())
        questao = resposta.get_json()["data"]["questao"]
        self.assertEqual(questao["enunciado"], dados["enunciado"])
        self.assertEqual(questao["alternativas"][0]["texto"], dados["alternativas"][0])
        resposta = self.client.put(f'/api/v1/questoes/{questao["_id"]}', json=payload)
        self.assertEqual(resposta.status_code, 200, resposta.get_json())

    def test_excesso_no_post_e_put_retorna_400_sem_gravar_ou_alterar(self):
        criado = self.client.post("/api/v1/questoes/", json=payload_questao(1)).get_json()["data"]["questao"]
        antes = deepcopy(self.dao.documentos)
        for campo in ["enunciado", 0, 1, 2, 3, 4]:
            payload = payload_questao(2)
            if campo == "enunciado":
                payload["questao"]["enunciado"] = f'<p>{"a" * 7001}</p>'
                limite = "7000"
            else:
                payload["questao"]["alternativas"][campo] = f'<p>{"😀" * 2001}</p>'
                payload["questao"]["alternativa_correta"] = payload["questao"]["alternativas"][0]
                limite = "2000"
            for metodo, rota in [(self.client.post, "/api/v1/questoes/"), (self.client.put, f'/api/v1/questoes/{criado["_id"]}')]:
                with self.subTest(campo=campo, rota=rota):
                    resposta = metodo(rota, json=payload)
                    self.assertEqual(resposta.status_code, 400)
                    self.assertIn(limite, resposta.get_json()["erro"]["detalhes"])
                    self.assertEqual(self.dao.documentos, antes)

    def test_conta_espacos_antes_de_normalizar_alternativa(self):
        payload = payload_questao(1)
        payload["questao"]["alternativas"][1] = " " * 2000 + "A"
        resposta = self.client.post("/api/v1/questoes/", json=payload)
        self.assertEqual(resposta.status_code, 400)
        self.assertEqual(self.dao.documentos, {})

    def test_aceita_tres_imagens_por_campo_sem_limite_total_adicional(self):
        imagem = '<img src="data:image/jpeg;base64,teste">'
        payload = payload_questao(1)
        payload["questao"]["enunciado"] = f'<p>Enunciado{imagem * 3}</p>'
        payload["questao"]["alternativas"] = [f'<p>Alternativa {i}{imagem * 3}</p>' for i in range(5)]
        payload["questao"]["alternativa_correta"] = payload["questao"]["alternativas"][0]
        resposta = self.client.post("/api/v1/questoes/", json=payload)
        self.assertEqual(resposta.status_code, 201, resposta.get_json())
        id_questao = resposta.get_json()["data"]["questao"]["_id"]
        self.assertEqual(self.client.put(f"/api/v1/questoes/{id_questao}", json=payload).status_code, 200)

    def test_quarta_imagem_rejeitada_em_todos_os_campos_sem_gravar(self):
        criado = self.client.post("/api/v1/questoes/", json=payload_questao(1)).get_json()["data"]["questao"]
        antes = deepcopy(self.dao.documentos)
        for campo in ["enunciado", 0, 1, 2, 3, 4]:
            payload = payload_questao(2)
            excesso = '<p>Texto' + '<img src="data:image/jpeg;base64,teste">' * 4 + '</p>'
            if campo == "enunciado":
                payload["questao"][campo] = excesso
            else:
                payload["questao"]["alternativas"][campo] = excesso
                payload["questao"]["alternativa_correta"] = payload["questao"]["alternativas"][0]
            for metodo, rota in [(self.client.post, "/api/v1/questoes/"), (self.client.put, f'/api/v1/questoes/{criado["_id"]}')]:
                with self.subTest(campo=campo, rota=rota):
                    resposta = metodo(rota, json=payload)
                    self.assertEqual(resposta.status_code, 400)
                    self.assertIn("no máximo 3 imagens", resposta.get_json()["erro"]["detalhes"])
                    self.assertEqual(self.dao.documentos, antes)
