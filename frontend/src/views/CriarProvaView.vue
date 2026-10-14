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
            <p class="mensagem-info">{{ editavel ? "Selecione as questões do banco. Os dados da prova e o conteúdo das questões são mantidos como cadastrados." : "Prova concluída: somente visualização. A edição não é mais permitida." }}</p>
            <div class="bloco">
              <h3>Dados da prova</h3>
              <div class="campo"><label for="professor">Professor responsável</label><input id="professor" :value="prova.professor.nome" readonly /></div>
              <div class="campo"><label for="turmas">Turma(s)</label><textarea id="turmas" :value="metadados.turmasTexto" rows="2" readonly></textarea></div>
              <div class="campo"><label for="disciplina">Disciplina</label><input id="disciplina" :value="metadados.nome_disciplina" readonly /></div>
              <div class="grade-campos">
                <div class="campo"><label for="tipo">Tipo</label><input id="tipo" value="Objetiva" readonly /></div>
                <div class="campo"><label for="serie">Série</label><input id="serie" :value="metadados.serie" readonly /></div>
                <div class="campo"><label for="bimestre">Bimestre</label><input id="bimestre" :value="metadados.bimestre" readonly /></div>
                <div class="campo"><label for="dataAplicacao">Data de aplicação</label><input id="dataAplicacao" :value="metadados.data_de_aplicacao" type="date" readonly /></div>
                <div class="campo"><label for="status">Status</label><input id="status" :value="metadados.status" readonly /></div>
              </div>
            </div>
            <div class="bloco">
              <h3>Questões ({{ questoes.length }}/{{ limiteQuestoes }})</h3>
              <p class="mensagem-info">O leitor de correção suporta provas de 1 a {{ limiteQuestoes }} questões.</p>
              <p v-if="editavel && questoes.length > limiteQuestoes" class="mensagem-erro" role="alert">Remova as questões excedentes antes de salvar ou enviar.</p>
              <p v-if="!questoes.length" class="mensagem-info">Nenhuma questão selecionada.</p>
              <QuestaoEditor v-for="(questao, index) in questoes" :key="questao._idBanco"
                :questao="questao" :numero="index + 1" :primeira="index === 0" :ultima="index === questoes.length - 1"
                :bloqueada="!editavel || salvando || Boolean(erroCarregamento)"
                @mover="moverQuestao(index, $event)" @remover="removerQuestao(index)" />
              <div v-if="editavel" class="acoes-questoes">
                <div class="importar-banco">
                  <select v-model="questaoBancoSelecionada" :disabled="salvando || Boolean(erroCarregamento) || questoes.length >= limiteQuestoes || !questoesBancoCompativeis.length" aria-label="Questão do banco">
                    <option value="">{{ questoesBancoCompativeis.length ? "Selecionar questão do banco..." : "Nenhuma questão compatível disponível" }}</option>
                    <option v-for="questao in questoesBancoCompativeis" :key="questao._id" :value="questao._id">{{ resumo(questao.enunciado) }}</option>
                  </select>
                  <button type="button" class="btn-secundario" :disabled="salvando || questoes.length >= limiteQuestoes || !questaoBancoSelecionada" @click="importarQuestao">Adicionar</button>
                </div>
              </div>
            </div>
          </template>
          <p v-if="aviso" class="mensagem-info" role="status">{{ aviso }}</p>
          <p v-if="erro" class="mensagem-erro" role="alert">{{ erro }}</p>
        </template>
      </section>
      <section class="painel painel-preview">
        <PreviewProva :template="template" :metadados="metadados" :questoes="questoes" :professor="prova?.professor.nome || ''" />
      </section>
    </div>
    <ModalSairEdicao :visivel="mostrarModalSair" :salvando="salvando" :provaSalva="Boolean(draft.provaId)"
      @cancelar="cancelarSaida" @sair-sem-salvar="sairSemSalvar" @salvar-e-sair="salvarESair" />
  </div>
</template>

