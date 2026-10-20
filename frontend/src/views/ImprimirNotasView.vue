<template>
  <div class="impressao-notas-container">
    <div class="organizacao-notas" :aria-busy="carregando || imprimindo">
      <div class="page-header">
        <div class="cabecalho-conteudo">
          <div><h2>Organizar folhas para impressão das notas</h2><p>Confira a sequência, ajuste o alinhamento e prepare a impressão.</p></div>
          <button class="btn-secundario btn-voltar" :disabled="imprimindo" @click="$router.push('/provas/corrigir')">← Voltar à correção</button>
        </div>
        <div class="header-line"></div>
      </div>
      <div v-if="carregando" class="estado-carregando painel" role="status"><span class="carregando" aria-hidden="true"></span>Carregando lote...</div>
      <p v-if="erro" class="erro" role="alert">{{ erro }}</p>
      <template v-if="lote">
        <section class="resumo-lote painel" aria-label="Resumo do lote">
          <div class="resumo-identificacao">
            <span class="resumo-icone" aria-hidden="true"><svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9zM14 3v6h6M8 13h8M8 17h5" /></svg></span>
            <div><h3>Seu lote de notas</h3><p class="ajuda">Salvo em {{ new Date(lote.criado_em).toLocaleString('pt-BR') }}</p><span class="lote-id">Lote {{ lote._id }}</span></div>
          </div>
          <div class="resumo-indicadores"><span class="total-folhas"><strong>{{ lote.itens.length }}</strong> {{ lote.itens.length === 1 ? 'folha' : 'folhas' }}</span><span class="etiqueta-status" :class="lote.imprimivel ? 'pronto' : 'pendente'">{{ lote.imprimivel ? 'Lote pronto' : 'Há pendências' }}</span></div>
        </section>
        <p v-if="!lote.imprimivel" class="erro" role="alert">Este lote tem cartões pendentes e não pode ser impresso. Resolva as falhas e corrija novamente o conjunto completo, na mesma ordem. Nenhuma folha será removida silenciosamente da sequência.</p>
        <div class="grade-organizacao">
          <section class="painel painel-sequencia" aria-labelledby="titulo-sequencia">
            <div class="painel-cabecalho"><span class="passo" aria-hidden="true">1</span><div><h3 id="titulo-sequencia">Confira a ordem das folhas</h3><p>Separe <strong>somente as folhas que contêm o gabarito</strong> e organize-as na sequência abaixo.</p></div></div>
            <p class="sequencia-orientacao">A ordem é a das imagens enviadas, não a ordem alfabética nem a de conclusão da correção.</p>
            <div class="tabela-container" tabindex="0" role="region" aria-label="Sequência das folhas do lote">
              <table>
                <thead><tr><th scope="col">Ordem da folha</th><th scope="col">Nome</th><th scope="col">Matrícula</th><th scope="col">Turma</th><th scope="col">Nota</th></tr></thead>
                <tbody><tr v-for="item in lote.itens" :key="item.posicao" :class="{ 'linha-pendente': !item.corrigida }">
                  <td><span class="numero-folha">{{ item.posicao }}</span></td><td class="nome-aluno">{{ item.nome || 'Aluno não identificado' }}</td><td class="matricula-aluno">{{ item.matricula ?? '—' }}</td><td>{{ item.turma || '—' }}</td>
                  <td><span class="nota-folha" :class="{ pendente: !item.corrigida }">{{ item.corrigida ? formatarNota(item.nota_prova) : 'Pendente' }}</span></td>
                </tr></tbody>
              </table>
            </div>
          </section>
          <aside class="paineis-preparo" aria-label="Preparação da impressora">
            <section class="painel" aria-labelledby="titulo-impressora">
              <div class="painel-cabecalho"><span class="passo" aria-hidden="true">2</span><h3 id="titulo-impressora">Prepare a impressora</h3></div>
              <div class="configuracao-impressora"><span>A4</span><span>100% · tamanho real</span><span>Somente frente</span><span>1 página por folha</span></div>
              <p class="texto-orientacao">Desative cabeçalhos, rodapés e ordem inversa. Confira a orientação e qual folha será alimentada primeiro.</p>
              <p class="ajuda">Serão impressos apenas os números das notas, sem cabeçalho ou QR Code.</p>
            </section>
            <section class="painel" aria-labelledby="titulo-alinhamento">
              <div class="painel-cabecalho"><span class="passo" aria-hidden="true">3</span><h3 id="titulo-alinhamento">Ajuste o alinhamento</h3></div>
              <p class="texto-orientacao">Deixe ambos em zero no primeiro teste.</p>
              <div class="ajustes">
                <label for="ajuste-horizontal">Horizontal <span>(mm)</span><input id="ajuste-horizontal" v-model.number="ajusteX" type="number" min="-10" max="10" step="0.5" :disabled="imprimindo" aria-describedby="ajuda-alinhamento" /></label>
                <label for="ajuste-vertical">Vertical <span>(mm)</span><input id="ajuste-vertical" v-model.number="ajusteY" type="number" min="-10" max="10" step="0.5" :disabled="imprimindo" aria-describedby="ajuda-alinhamento" /></label>
              </div>
              <p id="ajuda-alinhamento" class="ajuda">Valores positivos movem a nota para a direita/baixo; negativos para a esquerda/cima. Ajustes entre −10 e 10 mm.</p>
              <p v-if="!ajustesValidos" class="erro" role="alert">Informe ajustes numéricos entre −10 e 10 mm.</p>
            </section>
          </aside>
        </div>
        <section class="painel painel-imprimir" aria-labelledby="titulo-finalizar">
          <div class="painel-cabecalho"><span class="icone-impressora" aria-hidden="true"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M7 8V3h10v5M7 17H4V9h16v8h-3M7 14h10v7H7zM16 11h1" /></svg></span><h3 id="titulo-finalizar">Teste antes de imprimir o lote</h3></div>
          <p class="aviso">Faça primeiro um teste em uma cópia descartável do gabarito. O teste imprime somente a nota da primeira posição. Não envie o lote inteiro antes de conferir o alinhamento e a alimentação do papel.</p>
          <label class="conferencia" :class="{ conferida: conferido }"><input v-model="conferido" type="checkbox" :disabled="imprimindo || !lote.imprimivel" /> Conferi nomes, matrículas e turmas e organizei as folhas exatamente na ordem indicada.</label>
          <div class="rodape-impressao">
            <p class="ajuda">O lote preserva as notas deste envio. Reimprimir não corrige novamente nem altera dados. Abrir ou cancelar o diálogo não confirma impressão física.</p>
            <div class="acoes">
              <button class="btn-secundario" :disabled="!lote.imprimivel || !ajustesValidos || imprimindo" @click="imprimir(true)">Imprimir teste (1 folha)</button>
              <button class="btn-primario" :disabled="!lote.imprimivel || !conferido || !ajustesValidos || imprimindo" @click="imprimir(false)">{{ imprimindo ? 'Preparando...' : `Imprimir notas (${lote.itens.length} folhas)` }}</button>
            </div>
          </div>
        </section>
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
.impressao-notas-container { --superficie: #fff; --borda: #e0e6ed; --texto-suave: #637180; --fundo-suave: #f7f9fc; --azul-suave: #edf4fb; --azul-texto: #00488b; max-width: 1280px; margin: auto; padding: 28px; color: #263545; }
.page-header { margin-bottom: 24px; }
.cabecalho-conteudo { display: flex; align-items: center; justify-content: space-between; gap: 24px; margin-bottom: 20px; }
.page-header h2 { font-size: 28px; font-weight: 600; line-height: 1.3; margin: 0; }
.page-header p { margin: 8px 0 0; color: var(--texto-suave); font-size: 14px; }
.header-line { height: 2px; background: linear-gradient(90deg, #00488b 0%, #00488b 50%, transparent 100%); }
p { margin: 0; line-height: 1.6; }
h3 { margin: 0; font-size: 17px; font-weight: 600; line-height: 1.4; }
.painel { box-sizing: border-box; min-width: 0; padding: 24px; border: 1px solid var(--borda); border-radius: 12px; background: var(--superficie); box-shadow: 0 2px 8px #00488b05; }
.resumo-lote { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 20px; margin-bottom: 24px; background: linear-gradient(110deg, var(--azul-suave), var(--superficie)); }
.resumo-identificacao { display: flex; align-items: center; gap: 16px; min-width: 0; }
.resumo-identificacao > div { min-width: 0; }
.resumo-identificacao h3 { font-size: 18px; }
.resumo-icone { display: flex; align-items: center; justify-content: center; width: 52px; height: 52px; flex-shrink: 0; border-radius: 12px; background: #00488b; color: #fff; }
.resumo-identificacao .ajuda { margin-top: 4px; }
.lote-id { display: block; margin-top: 2px; color: var(--texto-suave); font-size: 11px; overflow-wrap: anywhere; }
.resumo-indicadores { display: flex; align-items: center; gap: 24px; }
.total-folhas { display: flex; align-items: baseline; gap: 8px; color: var(--texto-suave); font-size: 13px; white-space: nowrap; }
.total-folhas strong { font-size: 32px; font-weight: 600; line-height: 1; color: var(--azul-texto); font-variant-numeric: tabular-nums; }
.etiqueta-status { padding: 6px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; white-space: nowrap; }
.pronto { color: #1e7038; background: #e2f4e8; }
.pendente { color: #936817; background: #fff3d8; }
.grade-organizacao { display: grid; grid-template-columns: minmax(0, 1fr) 340px; align-items: start; gap: 24px; margin-bottom: 24px; }
.paineis-preparo { display: grid; gap: 20px; min-width: 0; }
.painel-cabecalho { display: flex; align-items: center; gap: 12px; margin-bottom: 18px; }
.painel-cabecalho p { margin-top: 6px; font-size: 13px; color: var(--texto-suave); }
.passo { display: flex; align-items: center; justify-content: center; width: 30px; height: 30px; flex-shrink: 0; border-radius: 9px; background: var(--azul-suave); color: var(--azul-texto); font-size: 14px; font-weight: 600; }
.painel-sequencia { padding: 24px 0 0; overflow: hidden; }
.painel-sequencia .painel-cabecalho { padding: 0 24px; align-items: flex-start; }
.sequencia-orientacao { margin: 0 24px 20px; padding: 10px 12px; border-radius: 6px; background: var(--fundo-suave); color: var(--texto-suave); font-size: 12px; }
.tabela-container { overflow: auto; max-height: 560px; border-top: 1px solid var(--borda); }
table { width: 100%; border-collapse: separate; border-spacing: 0; font-size: 13px; }
th, td { padding: 16px; border-bottom: 1px solid var(--borda); text-align: left; vertical-align: middle; }
th { position: sticky; top: 0; z-index: 1; background: var(--fundo-suave); color: var(--texto-suave); font-size: 11px; font-weight: 600; white-space: nowrap; }
td:first-child, th:first-child { padding-left: 24px; }
td:last-child, th:last-child { padding-right: 24px; text-align: right; }
tbody tr:last-child td { border-bottom: 0; }
tbody tr:hover { background: var(--fundo-suave); }
.numero-folha { display: inline-flex; align-items: center; justify-content: center; min-width: 28px; height: 28px; padding: 0 5px; box-sizing: border-box; border-radius: 7px; background: var(--azul-suave); color: var(--azul-texto); font-weight: 600; font-variant-numeric: tabular-nums; }
.nome-aluno { font-weight: 600; min-width: 120px; }
.matricula-aluno { color: var(--texto-suave); font-variant-numeric: tabular-nums; }
.nota-folha { display: inline-block; min-width: 40px; padding: 5px 8px; border-radius: 6px; background: #e2f4e8; color: #1e7038; font-weight: 600; text-align: center; font-variant-numeric: tabular-nums; }
.nota-folha.pendente { background: #fff3d8; color: #936817; }
.configuracao-impressora { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 16px; }
.configuracao-impressora span { padding: 5px 9px; border: 1px solid var(--borda); border-radius: 6px; color: var(--azul-texto); font-size: 12px; background: var(--fundo-suave); }
.texto-orientacao { margin-bottom: 12px; color: var(--texto-suave); font-size: 13px; }
.ajuda { font-size: 12px; color: var(--texto-suave); }
.ajustes { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; margin: 16px 0; }
.ajustes label { font-size: 13px; font-weight: 600; }
.ajustes label > span { color: var(--texto-suave); font-weight: 400; }
.ajustes input { display: block; width: 100%; box-sizing: border-box; margin-top: 8px; padding: 11px 12px; border: 1px solid #bdcbd9; border-radius: 8px; background: var(--superficie); color: inherit; font: inherit; font-variant-numeric: tabular-nums; }
.ajustes input:focus { outline: 2px solid #00488b30; border-color: #00488b; }
.icone-impressora { display: flex; align-items: center; color: var(--azul-texto); }
.aviso { padding: 14px 16px; margin-bottom: 20px; border: 1px solid #ecdcb3; border-left: 3px solid #ba8b27; border-radius: 8px; background: #fffaf0; color: #795a20; font-size: 13px; }
.erro { padding: 14px 16px; margin: 16px 0; border: 1px solid #f1c8c5; border-radius: 8px; background: #fff4f3; color: #a32e24; font-size: 13px; }
.conferencia { display: flex; align-items: flex-start; gap: 12px; padding: 16px; border: 1px solid var(--borda); border-radius: 8px; background: var(--fundo-suave); font-size: 14px; line-height: 1.6; cursor: pointer; }
.conferencia.conferida { border-color: #86b99a; background: #f1faf4; }
.conferencia input { flex-shrink: 0; width: 17px; height: 17px; margin: 3px 0 0; accent-color: #00488b; }
.rodape-impressao { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 24px; margin-top: 24px; }
.rodape-impressao > .ajuda { flex: 1 1 260px; max-width: 440px; }
.acoes { display: flex; flex-wrap: wrap; gap: 12px; }
.btn-primario, .btn-secundario { padding: 12px 18px; border-radius: 8px; cursor: pointer; font: inherit; font-size: 13px; font-weight: 600; line-height: 1.4; transition: background .2s, border-color .2s; }
.btn-primario { border: 1px solid #00488b; background: #00488b; color: white; }
.btn-primario:hover:not(:disabled) { background: #0066cc; border-color: #0066cc; }
.btn-secundario { border: 1px solid #b5c9dd; background: var(--superficie); color: var(--azul-texto); }
.btn-secundario:hover:not(:disabled) { border-color: #00488b; background: var(--azul-suave); }
.btn-voltar { flex-shrink: 0; }
button:disabled { opacity: .5; cursor: not-allowed; }
button:focus-visible, .tabela-container:focus-visible, .conferencia:has(input:focus-visible) { outline: 2px solid #00488b; outline-offset: 3px; }
.estado-carregando { display: flex; align-items: center; justify-content: center; gap: 12px; min-height: 180px; color: var(--texto-suave); }
.carregando { width: 20px; height: 20px; border: 2px solid #c9d9e9; border-top-color: #00488b; border-radius: 50%; animation: girar 1s linear infinite; }
@keyframes girar { to { transform: rotate(360deg); } }
@media (prefers-reduced-motion: reduce) { .carregando { animation: none; } .btn-primario, .btn-secundario { transition: none; } }
@media (max-width: 1024px) { .grade-organizacao { grid-template-columns: 1fr; } .paineis-preparo { grid-template-columns: repeat(2, minmax(0, 1fr)); align-items: start; } }
@media (max-width: 640px) {
  .impressao-notas-container { padding: 20px 16px; }
  .cabecalho-conteudo { align-items: flex-start; flex-direction: column; gap: 16px; }
  .page-header h2 { font-size: 23px; }
  .painel { padding: 20px; }
  .painel-sequencia { padding: 20px 0 0; }
  .painel-sequencia .painel-cabecalho { padding: 0 20px; }
  .sequencia-orientacao { margin-left: 20px; margin-right: 20px; }
  .paineis-preparo { grid-template-columns: 1fr; }
  .resumo-indicadores { width: 100%; justify-content: space-between; }
  .acoes, .acoes button { width: 100%; }
}
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
