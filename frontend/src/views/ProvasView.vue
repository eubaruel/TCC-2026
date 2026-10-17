<template>
  <div class="provas-container">
    <div class="page-header">
      <h2>{{ authStore.isProfessor ? "Minhas Provas" : "Provas" }}</h2>
      <div class="header-line"></div>
    </div>

    <!-- Tabs -->
    <div v-if="authStore.isProcessoPedagogico" class="actions-bar">
      <button class="btn-criar-prova btn-corrigir" @click="$router.push('/provas/corrigir')">Corrigir provas</button>
    </div>
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

    <div v-if="abaAtiva === 'minhas' && authStore.isProcessoPedagogico" class="actions-bar">
      <button @click="mostrarCriacaoBase = true" class="btn-criar-prova">
        <svg
          width="20"
          height="20"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <path d="M12 5V19M5 12H19" stroke="white" stroke-width="2" />
        </svg>
        Criar Prova-base
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
              <h4>{{ prova.titulo || "Prova sem título" }}</h4>
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
import { excluirProva as excluirProvaApi, listarProvas, provaEditavel } from "@/services/provas";
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

.actions-bar {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 24px;
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

.btn-corrigir {
  width: 100%;
  justify-content: center;
  padding: 16px 24px;
  font-size: 16px;
  font-weight: 600;
}

.btn-corrigir:hover {
  transform: none;
}

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
  gap: 16px;
  font-size: 12px;
  color: #888;
}

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
