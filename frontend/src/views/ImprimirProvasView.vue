<template>
  <div class="impressao-container">
    <header class="impressao-acoes">
      <button class="btn-secundario" :disabled="imprimindo" @click="$router.push('/provas')">← Voltar</button>
      <h2>Impressão individualizada</h2>
      <button class="btn-primario" :disabled="carregando || imprimindo || Boolean(erro) || !versoes.length" @click="imprimir">
        {{ imprimindo ? 'Preparando...' : 'Imprimir provas' }}
      </button>
    </header>
    <p v-if="carregando" class="mensagem">Carregando versões individuais...</p>
    <p v-if="erro" class="mensagem mensagem-erro" role="alert">{{ erro }}</p>
    <p v-if="!carregando && !erro && !versoes.length" class="mensagem">Nenhuma versão individual disponível. Confira os alunos vinculados à prova.</p>
    <main class="versoes">
      <template v-for="grupo in turmas" :key="grupo.turma">
        <ListaTurma :prova="prova" :turma="grupo.turma" :alunos="grupo.alunos" tipo="notas" />
        <ListaTurma :prova="prova" :turma="grupo.turma" :alunos="grupo.alunos" tipo="entrega" />
        <section v-for="versao in grupo.alunos" :key="versao.id_prova_aluno" class="versao-aluno documento-impressao">
        <PreviewProva :template="template" :metadados="metadados" :professor="prova.professor.nome"
          :matricula="versao.matricula_aluno" :questoes="versao.questoes">
          <template #cabecalho>
            <CartaoResposta :prova="{ ...prova, id_turma: grupo.turma }" :matricula="versao.matricula_aluno" :nomeAluno="versao.nome_aluno" :qrCode="versao.qrCode" />
            <p class="orientacao-cartao">Preencha todo o retângulo de uma alternativa em cada questão de 1 a {{ versao.questoes.length }}. Deixe as demais colunas em branco.</p>
          </template>
        </PreviewProva>
        </section>
      </template>
    </main>
  </div>
</template>

<script>
import QRCode from "qrcode";
import CartaoResposta from "@/components/CartaoResposta.vue";
import PreviewProva from "@/components/PreviewProva.vue";
import { buscarProva, imprimirProvas, provaEditavel } from "@/services/provas";
import { obterTemplateProva } from "@/services/templates";
import { questaoDoBanco } from "@/stores/provaDraft";
import { CARTAO_RESPOSTA } from "@/utils/cartaoResposta";
import ListaTurma from "@/components/ListaTurma.vue";
import { agruparVersoesPorTurma } from "@/utils/listasTurma";

export default {
  name: "ImprimirProvasView",
  components: { CartaoResposta, PreviewProva, ListaTurma },
  props: { id: { type: String, required: true } },
  data: () => ({ prova: null, template: "", versoes: [], turmas: [], carregando: true, imprimindo: false, erro: "" }),
  computed: {
    metadados() {
      if (!this.prova) return {};
      return { ...this.prova, ...this.prova.disciplina,
        turmasTexto: (Array.isArray(this.prova.id_turma) ? this.prova.id_turma : [this.prova.id_turma]).join("\n") };
    },
  },
  async mounted() { await this.carregar(); },
  methods: {
    async carregar() {
      this.carregando = true; this.erro = ""; this.versoes = []; this.turmas = [];
      try {
        const [prova, dados, template] = await Promise.all([buscarProva(this.id), imprimirProvas(this.id), obterTemplateProva()]);
        if (!prova || provaEditavel(prova)) throw new Error("Conclua e envie a prova antes de imprimir.");
        if (!Array.isArray(dados.provas_alunos)) throw new Error("O servidor retornou versões inválidas.");
        this.prova = prova; this.template = template;
        const versoes = await Promise.all(dados.provas_alunos.map(async (versao) => {
          if (!versao.id_prova_aluno || !versao.questoes?.length || versao.questoes.length > 10) {
            throw new Error("Uma versão está sem identificador ou fora do limite de 1 a 10 questões.");
          }
          if (prova.quantidade_questoes && versao.questoes.length !== prova.quantidade_questoes) {
            throw new Error("Uma versão não possui a quantidade de questões definida pelo processo pedagógico.");
          }
          return { ...versao, questoes: versao.questoes.map(questaoDoBanco),
            qrCode: await QRCode.toDataURL(versao.id_prova_aluno, { errorCorrectionLevel: "M", margin: CARTAO_RESPOSTA.qr.margem, width: 256 }) };
        }));
        this.turmas = agruparVersoesPorTurma(versoes, prova.id_turma);
        this.versoes = versoes;
      } catch (error) { this.erro = error?.details || error?.message || "Não foi possível montar a impressão."; }
      finally { this.carregando = false; }
    },
    async imprimir() {
      if (this.carregando || this.imprimindo || this.erro || !this.versoes.length) return;
      this.imprimindo = true;
      try {
        await this.$nextTick();
        await document.fonts.ready;
        // Inclui figuras das questões e as imagens do cartão SVG antes de abrir a impressão.
        await Promise.all([...document.querySelectorAll('.versoes img, .versoes image')].map((elemento) => {
          const imagem = new Image();
          imagem.src = elemento.currentSrc || elemento.src || elemento.href.baseVal;
          return imagem.decode();
        }));
        window.print();
      } catch (_) { this.erro = "Uma imagem não carregou. Atualize a página antes de imprimir."; }
      finally { this.imprimindo = false; }
    },
  },
};
</script>

<style scoped>
.impressao-container { padding: 20px; }
.impressao-acoes { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 16px; border-bottom: 2px solid #00488b; padding-bottom: 15px; }
.impressao-acoes h2 { font-size: 22px; }
.btn-primario, .btn-secundario { border: 0; border-radius: 6px; padding: 10px 16px; cursor: pointer; font-weight: 600; }
.btn-primario { background: #00488b; color: white; }
.btn-secundario { background: #eee; color: #333; }
button:disabled { opacity: .5; cursor: not-allowed; }
.mensagem { margin: 20px 0; text-align: center; }
.mensagem-erro { color: #c0392b; }
.versao-aluno { margin: 20px auto; }
.orientacao-cartao { font-size: 11px; margin: 8px 0 14px; }
@media screen {
  .versao-aluno :deep(.cartao-resposta) { width: 98%; height: auto; }
}
</style>

<style>
@media print {
  /* Sem margens de página, o navegador não reserva espaço para URL e paginação. */
  @page { size: A4; margin: 0; }
  html, body { margin: 0 !important; padding: 0 !important; background: white !important; color: black !important; }
  .app-container { display: block !important; min-height: 0 !important; }
  .sidebar, .conteudo-principal > .header, .modal-overlay { display: none !important; }
  .conteudo-principal { margin: 0 !important; min-height: 0 !important; }
  .conteudo { padding: 0 !important; }
  .impressao-container { padding: 0 !important; }
  .impressao-acoes, .impressao-container > .mensagem { display: none !important; }
  /* As listas mantêm seu modelo. As margens das provas pertencem à folha compartilhada. */
  .documento-impressao { box-sizing: border-box; width: 100% !important; max-width: none !important; padding: 9.5mm !important; margin: 0 !important; box-shadow: none !important; -webkit-box-decoration-break: clone; box-decoration-break: clone; break-after: page; }
  .versao-aluno.documento-impressao { padding: 0 !important; }
  .documento-impressao:last-child { break-after: auto; }
}
</style>
