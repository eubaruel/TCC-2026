<template>
  <!-- O desenho mantém as dez colunas, inclusive quando a prova tem menos questões. -->
  <svg class="cartao-resposta" :viewBox="`0 0 ${modelo.largura} ${modelo.altura}`" role="img" :aria-label="`Cartão-resposta da matrícula ${matricula}`">
    <rect width="1200" height="286" fill="white" />
    <!-- Recorta apenas os logotipos originais; a grade e os textos são vetoriais. -->
    <svg x="8" y="10" width="144" height="41" viewBox="16 18 288 72" preserveAspectRatio="none">
      <image :href="fundo" width="2400" height="504" />
    </svg>
    <svg x="1020" y="3" width="88" height="52" viewBox="2040 5 176 92" preserveAspectRatio="none">
      <image :href="fundo" width="2400" height="504" />
    </svg>
    <g class="grade" fill="none" stroke="black" stroke-width="1.2">
      <rect x="0.6" y="0.6" width="1198.8" height="284.8" />
      <path d="M160.5 0V57.5 M923 0V57.5 M0 57.5H1200 M0 86H1200 M111.5 57.5V286 M647 57.5V286 M0 143H1200 M111.5 114.5H1200 M111.5 171.5H1200 M111.5 200H1200 M111.5 228.5H647 M111.5 257H647 M923 171.5V200 M738 250H1107" />
      <path v-for="numero in 10" :key="`coluna-${numero}`" :d="`M${160.5 + (numero - 1) * 48.65} 86V257`" />
    </g>
    <g class="rotulos" text-anchor="middle">
      <text x="55.75" y="76">NOTA</text>
      <text x="379.25" y="76">QUESTÕES</text>
      <text x="923.5" y="76">INFORMAÇÕES GERAIS</text>
      <text v-for="numero in 10" :key="numero" class="indice" :x="184.825 + (numero - 1) * 48.65" y="105">{{ numero }}</text>
      <text v-for="(letra, indice) in ['A', 'B', 'C', 'D', 'E']" :key="letra" class="indice" x="136" :y="133 + indice * 28.5">{{ letra }}</text>
      <text x="379.25" y="275" class="legenda">GABARITO OFICIAL - PREENCHER TODO O RETÂNGULO</text>
      <text x="923.5" y="269">NOME DO ALUNO POR EXTENSO</text>
    </g>
    <g class="rotulos">
      <text x="651" y="105">Nome:</text>
      <text x="651" y="133.5">Matrícula:</text>
      <text x="651" y="162">Professor:</text>
      <text x="651" y="190.5">Turma:</text>
      <text x="927" y="190.5">Data:</text>
    </g>
    <g class="dados">
      <text x="172" y="35">{{ prova.disciplina.nome_disciplina }}</text>
      <text x="172" y="53">{{ prova.periodo_letivo }} · {{ prova.serie }}ª série</text>
      <text x="705" y="107" :textLength="nomeAluno.length > 50 ? 480 : undefined" lengthAdjust="spacingAndGlyphs">{{ nomeAluno }}</text>
      <text x="744" y="136">{{ matricula }}</text>
      <text x="744" y="164">{{ prova.professor.nome }}</text>
      <text x="705" y="192">{{ turmas }}</text>
      <text x="966" y="192">{{ dataAplicacao }}</text>
    </g>
    <!-- A área de nota é livre no modelo; o QR não invade a região das respostas. -->
    <image :href="qrCode" :x="modelo.qr.x" :y="modelo.qr.y" :width="modelo.qr.tamanho" :height="modelo.qr.tamanho" />
  </svg>
</template>

<script>
import fundo from "@/assets/templates/cartao-resposta.png";
import { CARTAO_RESPOSTA } from "@/utils/cartaoResposta";

export default {
  name: "CartaoResposta",
  props: {
    prova: { type: Object, required: true },
    matricula: { type: [String, Number], required: true },
    nomeAluno: { type: String, default: "" },
    qrCode: { type: String, required: true },
  },
  data: () => ({ fundo, modelo: CARTAO_RESPOSTA }),
  computed: {
    turmas() { return (Array.isArray(this.prova.id_turma) ? this.prova.id_turma : [this.prova.id_turma]).join(", "); },
    dataAplicacao() { return new Date(`${this.prova.data_de_aplicacao}T00:00:00`).toLocaleDateString("pt-BR"); },
  },
};
</script>

<style scoped>
.cartao-resposta { display: block; width: 100%; background: white; color: black; break-inside: avoid; }
text { fill: black; font-family: Arial, sans-serif; }
.rotulos { font-size: 15px; font-weight: 700; }
.indice { font-weight: 400; }
.legenda { font-size: 13px; }
.dados { font-size: 16px; }
</style>
