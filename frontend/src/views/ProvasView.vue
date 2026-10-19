<template>
  <div class="provas-container">
    <div class="page-header">
      <h2>{{ authStore.isProfessor ? "Minhas Provas" : "Provas" }}</h2>
      <div class="header-line"></div>
    </div>

    <div v-if="authStore.isProcessoPedagogico" class="acoes-principais" role="group" aria-label="Ações de provas">
      <button type="button" class="acao-prova acao-criar" @click="mostrarCriacaoBase = true">
        <span class="acao-icone" aria-hidden="true">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 5v14M5 12h14" /></svg>
        </span>
        <span class="acao-texto"><strong>Criar prova-base</strong><span>Defina a prova e atribua ao professor</span></span>
      </button>
      <button type="button" class="acao-prova acao-corrigir" @click="$router.push('/provas/corrigir')">
        <span class="acao-icone" aria-hidden="true">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9zM14 3v6h6m-12 6 3 3 5-6" /></svg>
        </span>
        <span class="acao-texto"><strong>Corrigir provas</strong><span>Envie imagens e confira os resultados</span></span>
      </button>
    </div>
    <!-- Tabs -->
    <div class="provas-tabs">
      <button
        @click="abaAtiva = 'minhas'"
        class="tab-btn"
        :class="{ ativo: abaAtiva === 'minhas' }"
      >
        {{ authStore.isProfessor ? "Aguardando questões" : "Provas Recebidas" }} ({{ authStore.isProfessor ? provasAguardandoQuestoes.length : provasRecebidas.length }})
      </button>
      <button
        v-if="authStore.isProfessor"
        @click="abaAtiva = 'enviadas'"
        class="tab-btn"
        :class="{ ativo: abaAtiva === 'enviadas' }"
      >
        Enviada ao processo pedagógico ({{ provasEnviadas.length }})
      </button>
      <button
        v-if="authStore.isProcessoPedagogico"
        @click="abaAtiva = 'impressas'"
        class="tab-btn"
        :class="{ ativo: abaAtiva === 'impressas' }"
      >
        Provas Impressas ({{ provasImpressas.length }})
      </button>
      <button
        v-if="authStore.isProcessoPedagogico"
        @click="abaAtiva = 'corrigidas'"
        class="tab-btn"
        :class="{ ativo: abaAtiva === 'corrigidas' }"
      >
        Provas Corrigidas ({{ provasCorrigidas.length }})
      </button>
    </div>

    <div v-if="erro" class="sem-provas">
      <div class="empty-state">
        <p>{{ erro }}</p>
        <button class="btn-criar-prova" @click="carregarTudo">Tentar novamente</button>
      </div>
    </div>
    <Transition name="toast">
      <div v-if="aviso" class="toast-aviso" role="status" aria-live="polite" aria-atomic="true">
        <svg class="toast-icone" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
          <circle cx="12" cy="12" r="9" /><path d="M12 11v6M12 7v1" />
        </svg>
        <div class="toast-conteudo">
          <strong>Prova-base criada!</strong>
          <p>{{ aviso }}</p>
        </div>
        <button type="button" class="toast-fechar" aria-label="Fechar aviso" @click="fecharAviso">&times;</button>
      </div>
    </Transition>

    <div v-if="!erro && carregando" class="sem-provas">
      <div class="empty-state"><p>Carregando provas...</p></div>
    </div>

    <!-- Lista de Provas -->
    <div v-if="!erro && !carregando" class="lista-provas">
      <div v-if="provasExibidas.length === 0" class="sem-provas">
        <div class="empty-state">
          <svg
            width="64"
            height="64"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="1.5"
          >
            <path
              d="M14 4H6C5.46957 4 4.96086 4.21071 4.58579 4.58579C4.21071 4.96086 4 5.46957 4 6V18C4 18.5304 4.21071 19.0391 4.58579 19.4142C4.96086 19.7893 5.46957 20 6 20H18C18.5304 20 19.0391 19.7893 19.4142 19.4142C19.7893 19.0391 20 18.5304 20 18V10M14 4L20 10M14 4V10H20"
              stroke="currentColor"
              stroke-width="2"
            />
            <path d="M12 16H8M16 12H8" stroke="currentColor" stroke-width="2" />
          </svg>
          <p>Nenhuma prova encontrada nesta categoria.</p>
          <p v-if="abaAtiva === 'minhas'" class="sub">
            {{ authStore.isProfessor ? "As provas atribuídas a você que ainda não foram enviadas aparecerão aqui." : "As provas concluídas e enviadas pelos professores aparecerão aqui." }}
          </p>
        </div>
      </div>
      <div v-else>
        <div v-for="prova in provasExibidas" :key="prova.id" class="prova-card">
          <div class="prova-info">
            <div class="prova-icon">
              <svg
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="1.5"
              >
                <path
                  d="M4 4H20V20H4V4Z"
                  stroke="currentColor"
                  stroke-width="2"
                />
                <path d="M8 8H16V10H8V8Z" fill="currentColor" />
                <path d="M8 12H14V14H8V12Z" fill="currentColor" />
                <path d="M8 16H12V18H8V16Z" fill="currentColor" />
              </svg>
            </div>
            <div class="prova-detalhes">
              <h4>{{ (authStore.isProfessor ? prova.tituloProfessor : '') || prova.titulo || "Prova sem título" }}</h4>
              <div class="prova-metadata">
                <span>📅 {{ formatarData(prova.criadaEm) }}</span>
                <span v-if="authStore.isProcessoPedagogico">Professor: {{ prova.professor.nome }}</span>
                <span class="status" :class="classeStatus(prova.status)">
                  {{
                    (prova.status || "rascunho").charAt(0).toUpperCase() +
                    (prova.status || "rascunho").slice(1)
                  }}
                </span>
              </div>
              <details v-if="authStore.isProfessor && prova.turmas?.length" class="turmas-prova">
                <summary>{{ prova.turmas.length }} {{ prova.turmas.length === 1 ? 'turma' : 'turmas' }}</summary>
                <ul class="lista-turmas" aria-label="Turmas que farão a prova">
                  <li v-for="turma in prova.turmas" :key="turma">{{ turma }}</li>
                </ul>
              </details>
              <p v-else-if="authStore.isProfessor" class="turmas-ausentes">Nenhuma turma informada</p>
              <div v-if="authStore.isProcessoPedagogico && prova.status === 'Impressa'" class="progresso-correcao">
                <span v-if="contagemCorrecaoValida(prova)" class="contador-correcao" title="Cada versão conta uma vez, incluindo tentativas com sucesso ou falha.">
                  Corrigidas: <strong>{{ prova.progresso_correcao.processadas }} / {{ prova.progresso_correcao.total }}</strong>
                </span>
                <span v-else class="contador-correcao">Contagem indisponível</span>
                <button v-if="podeIgnorarProvas(prova)" type="button" class="btn-ignorar-provas"
                  :disabled="ignorandoProvaId !== null" @click="solicitarIgnorarProvas(prova)">
                  {{ ignorandoProvaId === prova.id ? 'Confirmando...' : 'Ignorar provas não corrigidas' }}
                </button>
              </div>
            </div>
          </div>
          <div class="prova-actions">
            <button
              v-if="authStore.isProfessor"
              @click="editarProva(prova)"
              class="btn-editar"
              :title="provaEditavel(prova) ? 'Selecionar questões' : 'Visualizar prova'"
            >
              {{ provaEditavel(prova) ? "✏️" : "👁️" }}
            </button>
            <button
              v-if="authStore.isProcessoPedagogico"
              @click="visualizarImpressao(prova)"
              class="btn-baixar"
              title="Visualizar e imprimir versões individuais"
            >
              🖨️
            </button>
            <button
              v-if="authStore.isProcessoPedagogico && prova.status === 'Enviada ao pedagógico'"
              @click="solicitarConfirmacaoImpressao(prova)"
              class="btn-confirmar-impressao"
              title="Confirmar impressão realizada"
              aria-label="Confirmar impressão realizada"
              :disabled="confirmandoImpressaoId !== null"
            >
              <span v-if="confirmandoImpressaoId === prova.id">…</span>
              <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
                <path d="m5 12 4 4L19 6" />
              </svg>
            </button>
            <button
              v-if="authStore.isProcessoPedagogico && provaEditavel(prova)"
              @click="excluirProva(prova.id)"
              class="btn-excluir-prova"
              title="Excluir"
              :disabled="excluindoId === prova.id"
            >
              {{ excluindoId === prova.id ? "…" : "🗑️" }}
            </button>
          </div>
        </div>
      </div>
    </div>
    <CriarProvaBase v-if="mostrarCriacaoBase && authStore.isProcessoPedagogico" @fechar="mostrarCriacaoBase = false" @criada="provaBaseCriada" />
  </div>
