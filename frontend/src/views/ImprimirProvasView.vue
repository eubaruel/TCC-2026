<template>
  <div class="impressao-container">
    <header class="impressao-acoes">
      <button class="btn-secundario" @click="$router.push('/provas')">← Voltar</button>
      <h2>Impressão individualizada</h2>
      <button class="btn-primario" :disabled="carregando || imprimindo || Boolean(erro) || !versoes.length" @click="imprimir">
        {{ imprimindo ? 'Preparando...' : 'Imprimir provas' }}
      </button>
    </header>
    <p v-if="carregando" class="mensagem">Carregando versões individuais...</p>
    <p v-if="erro" class="mensagem mensagem-erro" role="alert">{{ erro }}</p>
    <p v-if="!carregando && !erro && !versoes.length" class="mensagem">Nenhuma versão individual disponível. Confira os alunos vinculados à prova.</p>
    <p v-if="versoes.length" class="mensagem instrucoes">
      {{ versoes.length }} versão(ões). Imprima em A4, escala 100%, sem cabeçalhos e rodapés do navegador.
      Para corrigir, recorte o cartão inteiro, preservando sua borda e o QR Code.
    </p>
    <main class="versoes">
      <section v-for="versao in versoes" :key="versao.id_prova_aluno" class="versao-aluno">
        <CartaoResposta :prova="prova" :matricula="versao.matricula_aluno" :qrCode="versao.qrCode" />
        <p class="orientacao-cartao">Preencha todo o retângulo de uma alternativa em cada questão de 1 a {{ versao.questoes.length }}. Deixe as demais colunas em branco.</p>
        <PreviewProva :template="template" :metadados="metadados" :professor="prova.professor.nome"
          :matricula="versao.matricula_aluno" :questoes="versao.questoes" />
      </section>
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

export default {
  name: "ImprimirProvasView",
  components: { CartaoResposta, PreviewProva },
  props: { id: { type: String, required: true } },
  data: () => ({ prova: null, template: "", versoes: [], carregando: true, imprimindo: false, erro: "" }),
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
      this.carregando = true; this.erro = ""; this.versoes = [];
      try {
        const [prova, dados, template] = await Promise.all([buscarProva(this.id), imprimirProvas(this.id), obterTemplateProva()]);
        if (!prova || provaEditavel(prova)) throw new Error("Conclua e envie a prova antes de imprimir.");
        if (!Array.isArray(dados.provas_alunos)) throw new Error("O servidor retornou versões inválidas.");
        this.prova = prova; this.template = template;
        this.versoes = await Promise.all(dados.provas_alunos.map(async (versao) => {
          if (!versao.id_prova_aluno || !versao.questoes?.length || versao.questoes.length > 10) {
            throw new Error("Uma versão está sem identificador ou fora do limite de 1 a 10 questões.");
          }
          return { ...versao, questoes: versao.questoes.map(questaoDoBanco),
            qrCode: await QRCode.toDataURL(versao.id_prova_aluno, { errorCorrectionLevel: "M", margin: 4, width: 256 }) };
        }));
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
.impressao-acoes { display: flex; align-items: center; justify-content: space-between; gap: 16px; border-bottom: 2px solid #00488b; padding-bottom: 15px; }
.impressao-acoes h2 { font-size: 22px; }
.btn-primario, .btn-secundario { border: 0; border-radius: 6px; padding: 10px 16px; cursor: pointer; font-weight: 600; }
.btn-primario { background: #00488b; color: white; }
.btn-secundario { background: #eee; color: #333; }
button:disabled { opacity: .5; cursor: not-allowed; }
.mensagem { margin: 20px 0; text-align: center; }
.mensagem-erro { color: #c0392b; }
.versao-aluno { width: 186mm; max-width: 100%; margin: 20px auto; padding: 12px; background: white; color: #222; box-shadow: 0 4px 20px #0002; }
.orientacao-cartao { font-size: 11px; margin: 8px 0 14px; }
</style>

<style>
@media print {
  @page { size: A4; margin: 12mm; }
  html, body { background: white !important; color: black !important; }
  .impressao-container { padding: 0 !important; }
  .impressao-acoes, .impressao-container > .mensagem { display: none !important; }
  .versao-aluno { width: 100% !important; max-width: none !important; padding: 0 !important; margin: 0 !important; box-shadow: none !important; break-after: page; }
  .versao-aluno:last-child { break-after: auto; }
}
</style>
