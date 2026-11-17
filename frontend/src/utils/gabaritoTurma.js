import { LETRAS } from "@/stores/provaDraft";

// Cada aluno recebe uma versão embaralhada: a letra correta é calculada por versão.
// "questoes" já vem no formato do editor (questaoDoBanco), com indiceCorreta.
export function linhasGabarito(alunos) {
  return alunos.map((aluno) => ({
    numero_chamada: aluno.numero_chamada,
    matricula_aluno: aluno.matricula_aluno,
    nome_aluno: aluno.nome_aluno,
    respostas: (aluno.questoes || []).map((questao) => LETRAS[questao.indiceCorreta] || "?"),
  }));
}

export function paginarGabarito(linhas, porPagina = 28) {
  const paginas = [];
  for (let inicio = 0; inicio < linhas.length; inicio += porPagina) paginas.push(linhas.slice(inicio, inicio + porPagina));
  return paginas;
}
