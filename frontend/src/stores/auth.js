import { defineStore } from "pinia";
import { autenticarUsuario } from "@/services/usuarios";

export const useAuthStore = defineStore("auth", {
  state: () => ({ user: null, loading: false }),
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
        this.user = data.usuario;
        return { success: true, user: this.user };
      } catch (error) {
        return { success: false, message: error.details || error.message };
      } finally {
        this.loading = false;
      }
    },
    logout() {
      this.user = null;
    },
    async trocarSenha() {
      // A API não disponibiliza endpoint para alteração de senha.
    },
  },
});
