import { defineStore } from "pinia";

export const LETRAS = ["A", "B", "C", "D", "E"];

export const novosMetadados = () => ({
  turmasTexto: "",
  codigo_disciplina: "",
  nome_disciplina: "",
  tipo: "Objetiva",
  serie: 3,
  bimestre: "",
  data_de_aplicacao: "",
  status: "Aguardando questões",
});

// Converte uma questão vinda da API para o formato usado no editor.
export const questaoDoBanco = (questao) => {
  const alternativas = Array.isArray(questao.alternativas) ? questao.alternativas : [];
  const indiceCorreta = alternativas.findIndex((alternativa) => alternativa.id === questao.alternativa_correta);
  return {
    _idBanco: questao._id,
    assunto: questao.assunto || "",
    dificuldade: questao.dificuldade || "Médio",
    enunciado: questao.enunciado || "",
    alternativas: alternativas.map((alternativa) => alternativa.texto || ""),
    indiceCorreta,
  };
};

export const useProvaDraftStore = defineStore("provaDraft", {
  state: () => ({
    // Questões escolhidas no banco para adicionar a uma prova-base existente.
    questoes: [],
    // Seleção local: o salvamento envia somente os IDs para a prova-base.
    provaId: null,
    metadados: novosMetadados(),
    questoesEditor: [],
    sujo: false,
  }),
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
    iniciarNova() {
      this.provaId = null;
      this.metadados = novosMetadados();
      this.questoesEditor = [];
      this.sujo = false;
    },
    marcarSujo() {
      this.sujo = true;
    },
    descartarRascunho() {
      this.provaId = null;
      this.metadados = novosMetadados();
      this.questoesEditor = [];
      this.sujo = false;
      this.limpar();
    },
  },
});
