<template>
  <section v-for="(pagina, indicePagina) in paginas" :key="indicePagina" class="lista-turma-folha documento-impressao" :class="tipo" :aria-label="`${tipo === 'notas' ? 'Planilha de notas' : 'Relatório de entrega'} — ${turma} — página ${indicePagina + 1}`">
    <header class="lista-cabecalho">
      <div class="lista-instituicao">
        <svg class="logo-fve" viewBox="16 18 288 72" role="img" aria-label="Fundação Valeparaibana de Ensino">
          <image :href="logos" width="2400" height="504" />
        </svg>
        <div v-if="tipo === 'notas'" class="instituicao-nome">
          <strong>Colégio Técnico Antônio Teixeira Fernandes</strong>
          <strong>Colégios Univap - Unidade Centro</strong>
        </div>
        <div v-else class="entrega-titulo">
          <h2>RELATÓRIO DE ENTREGA - AVALIAÇÃO OBJETIVA</h2>
          <p>{{ prova.periodo_letivo }}</p>
        </div>
        <svg class="logo-univap" viewBox="2040 5 176 92" role="img" aria-label="Colégios Univap">
          <image :href="logos" width="2400" height="504" />
        </svg>
      </div>
      <h2 v-if="tipo === 'notas'" class="notas-titulo">PLANILHA DE NOTAS - AVALIAÇÃO OBJETIVA - {{ ano }}</h2>
      <div v-else class="turma-faixa">{{ turma }}</div>
      <div class="lista-identificacao">
        <div>
          <p v-if="tipo === 'notas'"><strong>TURMA: {{ turma }}</strong></p>
          <p><strong>DISCIPLINA: {{ prova.disciplina.nome_disciplina }}</strong></p>
          <p><strong>PROFESSOR (A): {{ prova.professor.nome }}</strong></p>
        </div>
        <div v-if="tipo === 'notas'" class="lista-data">
          <p><strong>Data da Aplicação: {{ dataAplicacao }}</strong></p>
          <p><strong>{{ prova.periodo_letivo }}</strong></p>
        </div>
      </div>
    </header>
    <table class="lista-alunos">
      <colgroup>
        <col class="col-numero" /><col class="col-matricula" /><col class="col-nome" /><col class="col-assinatura" />
        <col v-if="tipo === 'notas'" class="col-nota" />
      </colgroup>
      <thead><tr><th scope="col">Nº</th><th scope="col">MATRÍCULA</th><th scope="col">{{ tipo === 'notas' ? 'NOME DO ALUNO' : 'NOME' }}</th><th scope="col">ASSINATURA</th><th v-if="tipo === 'notas'" scope="col">NOTA</th></tr></thead>
      <tbody>
        <tr v-for="aluno in pagina" :key="aluno.matricula_aluno">
          <td>{{ aluno.numero_chamada }}</td><td>{{ aluno.matricula_aluno }}</td><td>{{ aluno.nome_aluno }}</td><td class="assinatura-aluno"></td><td v-if="tipo === 'notas'" class="nota-aluno"></td>
        </tr>
      </tbody>
    </table>
    <footer v-if="tipo === 'notas'" class="lista-rodape notas-rodape">
      <div class="datas-controle"><div>Data Entrega para Proc. Pedagógico:</div><div>Data Lançamento no Sistema:</div></div>
      <div class="assinatura-professor">Assinatura do Professor (a):</div>
    </footer>
    <footer v-else class="lista-rodape entrega-rodape"><div>Assinatura do Professor (a)</div></footer>
  </section>
</template>

<script>
import logos from "@/assets/templates/cartao-resposta.png";

export default {
  name: "ListaTurma",
  props: {
    prova: { type: Object, required: true },
    turma: { type: String, required: true },
    alunos: { type: Array, required: true },
    tipo: { type: String, required: true },
  },
  data: () => ({ logos }),
  computed: {
    paginas() {
      const paginas = [];
      for (let inicio = 0; inicio < this.alunos.length; inicio += 28) paginas.push(this.alunos.slice(inicio, inicio + 28));
      return paginas;
    },
    ano() { return this.prova.data_de_aplicacao.slice(0, 4); },
    dataAplicacao() { return new Date(`${this.prova.data_de_aplicacao}T00:00:00`).toLocaleDateString("pt-BR"); },
  },
};
</script>

