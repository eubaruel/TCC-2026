<template>
  <div class="provas-container">
    <div class="page-header">
      <h2>{{ authStore.isProfessor ? "Minhas Provas" : "Provas" }}</h2>
      <div class="header-line"></div>
    </div>

    <!-- Tabs -->
    <div class="provas-tabs">
      <button
        @click="abaAtiva = 'minhas'"
        class="tab-btn"
        :class="{ ativo: abaAtiva === 'minhas' }"
      >
        {{ authStore.isProfessor ? "Minhas Provas" : "Provas Recebidas" }} ({{ minhasProvas.length }})
      </button>
      <button
        @click="abaAtiva = 'naoCorrigidas'"
        class="tab-btn"
        :class="{ ativo: abaAtiva === 'naoCorrigidas' }"
      >
        Não Corrigidas ({{ provasNaoCorrigidas.length }})
      </button>
      <button
        @click="abaAtiva = 'corrigidas'"
        class="tab-btn"
        :class="{ ativo: abaAtiva === 'corrigidas' }"
      >
        Corrigidas ({{ provasCorrigidas.length }})
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
    <p v-if="aviso" role="status">{{ aviso }}</p>

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
            {{ authStore.isProfessor ? "As provas atribuídas a você aparecerão aqui." : "As provas concluídas e enviadas pelos professores aparecerão aqui." }}
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
              v-if="provaEditavel(prova)"
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
    carregando: true,
    excluindoId: null,
    mostrarCriacaoBase: false,
  }),
  computed: {
    provasNaoCorrigidas() {
      return this.minhasProvas.filter((prova) => ["Enviada ao pedagógico", "Não Corrigida"].includes(prova.status));
    },
    provasCorrigidas() {
      return this.minhasProvas.filter((prova) => prova.status === "Corrigida");
    },
    provasExibidas() {
      if (this.abaAtiva === "naoCorrigidas") return this.provasNaoCorrigidas;
      if (this.abaAtiva === "corrigidas") return this.provasCorrigidas;
      return this.minhasProvas;
    },
  },
  async mounted() {
    await this.carregarTudo();
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
          .filter((prova) => this.authStore.isProfessor || ["Enviada ao pedagógico", "Não Corrigida", "Corrigida"].includes(prova.status))
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
      this.aviso = `Prova-base criada e atribuída a ${prova.professor.nome}. Ela aparecerá nesta lista quando o professor concluir e enviar.`;
      this.mostrarCriacaoBase = false;
    },
    editarProva(prova) {
      this.$router.push(`/provas/editor/${prova.id}`);
    },
    formatarData(data) {
      return data ? new Date(`${data}T00:00:00`).toLocaleDateString("pt-BR") : "Data desconhecida";
    },
    classeStatus(status) {
      return status === "Corrigida" ? "corrigido" : "rascunho";
    },
    visualizarImpressao(prova) {
      this.$router.push(`/provas/imprimir/${prova.id}`);
    },
    excluirProva(id) {
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
}

.status.rascunho {
  background: #ffc10720;
  color: #ffc107;
}

.status.enviado {
  background: #17a2b820;
  color: #17a2b8;
}

.status.corrigido {
  background: #28a74520;
  color: #28a745;
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


@media (max-width: 768px) {
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
