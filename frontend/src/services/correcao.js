import { api } from "./api";
import { recortarCartao } from "@/utils/recortarCartao";

export const criarLoteCorrecao = (entradas) => api("/provas/lotes-correcao", { method: "POST", body: { entradas } });
export const buscarLoteCorrecao = (id) => api(`/provas/lotes-correcao/${id}`);

export async function corrigirImagens(arquivos, atualizar = () => {}, { recortar = false } = {}) {
  const resultados = [], erros = [];
  let lote = [], bytes = 0, preparadas = 0, processadas = 0, recortadas = 0;
  const progresso = () => atualizar({ preparadas, processadas, recortadas, total: arquivos.length });
  const enviar = async () => {
    if (!lote.length) return;
    const form = new FormData();
    lote.forEach((item) => form.append("imagens", item.imagem));
    form.append("ids_provas_alunos", JSON.stringify(lote.map((item) => item.id_prova_aluno || null)));
    try {
      const dados = await api("/provas/corrigir-provas", { method: "POST", body: form });
      if (!Array.isArray(dados?.resultados) || !Array.isArray(dados?.erros)) throw new Error("Resposta de correção inválida.");
      const itens = [...dados.resultados, ...dados.erros];
      if (itens.length !== lote.length || new Set(itens.map((item) => item.indice)).size !== lote.length ||
          itens.some((item) => !Number.isInteger(item.indice) || !lote[item.indice])) throw new Error("Resposta incompleta ou com índices inválidos.");
      const adaptar = (item) => ({ ...item, indice: lote[item.indice].indice, arquivo: arquivos[lote[item.indice].indice].name });
      resultados.push(...dados.resultados.map(adaptar)); erros.push(...dados.erros.map(adaptar));
    } catch (erro) {
      lote.forEach((item) => erros.push({ indice: item.indice, arquivo: arquivos[item.indice].name,
        codigo: erro.status || 0, mensagem: erro.message || "Não foi possível enviar este lote." }));
    }
    processadas += lote.length; lote = []; bytes = 0; progresso();
  };
  for (let indice = 0; indice < arquivos.length; indice++) {
    const original = arquivos[indice];
    if (!original.size || !original.type.startsWith("image/")) {
      erros.push({ indice, arquivo: original.name, mensagem: "Selecione uma imagem válida e não vazia." });
      processadas++; preparadas++; progresso(); continue;
    }
    const { arquivo: imagem, recortada, id_prova_aluno } = await recortarCartao(original, { permitirRecorte: recortar });
    preparadas++; if (recortada) recortadas++;
    if (imagem.size > 5 * 1024 * 1024) {
      erros.push({ indice, arquivo: original.name, mensagem: "Imagem acima de 5 MiB. Digitalize em um tamanho menor ou, para folhas completas, ative o recorte automático." });
      processadas++; progresso(); continue;
    }
    // A API aceita 50 arquivos; reserva espaço para o multipart dentro do limite de 50 MiB.
    if (lote.length === 50 || bytes + imagem.size > 40 * 1024 * 1024) await enviar();
    lote.push({ indice, imagem, id_prova_aluno }); bytes += imagem.size; progresso();
    await new Promise((resolve) => setTimeout(resolve, 0)); // Permite atualizar a tela entre imagens.
  }
  await enviar();
  return { resultados: resultados.sort((a, b) => a.indice - b.indice), erros: erros.sort((a, b) => a.indice - b.indice), recortadas };
}
