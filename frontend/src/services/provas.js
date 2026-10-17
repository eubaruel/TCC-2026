import { api } from "./api";

export const listarProvas = (params = {}) => {
  const query = new URLSearchParams(
    Object.entries(params).filter(([, value]) => value !== "" && value !== null && value !== undefined),
  );
  return api(`/provas/${query.size ? `?${query.toString()}` : ""}`);
};

export const buscarProva = async (id) => (await listarProvas({ id })).provas?.[0] || null;

export const criarProva = (prova) => api("/provas/criar-prova", { method: "POST", body: { prova } });

export const adicionarQuestoes = (id, questoes) =>
  api(`/provas/${id}/adicionar-questoes`, { method: "PATCH", body: { prova: { questoes } } });

export const atualizarProva = (id, prova) => api(`/provas/${id}`, { method: "PUT", body: { prova } });

export const excluirProva = (id) => api(`/provas/${id}`, { method: "DELETE" });

export const enviarProva = (id) => api(`/provas/${id}/enviar`, { method: "PATCH" });

export const imprimirProvas = (id) => api(`/provas/imprimir-provas/${id}`);

export const confirmarImpressao = (id) => api(`/provas/${id}/confirmar-impressao`, { method: "PATCH" });

export const provaEditavel = (prova) => ["Aguardando questões", "Em elaboração"].includes(prova.status);