<script>
import QuestaoEditor from "@/components/QuestaoEditor.vue";
import PreviewProva from "@/components/PreviewProva.vue";
import ModalSairEdicao from "@/components/ModalSairEdicao.vue";
import { useAuthStore } from "@/stores/auth";
import { questaoDoBanco, useProvaDraftStore } from "@/stores/provaDraft";
import { listarQuestoes } from "@/services/questoes";
import { adicionarQuestoes, buscarProva, enviarProva, provaEditavel } from "@/services/provas";
import { obterTemplateProva } from "@/services/templates";
import { htmlVazio, textoPuro } from "@/utils/html";

export default {
  name: "CriarProvaView",
  components: { QuestaoEditor, PreviewProva, ModalSairEdicao },
  props: { id: { type: String, required: true } },
  setup() {
    return { authStore: useAuthStore(), draft: useProvaDraftStore() };
  },
  data: () => ({
    limiteQuestoes: 10,
    temaAtual: "tema-claro", template: "", prova: null, bancoQuestoes: [],
    questaoBancoSelecionada: "", carregando: true, salvando: false,
    erro: "", erroCarregamento: "", aviso: "", versoes: null,
    mostrarModalSair: false, destinoPendente: null, liberarSaida: false, monitorandoAlteracoes: false,
  }),
  computed: {
    metadados() { return this.draft.metadados; },
    questoes() { return this.draft.questoesEditor; },
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
    mensagemErro(error) { return error?.details || error?.message || "Não foi possível concluir a operação."; },
    resumo(html) {
      const texto = textoPuro(html) || "[questão com imagem]";
      return texto.length > 90 ? `${texto.slice(0, 90)}…` : texto;
    },
    async carregar() {
      this.monitorandoAlteracoes = false;
      this.carregando = true;
      this.erro = ""; this.erroCarregamento = ""; this.aviso = ""; this.prova = null;
      this.versoes = null; this.questaoBancoSelecionada = "";
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
          tipo: prova.tipo, serie: prova.serie, bimestre: prova.bimestre,
          data_de_aplicacao: prova.data_de_aplicacao, status: prova.status,
        });
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
    importarQuestao() {
      if (!this.editavel || this.salvando || this.erroCarregamento) return;
      if (this.questoes.length >= this.limiteQuestoes) {
        this.erro = `A prova permite no máximo ${this.limiteQuestoes} questões.`;
        return;
      }
      this.erro = "";
      const questao = this.questoesBancoCompativeis.find((item) => item._id === this.questaoBancoSelecionada);
      if (questao) this.draft.questoesEditor.push(questaoDoBanco(questao));
      this.questaoBancoSelecionada = "";
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
    validar() {
      if (!this.draft.provaId || !this.editavel) return "Esta prova não está disponível para preenchimento.";
      if (!this.questoes.length) return "Selecione ao menos uma questão do banco.";
      if (this.questoes.length > this.limiteQuestoes) return `A prova permite no máximo ${this.limiteQuestoes} questões. Remova as questões excedentes.`;
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
      this.erro = this.validar();
      if (this.erro) return;
      window.$modal.abrir({
        titulo: "Concluir e enviar prova",
        mensagem: "Após enviar ao processo pedagógico, não será mais possível editar esta prova. Deseja continuar?",
        tipo: "confirmacao", onConfirm: () => this.enviar(),
      });
    },
    async enviar() {
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

.campo {
  margin-bottom: 12px;
}

.campo label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  margin-bottom: 6px;
  color: #666;
}

.tema-escuro .campo label {
  color: #aaa;
}

.campo input,
.campo select,
.campo textarea,
.importar-banco select {
  width: 100%;
  padding: 9px 10px;
  border: 1px solid #d8d8d8;
  border-radius: 6px;
  font: inherit;
  background: white;
  color: inherit;
}

.tema-escuro .campo input,
.tema-escuro .campo select,
.tema-escuro .campo textarea,
.tema-escuro .importar-banco select {
  background: #2a2a2a;
  border-color: #404040;
}

.grade-campos {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0 12px;
}

.acoes-questoes {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.importar-banco {
  display: flex;
  gap: 8px;
}

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

  .grade-campos {
    grid-template-columns: 1fr;
  }

  .indicador-alteracoes {
    display: none;
  }
}
</style>
