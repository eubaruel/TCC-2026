<template>
  <div class="criar-prova" :class="temaAtual">
    <header class="barra-superior">
      <button type="button" class="btn-voltar" title="Voltar" :disabled="salvando" @click="voltar">
        <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 18L9 12L15 6" stroke-linecap="round" stroke-linejoin="round" /></svg>
      </button>
      <h1>{{ tituloTela }}</h1>
      <span v-if="draft.sujo" class="indicador-alteracoes">Alterações não salvas</span>
      <template v-if="editavel">
        <button type="button" class="btn-salvar" :disabled="salvando || carregando || Boolean(erroCarregamento)" @click="salvar">
          {{ salvando ? "Aguarde..." : "💾 Salvar seleção" }}
        </button>
        <button type="button" class="btn-salvar" :disabled="salvando || carregando || Boolean(erroCarregamento)" @click="confirmarEnvio">Concluir e enviar</button>
      </template>
    </header>

    <div class="area-trabalho">
      <section class="painel painel-campos">
        <p v-if="carregando" class="mensagem-info">Carregando dados da prova...</p>
        <template v-else>
          <p v-if="erroCarregamento" class="mensagem-erro">
            {{ erroCarregamento }}
            <button type="button" class="btn-secundario" @click="carregar">Tentar novamente</button>
          </p>
          <template v-if="prova">
            <p v-if="!editavel" class="mensagem-info">Prova concluída: somente visualização. A edição não é mais permitida.</p>
            <div class="bloco">
              <h3>Questões ({{ questoes.length }})</h3>
              <p v-if="prova.quantidade_questoes" class="mensagem-info">Quantidade definida pelo processo pedagógico: {{ prova.quantidade_questoes }} questões.</p>
              <p v-if="editavel && questoes.length > limiteQuestoes" class="mensagem-erro" role="alert">Remova as questões excedentes antes de salvar ou enviar.</p>
              <div v-if="editavel" class="banco-questoes">
                <h4>Banco de questões</h4>
                <FiltrosQuestoes v-model="filtrosQuestoes" :disciplinas="disciplinasFiltro" :desabilitado="salvando || Boolean(erroCarregamento)" />
                <div v-if="questoesBancoFiltradas.length" class="lista-banco">
                  <article v-for="questao in questoesBancoFiltradas" :key="questao._id" class="questao-card">
                    <div class="questao-header">
                      <span class="disciplina">{{ metadados.nome_disciplina }}</span>
                      <span class="tipo-questao">Objetiva</span>
                      <span class="dificuldade">{{ questao.dificuldade || 'Médio' }}</span>
                    </div>
                    <div v-if="questao.assunto || questao.professor?.nome" class="questao-metadata">
                      <span v-if="questao.assunto">{{ questao.assunto }}</span>
                      <span v-if="questao.professor?.nome">Autor: {{ questao.professor.nome }}</span>
                    </div>
                    <details>
                      <summary><p class="questao-resumo texto-questao">{{ resumo(questao.enunciado) }}</p><span class="ver-questao">Ver questão completa</span></summary>
                      <!-- eslint-disable-next-line vue/no-v-html -->
                      <div class="questao-texto texto-questao" v-html="sanitizar(questao.enunciado)"></div>
                      <ol class="alternativas texto-questao">
                        <li v-for="(alternativa, index) in questao.alternativas" :key="alternativa.id" :class="{ correta: alternativa.id === questao.alternativa_correta }">
                          <strong>{{ letras[index] }})</strong>
                          <!-- eslint-disable-next-line vue/no-v-html -->
                          <div v-html="sanitizar(alternativa.texto)"></div>
                        </li>
                      </ol>
                    </details>
                    <div class="questao-footer">
                      <button type="button" class="btn-adicionar" :disabled="salvando || Boolean(erroCarregamento) || questoes.length >= limiteQuestoes" @click="importarQuestao(questao._id)">Adicionar à prova</button>
                    </div>
                  </article>
                </div>
                <p v-else class="mensagem-info">{{ questoesBancoCompativeis.length ? 'Nenhuma questão encontrada para esta busca.' : 'Nenhuma questão compatível disponível para adicionar.' }}</p>
              </div>
              <h4 v-if="editavel && questoes.length">Questões selecionadas</h4>
              <p v-if="!questoes.length" class="mensagem-info">Nenhuma questão selecionada.</p>
              <QuestaoEditor v-for="(questao, index) in questoes" :key="questao._idBanco"
                :questao="questao" :numero="index + 1" :primeira="index === 0" :ultima="index === questoes.length - 1"
                :bloqueada="!editavel || salvando || Boolean(erroCarregamento)"
                @mover="moverQuestao(index, $event)" @remover="removerQuestao(index)" />
            </div>
          </template>
          <p v-if="aviso" class="mensagem-info" role="status">{{ aviso }}</p>
          <p v-if="erro" class="mensagem-erro" role="alert">{{ erro }}</p>
        </template>
      </section>
      <section class="painel painel-preview">
        <PreviewProva :template="template" :metadados="metadados" :questoes="questoes" :professor="prova?.professor.nome || ''">
          <template #cabecalho>
            <CartaoResposta v-if="prova && !carregando && !erroCarregamento" class="cabecalho-preview" :prova="prova" matricula="" qrCode="" />
          </template>
        </PreviewProva>
      </section>
    </div>
    <ModalSairEdicao :visivel="mostrarModalSair" :salvando="salvando" :provaSalva="Boolean(draft.provaId)"
      @cancelar="cancelarSaida" @sair-sem-salvar="sairSemSalvar" @salvar-e-sair="salvarESair" />
  </div>
