from api.modelos.alternativa import Alternativa
from api.modelos.questao import Questao


print("TESTANDO QUESTÃO")

questao = Questao()
questao.tipo_questao = "Objetiva"
questao.alternativas = [
    Alternativa("alt-a", "A"),
    Alternativa("alt-b", "B"),
    Alternativa("alt-c", "C"),
    Alternativa("alt-d", "D"),
    Alternativa("alt-e", "E")
]
questao.alternativa_correta = "alt-a"

print("OK - alternativas como objetos e gabarito por id")

try:
    questao.alternativa_correta = "id-inexistente"
    print("ERRO - alternativa inválida passou")
except ValueError:
    print("OK - alternativa inválida rejeitada")
