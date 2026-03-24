import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from prova import Prova
from professor import Professor
from disciplina import Disciplina

print("TESTANDO PROVA")

p = Prova()
prof = Professor()
disc = Disciplina()

prof.nome_professor = "João Silva"
disc.nome_disciplina = "Matemática"

# Tipo
try:
    p.tipo = "objetiva"
    print("OK - tipo")
except Exception as e:
    print("ERRO:", e)

# Status
try:
    p.status = "Corrigida"
    print("OK - status")
except Exception as e:
    print("ERRO:", e)

# Ano
try:
    p.ano = 2024
    print("OK - ano")
except Exception as e:
    print("ERRO:", e)

# Questões válidas
try:
    p.id_questao = [1,2,3,4,5]
    print("OK - questões válidas")
except Exception as e:
    print("ERRO:", e)

# Questões inválidas
try:
    p.id_questao = [1,2]
    print("ERRO - poucas questões passou")
except:
    print("OK - poucas questões bloqueadas")