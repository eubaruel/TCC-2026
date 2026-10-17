<template>
  <div class="correcao-container">
    <div class="page-header"><h2>Correção de provas</h2><div class="header-line"></div></div>
    <p>Selecione as imagens das páginas com o cartão-resposta. O recorte é automático e mantém as dez colunas e o QR Code.</p>
    <p>Se o cartão não for reconhecido com segurança, a imagem original será enviada, sem interromper o lote. Envie uma página por imagem (PNG ou JPEG), não PDF.</p>
    <div class="actions-bar">
      <input aria-label="Imagens dos cartões-resposta" type="file" accept="image/*" multiple :disabled="processando || salvandoLote" @change="selecionar" />
      <button class="btn-primario" :disabled="processando || salvandoLote || !arquivos.length" @click="corrigir">{{ processando ? 'Processando...' : 'Corrigir imagens' }}</button>
      <button class="btn-secundario" :disabled="processando || salvandoLote" @click="$router.push('/provas')">Voltar</button>
    </div>
    <p>{{ arquivos.length }} imagem(ns) selecionada(s).</p>
    <p v-if="processando || finalizado" role="status">
      Preparadas: {{ progresso.preparadas }} / {{ arquivos.length }}. Processadas: {{ progresso.processadas }} / {{ arquivos.length }}.
      Recortadas: {{ progresso.recortadas }}. Preservadas sem recorte: {{ progresso.preparadas - progresso.recortadas }}.
    </p>
    <p v-if="erro" class="erro" role="alert">{{ erro }}</p>
    <div v-if="idLote && !processando" class="actions-bar">
      <button class="btn-primario" @click="$router.push(`/provas/notas/${idLote}`)">Organizar folhas e imprimir notas do lote salvo</button>
    </div>
    <template v-if="finalizado">
      <p>{{ resultados.length }} corrigida(s), {{ erros.length }} não corrigida(s). Os resultados confirmados foram salvos no banco. Provas com correção bem-sucedida que estavam impressas passam para o status Corrigida, mesmo que ainda existam cartões pendentes. A impressão das notas só é liberada para um lote sem pendências.</p>
      <p v-if="erroLote" class="erro" role="alert">{{ erroLote }} A impressão deste envio permanece bloqueada.</p>
      <button v-if="erroLote" class="btn-secundario" :disabled="processando || salvandoLote" @click="salvarLote">{{ salvandoLote ? 'Salvando...' : 'Tentar salvar lote novamente' }}</button>
      <section v-if="erros.length" class="provas-pendentes" aria-labelledby="titulo-provas-pendentes">
        <div class="pendentes-cabecalho">
          <h3 id="titulo-provas-pendentes">Provas não corrigidas</h3>
          <span class="pendentes-contador">{{ erros.length }} prova(s)</span>
        </div>
        <p>Estas provas não tiveram a correção confirmada neste envio. Separe-as para uma nova tentativa.</p>
        <ol class="pendentes-lista" aria-label="Provas sem correção confirmada">
          <li v-for="item in erros" :key="item.indice">
            <span class="pendente-posicao">#{{ item.indice + 1 }}</span>
            <div class="pendente-aluno">
              <strong>{{ item.nome || (item.matricula != null ? 'Nome não disponível' : 'Aluno não identificado') }}</strong>
              <span>Matrícula: {{ item.matricula ?? 'Não identificada' }}</span>
              <span>Turma: {{ item.turma || 'Não identificada' }}</span>
              <template v-if="item.matricula == null">
                <span class="pendente-arquivo">Arquivo: {{ item.arquivo }}</span>
                <a v-if="item.imagemOriginal && !item.previaIndisponivel" class="pendente-original" :href="item.imagemOriginal" target="_blank" rel="noopener noreferrer" :aria-label="`Visualizar página original da imagem ${item.indice + 1}`">
                  <img :src="item.imagemOriginal" :alt="`Página original da imagem ${item.indice + 1}`" loading="lazy" decoding="async" @error="item.previaIndisponivel = true" />
                  <span>Visualizar página original</span>
                </a>
                <span v-else class="previa-indisponivel">Prévia indisponível para este arquivo.</span>
              </template>
            </div>
            <span class="pendente-status">Não corrigida</span>
          </li>
        </ol>
      </section>
      <p v-else class="sem-pendencias" role="status">Não há provas pendentes neste envio.</p>
      <div class="tabela-container">
        <table v-if="resultados.length">
          <thead><tr><th>Arquivo</th><th>Matrícula</th><th>Nome</th><th>Nota</th><th>Respostas do aluno</th><th>Gabarito correto</th></tr></thead>
          <tbody><tr v-for="resultado in resultados" :key="resultado.indice">
            <td>{{ resultado.arquivo }}</td><td>{{ resultado.matricula }}</td><td>{{ resultado.nome }}</td><td>{{ resultado.nota_prova }}</td>
            <td>{{ formatarGabarito(resultado.gabarito_aluno) }}</td><td>{{ formatarGabarito(resultado.gabarito_correto) }}</td>
          </tr></tbody>
        </table>
      </div>
    </template>
  </div>
