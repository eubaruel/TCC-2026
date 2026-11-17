import { api } from "./api";

export const listarUsuarios = (params = {}) => {
  const query = new URLSearchParams(
    Object.entries(params).filter(([, value]) => value !== "" && value !== null && value !== undefined),
  );
  return api(`/usuarios/${query.size ? `?${query.toString()}` : ""}`);
};

export const autenticarUsuario = (registro, senha) =>
  api("/usuarios/login", { method: "POST", body: { usuario: { registro, senha } } });

export const alterarSenha = (registro, senha_atual, nova_senha) =>
  api(`/usuarios/${registro}/alterar-senha`, { method: "PATCH", body: { usuario: { senha_atual, nova_senha } } });

export const criarUsuario = (usuario) => api("/usuarios/", { method: "POST", body: { usuario } });

export const atualizarUsuario = (registro, usuario) =>
  api(`/usuarios/${registro}`, { method: "PUT", body: { usuario } });

export const excluirUsuario = (registro) => api(`/usuarios/${registro}`, { method: "DELETE" });