</template>

<script>
import { useAuthStore } from "@/stores/auth";
import { excluirProva as excluirProvaApi, listarProvas, provaEditavel, confirmarImpressao as confirmarImpressaoApi, ignorarProvasNaoCorrigidas as ignorarProvasNaoCorrigidasApi } from "@/services/provas";
import CriarProvaBase from "@/components/CriarProvaBase.vue";

export default {
  name: "ProvasView",
  components: { CriarProvaBase },
  setup() {
    return { authStore: useAuthStore() };
  },
  data: () => ({
    abaAtiva: "minhas",
    minhasProvas: [],
    erro: "",
    aviso: "",
    temporizadorAviso: null,
    carregando: true,
    excluindoId: null,
    confirmandoImpressaoId: null,
    ignorandoProvaId: null,
    mostrarCriacaoBase: false,
  }),
  computed: {
    provasAguardandoQuestoes() {
      return this.minhasProvas.filter(provaEditavel);
    },
    provasEnviadas() {
      return this.minhasProvas.filter((prova) => ["Enviada ao pedagógico", "Impressa", "Corrigida"].includes(prova.status));
    },
    provasRecebidas() {
      return this.minhasProvas.filter((prova) => prova.status === "Enviada ao pedagógico");
    },
    provasImpressas() {
      return this.minhasProvas.filter((prova) => prova.status === "Impressa");
    },
    provasCorrigidas() {
      return this.minhasProvas.filter((prova) => prova.status === "Corrigida");
    },
    provasExibidas() {
      if (this.authStore.isProfessor) {
        return this.abaAtiva === "enviadas" ? this.provasEnviadas : this.provasAguardandoQuestoes;
      }
      if (this.abaAtiva === "impressas") return this.provasImpressas;
      if (this.abaAtiva === "corrigidas") return this.provasCorrigidas;
      return this.provasRecebidas;
    },
  },
  async mounted() {
    await this.carregarTudo();
  },
  beforeUnmount() {
    clearTimeout(this.temporizadorAviso);
  },
  methods: {
    provaEditavel,
    mensagemErro(error) {
      return error?.details || error?.message || "Não foi possível carregar os dados.";
    },
    async carregarTudo() {
      this.carregando = true;
      this.erro = "";
      await this.carregarProvas();
      this.carregando = false;
    },
    async carregarProvas() {
      try {
        const filtro = this.authStore.isProfessor ? { registro: this.authStore.user.registro } : {};
        const provas = (await listarProvas(filtro)).provas;
        if (!Array.isArray(provas)) throw new Error("O servidor retornou uma lista de provas inválida.");
        this.minhasProvas = provas
          .filter((prova) => this.authStore.isProfessor || ["Enviada ao pedagógico", "Impressa", "Corrigida"].includes(prova.status))
          .map(this.adaptarProva);
      } catch (error) {
        this.minhasProvas = [];
        this.erro = this.mensagemErro(error);
      }
    },
    adaptarProva(prova) {
      return {
        ...prova,
        id: prova._id,
        titulo: `${prova.disciplina.nome_disciplina} - ${Array.isArray(prova.id_turma) ? prova.id_turma.join(", ") : prova.id_turma}`,
        tituloProfessor: `${prova.disciplina.nome_disciplina} - ${prova.periodo_letivo || "Período letivo não informado"}`,
        turmas: [...new Set((Array.isArray(prova.id_turma) ? prova.id_turma : [prova.id_turma])
          .map((turma) => String(turma ?? "").trim()).filter(Boolean))],
        criadaEm: prova.data_de_aplicacao,
      };
    },
    provaBaseCriada(prova) {
      this.fecharAviso();
      this.aviso = `Atribuída a ${prova.professor.nome}. Ela aparecerá em Provas Recebidas quando o professor concluir e enviar.`;
      this.mostrarCriacaoBase = false;
      this.temporizadorAviso = setTimeout(this.fecharAviso, 8000);
    },
    fecharAviso() {
      clearTimeout(this.temporizadorAviso);
      this.temporizadorAviso = null;
      this.aviso = "";
    },
    editarProva(prova) {
      this.$router.push(`/provas/editor/${prova.id}`);
    },
    formatarData(data) {
      return data ? new Date(`${data}T00:00:00`).toLocaleDateString("pt-BR") : "Data desconhecida";
    },
    classeStatus(status) {
      return {
        "Aguardando questões": "aguardando",
        "Em elaboração": "elaboracao",
        "Enviada ao pedagógico": "enviado",
        "Impressa": "impressa",
        "Corrigida": "corrigido",
      }[status] || "";
    },
    visualizarImpressao(prova) {
      this.$router.push(`/provas/imprimir/${prova.id}`);
    },
    solicitarConfirmacaoImpressao(prova) {
      if (!this.authStore.isProcessoPedagogico || this.confirmandoImpressaoId !== null || prova.status !== "Enviada ao pedagógico") return;
      window.$modal.abrir({
        titulo: "Confirmar impressão",
        mensagem: "Confirmar impressão da prova? Confirme somente se ela já foi impressa.",
        tipo: "confirmacao",
        onConfirm: () => this.confirmarImpressao(prova),
      });
    },
    async confirmarImpressao(prova) {
      if (!this.authStore.isProcessoPedagogico || this.confirmandoImpressaoId !== null || prova.status !== "Enviada ao pedagógico") return;
      this.confirmandoImpressaoId = prova.id;
      try {
        const resposta = await confirmarImpressaoApi(prova.id);
        if (resposta.prova?.status !== "Impressa") throw new Error("O servidor não confirmou o status da impressão. Tente novamente.");
        Object.assign(prova, this.adaptarProva(resposta.prova));
      } catch (error) {
        window.$modal.abrir({ titulo: "Não foi possível confirmar a impressão", mensagem: this.mensagemErro(error), tipo: "alerta" });
      } finally { this.confirmandoImpressaoId = null; }
    },
    contagemCorrecaoValida(prova) {
      const contagem = prova.progresso_correcao;
      return Boolean(contagem && Number.isInteger(contagem.total) && Number.isInteger(contagem.processadas)
        && contagem.total >= 0 && contagem.processadas >= 0 && contagem.processadas <= contagem.total);
    },
    podeIgnorarProvas(prova) {
      return this.authStore.isProcessoPedagogico && prova.status === "Impressa" && this.contagemCorrecaoValida(prova)
        && prova.progresso_correcao.total > 0 && prova.progresso_correcao.processadas * 2 > prova.progresso_correcao.total;
    },
    solicitarIgnorarProvas(prova) {
      if (!this.podeIgnorarProvas(prova) || this.ignorandoProvaId !== null) return;
      const { processadas, total } = prova.progresso_correcao;
      const restantes = total - processadas;
      window.$modal.abrir({
        titulo: "Ignorar provas não corrigidas",
        mensagem: `${processadas} de ${total} versões de ${prova.titulo} já tiveram uma tentativa de correção. Deseja ignorar ${restantes} ${restantes === 1 ? 'versão restante' : 'versões restantes'} e marcar a prova como Corrigida? Esta ação não atribui notas às versões restantes.`,
        tipo: "confirmacao",
        onConfirm: () => this.ignorarProvasNaoCorrigidas(prova),
      });
    },
    async ignorarProvasNaoCorrigidas(prova) {
      if (!this.podeIgnorarProvas(prova) || this.ignorandoProvaId !== null) return;
      this.ignorandoProvaId = prova.id;
      try {
        const resposta = await ignorarProvasNaoCorrigidasApi(prova.id);
        if (resposta.prova?.status !== "Corrigida") throw new Error("O servidor não confirmou a alteração do status. Tente novamente.");
        Object.assign(prova, this.adaptarProva(resposta.prova));
      } catch (error) {
        window.$modal.abrir({ titulo: "Não foi possível concluir a correção", mensagem: this.mensagemErro(error), tipo: "alerta" });
      } finally { this.ignorandoProvaId = null; }
    },
    excluirProva(id) {
      if (!this.authStore.isProcessoPedagogico) return;
      window.$modal.abrir({ titulo: "Excluir prova", mensagem: "Deseja excluir esta prova?", tipo: "confirmacao", onConfirm: async () => { try { this.excluindoId = id; await excluirProvaApi(id); await this.carregarProvas(); } catch (error) { this.erro = this.mensagemErro(error); } finally { this.excluindoId = null; } } });
    },
  },
};
</script>

