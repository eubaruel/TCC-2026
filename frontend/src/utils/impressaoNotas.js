import { CARTAO_RESPOSTA, PAGINA_PROVA } from "./cartaoResposta";

export function formatarNota(nota) {
  if (typeof nota !== "number" || !Number.isFinite(nota) || nota < 0 || nota > 10) throw new Error("Nota inválida para impressão.");
  return nota.toFixed(2).replace(".", ",");
}

export function ajusteValido(valor) {
  return typeof valor === "number" && Number.isFinite(valor) && Math.abs(valor) <= 10;
}

export function posicaoNota(ajusteX = 0, ajusteY = 0) {
  const escala = (PAGINA_PROVA.largura - 2 * PAGINA_PROVA.margem) / CARTAO_RESPOSTA.largura;
  const campo = CARTAO_RESPOSTA.nota;
  return {
    left: `${PAGINA_PROVA.margem + (campo.x + campo.largura / 2) * escala + ajusteX}mm`,
    top: `${PAGINA_PROVA.margem + (campo.y + campo.altura / 2) * escala + ajusteY}mm`,
    width: `${campo.largura * escala}mm`, height: `${campo.altura * escala}mm`,
  };
}

// Não ordena por aluno: a posição é a do arquivo original, inclusive falhas locais.
export function entradasDoLote(arquivos, resultados, erros) {
  const porIndice = new Map(resultados.map((item) => [item.indice, item]));
  const falhas = new Set(erros.map((item) => item.indice));
  return arquivos.map((arquivo, indice) => {
    const resultado = porIndice.get(indice);
    if (!resultado || falhas.has(indice)) return { arquivo: arquivo.name, erro: true };
    if (!resultado.id_prova_aluno || !resultado.id_correcao) throw new Error("O servidor não confirmou o salvamento de uma das notas. Corrija o conjunto novamente.");
    return { arquivo: arquivo.name, id_prova_aluno: resultado.id_prova_aluno, id_correcao: resultado.id_correcao };
  });
}
