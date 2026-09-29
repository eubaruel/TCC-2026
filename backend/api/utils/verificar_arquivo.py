from api.utils.resposta_json import Resposta_json

class Verificar_arquivo:
    
    @staticmethod
    def verificar_integridade(arquivo,tipo_arquivo):
        if not arquivo:
            return Resposta_json.erro(
                mensagem = "Arquivo não enviado",
                detalhes = "O arquivo excel não foi enviado na requisição",
                codigo = 400
            )
        
        if not arquivo.filename.endswith(tipo_arquivo):
            return Resposta_json.erro(
                mensagem = "Formato inválido",
                detalhes = f"O tipo de arquivo deve ser {tipo_arquivo}",
                codigo = 400
            )
        
        return None