<style scoped>
.provas-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h2 {
  font-size: 28px;
  font-weight: 600;
  margin-bottom: 15px;
  margin-top: 20px;
  color: inherit;
}

.header-line {
  height: 2px;
  background: linear-gradient(90deg, #00488b 0%, #00488b 50%, transparent 100%);
  width: 100%;
}

.provas-tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.tab-btn {
  padding: 10px 20px;
  background: transparent;
  border: none;
  font-size: 16px;
  cursor: pointer;
  color: #666;
  transition: all 0.3s ease;
}

.tab-btn.ativo {
  color: #00488b;
  border-bottom: 2px solid #00488b;
}

.tema-escuro .tab-btn {
  color: #aaa;
}

.tema-escuro .tab-btn.ativo {
  color: #0066cc;
  border-bottom-color: #0066cc;
}

.btn-criar-prova {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: #00488b;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.btn-criar-prova:hover {
  background: #0066cc;
  transform: scale(1.02);
}

.acoes-principais { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; margin-bottom: 24px; }
.acao-prova { display: flex; align-items: center; gap: 16px; min-height: 88px; padding: 20px; border: 1px solid #00488b; border-radius: 12px; font: inherit; text-align: left; cursor: pointer; transition: background .2s, border-color .2s; }
.acao-icone { display: flex; align-items: center; justify-content: center; flex-shrink: 0; width: 44px; height: 44px; border-radius: 10px; }
.acao-texto { display: flex; flex-direction: column; gap: 5px; }
.acao-texto strong { font-size: 16px; font-weight: 600; }
.acao-texto > span { font-size: 13px; line-height: 1.4; }
.acao-criar { background: #00488b; color: #fff; }
.acao-criar .acao-icone { background: #ffffff26; }
.acao-criar .acao-texto > span { color: #ffffffd6; }
.acao-criar:hover { background: #0066cc; border-color: #0066cc; }
.acao-corrigir { background: #fff; color: #00488b; border-color: #a9c2dc; }
.acao-corrigir .acao-icone { background: #edf4fb; }
.acao-corrigir .acao-texto > span { color: #596b7b; }
.acao-corrigir:hover { background: #edf4fb; border-color: #00488b; }
.acao-prova:focus-visible { outline: 3px solid #0066cc; outline-offset: 3px; }
.tema-escuro .acao-corrigir { background: #2a2a2a; color: #8ac4ff; border-color: #526a82; }
.tema-escuro .acao-corrigir .acao-icone { background: #20364c; }
.tema-escuro .acao-corrigir .acao-texto > span { color: #b5b5b5; }
.tema-escuro .acao-corrigir:hover { background: #20364c; border-color: #8ac4ff; }
@media (prefers-reduced-motion: reduce) { .acao-prova { transition: none; } }

.lista-provas {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.prova-card {
  background: white;
  border-radius: 12px;
  padding: 16px 20px;
  border: 1px solid #e0e0e0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: all 0.3s ease;
}

.tema-escuro .prova-card {
  background: #2a2a2a;
  border-color: #404040;
}

.prova-card:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.prova-info {
  display: flex;
  align-items: center;
  gap: 16px;
  flex: 1;
}

.prova-icon {
  width: 40px;
  height: 40px;
  background: #00488b20;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #00488b;
}

.tema-escuro .prova-icon {
  background: #0066cc20;
  color: #0066cc;
}

.prova-detalhes h4 {
  font-size: 16px;
  font-weight: 500;
  margin: 0 0 4px 0;
  color: inherit;
}

.prova-metadata {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  font-size: 12px;
  color: #888;
}

.prova-info, .prova-detalhes { min-width: 0; }
.prova-icon { flex-shrink: 0; }
.prova-detalhes h4 { overflow-wrap: anywhere; }
.turmas-prova { margin-top: 10px; font-size: 12px; }
.turmas-prova summary { width: fit-content; color: #00488b; cursor: pointer; border-radius: 4px; }
.turmas-prova summary:hover { text-decoration: underline; }
.turmas-prova summary:focus-visible { outline: 2px solid #00488b; outline-offset: 4px; }
.lista-turmas { display: flex; flex-wrap: wrap; gap: 6px; list-style: none; padding: 0; margin: 8px 0 0; }
.lista-turmas li { padding: 4px 8px; border-radius: 6px; background: #edf4fb; color: #00488b; overflow-wrap: anywhere; }
.turmas-ausentes { margin: 10px 0 0; font-size: 12px; color: #888; }
:global(.tema-escuro .turmas-prova summary) { color: #8ac4ff; }
:global(.tema-escuro .turmas-prova summary:focus-visible) { outline-color: #8ac4ff; }
:global(.tema-escuro .lista-turmas li) { background: #20364c; color: #8ac4ff; }

.status {
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
  background: #e9ecef;
  color: #495057;
}

.status.aguardando {
  background: #fff3cd;
  color: #856404;
}

.status.elaboracao {
  background: #e3f0ff;
  color: #1558a6;
}

.status.enviado {
  background: #eee5ff;
  color: #6a35a8;
}

.status.impressa {
  background: #fff0dd;
  color: #9a4d00;
}

.status.corrigido {
  background: #e2f4e8;
  color: #1e7038;
}

.prova-actions {
  display: flex;
  gap: 8px;
}

.prova-actions button {
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  transition: all 0.3s ease;
  background: transparent;
}

.prova-actions button:hover {
  background: #f0f0f0;
  transform: scale(1.05);
}

.progresso-correcao { display: flex; align-items: center; flex-wrap: wrap; gap: 10px; margin-top: 12px; }
.contador-correcao { display: inline-flex; align-items: center; gap: 6px; padding: 6px 10px; border-radius: 6px; background: #edf4fb; color: #00488b; font-size: 12px; }
.contador-correcao strong { font-variant-numeric: tabular-nums; }
.btn-ignorar-provas { padding: 6px 10px; border: 1px solid #bdcfe2; border-radius: 6px; background: transparent; color: #00488b; font-size: 12px; cursor: pointer; }
.btn-ignorar-provas:hover:not(:disabled) { background: #edf4fb; }
.btn-ignorar-provas:focus-visible { outline: 2px solid #00488b; outline-offset: 3px; }
.btn-ignorar-provas:disabled { opacity: .5; cursor: wait; }
:global(.tema-escuro .progresso-correcao .contador-correcao) { background: #20364c; color: #8ac4ff; }
:global(.tema-escuro .progresso-correcao .btn-ignorar-provas) { color: #8ac4ff; border-color: #4c6682; }
:global(.tema-escuro .progresso-correcao .btn-ignorar-provas:hover:not(:disabled)) { background: #20364c; }
.prova-actions .btn-confirmar-impressao { color: #00488b; display: inline-flex; align-items: center; justify-content: center; }
.tema-escuro .prova-actions .btn-confirmar-impressao { color: #7bbcff; }
.prova-actions button:disabled { opacity: .5; cursor: wait; transform: none; }

.tema-escuro .prova-actions button:hover {
  background: #3a3a3a;
}

.btn-excluir-prova:hover {
  background: #dc3545 !important;
  color: white !important;
}

.sem-provas {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 60px 20px;
}

.empty-state {
  text-align: center;
  color: #888;
}

.empty-state svg {
  color: #ccc;
  margin-bottom: 16px;
}

.tema-escuro .empty-state svg {
  color: #555;
}

.empty-state p {
  font-size: 16px;
  margin: 4px 0;
}

.empty-state .sub {
  font-size: 14px;
  color: #aaa;
}


.toast-aviso {
  position: fixed;
  top: 24px;
  right: 24px;
  z-index: 11000;
  display: flex;
  align-items: flex-start;
  gap: 12px;
  box-sizing: border-box;
  width: 420px;
  max-width: calc(100vw - 32px);
  padding: 16px;
  border: 1px solid #00488b;
  border-left: 4px solid #00488b;
  border-radius: 10px;
  background: #00488b;
  color: #fff;
  box-shadow: 0 8px 24px #00488b40;
}
.toast-icone { flex-shrink: 0; margin-top: 1px; }
.toast-conteudo { flex: 1; min-width: 0; overflow-wrap: anywhere; }
.toast-conteudo strong { display: block; font-size: 15px; margin-bottom: 4px; }
.toast-conteudo p { margin: 0; color: inherit; font-size: 13px; line-height: 1.5; }
.toast-fechar { flex-shrink: 0; width: 28px; height: 28px; padding: 0; border: 0; border-radius: 4px; background: transparent; color: inherit; font-size: 24px; cursor: pointer; }
.toast-fechar:hover, .toast-fechar:focus-visible { background: #ffffff26; }
.toast-enter-active, .toast-leave-active { transition: opacity .2s ease, transform .2s ease; }
.toast-enter-from, .toast-leave-to { opacity: 0; transform: translateY(-12px); }
@media (prefers-reduced-motion: reduce) { .toast-enter-active, .toast-leave-active { transition: none; } }
@media print { .toast-aviso { display: none !important; } }

@media (max-width: 768px) {
  .acoes-principais { grid-template-columns: 1fr; gap: 12px; }
  .toast-aviso { top: 16px; right: 16px; }
  .prova-card {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }

  .prova-actions {
    justify-content: flex-end;
  }

  .provas-tabs {
    overflow-x: auto;
  }
}
</style>