</template>

<script>
import { corrigirImagens, criarLoteCorrecao } from "@/services/correcao";
import { entradasDoLote } from "@/utils/impressaoNotas";

export default {
  name: "CorrigirProvasView",
  data: () => ({ arquivos: [], resultados: [], erros: [], erro: "", processando: false, finalizado: false, idLote: "", erroLote: "", salvandoLote: false,
    progresso: { preparadas: 0, processadas: 0, recortadas: 0 } }),
  beforeRouteLeave() { return !this.processando && !this.salvandoLote; },
  mounted() {
    window.addEventListener("beforeunload", this.impedirSaida);
    try { this.idLote = localStorage.getItem("ultimoLoteNotas") || ""; } catch (_) { /* O link atual continua disponível sem armazenamento local. */ }
  },
  beforeUnmount() {
    window.removeEventListener("beforeunload", this.impedirSaida);
    this.limparPrevias();
  },
  methods: {
    impedirSaida(evento) { if (this.processando || this.salvandoLote) { evento.preventDefault(); evento.returnValue = ""; } },
    limparPrevias() {
      this.erros.forEach((item) => { if (item.imagemOriginal) URL.revokeObjectURL(item.imagemOriginal); });
    },
    selecionar(evento) {
      if (this.processando || this.salvandoLote) return;
      this.limparPrevias();
      this.arquivos = Array.from(evento.target.files); this.finalizado = false; this.erro = "";
      this.resultados = []; this.erros = [];
      this.idLote = ""; this.erroLote = "";
    },
    async corrigir() {
      if (this.processando || this.salvandoLote || !this.arquivos.length) return;
      this.processando = true; this.finalizado = false; this.erro = "";
      this.limparPrevias();
      this.resultados = []; this.erros = []; this.progresso = { preparadas: 0, processadas: 0, recortadas: 0 };
      this.idLote = ""; this.erroLote = "";
      try {
        const dados = await corrigirImagens(this.arquivos, (progresso) => { this.progresso = progresso; });
        this.resultados = dados.resultados;
        this.erros = dados.erros.map((item) => {
          const original = this.arquivos[item.indice];
          return { ...item, previaIndisponivel: false,
            imagemOriginal: item.matricula == null && ["image/png", "image/jpeg"].includes(original?.type) ? URL.createObjectURL(original) : null };
        });
        this.finalizado = true;
        await this.salvarLote();
      } catch (_) { this.erro = "O processamento foi interrompido. Não há confirmação de correção de todas as imagens."; }
      finally { this.processando = false; }
    },
    async salvarLote() {
      if (this.salvandoLote || this.idLote || !this.finalizado) return;
      this.salvandoLote = true; this.erroLote = "";
      try {
        const entradas = entradasDoLote(this.arquivos, this.resultados, this.erros);
        const { lote } = await criarLoteCorrecao(entradas);
        if (!lote?._id) throw new Error("O servidor não confirmou o salvamento do lote.");
        this.idLote = lote._id;
        try { localStorage.setItem("ultimoLoteNotas", lote._id); } catch (_) { /* O lote permanece salvo no banco. */ }
      } catch (error) { this.erroLote = error?.details || error?.message || "Não foi possível salvar a ordem do lote."; }
      finally { this.salvandoLote = false; }
    },
    formatarGabarito(gabarito) { return Object.entries(gabarito || {}).map(([numero, resposta]) => `${numero}: ${resposta ?? 'Em branco'}`).join(" · "); },
  },
};
</script>

