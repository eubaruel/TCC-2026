import { defineStore } from "pinia";

export const useProvaDraftStore = defineStore("provaDraft", {
  state: () => ({ questoes: [] }),
  actions: {
    adicionar(questao) {
      if (!this.questoes.some((item) => item._id === questao._id)) this.questoes.push(questao);
    },
    remover(id) {
      this.questoes = this.questoes.filter((item) => item._id !== id);
    },
    limpar() {
      this.questoes = [];
    },
  },
});
