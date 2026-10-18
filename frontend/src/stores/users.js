import { defineStore } from "pinia";
import {
  atualizarUsuario,
  criarUsuario,
  excluirUsuario,
  listarUsuarios,
} from "@/services/usuarios";

export const useUsersStore = defineStore("users", {
  state: () => ({ users: [], loading: false, error: null }),
  getters: {
    activeUsers: (state) => state.users.filter((user) => user.ativo),
    professores: (state) => state.users.filter((user) => user.role === "Professor" && user.ativo),
    processoPedagogico: (state) => state.users.filter((user) => user.role === "Processo pedagógico" && user.ativo),
    getByRegistro: (state) => (registro) =>
      state.users.filter((user) => String(user.registro).includes(String(registro)) && user.ativo),
    getByNome: (state) => (nome) =>
      state.users.filter((user) => user.nome.toLowerCase().includes(nome.toLowerCase()) && user.ativo),
    getByEmail: (state) => (email) =>
      state.users.filter((user) => user.email.toLowerCase().includes(email.toLowerCase()) && user.ativo),
  },
  actions: {
    async fetchUsers() {
      this.loading = true;
      this.error = null;
      try {
        const data = await listarUsuarios();
        this.users = data.usuarios;
      } catch (error) {
        this.error = error.details || error.message;
        this.users = [];
        throw error;
      } finally {
        this.loading = false;
      }
    },
    async createUser(userData) {
      const data = await criarUsuario({
        registro: Number(userData.registro),
        nome: userData.nome,
        email: userData.email,
        senha: userData.senha,
        role: userData.role,
      });
      await this.fetchUsers();
      return data.usuario;
    },
    async updateUser(registro, updates) {
      const data = await atualizarUsuario(registro, {
        nome: updates.nome,
        email: updates.email,
        role: updates.role,
        ativo: updates.ativo,
      });
      await this.fetchUsers();
      return data.usuario;
    },
    async softDeleteUser(registro) {
      await excluirUsuario(registro);
      await this.fetchUsers();
    },
    async resetarSenha() {
      // A API não disponibiliza endpoint para redefinição de senha.
    },
  },
});