<style scoped>
.correcao-container { padding: 20px; }
.page-header h2 { font-size: 24px; margin: 20px 0 15px; }
.header-line { height: 2px; background: linear-gradient(90deg, #00488b 0%, #00488b 50%, transparent 100%); margin-bottom: 20px; }
p { line-height: 1.6; }
.actions-bar { display: flex; align-items: center; flex-wrap: wrap; gap: 12px; margin: 24px 0; }
.btn-primario, .btn-secundario { border: 0; border-radius: 8px; padding: 10px 20px; cursor: pointer; font-weight: 500; }
.btn-primario { background: #00488b; color: white; }
.btn-primario:hover { background: #0066cc; }
.btn-secundario { background: #eee; color: #333; }
button:disabled { opacity: .5; cursor: not-allowed; }
.tabela-container { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; margin-top: 20px; }
th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
th { color: #00488b; }
.erro { color: #c0392b; }
.provas-pendentes { margin: 24px 0; padding: 20px; border: 1px solid #e9c16b; border-left: 4px solid #d89a24; border-radius: 10px; background: #fff8e8; color: #704d12; }
.pendentes-cabecalho { display: flex; align-items: center; flex-wrap: wrap; gap: 12px; }
.pendentes-cabecalho h3 { margin: 0; font-size: 18px; }
.pendentes-contador, .pendente-status { padding: 4px 10px; border-radius: 20px; background: #f9e7bd; font-size: 12px; font-weight: 600; }
.provas-pendentes > p { margin: 10px 0 16px; font-size: 14px; }
.pendentes-lista { max-height: 320px; overflow-y: auto; list-style: none; margin: 0; padding: 0; }
.pendentes-lista li { display: flex; align-items: center; gap: 12px; padding: 12px 0; border-top: 1px solid #e9c16b; }
.pendente-posicao { flex-shrink: 0; font-size: 12px; }
.pendente-aluno { display: flex; flex: 1; flex-direction: column; gap: 4px; min-width: 0; overflow-wrap: anywhere; font-size: 13px; }
.pendente-aluno strong { font-size: 14px; }
.pendente-arquivo { margin-top: 4px; }
.pendente-original { display: flex; flex-direction: column; align-self: flex-start; gap: 6px; max-width: 100%; margin-top: 8px; color: #00488b; font-size: 12px; text-decoration: none; }
.pendente-original img { display: block; width: 140px; height: 190px; max-width: 100%; object-fit: contain; background: white; border: 1px solid #d8d8d8; border-radius: 6px; }
.pendente-original:hover span { text-decoration: underline; }
.previa-indisponivel { margin-top: 8px; font-style: italic; }
.pendente-status { flex-shrink: 0; }
.sem-pendencias { margin: 24px 0; color: #218838; }
:global(.tema-escuro .provas-pendentes) { background: #352d1e; border-color: #a27a32; color: #ffe0a0; }
:global(.tema-escuro .pendentes-lista li) { border-color: #69522d; }
:global(.tema-escuro .pendentes-contador), :global(.tema-escuro .pendente-status) { background: #5a4522; }
:global(.tema-escuro .sem-pendencias) { color: #75d98c; }
:global(.tema-escuro .pendente-original) { color: #8ac4ff; }
@media (max-width: 600px) {
  .provas-pendentes { padding: 16px; }
  .pendentes-lista li { flex-wrap: wrap; gap: 8px; }
  .pendente-aluno { flex-basis: calc(100% - 48px); }
  .pendente-status { margin-left: 36px; }
}
</style>
