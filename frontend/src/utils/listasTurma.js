// A turma já contém a identificação completa: série, letra e curso.
export function agruparVersoesPorTurma(versoes, turmasProva) {
  const permitidas = new Set(Array.isArray(turmasProva) ? turmasProva : [turmasProva]);
  const grupos = new Map(), matriculas = new Set();
  for (const versao of versoes) {
    if (typeof versao.nome_aluno !== "string" || !versao.nome_aluno.trim()
        || typeof versao.turma_aluno !== "string" || !versao.turma_aluno.trim()) {
      throw new Error(`Confira o nome e a turma do aluno de matrícula ${versao.matricula_aluno} antes de imprimir as listas.`);
    }
    const turma = versao.turma_aluno.trim();
    if (!permitidas.has(turma)) throw new Error(`A turma do aluno de matrícula ${versao.matricula_aluno} não pertence a esta prova.`);
    if (matriculas.has(versao.matricula_aluno)) throw new Error(`Há versões repetidas para a matrícula ${versao.matricula_aluno}. Confira os registros antes de imprimir.`);
    matriculas.add(versao.matricula_aluno);
    if (!grupos.has(turma)) grupos.set(turma, []);
    grupos.get(turma).push(versao);
  }
  return [...grupos].sort(([a], [b]) => a.localeCompare(b, "pt-BR", { sensitivity: "base", numeric: true }))
    .map(([turma, alunos]) => ({ turma, alunos: [...alunos]
      .sort((a, b) => a.nome_aluno.localeCompare(b.nome_aluno, "pt-BR", { sensitivity: "base" })
        || String(a.matricula_aluno).localeCompare(String(b.matricula_aluno), "pt-BR", { numeric: true }))
      .map((aluno, indice) => ({ ...aluno, numero_chamada: indice + 1 })) }));
}
