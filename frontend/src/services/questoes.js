import { api } from "./api";

export const listarQuestoes = (params = {}) => {
  const query = new URLSearchParams(
    Object.entries(params).filter(([, value]) => value !== "" && value !== null && value !== undefined),
  );
  return api(`/questoes/${query.size ? `?${query.toString()}` : ""}`);
};

export const criarQuestao = (questao) => api("/questoes/", { method: "POST", body: { questao } });

export const atualizarQuestao = (id, questao) =>
  api(`/questoes/${id}`, { method: "PUT", body: { questao } });

export const excluirQuestao = (id) => api(`/questoes/${id}`, { method: "DELETE" });
