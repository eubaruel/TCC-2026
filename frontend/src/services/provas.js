import { api } from "./api";

export const listarProvas = (params = {}) => {
  const query = new URLSearchParams(
    Object.entries(params).filter(([, value]) => value !== "" && value !== null && value !== undefined),
  );
  return api(`/provas/${query.size ? `?${query.toString()}` : ""}`);
};

export const criarProva = (prova) => api("/provas/", { method: "POST", body: { prova } });

export const atualizarProva = (id, prova) => api(`/provas/${id}`, { method: "PUT", body: { prova } });

export const excluirProva = (id) => api(`/provas/${id}`, { method: "DELETE" });