</template>

<script>
import QuestaoEditor from "@/components/QuestaoEditor.vue";
import PreviewProva from "@/components/PreviewProva.vue";
import CartaoResposta from "@/components/CartaoResposta.vue";
import ModalSairEdicao from "@/components/ModalSairEdicao.vue";
import FiltrosQuestoes from "@/components/FiltrosQuestoes.vue";
import { useAuthStore } from "@/stores/auth";
import { LETRAS, questaoDoBanco, useProvaDraftStore } from "@/stores/provaDraft";
import { listarQuestoes } from "@/services/questoes";
import { adicionarQuestoes, buscarProva, enviarProva, provaEditavel } from "@/services/provas";
import { obterTemplateProva } from "@/services/templates";
import { htmlVazio, sanitizar, textoPuro } from "@/utils/html";
import { filtrarQuestoes, novosFiltrosQuestoes } from "@/utils/filtrosQuestoes";

export default {
  name: "CriarProvaView",
  components: { QuestaoEditor, PreviewProva, CartaoResposta, ModalSairEdicao, FiltrosQuestoes },
  props: { id: { type: String, required: true } },
  setup() {
    return { authStore: useAuthStore(), draft: useProvaDraftStore() };
  },
  data: () => ({
    temaAtual: "tema-claro", template: "", prova: null, bancoQuestoes: [],
    filtrosQuestoes: novosFiltrosQuestoes(), letras: LETRAS, carregando: true, salvando: false,
    erro: "", erroCarregamento: "", aviso: "", versoes: null,
    mostrarModalSair: false, destinoPendente: null, liberarSaida: false, monitorandoAlteracoes: false,
  }),
  computed: {
    metadados() { return this.draft.metadados; },
    questoes() { return this.draft.questoesEditor; },
    limiteQuestoes() { return this.prova?.quantidade_questoes ?? 10; },
    editavel() { return Boolean(this.prova && provaEditavel(this.prova)); },
    tituloTela() { return `${this.editavel ? "Selecionar questões" : "Visualizar prova"} · ${this.metadados.nome_disciplina || "Prova"}`; },
    questoesBancoCompativeis() {
      if (!this.prova) return [];
      const referencias = [this.metadados.codigo_disciplina, this.metadados.nome_disciplina].map((valor) => valor.trim().toLowerCase());
      const selecionadas = new Set(this.questoes.map((questao) => questao._idBanco));
      return this.bancoQuestoes.filter((questao) => !selecionadas.has(questao._id)
        && questao.tipo_questao === "Objetiva"
        && questao.disciplina?.some((valor) => referencias.includes(String(valor).trim().toLowerCase())));
    },
    questoesBancoFiltradas() {
      return filtrarQuestoes(this.questoesBancoCompativeis, this.filtrosQuestoes, this.disciplinasFiltro);
    },
    disciplinasFiltro() {
      return [{ codigo_disciplina: this.metadados.codigo_disciplina, nome_disciplina: this.metadados.nome_disciplina }];
    },
  },
  watch: {
    "draft.questoesEditor": { deep: true, handler() {
      if (this.monitorandoAlteracoes && this.editavel) this.draft.marcarSujo();
    } },
  },
  async mounted() {
    window.addEventListener("beforeunload", this.aoFecharJanela);
    await this.carregar();
  },
  beforeUnmount() { window.removeEventListener("beforeunload", this.aoFecharJanela); },
  beforeRouteLeave(to) {
    if (this.salvando) return false;
    if (this.liberarSaida || !this.draft.sujo) {
      this.draft.descartarRascunho();
      return true;
    }
    this.destinoPendente = to.fullPath;
    this.mostrarModalSair = true;
    return false;
  },
  methods: {
    sanitizar,
    mensagemErro(error) { return error?.details || error?.message || "Não foi possível concluir a operação."; },
    resumo(html) {
      const texto = textoPuro(html) || "[questão com imagem]";
      return texto.length > 90 ? `${texto.slice(0, 90)}…` : texto;
    },
    async carregar() {
      this.monitorandoAlteracoes = false;
      this.carregando = true;
      this.erro = ""; this.erroCarregamento = ""; this.aviso = ""; this.prova = null;
      this.versoes = null; this.filtrosQuestoes = novosFiltrosQuestoes();
      this.draft.iniciarNova();
      try {
        const [template, banco, prova] = await Promise.all([obterTemplateProva(), listarQuestoes(), buscarProva(this.id)]);
        if (!prova) throw new Error("A prova não foi encontrada ou está inativa.");
        if (prova.professor.registro !== this.authStore.user.registro) throw new Error("Esta prova não está atribuída a você.");
        this.template = template; this.bancoQuestoes = banco.questoes; this.prova = prova;
        this.draft.provaId = prova._id;
        Object.assign(this.metadados, {
          turmasTexto: (Array.isArray(prova.id_turma) ? prova.id_turma : [prova.id_turma]).join("\n"),
          codigo_disciplina: prova.disciplina.codigo_disciplina, nome_disciplina: prova.disciplina.nome_disciplina,
          tipo: prova.tipo, serie: prova.serie, periodo_letivo: prova.periodo_letivo,
          data_de_aplicacao: prova.data_de_aplicacao, status: prova.status,
        });
        this.filtrosQuestoes.disciplina = prova.disciplina.codigo_disciplina;
        const porId = new Map(this.bancoQuestoes.map((questao) => [questao._id, questao]));
        if (prova.questoes.some((id) => !porId.has(id))) throw new Error("Uma questão vinculada está indisponível. Confira o banco antes de continuar.");
        this.draft.questoesEditor = prova.questoes.map((id) => questaoDoBanco(porId.get(id)));
        if (this.editavel && this.draft.questoes.length) {
          const compativeis = new Set(this.questoesBancoCompativeis.map((questao) => questao._id));
          const fila = this.draft.questoes.filter((questao) => compativeis.has(questao._id));
          if (this.questoes.length + fila.length > this.limiteQuestoes) {
            this.aviso = `A seleção do banco excede o limite de ${this.limiteQuestoes} questões. Nenhuma questão dessa seleção foi adicionada; adicione individualmente as desejadas.`;
          } else {
            this.draft.questoesEditor.push(...fila.map((questao) => questaoDoBanco(porId.get(questao._id))));
            this.draft.sujo = Boolean(fila.length);
            this.aviso = fila.length ? "Questões selecionadas no banco adicionadas à prova." : "Nenhuma questão da seleção anterior pôde ser adicionada a esta prova.";
          }
        }
        this.draft.limpar();
      } catch (error) {
        this.erroCarregamento = this.mensagemErro(error);
      } finally {
        this.carregando = false;
        await this.$nextTick();
        this.monitorandoAlteracoes = true;
      }
    },
    importarQuestao(id) {
      if (!this.editavel || this.salvando || this.erroCarregamento) return;
      if (this.questoes.length >= this.limiteQuestoes) {
        this.erro = `A prova permite no máximo ${this.limiteQuestoes} questões.`;
        return;
      }
      this.erro = "";
      const questao = this.questoesBancoCompativeis.find((item) => item._id === id);
      if (questao) this.draft.questoesEditor.push(questaoDoBanco(questao));
    },
    moverQuestao(index, direcao) {
      if (!this.editavel || this.salvando || this.erroCarregamento) return;
      const destino = index + direcao;
      if (destino < 0 || destino >= this.questoes.length) return;
      const lista = [...this.questoes];
      [lista[index], lista[destino]] = [lista[destino], lista[index]];
      this.draft.questoesEditor = lista;
    },
    removerQuestao(index) {
      if (!this.editavel || this.salvando || this.erroCarregamento) return;
      this.draft.questoesEditor.splice(index, 1);
    },
    validar(concluir = false) {
      if (!this.draft.provaId || !this.editavel) return "Esta prova não está disponível para preenchimento.";
      if (this.questoes.length < 2) return "Selecione ao menos duas questões do banco.";
      if (this.questoes.length > this.limiteQuestoes) return `A prova permite no máximo ${this.limiteQuestoes} questões. Remova as questões excedentes.`;
      if (concluir && this.prova.quantidade_questoes && this.questoes.length !== this.prova.quantidade_questoes) {
        return `Selecione exatamente ${this.prova.quantidade_questoes} questões para concluir a prova.`;
      }
      const ids = this.questoes.map((questao) => questao._idBanco);
      if (ids.some((id) => !id) || new Set(ids).size !== ids.length) return "Selecione questões válidas, sem repetição.";
      for (const [index, questao] of this.questoes.entries()) {
        if (htmlVazio(questao.enunciado) || questao.alternativas.length !== 5 || questao.alternativas.some(htmlVazio)
            || new Set(questao.alternativas.map((alternativa) => alternativa.trim())).size !== 5
            || !Number.isInteger(questao.indiceCorreta) || questao.indiceCorreta < 0 || questao.indiceCorreta > 4) {
          return `Questão ${index + 1}: confira no banco o enunciado, cinco alternativas e a indicação da correta.`;
        }
      }
      return "";
    },
    async salvar() {
      if (this.salvando || this.carregando || this.erroCarregamento) return false;
      this.erro = this.validar();
      if (this.erro) return false;
      this.salvando = true; this.aviso = "";
      try {
        // Apenas IDs, na ordem definida pelo professor. A API preserva versões sem mudanças.
        const resposta = await adicionarQuestoes(this.draft.provaId, this.questoes.map((questao) => questao._idBanco));
        this.prova = resposta.prova; this.metadados.status = resposta.prova.status;
        this.versoes = resposta.provas_alunos_geradas;
        this.aviso = this.versoes === 0
          ? "Seleção salva, mas nenhuma versão foi criada. Confira os alunos ativos das turmas e salve novamente antes de enviar."
          : `Seleção salva. ${this.versoes} versão(ões) individual(is) disponível(is).`;
        await this.$nextTick();
        this.draft.sujo = false;
        return true;
      } catch (error) { this.erro = this.mensagemErro(error); return false; }
      finally { this.salvando = false; }
    },
    confirmarEnvio() {
      if (!this.editavel || this.salvando || this.carregando || this.erroCarregamento) return;
      this.erro = this.validar(true);
      if (this.erro) return;
      window.$modal.abrir({
        titulo: "Concluir e enviar prova",
        mensagem: "Após enviar ao processo pedagógico, não será mais possível editar esta prova. Deseja continuar?",
        tipo: "confirmacao", onConfirm: () => this.enviar(),
      });
    },
    async enviar() {
      if (this.salvando || this.carregando || this.erroCarregamento) return;
      this.erro = this.validar(true);
      if (this.erro) return;
      if (!await this.salvar() || !this.versoes) return;
      this.salvando = true;
      try {
        const resposta = await enviarProva(this.draft.provaId);
        this.prova = resposta.prova; this.metadados.status = resposta.prova.status;
        this.aviso = "Prova enviada ao processo pedagógico. Edição encerrada.";
        this.draft.sujo = false;
      } catch (error) { this.erro = this.mensagemErro(error); }
      finally { this.salvando = false; }
    },
    voltar() { this.$router.push("/provas"); },
    cancelarSaida() { if (!this.salvando) { this.mostrarModalSair = false; this.destinoPendente = null; } },
    sairSemSalvar() {
      if (this.salvando) return;
      this.mostrarModalSair = false; this.liberarSaida = true;
      this.$router.push(this.destinoPendente || "/provas");
    },
    async salvarESair() {
      if (!await this.salvar()) return;
      this.mostrarModalSair = false; this.liberarSaida = true;
      this.$router.push(this.destinoPendente || "/provas");
    },
    aoFecharJanela(evento) {
      if (!this.draft.sujo && !this.salvando) return;
      evento.preventDefault(); evento.returnValue = "";
    },
  },
};
</script>

