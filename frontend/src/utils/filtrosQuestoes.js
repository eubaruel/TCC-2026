import { textoPuro } from "./html";

const normalizar = (valor) => String(valor ?? "").normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/\s+/g, " ").trim().toLowerCase();
const referenciasDaQuestao = (questao) => {
  const referencias = questao.disciplinasOriginais || questao.disciplina || [];
  return Array.isArray(referencias) ? referencias : [referencias];
};

export const novosFiltrosQuestoes = () => ({ disciplina: "", dificuldade: "", autor: "", enunciado: "" });

export function opcoesDisciplinas(questoes, cadastradas = []) {
  const opcoes = cadastradas.filter((disciplina) => disciplina.nome_disciplina).map((disciplina) => ({ ...disciplina }));
  for (const questao of questoes) {
    for (const referencia of referenciasDaQuestao(questao)) {
      if (!normalizar(referencia)) continue;
      const conhecida = opcoes.some((disciplina) => [disciplina.codigo_disciplina, disciplina.nome_disciplina]
        .some((valor) => normalizar(valor) === normalizar(referencia)));
      if (!conhecida) opcoes.push({ codigo_disciplina: referencia, nome_disciplina: referencia });
    }
  }
  return opcoes.sort((a, b) => a.nome_disciplina.localeCompare(b.nome_disciplina, "pt-BR"));
}

export function filtrarQuestoes(questoes, filtros, disciplinas = []) {
  const disciplina = normalizar(filtros.disciplina), dificuldade = normalizar(filtros.dificuldade);
  const autor = normalizar(filtros.autor), enunciado = normalizar(filtros.enunciado);
  const cadastrada = disciplinas.find((item) => [item.codigo_disciplina, item.nome_disciplina].some((valor) => normalizar(valor) === disciplina));
  const referencias = cadastrada ? [cadastrada.codigo_disciplina, cadastrada.nome_disciplina].map(normalizar) : [disciplina];
  return questoes.filter((questao) =>
    (!disciplina || referenciasDaQuestao(questao).some((valor) => referencias.includes(normalizar(valor))))
    && (!dificuldade || normalizar(questao.dificuldade || "Médio") === dificuldade)
    && (!autor || normalizar(`${questao.professor?.nome || ""} ${questao.autor || ""}`).includes(autor))
    && (!enunciado || normalizar(textoPuro(questao.enunciado ?? questao.texto)).includes(enunciado)));
}
