<template>
  <section v-for="(pagina, indicePagina) in paginas" :key="indicePagina" class="gabarito-folha documento-impressao"
    :aria-label="`Gabarito do professor — ${turma} — página ${indicePagina + 1}`">
    <header class="gabarito-cabecalho">
      <div class="gabarito-instituicao">
        <svg class="logo-fve" viewBox="16 18 288 72" role="img" aria-label="Fundação Valeparaibana de Ensino">
          <image :href="logos" width="2400" height="504" />
        </svg>
        <div class="gabarito-titulo">
          <h2>GABARITO DO PROFESSOR — USO INTERNO</h2>
          <p>{{ prova.periodo_letivo }}</p>
        </div>
        <svg class="logo-univap" viewBox="2040 5 176 92" role="img" aria-label="Colégios Univap">
          <image :href="logos" width="2400" height="504" />
        </svg>
      </div>
      <div class="gabarito-identificacao">
        <div>
          <p><strong>TURMA: {{ turma }}</strong></p>
          <p><strong>DISCIPLINA: {{ prova.disciplina.nome_disciplina }}</strong></p>
          <p><strong>PROFESSOR (A): {{ prova.professor.nome }}</strong></p>
        </div>
        <p class="gabarito-data"><strong>Data da Aplicação: {{ dataAplicacao }}</strong></p>
      </div>
      <p class="gabarito-aviso">Cada aluno recebeu uma versão embaralhada. Confira a linha da matrícula correspondente.</p>
    </header>
    <table class="gabarito-tabela">
      <thead>
        <tr>
          <th scope="col" class="col-numero">Nº</th>
          <th scope="col" class="col-matricula">MATRÍCULA</th>
          <th scope="col" class="col-nome">NOME</th>
          <th v-for="numero in quantidade" :key="numero" scope="col" class="col-questao">{{ numero }}</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="linha in pagina" :key="linha.matricula_aluno">
          <td>{{ linha.numero_chamada }}</td>
          <td>{{ linha.matricula_aluno }}</td>
          <td class="nome">{{ linha.nome_aluno }}</td>
          <td v-for="(letra, indice) in linha.respostas" :key="indice" class="letra">{{ letra }}</td>
        </tr>
      </tbody>
    </table>
  </section>
</template>

<script>
import logos from "@/assets/templates/cartao-resposta.png";
import { linhasGabarito, paginarGabarito } from "@/utils/gabaritoTurma";

export default {
  name: "GabaritoTurma",
  props: {
    prova: { type: Object, required: true },
    turma: { type: String, required: true },
    alunos: { type: Array, required: true },
  },
  data: () => ({ logos }),
  computed: {
    linhas() { return linhasGabarito(this.alunos); },
    paginas() { return paginarGabarito(this.linhas); },
    quantidade() { return Math.max(0, ...this.linhas.map((linha) => linha.respostas.length)); },
    dataAplicacao() { return new Date(`${this.prova.data_de_aplicacao}T00:00:00`).toLocaleDateString("pt-BR"); },
  },
};
</script>

<style scoped>
.gabarito-folha { box-sizing: border-box; width: 186mm; max-width: 100%; min-height: 273mm; margin: 20px auto; padding: 12px; background: white; color: black; box-shadow: 0 4px 20px #0002; font: 10pt Arial, sans-serif; }
.gabarito-instituicao { display: flex; align-items: center; justify-content: space-between; gap: 12px; min-height: 18mm; }
.logo-fve { flex-shrink: 0; width: 30mm; height: 9mm; }
.logo-univap { flex-shrink: 0; width: 23mm; height: 13mm; }
.gabarito-titulo { flex: 1; text-align: center; }
.gabarito-titulo h2 { margin: 0; font-size: 11pt; font-weight: 700; }
.gabarito-titulo p { margin: 0; text-transform: uppercase; }
.gabarito-identificacao { display: flex; justify-content: space-between; gap: 10px; margin: 5mm 0 2mm; text-transform: uppercase; font-size: 9pt; line-height: 1.4; }
.gabarito-identificacao p { margin: 0; }
.gabarito-data { flex-shrink: 0; text-transform: none; font-size: 8pt; }
.gabarito-aviso { margin: 0 0 3mm; font-size: 8pt; font-style: italic; }
.gabarito-tabela { width: 100%; border-collapse: collapse; table-layout: fixed; }
.gabarito-tabela th, .gabarito-tabela td { box-sizing: border-box; border: .25mm solid #333; padding: .5mm 1mm; height: 6.2mm; text-align: center; font-size: 9pt; overflow-wrap: anywhere; }
.gabarito-tabela td.nome { text-align: left; }
.gabarito-tabela td.letra { font-weight: 700; }
.gabarito-tabela tbody tr:nth-child(odd) { background: #e9e9e9; }
.col-numero { width: 6%; }
.col-matricula { width: 14%; }
.col-nome { width: 36%; }
@media print {
  .gabarito-folha { min-height: 296mm; box-shadow: none; print-color-adjust: exact; -webkit-print-color-adjust: exact; }
  .gabarito-tabela thead { display: table-header-group; }
  .gabarito-tabela tr { break-inside: avoid; }
}
@media screen and (max-width: 600px) {
  .gabarito-folha { overflow-x: auto; }
  .gabarito-cabecalho, .gabarito-tabela { min-width: 170mm; }
}
</style>