<style scoped>
.lista-turma-folha { box-sizing: border-box; width: 186mm; max-width: 100%; min-height: 273mm; margin: 20px auto; padding: 12px; display: flex; flex-direction: column; background: white; color: black; box-shadow: 0 4px 20px #0002; font: 10pt Arial, sans-serif; }
.lista-instituicao { display: flex; align-items: center; justify-content: space-between; gap: 12px; min-height: 18mm; }
.logo-fve { flex-shrink: 0; width: 30mm; height: 9mm; }
.logo-univap { flex-shrink: 0; width: 23mm; height: 13mm; }
.instituicao-nome, .entrega-titulo { flex: 1; text-align: center; }
.instituicao-nome { font-size: 8pt; line-height: 1.4; }
.instituicao-nome strong { display: block; }
h2 { margin: 0; font-size: 11pt; line-height: 1.4; font-weight: 700; }
.notas-titulo { margin: 5mm 0 7mm; text-align: center; text-decoration: underline; }
.entrega-titulo h2 { font-size: 10.5pt; font-weight: 400; }
.entrega-titulo p { margin: 0; text-transform: uppercase; }
.turma-faixa { margin: 5mm 0; padding: 2mm; background: #222; color: white; text-align: center; font-size: 13pt; font-weight: 700; text-transform: uppercase; }
.lista-identificacao { display: flex; align-items: flex-start; justify-content: space-between; gap: 10px; margin-bottom: 4mm; text-transform: uppercase; font-size: 9pt; line-height: 1.4; }
.lista-identificacao p { margin: 0; }
.lista-data { flex-shrink: 0; text-align: right; font-size: 8pt; }
.lista-data p:first-child { text-transform: none; }
.lista-alunos { width: 100%; border-collapse: collapse; table-layout: fixed; }
.lista-alunos th, .lista-alunos td { border: .25mm solid #333; padding: 1mm; text-align: center; overflow-wrap: anywhere; }
.lista-alunos th { box-sizing: border-box; height: 6mm; padding: .5mm; font-size: 9pt; }
.lista-alunos td { box-sizing: border-box; height: 6.2mm; padding: .4mm 1mm; font-size: 9pt; line-height: 1.15; }
.lista-alunos tbody tr:nth-child(odd) { background: #e9e9e9; }
.col-numero { width: 5%; }
.col-matricula { width: 14%; }
.col-nome { width: 43%; }
.col-assinatura { width: 28%; }
.col-nota { width: 10%; }
.entrega .col-nome { width: 46%; }
.entrega .col-assinatura { width: 35%; }
.lista-rodape { margin-top: auto; padding-top: 7mm; font-size: 9pt; }
.datas-controle { display: grid; grid-template-columns: 1fr 1fr; border: .25mm solid #333; }
.datas-controle > div { min-height: 8mm; padding: 1mm; }
.datas-controle > div + div { border-left: .25mm solid #333; }
.assinatura-professor { min-height: 12mm; padding: 1mm; border: .25mm solid #333; border-top: 0; }
.entrega-rodape { padding-top: 12mm; }
.entrega-rodape > div { width: 55%; max-width: 100%; border-top: .25mm solid #333; padding-top: 2mm; }
@media print {
  .lista-turma-folha { min-height: 296mm; print-color-adjust: exact; -webkit-print-color-adjust: exact; }
  .lista-alunos thead { display: table-header-group; }
  .lista-alunos tr, .lista-rodape { break-inside: avoid; }
}
@media screen and (max-width: 600px) {
  .lista-turma-folha { overflow-x: auto; }
  .lista-cabecalho, .lista-alunos, .lista-rodape { min-width: 170mm; }
}
</style>
