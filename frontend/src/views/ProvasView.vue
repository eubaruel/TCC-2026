<template>
  <div class="provas-container">
    <div class="page-header">
      <h2>Minhas Provas</h2>
      <div class="header-line"></div>
    </div>

    <!-- Tabs -->
    <div class="provas-tabs">
      <button
        @click="abaAtiva = 'minhas'"
        class="tab-btn"
        :class="{ ativo: abaAtiva === 'minhas' }"
      >
        Minhas Provas ({{ minhasProvas.length }})
      </button>
      <button
        @click="abaAtiva = 'enviadas'"
        class="tab-btn"
        :class="{ ativo: abaAtiva === 'enviadas' }"
      >
        Provas Enviadas
      </button>
      <button
        @click="abaAtiva = 'devolvidas'"
        class="tab-btn"
        :class="{ ativo: abaAtiva === 'devolvidas' }"
      >
        Provas Devolvidas
      </button>
    </div>

    <!-- Botão Criar Prova - APENAS na aba "Minhas Provas" -->
    <div v-if="abaAtiva === 'minhas'" class="actions-bar">
      <button @click="abrirEditor" class="btn-criar-prova">
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
        Criar Prova
      </button>
    </div>

    <!-- Lista de Provas - Minhas Provas -->
    <div v-if="abaAtiva === 'minhas'" class="lista-provas">
      <div v-if="minhasProvas.length === 0" class="sem-provas">
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
          <p>Você ainda não criou nenhuma prova.</p>
          <p class="sub">Clique em "Criar Prova" para começar.</p>
        </div>
      </div>
      <div v-else>
        <div v-for="prova in minhasProvas" :key="prova.id" class="prova-card">
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
                <span class="status" :class="prova.status || 'rascunho'">
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
              @click="editarProva(prova)"
              class="btn-editar"
              title="Editar"
            >
              ✏️
            </button>
            <button
              @click="baixarProva(prova)"
              class="btn-baixar"
              title="Baixar"
            >
              📥
            </button>
            <button
              @click="enviarDrive(prova)"
              class="btn-drive"
              title="Enviar para Drive"
            >
              ☁️
            </button>
            <button
              @click="excluirProva(prova.id)"
              class="btn-excluir-prova"
              title="Excluir"
            >
              🗑️
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Provas Enviadas -->
    <div v-if="abaAtiva === 'enviadas'" class="lista-provas">
      <div class="sem-provas">
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
              d="M22 2L11 13M22 2L15 22L11 13M22 2L9 7M11 13L2 9"
              stroke="currentColor"
              stroke-width="2"
            />
          </svg>
          <p>Nenhuma prova enviada</p>
          <p class="sub">
            As provas enviadas para o Processo Pedagógico aguardando análise
            aparecerão aqui.
          </p>
          <p class="sub" style="margin-top: 8px; color: #17a2b8">
            📤 Acompanhe o status das suas provas após o envio.
          </p>
        </div>
      </div>
    </div>

    <!-- Provas Devolvidas -->
    <div v-if="abaAtiva === 'devolvidas'" class="lista-provas">
      <div class="sem-provas">
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
              d="M12 2L15 8L22 9L17 14L18 21L12 17.5L6 21L7 14L2 9L9 8L12 2Z"
              stroke="currentColor"
              stroke-width="2"
            />
            <path
              d="M12 8V12M12 16H12.01"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
            />
          </svg>
          <p>Nenhuma prova devolvida</p>
          <p class="sub">
            As provas que forem devolvidas pelo Processo Pedagógico por estarem
            fora do padrão exigido pela escola aparecerão aqui.
          </p>
          <p class="sub" style="margin-top: 8px; color: #dc3545">
            📌 Verifique o motivo da devolução e faça os ajustes necessários
            antes de reenviar.
          </p>
        </div>
      </div>
    </div>

    <!-- Modal do Editor -->
    <div v-if="mostrarEditor" class="modal-overlay" @click.self="fecharEditor">
      <EditorProva
        :provaId="provaEmEdicao?.id || null"
        :titulo="provaEmEdicao?.titulo || 'Nova Prova'"
        @salvo="provaSalva"
        @fechar="fecharEditor"
      />
    </div>
  </div>
</template>

<script>
import EditorProva from "@/components/EditorProva.vue";
import { useAuthStore } from "@/stores/auth";
import { listarQuestoes } from "@/services/questoes";
import { excluirProva as excluirProvaApi, listarProvas } from "@/services/provas";

export default {
  name: "ProvasView",
  components: { EditorProva },
  setup() {
    return { authStore: useAuthStore() };
  },
  data: () => ({
    abaAtiva: "minhas",
    minhasProvas: [],
    todasQuestoes: [],
    mostrarEditor: false,
    provaEmEdicao: null,
    erro: "",
  }),
  async mounted() {
    await Promise.all([this.carregarQuestoes(), this.carregarProvas()]);
  },
  methods: {
    async carregarQuestoes() {
      try {
        this.todasQuestoes = (await listarQuestoes()).questoes;
      } catch (error) {
        this.erro = error.details || error.message;
      }
    },
    async carregarProvas() {
      try {
        const provas = (await listarProvas({ nome: this.authStore.user?.nome })).provas;
        this.minhasProvas = provas.map((prova) => ({
          ...prova,
          id: prova._id,
          titulo: `${prova.disciplina.nome_disciplina} - ${Array.isArray(prova.id_turma) ? prova.id_turma.join(", ") : prova.id_turma}`,
          criadaEm: prova.data_de_aplicacao,
        }));
      } catch (error) {
        this.erro = error.details || error.message;
      }
    },
    abrirEditor(prova = null) {
      this.provaEmEdicao = prova?.id ? prova : null;
      this.mostrarEditor = true;
    },
    editarProva(prova) {
      this.abrirEditor(prova);
    },
    fecharEditor() {
      this.mostrarEditor = false;
      this.provaEmEdicao = null;
    },
    async provaSalva() {
      this.fecharEditor();
      await Promise.all([this.carregarQuestoes(), this.carregarProvas()]);
    },
    formatarData(data) {
      return data ? new Date(`${data}T00:00:00`).toLocaleDateString("pt-BR") : "Data desconhecida";
    },
    async baixarProva(prova) {
      const questoes = this.todasQuestoes.filter((questao) => prova.questoes.includes(questao._id));
      const corpo = questoes.map((questao, index) => `<section><p><strong>${index + 1}.</strong> ${questao.enunciado}</p>${questao.alternativas ? `<ol>${questao.alternativas.map((alternativa) => `<li>${alternativa.texto}</li>`).join("")}</ol>` : `<p>Linhas para resposta: ${questao.numero_linhas}</p>`}</section>`).join("");
      const blob = new Blob([`<html><meta charset="UTF-8"><body><h1>${prova.titulo}</h1>${corpo}</body></html>`], { type: "text/html" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `${prova.titulo}.html`;
      link.click();
      URL.revokeObjectURL(url);
    },
    enviarDrive() {
      // A API não disponibiliza endpoint para envio ao Google Drive.
    },
    excluirProva(id) {
      window.$modal.abrir({ titulo: "Excluir prova", mensagem: "Deseja excluir esta prova?", tipo: "confirmacao", onConfirm: async () => { try { await excluirProvaApi(id); await this.carregarProvas(); } catch (error) { this.erro = error.details || error.message; } } });
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

/* Modal Editor Overlay */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 20px;
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

  .modal-overlay {
    padding: 10px;
  }
}
</style>
