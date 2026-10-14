<template>
  <!-- O desenho mantém as dez colunas, inclusive quando a prova tem menos questões. -->
  <svg class="cartao-resposta" viewBox="0 0 1200 286" role="img" :aria-label="`Cartão-resposta da matrícula ${matricula}`">
    <image :href="fundo" width="1200" height="286" preserveAspectRatio="none" />
    <text x="172" y="35" font-size="20">{{ prova.disciplina.nome_disciplina }}</text>
    <text x="172" y="53" font-size="14">{{ prova.bimestre }} · {{ prova.serie }}ª série</text>
    <text x="744" y="136">{{ matricula }}</text>
    <text x="744" y="164">{{ prova.professor.nome }}</text>
    <text x="705" y="192">{{ turmas }}</text>
    <text x="966" y="192">{{ dataAplicacao }}</text>
    <!-- A área de nota é livre no modelo; o QR não invade a região das respostas. -->
    <image :href="qrCode" x="9" y="168" width="94" height="94" />
  </svg>
</template>

<script>
import fundo from "@/assets/templates/cartao-resposta.png";

export default {
  name: "CartaoResposta",
  props: {
    prova: { type: Object, required: true },
    matricula: { type: [String, Number], required: true },
    qrCode: { type: String, required: true },
  },
  data: () => ({ fundo }),
  computed: {
    turmas() { return (Array.isArray(this.prova.id_turma) ? this.prova.id_turma : [this.prova.id_turma]).join(", "); },
    dataAplicacao() { return new Date(`${this.prova.data_de_aplicacao}T00:00:00`).toLocaleDateString("pt-BR"); },
  },
};
</script>

<style scoped>
.cartao-resposta { display: block; width: 100%; background: white; color: black; break-inside: avoid; }
text { fill: black; font: 16px Arial, sans-serif; }
</style>
