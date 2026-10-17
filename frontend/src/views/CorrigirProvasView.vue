<template>
  <div class="correcao-container">
    <div class="page-header"><h2>Correção de provas</h2><div class="header-line"></div></div>
    <p>Selecione as imagens das páginas com o cartão-resposta. O recorte é automático e mantém as dez colunas e o QR Code.</p>
    <p>Se o cartão não for reconhecido com segurança, a imagem original será enviada, sem interromper o lote. Envie uma página por imagem (PNG ou JPEG), não PDF.</p>
    <div class="actions-bar">
      <input aria-label="Imagens dos cartões-resposta" type="file" accept="image/*" multiple :disabled="processando" @change="selecionar" />
      <button class="btn-primario" :disabled="processando || !arquivos.length" @click="corrigir">{{ processando ? 'Processando...' : 'Corrigir imagens' }}</button>
      <button class="btn-secundario" :disabled="processando" @click="$router.push('/provas')">Voltar</button>
    </div>
    <p>{{ arquivos.length }} imagem(ns) selecionada(s).</p>
    <p v-if="processando || finalizado" role="status">
      Preparadas: {{ progresso.preparadas }} / {{ arquivos.length }}. Processadas: {{ progresso.processadas }} / {{ arquivos.length }}.
      Recortadas: {{ progresso.recortadas }}. Preservadas sem recorte: {{ progresso.preparadas - progresso.recortadas }}.
    </p>
    <p v-if="erro" class="erro" role="alert">{{ erro }}</p>
    <template v-if="finalizado">
      <p>{{ resultados.length }} correção(ões), {{ erros.length }} erro(s). As notas abaixo foram calculadas pela API, mas não foram salvas no banco; o status das provas não foi alterado.</p>
      <div class="tabela-container">
        <table v-if="resultados.length">
          <thead><tr><th>Arquivo</th><th>Matrícula</th><th>Nome</th><th>Nota</th><th>Respostas do aluno</th><th>Gabarito correto</th></tr></thead>
          <tbody><tr v-for="resultado in resultados" :key="resultado.indice">
            <td>{{ resultado.arquivo }}</td><td>{{ resultado.matricula }}</td><td>{{ resultado.nome }}</td><td>{{ resultado.nota_prova }}</td>
            <td>{{ formatarGabarito(resultado.gabarito_aluno) }}</td><td>{{ formatarGabarito(resultado.gabarito_correto) }}</td>
          </tr></tbody>
        </table>
      </div>
      <ul v-if="erros.length" class="erros"><li v-for="item in erros" :key="item.indice">{{ item.arquivo }}: {{ item.mensagem }}</li></ul>
    </template>
  </div>
</template>

<script>
import { corrigirImagens } from "@/services/correcao";

export default {
  name: "CorrigirProvasView",
  data: () => ({ arquivos: [], resultados: [], erros: [], erro: "", processando: false, finalizado: false,
    progresso: { preparadas: 0, processadas: 0, recortadas: 0 } }),
  beforeRouteLeave() { return !this.processando; },
  mounted() { window.addEventListener("beforeunload", this.impedirSaida); },
  beforeUnmount() { window.removeEventListener("beforeunload", this.impedirSaida); },
  methods: {
    impedirSaida(evento) { if (this.processando) { evento.preventDefault(); evento.returnValue = ""; } },
    selecionar(evento) {
      if (this.processando) return;
      this.arquivos = Array.from(evento.target.files); this.finalizado = false; this.erro = "";
      this.resultados = []; this.erros = [];
    },
    async corrigir() {
      if (this.processando || !this.arquivos.length) return;
      this.processando = true; this.finalizado = false; this.erro = "";
      this.resultados = []; this.erros = []; this.progresso = { preparadas: 0, processadas: 0, recortadas: 0 };
      try {
        const dados = await corrigirImagens(this.arquivos, (progresso) => { this.progresso = progresso; });
        this.resultados = dados.resultados; this.erros = dados.erros; this.finalizado = true;
      } catch (_) { this.erro = "O processamento foi interrompido. Não há confirmação de correção de todas as imagens."; }
      finally { this.processando = false; }
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
.erro, .erros { color: #c0392b; }
.erros li { margin: 8px 0; }
</style>