<style scoped>
.criar-prova {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
}

.criar-prova.tema-claro {
  background-color: #f5f5f5;
  color: #333;
}

.criar-prova.tema-escuro {
  background-color: #1a1a1a;
  color: #e5e5e5;
}

/* Barra superior no mesmo azul da barra lateral */
.barra-superior {
  display: flex;
  align-items: center;
  gap: 16px;
  height: 64px;
  padding: 0 20px;
  background: linear-gradient(135deg, #00488b 0%, #003366 100%);
  color: white;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  flex-shrink: 0;
}

.barra-superior h1 {
  flex: 1;
  font-size: 18px;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.btn-voltar {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border: none;
  border-radius: 8px;
  background: transparent;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-voltar:hover {
  background: rgba(255, 255, 255, 0.15);
}

.indicador-alteracoes {
  font-size: 12px;
  padding: 4px 10px;
  border-radius: 12px;
  background: #ffc10730;
  color: #ffe08a;
}

.btn-salvar {
  padding: 8px 18px;
  background: white;
  color: #00488b;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.btn-salvar:hover:not(:disabled) {
  transform: scale(1.02);
  background: #e8f0f8;
}

.btn-salvar:disabled {
  opacity: 0.65;
  cursor: wait;
}

/* Duas metades */
.area-trabalho {
  flex: 1;
  display: grid;
  grid-template-columns: 1fr 1fr;
  min-height: 0;
}

.painel {
  min-width: 0;
  overflow-y: auto;
  padding: 24px;
}

.painel-campos {
  border-right: 1px solid #e0e0e0;
}

.tema-escuro .painel-campos {
  border-right-color: #404040;
}

.painel-preview {
  background: #e9ecef;
}

.cabecalho-preview { margin-bottom: 20px; }

.tema-escuro .painel-preview {
  background: #111;
}

.bloco {
  margin-bottom: 24px;
}

.bloco h3 {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 2px solid #00488b;
}

.banco-questoes { margin-bottom: 24px; }
.bloco h4 { font-size: 15px; margin: 0 0 12px; }
.lista-banco { display: grid; gap: 12px; max-height: 420px; overflow-y: auto; margin-top: 12px; padding: 2px 6px 2px 0; }
.questao-card { min-width: 0; background: white; border: 1px solid #e0e0e0; border-radius: 12px; padding: 16px; overflow-wrap: anywhere; transition: box-shadow .3s ease; }
.questao-card:hover { box-shadow: 0 4px 12px #0001; }
.questao-header, .questao-metadata { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 10px; }
.questao-header span { padding: 4px 10px; border-radius: 20px; font-size: 12px; }
.disciplina { background: #00488b20; color: #00488b; }
.tipo-questao { background: #17a2b820; color: #117786; }
.dificuldade { background: #ffc10720; color: #856404; }
.questao-metadata { font-size: 12px; color: #777; }
summary { cursor: pointer; }
.questao-resumo { display: inline; font-size: 14px; line-height: 1.5; }
.ver-questao { display: block; color: #00488b; font-size: 12px; margin-top: 8px; }
details[open] .ver-questao { display: none; }
.questao-texto { margin-top: 12px; font-size: 14px; line-height: 1.5; overflow-x: auto; }
.alternativas { list-style: none; padding: 0; margin: 12px 0; }
.alternativas li { display: flex; gap: 8px; font-size: 13px; margin: 8px 0; }
.alternativas li > div { min-width: 0; }
.alternativas .correta { color: #218838; font-weight: 500; }
.questao-texto :deep(img), .alternativas :deep(img) { max-width: 100%; height: auto; }
.questao-footer { display: flex; justify-content: flex-end; margin-top: 12px; padding-top: 12px; border-top: 1px solid #eee; }
.btn-adicionar { padding: 8px 12px; background: #00488b; color: white; border: 0; border-radius: 6px; cursor: pointer; font-size: 13px; }
.btn-adicionar:hover:not(:disabled) { background: #0066cc; }
.btn-adicionar:disabled { opacity: .5; cursor: not-allowed; }
.tema-escuro .questao-card { background: #2a2a2a; border-color: #404040; }
.tema-escuro .questao-metadata { color: #aaa; }
.tema-escuro .disciplina, .tema-escuro .ver-questao { color: #8ac4ff; }
.tema-escuro .tipo-questao { color: #66d9e8; }
.tema-escuro .dificuldade { color: #ffe08a; }
.tema-escuro .correta { color: #75d98c; }
.tema-escuro .questao-footer { border-color: #404040; }

.btn-secundario {
  padding: 8px 14px;
  border: 1px solid #00488b;
  border-radius: 6px;
  background: transparent;
  color: #00488b;
  cursor: pointer;
  white-space: nowrap;
}

.btn-secundario:disabled {
  opacity: 0.5;
  cursor: default;
}

.tema-escuro .btn-secundario {
  border-color: #0066cc;
  color: #0066cc;
}

.mensagem-info {
  color: #888;
}

.mensagem-erro {
  color: #b42318;
  font-weight: 500;
  margin: 12px 0;
}

@media (max-width: 768px) {
  .area-trabalho {
    grid-template-columns: 1fr;
    overflow-y: auto;
  }

  .painel {
    overflow: visible;
    padding: 16px;
  }

  .painel-campos {
    border-right: none;
    border-bottom: 1px solid #e0e0e0;
  }

  .indicador-alteracoes {
    display: none;
  }
}
</style>
