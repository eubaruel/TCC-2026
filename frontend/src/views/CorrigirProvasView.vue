<template>
  <div class="correcao-container">
    <div class="page-header">
      <div class="cabecalho-conteudo">
        <h2>Correção de provas</h2>
        <button class="btn-secundario" :disabled="processando || salvandoLote" @click="$router.push('/provas')">← Voltar às provas</button>
      </div>
      <div class="header-line"></div>
    </div>
    <section class="painel envio-painel" aria-labelledby="titulo-envio" :aria-busy="processando || salvandoLote">
      <div class="painel-titulo">
        <span class="painel-icone" aria-hidden="true">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9zM14 3v6h6M8 14h8M8 17h5" /></svg>
        </span>
        <div><h3 id="titulo-envio">Enviar provas para correção</h3><p>Selecione as páginas com o cartão-resposta para corrigir um conjunto de provas.</p></div>
      </div>
      <div class="selecao-imagens">
        <input id="imagens-correcao" class="input-arquivos" aria-label="Imagens dos cartões-resposta" aria-describedby="orientacao-imagens" type="file" accept="image/*" multiple :disabled="processando || salvandoLote" @change="selecionar" />
        <label for="imagens-correcao" class="seletor-arquivos" :class="{ desabilitado: processando || salvandoLote }">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M12 16V4m-4 4 4-4 4 4M4 15v4a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-4" /></svg>
          <strong>{{ arquivos.length ? 'Alterar seleção de imagens' : 'Selecionar imagens' }}</strong>
          <span>Escolha uma ou mais páginas no seu computador</span>
        </label>
        <p id="orientacao-imagens" class="orientacao-imagens">PNG ou JPEG · Uma página por imagem · Cartão-resposta e QR Code legíveis</p>
        <ul v-if="arquivos.length" class="arquivos-selecionados" aria-label="Arquivos selecionados">
          <li v-for="(arquivo, indice) in arquivos.slice(0, 3)" :key="indice" :title="arquivo.name">{{ arquivo.name }}</li>
          <li v-if="arquivos.length > 3" class="arquivos-restantes">+ {{ arquivos.length - 3 }} imagem(ns)</li>
        </ul>
      </div>
      <div class="envio-rodape">
        <p class="selecao-contador" role="status"><strong>{{ arquivos.length }}</strong> imagem(ns) selecionada(s)</p>
        <button class="btn-primario" :disabled="processando || salvandoLote || !arquivos.length" @click="corrigir"><span v-if="processando" class="carregando" aria-hidden="true"></span>{{ processando ? 'Processando...' : 'Corrigir imagens' }}</button>
      </div>
    </section>
    <section v-if="processando || finalizado" class="painel progresso-painel" aria-labelledby="titulo-progresso">
      <div class="secao-cabecalho"><h3 id="titulo-progresso">{{ processando ? 'Correção em andamento' : 'Processamento concluído' }}</h3><span class="etiqueta">{{ progresso.processadas }} / {{ arquivos.length }} imagens</span></div>
      <progress :value="progresso.processadas" :max="arquivos.length || 1" aria-label="Imagens processadas"></progress>
      <p class="progresso-detalhes" role="status">Preparadas: {{ progresso.preparadas }} / {{ arquivos.length }}. Processadas: {{ progresso.processadas }} / {{ arquivos.length }}. Recortadas: {{ progresso.recortadas }}. Preservadas sem recorte: {{ progresso.preparadas - progresso.recortadas }}.</p>
    </section>
    <p v-if="erro" class="erro" role="alert">{{ erro }}</p>
    <div v-if="idLote && !processando" class="lote-salvo">
      <div><strong>{{ finalizado ? 'Lote salvo' : 'Último lote salvo' }}</strong><p>Consulte a ordem das folhas e prepare a impressão das notas.</p></div>
      <button class="btn-primario" @click="$router.push(`/provas/notas/${idLote}`)">Organizar folhas e imprimir notas <span aria-hidden="true">→</span></button>
    </div>
    <template v-if="finalizado">
      <div class="resumo-correcao">
        <div class="resumo-item"><span class="resumo-numero sucesso">{{ resultados.length }}</span><div><strong>Provas corrigidas</strong><span>Resultados confirmados e salvos</span></div></div>
        <div class="resumo-item"><span class="resumo-numero" :class="{ atencao: erros.length }">{{ erros.length }}</span><div><strong>Pendências</strong><span>{{ erros.length ? 'Precisam de uma nova tentativa' : 'Nenhuma pendência neste envio' }}</span></div></div>
      </div>
      <p class="resultado-orientacao">Os resultados confirmados foram salvos no banco. A prova passa automaticamente para o status Corrigida quando todas as versões dos alunos tiverem uma tentativa de correção registrada, com sucesso ou falha. Após mais da metade, o processo pedagógico também pode ignorar as restantes na aba Provas Impressas. A impressão das notas só é liberada para um lote sem pendências.</p>
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
      <section v-if="resultados.length" class="painel resultados-painel" aria-labelledby="titulo-resultados">
        <div class="secao-cabecalho"><h3 id="titulo-resultados">Resultados da correção</h3><span class="etiqueta">{{ resultados.length }} prova(s)</span></div>
        <div class="tabela-container">
        <table>
          <thead><tr><th>Arquivo</th><th>Matrícula</th><th>Nome</th><th>Nota</th><th>Respostas do aluno</th><th>Gabarito correto</th></tr></thead>
          <tbody><tr v-for="resultado in resultados" :key="resultado.indice">
            <td class="arquivo-resultado">{{ resultado.arquivo }}</td><td>{{ resultado.matricula }}</td><td>{{ resultado.nome }}</td><td><span class="nota-valor">{{ resultado.nota_prova }}</span></td>
            <td>{{ formatarGabarito(resultado.gabarito_aluno) }}</td><td>{{ formatarGabarito(resultado.gabarito_correto) }}</td>
          </tr></tbody>
        </table>
        </div>
      </section>
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
.correcao-container { --superficie: #fff; --borda: #e0e0e0; --texto-suave: #666; --fundo-suave: #f7f9fc; --azul-suave: #edf4fb; --azul-texto: #00488b; --verde: #218838; --amarelo: #936817; max-width: 1200px; margin: 0 auto; padding: 0 20px 32px; }
.page-header { margin: 20px 0 24px; }
.cabecalho-conteudo { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 16px; margin-bottom: 15px; }
.page-header h2 { font-size: 28px; font-weight: 600; margin: 0; }
.header-line { height: 2px; background: linear-gradient(90deg, #00488b 0%, #00488b 50%, transparent 100%); }
p { line-height: 1.6; }
.painel { min-width: 0; margin-bottom: 20px; padding: 24px; background: var(--superficie); border: 1px solid var(--borda); border-radius: 12px; }
.painel-titulo { display: flex; align-items: flex-start; gap: 14px; margin-bottom: 24px; }
.painel-icone { display: flex; align-items: center; justify-content: center; flex-shrink: 0; width: 46px; height: 46px; border-radius: 10px; background: var(--azul-suave); color: var(--azul-texto); }
h3 { margin: 0; font-size: 18px; font-weight: 600; }
.painel-titulo p { margin-top: 6px; font-size: 14px; color: var(--texto-suave); }
.selecao-imagens { position: relative; }
.input-arquivos { position: absolute; width: 1px; height: 1px; overflow: hidden; clip-path: inset(50%); white-space: nowrap; }
.seletor-arquivos { display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 10px; min-height: 168px; padding: 24px; border: 1px dashed #9cb9d5; border-radius: 10px; background: var(--fundo-suave); text-align: center; cursor: pointer; transition: background .2s, border-color .2s; }
.seletor-arquivos svg, .seletor-arquivos strong { color: var(--azul-texto); }
.seletor-arquivos strong { font-size: 16px; font-weight: 600; }
.seletor-arquivos span { color: var(--texto-suave); font-size: 13px; }
.seletor-arquivos:hover { background: var(--azul-suave); border-color: var(--azul-texto); }
.input-arquivos:focus-visible + .seletor-arquivos { outline: 3px solid var(--azul-texto); outline-offset: 3px; }
.seletor-arquivos.desabilitado { cursor: not-allowed; opacity: .6; }
.orientacao-imagens { margin-top: 12px; font-size: 12px; text-align: center; color: var(--texto-suave); }
.arquivos-selecionados { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 16px; padding: 0; list-style: none; }
.arquivos-selecionados li { max-width: 240px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; padding: 6px 10px; border-radius: 6px; background: var(--fundo-suave); border: 1px solid var(--borda); font-size: 12px; }
.arquivos-selecionados .arquivos-restantes { background: var(--azul-suave); color: var(--azul-texto); border-color: transparent; }
.envio-rodape { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 16px; border-top: 1px solid var(--borda); margin-top: 24px; padding-top: 20px; }
.selecao-contador { font-size: 14px; color: var(--texto-suave); }
.selecao-contador strong { color: var(--azul-texto); }
.btn-primario, .btn-secundario { display: inline-flex; justify-content: center; align-items: center; gap: 10px; min-height: 42px; border: 1px solid transparent; border-radius: 8px; padding: 10px 20px; cursor: pointer; font: inherit; font-size: 14px; font-weight: 500; transition: background .2s; }
.btn-primario { background: #00488b; color: white; }
.btn-primario:hover:not(:disabled) { background: #0066cc; }
.btn-secundario { background: var(--superficie); color: var(--texto-suave); border-color: var(--borda); }
.btn-secundario:hover:not(:disabled) { background: var(--fundo-suave); }
button:focus-visible, a:focus-visible { outline: 3px solid var(--azul-texto); outline-offset: 3px; }
button:disabled { opacity: .5; cursor: not-allowed; }
.carregando { width: 15px; height: 15px; border: 2px solid #ffffff70; border-top-color: white; border-radius: 50%; animation: girar .8s linear infinite; }
@keyframes girar { to { transform: rotate(360deg); } }
.secao-cabecalho { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px; }
.etiqueta { padding: 5px 10px; border-radius: 20px; background: var(--azul-suave); color: var(--azul-texto); font-size: 12px; font-weight: 600; }
progress { display: block; width: 100%; height: 8px; margin-top: 20px; border: 0; border-radius: 8px; overflow: hidden; background: var(--azul-suave); accent-color: #00488b; }
progress::-webkit-progress-bar { background: var(--azul-suave); }
progress::-webkit-progress-value { background: #00488b; border-radius: 8px; }
progress::-moz-progress-bar { background: #00488b; border-radius: 8px; }
.progresso-detalhes { margin-top: 12px; color: var(--texto-suave); font-size: 12px; }
.lote-salvo { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 20px; margin-bottom: 20px; padding: 20px 24px; background: var(--azul-suave); border: 1px solid var(--borda); border-radius: 12px; }
.lote-salvo strong { color: var(--azul-texto); font-size: 15px; }
.lote-salvo p { margin-top: 4px; color: var(--texto-suave); font-size: 13px; }
.resumo-correcao { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
.resumo-item { display: flex; align-items: center; gap: 16px; padding: 20px 24px; background: var(--superficie); border: 1px solid var(--borda); border-radius: 12px; }
.resumo-numero { font-size: 32px; line-height: 1; font-weight: 600; color: var(--texto-suave); }
.resumo-numero.sucesso { color: var(--verde); }
.resumo-numero.atencao { color: var(--amarelo); }
.resumo-item > div { display: flex; flex-direction: column; gap: 5px; }
.resumo-item strong { font-size: 14px; font-weight: 600; }
.resumo-item div > span { font-size: 12px; color: var(--texto-suave); }
.resultado-orientacao { margin: 14px 0 20px; color: var(--texto-suave); font-size: 13px; }
.resultados-painel { padding: 0; overflow: hidden; }
.resultados-painel .secao-cabecalho { padding: 20px 24px; }
.tabela-container { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; font-size: 13px; }
th, td { padding: 14px 18px; text-align: left; border-bottom: 1px solid var(--borda); }
th { background: var(--fundo-suave); color: var(--texto-suave); font-size: 12px; font-weight: 600; white-space: nowrap; }
td { line-height: 1.5; }
tbody tr:last-child td { border-bottom: 0; }
tbody tr:hover { background: var(--fundo-suave); }
.arquivo-resultado { max-width: 190px; overflow-wrap: anywhere; color: var(--texto-suave); }
.nota-valor { display: inline-block; min-width: 40px; padding: 5px 8px; border-radius: 6px; background: var(--azul-suave); color: var(--azul-texto); text-align: center; font-weight: 600; }
.erro { margin: 16px 0; padding: 14px 18px; border: 1px solid #e7b5b5; border-radius: 8px; background: #fff1f1; color: #a32c2c; font-size: 14px; }
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
.sem-pendencias { margin: 20px 0; padding: 14px 18px; border-radius: 8px; background: #edf8ef; color: var(--verde); font-size: 14px; }
:global(.tema-escuro .correcao-container) { --superficie: #2a2a2a; --borda: #404040; --texto-suave: #b5b5b5; --fundo-suave: #242424; --azul-suave: #20364c; --azul-texto: #8ac4ff; --verde: #75d98c; --amarelo: #ffe0a0; }
:global(.tema-escuro .correcao-container .erro) { background: #3e2525; border-color: #794040; color: #ffb3b3; }
:global(.tema-escuro .correcao-container .sem-pendencias) { background: #22382a; }
:global(.tema-escuro .provas-pendentes) { background: #352d1e; border-color: #a27a32; color: #ffe0a0; }
:global(.tema-escuro .pendentes-lista li) { border-color: #69522d; }
:global(.tema-escuro .pendentes-contador), :global(.tema-escuro .pendente-status) { background: #5a4522; }
:global(.tema-escuro .sem-pendencias) { color: #75d98c; }
:global(.tema-escuro .pendente-original) { color: #8ac4ff; }
@media (max-width: 600px) {
  .correcao-container { padding: 0 12px 24px; }
  .page-header h2 { font-size: 24px; }
  .painel { padding: 18px; }
  .painel-titulo { gap: 10px; }
  .painel-icone { width: 38px; height: 38px; }
  .painel-titulo h3 { font-size: 16px; }
  .seletor-arquivos { padding: 20px 14px; }
  .envio-rodape .btn-primario, .lote-salvo .btn-primario { width: 100%; }
  .resumo-correcao { grid-template-columns: 1fr; gap: 12px; }
  .resumo-item, .lote-salvo { padding: 18px; }
  .resultados-painel { padding: 0; }
  .resultados-painel .secao-cabecalho { padding: 18px; }
  .provas-pendentes { padding: 16px; }
  .pendentes-lista li { flex-wrap: wrap; gap: 8px; }
  .pendente-aluno { flex-basis: calc(100% - 48px); }
  .pendente-status { margin-left: 36px; }
}
@media (prefers-reduced-motion: reduce) {
  .carregando { animation: none; }
}
</style>
