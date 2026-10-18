import { defineStore } from "pinia";
import { autenticarUsuario } from "@/services/usuarios";

const CHAVE_USUARIO = "tcc.usuario";

function dadosDoUsuario(usuario) {
  if (!usuario?.registro || typeof usuario.nome !== "string" || typeof usuario.email !== "string" ||
      !["Professor", "Processo pedagógico"].includes(usuario.role)) return null;
  const { registro, nome, email, role, deve_alterar_senha } = usuario;
  return { registro, nome, email, role, deve_alterar_senha };
}

function restaurarUsuario() {
  try { return dadosDoUsuario(JSON.parse(sessionStorage.getItem(CHAVE_USUARIO))); }
  catch (_) { return null; }
}

function salvarUsuario(usuario) {
  try {
    if (usuario) sessionStorage.setItem(CHAVE_USUARIO, JSON.stringify(usuario));
    else sessionStorage.removeItem(CHAVE_USUARIO);
  } catch (_) {
    // Armazenamento bloqueado não deve impedir login ou saída; nesse caso, usa só a memória.
  }
}

export const useAuthStore = defineStore("auth", {
  // A restauração é síncrona: o router já encontra o usuário na primeira navegação.
  state: () => ({ user: restaurarUsuario(), loading: false }),
  getters: {
    isProfessor: (state) => state.user?.role === "Professor",
    isProcessoPedagogico: (state) => state.user?.role === "Processo pedagógico",
    isLoggedIn: (state) => Boolean(state.user),
  },
  actions: {
    async login(registro, senha) {
      this.loading = true;
      try {
        const data = await autenticarUsuario(registro, senha);
        const usuario = dadosDoUsuario(data.usuario);
        if (!usuario) throw new Error("O servidor retornou dados de usuário inválidos.");
        this.user = usuario;
        salvarUsuario(usuario);
        return { success: true, user: this.user };
      } catch (error) {
        return { success: false, message: error.details || error.message };
      } finally {
        this.loading = false;
      }
    },
    logout() {
      this.user = null;
      salvarUsuario(null);
    },
    async trocarSenha() {
      // A API não disponibiliza endpoint para alteração de senha.
    },
  },
});
