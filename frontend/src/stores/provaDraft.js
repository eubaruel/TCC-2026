import { defineStore } from "pinia";

export const LETRAS = ["A", "B", "C", "D", "E"];

let contadorLocal = 0;
const novoIdLocal = () => `local-${Date.now()}-${++contadorLocal}`;

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

export const novaQuestaoEditor = () => ({
  _idLocal: novoIdLocal(),
  _idBanco: null,
  assunto: "",
  dificuldade: "Médio",
  enunciado: "",
  alternativas: LETRAS.map(() => ""),
  indiceCorreta: 0,
  numeroLinhas: 10,
  assinaturaSalva: null,
});

// Converte uma questão vinda da API para o formato usado no editor.
export const questaoDoBanco = (questao) => {
  const alternativas = Array.isArray(questao.alternativas) ? questao.alternativas : [];
  const indiceCorreta = alternativas.findIndex((alternativa) => alternativa.id === questao.alternativa_correta);
  return {
    ...novaQuestaoEditor(),
    _idBanco: questao._id,
    assunto: questao.assunto || "",
    dificuldade: questao.dificuldade || "Médio",
    enunciado: questao.enunciado || "",
    alternativas: LETRAS.map((_, index) => alternativas[index]?.texto || ""),
    indiceCorreta: indiceCorreta >= 0 ? indiceCorreta : 0,
    numeroLinhas: questao.numero_linhas || 10,
    professor: questao.professor,
    autor: questao.autor,
  };
};

export const useProvaDraftStore = defineStore("provaDraft", {
  state: () => ({
    // Questões escolhidas no banco (QuestoesView) para iniciar uma nova prova.
    questoes: [],
    // Rascunho da tela de criação: só vai para o banco no primeiro salvamento.
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
      this.questoesEditor = [novaQuestaoEditor()];
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
