<template>
  <div class="impressao-notas-container">
    <div class="organizacao-notas">
      <div class="page-header"><h2>Organizar folhas para impressão das notas</h2><div class="header-line"></div></div>
      <button class="btn-secundario" :disabled="imprimindo" @click="$router.push('/provas/corrigir')">← Voltar à correção</button>
      <p v-if="carregando">Carregando lote...</p>
      <p v-if="erro" class="erro" role="alert">{{ erro }}</p>
      <template v-if="lote">
        <p class="ajuda">Lote {{ lote._id }} · Salvo em {{ new Date(lote.criado_em).toLocaleString('pt-BR') }}</p>
        <p>Separe <strong>somente as folhas que contêm o gabarito</strong> e organize-as na sequência abaixo. A ordem é a das imagens enviadas, não a ordem alfabética nem a de conclusão da correção.</p>
        <p>Na impressora: A4, escala 100% (tamanho real), uma página por folha, somente frente, sem cabeçalhos/rodapés ou ordem inversa. Confira a orientação e qual folha será alimentada primeiro. Serão impressos apenas os números das notas, sem cabeçalho ou QR Code.</p>
        <p class="aviso">Faça primeiro um teste em uma cópia descartável do gabarito. O teste imprime somente a nota da primeira posição. Não envie o lote inteiro antes de conferir o alinhamento e a alimentação do papel.</p>
        <p v-if="!lote.imprimivel" class="erro" role="alert">Este lote tem cartões pendentes e não pode ser impresso. Resolva as falhas e corrija novamente o conjunto completo, na mesma ordem. Nenhuma folha será removida silenciosamente da sequência.</p>
        <div class="tabela-container">
          <table>
            <thead><tr><th>Ordem da folha</th><th>Nome</th><th>Matrícula</th><th>Turma</th><th>Nota</th></tr></thead>
            <tbody><tr v-for="item in lote.itens" :key="item.posicao">
              <td>{{ item.posicao }}</td><td>{{ item.nome || 'Aluno não identificado' }}</td><td>{{ item.matricula ?? '—' }}</td><td>{{ item.turma || '—' }}</td>
              <td>{{ item.corrigida ? formatarNota(item.nota_prova) : 'Pendente' }}</td>
            </tr></tbody>
          </table>
        </div>
        <div class="ajustes">
          <label>Ajuste horizontal (mm)<input v-model.number="ajusteX" type="number" min="-10" max="10" step="0.5" :disabled="imprimindo" /></label>
          <label>Ajuste vertical (mm)<input v-model.number="ajusteY" type="number" min="-10" max="10" step="0.5" :disabled="imprimindo" /></label>
        </div>
        <p class="ajuda">Deixe ambos em zero no primeiro teste. Valores positivos movem a nota para a direita/baixo; negativos para a esquerda/cima. Ajustes entre −10 e 10 mm.</p>
        <p v-if="!ajustesValidos" class="erro">Informe ajustes numéricos entre −10 e 10 mm.</p>
        <label class="conferencia"><input v-model="conferido" type="checkbox" :disabled="imprimindo || !lote.imprimivel" /> Conferi nomes, matrículas e turmas e organizei as folhas exatamente na ordem indicada.</label>
        <div class="acoes">
          <button class="btn-secundario" :disabled="!lote.imprimivel || !ajustesValidos || imprimindo" @click="imprimir(true)">Imprimir teste (1 folha)</button>
          <button class="btn-primario" :disabled="!lote.imprimivel || !conferido || !ajustesValidos || imprimindo" @click="imprimir(false)">{{ imprimindo ? 'Preparando...' : `Imprimir notas (${lote.itens.length} folhas)` }}</button>
        </div>
        <p class="ajuda">O lote preserva as notas deste envio. Reimprimir não corrige novamente nem altera dados. Abrir ou cancelar o diálogo não confirma impressão física.</p>
      </template>
    </div>
    <div class="notas-para-imprimir" aria-hidden="true">
      <section v-for="item in paginasImpressao" :key="item.posicao" class="folha-nota"><NotaSobreposta :nota="item.nota_prova" :ajusteX="ajusteX" :ajusteY="ajusteY" /></section>
    </div>
  </div>
</template>

