<template>
  <div class="preview-prova">
    <div v-if="!template" class="preview-carregando">Carregando template da prova...</div>
    <!-- Conteúdo sanitizado com DOMPurify em utils/html.js -->
    <!-- eslint-disable-next-line vue/no-v-html -->
    <div v-else class="folha" v-html="htmlFinal"></div>
  </div>
</template>

<script>
import { LETRAS } from "@/stores/provaDraft";
import { escaparHtml, htmlVazio, sanitizar } from "@/utils/html";

const VAZIO = '<span class="preview-vazio">—</span>';

export default {
  name: "PreviewProva",
  props: {
    template: { type: String, default: "" },
    metadados: { type: Object, required: true },
    questoes: { type: Array, default: () => [] },
    professor: { type: String, default: "" },
  },
  computed: {
    htmlQuestoes() {
      if (!this.questoes.length) return '<p class="preview-vazio">Nenhuma questão adicionada.</p>';
      return this.questoes.map((questao, index) => {
        const enunciado = htmlVazio(questao.enunciado) ? `<p>${VAZIO}</p>` : questao.enunciado;
        const resposta = this.metadados.tipo === "Objetiva"
          ? `<ol class="preview-alternativas">${questao.alternativas.map((alternativa, i) => `<li><span class="preview-letra">${LETRAS[i]})</span><div>${htmlVazio(alternativa) ? VAZIO : alternativa}</div></li>`).join("")}</ol>`
          : `<div class="preview-linhas">${'<div class="preview-linha"></div>'.repeat(Math.max(1, Number(questao.numeroLinhas) || 1))}</div>`;
        return `<div class="preview-questao"><div class="preview-numero">${index + 1}.</div><div class="preview-corpo">${enunciado}${resposta}</div></div>`;
      }).join("");
    },
    htmlFinal() {
      const m = this.metadados;
      const turmas = m.turmasTexto.split(/\r?\n/).map((t) => t.trim()).filter(Boolean).join(", ");
      const data = m.data_de_aplicacao ? new Date(`${m.data_de_aplicacao}T00:00:00`).toLocaleDateString("pt-BR") : "";
      const valor = (texto) => (texto ? escaparHtml(texto) : VAZIO);
      const substituicoes = {
        DISCIPLINA: valor(m.nome_disciplina),
        CODIGO_DISCIPLINA: valor(m.codigo_disciplina),
        TURMAS: valor(turmas),
        SERIE: valor(m.serie ? `${m.serie}ª` : ""),
        BIMESTRE: valor(m.bimestre),
        DATA_APLICACAO: valor(data),
        PROFESSOR: valor(this.professor),
        TIPO: valor(m.tipo),
        QUESTOES: this.htmlQuestoes,
      };
      const html = this.template.replace(/\{\{\s*([A-Z_]+)\s*\}\}/g, (marcador, chave) =>
        chave in substituicoes ? substituicoes[chave] : marcador,
      );
      return sanitizar(html);
    },
  },
};
</script>

<style scoped>
.preview-prova {
  min-height: 100%;
  display: flex;
  justify-content: center;
}

.preview-carregando {
  color: #888;
  padding: 40px;
}

/* A folha simula o papel impresso e permanece clara mesmo no tema escuro. */
.folha {
  width: 100%;
  max-width: 794px;
  min-height: 1123px;
  background: white;
  color: #222;
  padding: 48px 56px;
  border-radius: 4px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  font-size: 14px;
  line-height: 1.5;
  word-wrap: break-word;
}

.folha :deep(h1) {
  font-size: 20px;
  text-align: center;
  margin-bottom: 12px;
  color: #00488b;
}

.folha :deep(.prova-dados) {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 8px;
}

.folha :deep(.prova-dados td) {
  border: 1px solid #ccc;
  padding: 6px 8px;
  font-size: 13px;
}

.folha :deep(.prova-tipo) {
  text-align: right;
  font-size: 12px;
  color: #666;
}

.folha :deep(hr) {
  border: none;
  border-top: 2px solid #00488b;
  margin: 12px 0 20px;
}

.folha :deep(img) {
  max-width: 100%;
  height: auto;
  display: block;
  margin: 6px 0;
}

.folha :deep(p) {
  margin: 0 0 4px;
}

.folha :deep(.preview-questao) {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
}

.folha :deep(.preview-numero) {
  font-weight: 700;
}

.folha :deep(.preview-corpo) {
  flex: 1;
  min-width: 0;
}

.folha :deep(.preview-alternativas) {
  list-style: none;
  margin-top: 8px;
}

.folha :deep(.preview-alternativas li) {
  display: flex;
  gap: 6px;
  margin-bottom: 4px;
}

.folha :deep(.preview-letra) {
  font-weight: 600;
}

.folha :deep(.preview-linha) {
  border-bottom: 1px solid #bbb;
  height: 26px;
}

.folha :deep(.preview-vazio) {
  color: #bbb;
}

@media (max-width: 768px) {
  .folha {
    padding: 24px 20px;
    min-height: auto;
  }
}
</style>
