<template>
  <div class="preview-prova" :style="estiloPagina">
    <div v-if="!template" class="preview-carregando">Carregando template da prova...</div>
    <div v-else class="folha">
      <slot name="cabecalho"></slot>
      <!-- Conteúdo sanitizado com DOMPurify em utils/html.js -->
      <!-- eslint-disable-next-line vue/no-v-html -->
      <div class="conteudo-prova texto-questao" v-html="htmlFinal"></div>
    </div>
  </div>
</template>

<script>
import { LETRAS } from "@/stores/provaDraft";
import { escaparHtml, htmlVazio, sanitizar } from "@/utils/html";
import { PAGINA_PROVA } from "@/utils/cartaoResposta";

const VAZIO = '<span class="preview-vazio">—</span>';

export default {
  name: "PreviewProva",
  props: {
    template: { type: String, default: "" },
    metadados: { type: Object, required: true },
    questoes: { type: Array, default: () => [] },
    professor: { type: String, default: "" },
    matricula: { type: [String, Number], default: "" },
  },
  computed: {
    estiloPagina() {
      const { largura, altura, margemLateral, margemSuperior, margemInferior } = PAGINA_PROVA;
      // Em tela, a folha reduz proporcionalmente para caber no painel; no papel, usa mm reais.
      return {
        "--largura-pagina": `${largura}mm`, "--proporcao-pagina": `${largura} / ${altura}`,
        "--margens-previa": `${margemSuperior / largura * 100}% ${margemLateral / largura * 100}% ${margemInferior / largura * 100}%`,
        "--margens-impressao": `${margemSuperior}mm ${margemLateral}mm ${margemInferior}mm`,
      };
    },
    htmlQuestoes() {
      if (!this.questoes.length) return '<p class="preview-vazio">Nenhuma questão adicionada.</p>';
      return this.questoes.map((questao, index) => {
        const enunciado = htmlVazio(questao.enunciado) ? `<p>${VAZIO}</p>` : questao.enunciado;
        const resposta = `<ol class="preview-alternativas">${questao.alternativas.map((alternativa, i) => `<li><span class="preview-letra">${LETRAS[i]})</span><div>${htmlVazio(alternativa) ? VAZIO : alternativa}</div></li>`).join("")}</ol>`;
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
        PERIODO_LETIVO: valor(m.periodo_letivo),
        DATA_APLICACAO: valor(data),
        PROFESSOR: valor(this.professor),
        MATRICULA: this.matricula === "" ? "______" : valor(this.matricula),
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
  width: var(--largura-pagina);
  max-width: 100%;
  margin: 0 auto;
  display: flex;
  justify-content: center;
}

.preview-carregando {
  color: #888;
  padding: 40px;
}

/* A folha simula o papel impresso e permanece clara mesmo no tema escuro. */
.folha {
  box-sizing: border-box;
  width: 100%;
  aspect-ratio: var(--proporcao-pagina);
  background: white;
  color: #222;
  padding: var(--margens-previa);
  border-radius: 4px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  line-height: 1.5;
  word-wrap: break-word;
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

.folha :deep(.preview-vazio) {
  color: #bbb;
}

@media print {
  .preview-prova { width: 100%; max-width: none; display: block; }
  .folha { aspect-ratio: auto; padding: var(--margens-impressao); box-shadow: none; border-radius: 0; -webkit-box-decoration-break: clone; box-decoration-break: clone; }
  .folha :deep(.preview-questao) { break-inside: avoid; }
}
</style>