<script>
import { buscarLoteCorrecao } from "@/services/correcao";
import { formatarNota, ajusteValido } from "@/utils/impressaoNotas";
import NotaSobreposta from "@/components/NotaSobreposta.vue";

export default {
  name: "ImprimirNotasView",
  components: { NotaSobreposta },
  props: { id: { type: String, required: true } },
  data: () => ({ lote: null, carregando: true, erro: "", conferido: false, imprimindo: false, teste: false, ajusteX: 0, ajusteY: 0 }),
  beforeRouteLeave() { return !this.imprimindo; },
  computed: {
    ajustesValidos() { return ajusteValido(this.ajusteX) && ajusteValido(this.ajusteY); },
    paginasImpressao() {
      if (!this.lote?.imprimivel || !this.ajustesValidos || (!this.conferido && !this.teste)) return [];
      return this.teste ? this.lote.itens.slice(0, 1) : this.lote.itens;
    },
  },
  async mounted() {
    try {
      const { lote } = await buscarLoteCorrecao(this.id);
      if (!lote || !Array.isArray(lote.itens) || !lote.itens.length || lote.itens.some((item, indice) => item.posicao !== indice + 1)) throw new Error("O servidor retornou um lote inválido.");
      lote.itens.filter((item) => item.corrigida).forEach((item) => formatarNota(item.nota_prova));
      if (lote.imprimivel && lote.itens.some((item) => !item.corrigida || !item.nome || !item.turma || item.matricula == null)) throw new Error("O lote não possui identificação e nota para todas as folhas.");
      this.lote = lote;
    } catch (error) { this.erro = error?.details || error?.message || "Não foi possível carregar o lote."; }
    finally { this.carregando = false; }
  },
  methods: {
    formatarNota,
    async imprimir(teste = false) {
      if (this.imprimindo || !this.lote?.imprimivel || !this.ajustesValidos || (!teste && !this.conferido)) return;
      this.imprimindo = true; this.teste = teste; this.erro = "";
      try { await this.$nextTick(); await document.fonts.ready; window.print(); }
      catch (_) { this.erro = "Não foi possível abrir a impressão. Tente novamente."; }
      finally { this.imprimindo = false; }
    },
  },
};
</script>

<style scoped>
.impressao-notas-container { max-width: 1200px; margin: auto; padding: 20px; }
.page-header h2 { font-size: 26px; margin: 0 0 15px; }
.header-line { height: 2px; background: linear-gradient(90deg, #00488b 0%, #00488b 50%, transparent 100%); margin-bottom: 24px; }
p { line-height: 1.6; }
.aviso { padding: 16px; border-left: 4px solid #00488b; background: #00488b12; }
.erro { color: #c0392b; }
.tabela-container { overflow-x: auto; margin: 24px 0; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 12px; border-bottom: 1px solid #ddd; text-align: left; }
th { color: #00488b; }
.ajustes, .acoes { display: flex; flex-wrap: wrap; gap: 16px; margin: 20px 0; }
.ajustes label { display: flex; flex-direction: column; gap: 8px; }
.ajustes input { width: 150px; padding: 10px; border: 1px solid #ccc; border-radius: 6px; background: transparent; color: inherit; }
.conferencia { display: flex; align-items: flex-start; gap: 10px; line-height: 1.5; }
.conferencia input { margin-top: 5px; }
.ajuda { font-size: 13px; color: #777; }
.btn-primario, .btn-secundario { padding: 12px 18px; border-radius: 6px; cursor: pointer; font-weight: 600; border: 1px solid #00488b; }
.btn-primario { background: #00488b; color: white; }
.btn-secundario { background: transparent; color: inherit; }
button:disabled { opacity: .5; cursor: not-allowed; }
.notas-para-imprimir { display: none; }
</style>

<style>
@media print {
  @page { size: A4; margin: 0; }
  html, body { margin: 0 !important; padding: 0 !important; background: white !important; }
  .impressao-notas-container { margin: 0 !important; padding: 0 !important; max-width: none !important; }
  .organizacao-notas { display: none !important; }
  .notas-para-imprimir { display: block !important; }
  .folha-nota { position: relative; box-sizing: border-box; width: 210mm; height: 296mm; margin: 0; padding: 0; break-after: page; overflow: hidden; }
  .folha-nota:last-child { break-after: auto; }
}
</style>
