import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from disciplina import Disciplina
from professor import Professor

print("TESTANDO DISCIPLINA")

disc = Disciplina()
prof = Professor()

prof.nome_professor = "Carlos Silva"

# Professor válido
try:
    disc.professor = prof
    print("OK - professor válido")
except Exception as e:
    print("ERRO:", e)

# Nome disciplina
try:
    disc.nome_disciplina = "Matemática"
    print("OK - nome disciplina")
except Exception as e:
    print("ERRO:", e)

# Alunos válidos
try:
    disc.alunos = [12345678, 87654321]
    print("OK - alunos válidos")
except Exception as e:
    print("ERRO:", e)