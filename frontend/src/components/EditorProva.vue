<template>
  <div class="editor-container">
    <div class="editor-header">
      <h2>{{ titulo }}</h2>
      <div class="editor-actions">
        <button @click="salvar" class="btn-salvar">💾 Salvar</button>
        <button @click="fechar" class="btn-fechar">✕ Fechar</button>
      </div>
    </div>
    <form class="quill-editor" @submit.prevent="salvar">
      <table>
        <tbody>
          <tr><td><label for="turma">Turma</label></td><td><input id="turma" v-model.trim="form.id_turma" required minlength="10" placeholder="Turma 2026 A" /></td></tr>
          <tr><td><label for="disciplina">Disciplina</label></td><td><select id="disciplina" v-model="form.codigo_disciplina" required><option value="">Selecione</option><option v-for="disciplina in disciplinas" :key="disciplina.codigo_disciplina" :value="disciplina.codigo_disciplina">{{ disciplina.nome_disciplina }}</option></select></td></tr>
          <tr><td><label for="tipo">Tipo</label></td><td><select id="tipo" v-model="form.tipo"><option>Objetiva</option><option>Dissertativa</option></select></td></tr>
          <tr><td><label for="serie">Série</label></td><td><input id="serie" v-model.number="form.serie" type="number" min="1" required /></td></tr>
          <tr><td><label for="bimestre">Bimestre</label></td><td><input id="bimestre" v-model.trim="form.bimestre" required placeholder="1° bimestre" /></td></tr>
          <tr><td><label for="dataAplicacao">Data de aplicação</label></td><td><input id="dataAplicacao" v-model="form.data_de_aplicacao" type="date" required /></td></tr>
          <tr><td><label for="status">Status</label></td><td><select id="status" v-model="form.status"><option>Não Corrigida</option><option>Corrigida</option></select></td></tr>
        </tbody>
      </table>
      <label for="questoes">Questões (selecione pelo menos cinco)</label>
      <select id="questoes" v-model="form.questoes" multiple size="8" required>
        <option v-for="questao in questoesDisponiveis" :key="questao._id" :value="questao._id">{{ questao.enunciado }}</option>
      </select>
      <p v-if="erro">{{ erro }}</p>
    </form>
  </div>
</template>

<script>
import { useAuthStore } from "@/stores/auth";
import { useProvaDraftStore } from "@/stores/provaDraft";
import { listarDisciplinas } from "@/services/disciplinas";
import { listarQuestoes } from "@/services/questoes";
import { atualizarProva, criarProva, listarProvas } from "@/services/provas";

const novoFormulario = () => ({ id_turma: "", codigo_disciplina: "", tipo: "Objetiva", serie: 3, bimestre: "", data_de_aplicacao: "", status: "Não Corrigida", questoes: [] });

export default {
  name: "EditorProva",
  props: {
    provaId: { type: [String, Number], default: null },
    titulo: { type: String, default: "Nova Prova" },
  },
  emits: ["fechar", "salvo"],
  setup() {
    return { authStore: useAuthStore(), draftStore: useProvaDraftStore() };
  },
  data: () => ({ form: novoFormulario(), disciplinas: [], questoes: [], erro: "" }),
  computed: {
    questoesDisponiveis() {
      const disciplina = this.disciplinas.find((item) => item.codigo_disciplina === this.form.codigo_disciplina);
      if (!disciplina) return [];
      const referencias = [disciplina.codigo_disciplina.toLowerCase(), disciplina.nome_disciplina.toLowerCase()];
      return this.questoes.filter((questao) => questao.tipo_questao === this.form.tipo && questao.disciplina.some((item) => referencias.includes(item.toLowerCase())));
    },
  },
  async mounted() {
    try {
      const [disciplinas, questoes] = await Promise.all([listarDisciplinas(), listarQuestoes()]);
      this.disciplinas = disciplinas.disciplinas;
      this.questoes = questoes.questoes;
      if (this.provaId) {
        const provas = (await listarProvas({ id: this.provaId })).provas;
        const prova = provas[0];
        if (prova) this.form = { id_turma: Array.isArray(prova.id_turma) ? prova.id_turma.join(", ") : prova.id_turma, codigo_disciplina: prova.disciplina.codigo_disciplina, tipo: prova.tipo, serie: prova.serie, bimestre: prova.bimestre, data_de_aplicacao: prova.data_de_aplicacao, status: prova.status, questoes: [...prova.questoes] };
      } else {
        this.form.questoes = this.draftStore.questoes.map((questao) => questao._id);
      }
    } catch (error) {
      this.erro = error.details || error.message;
    }
  },
  methods: {
    disciplinaSelecionada() {
      return this.disciplinas.find((disciplina) => disciplina.codigo_disciplina === this.form.codigo_disciplina);
    },
    payload() {
      const disciplina = this.disciplinaSelecionada();
      return { id_turma: this.form.id_turma, professor: { nome: this.authStore.user.nome }, disciplina: { codigo_disciplina: disciplina.codigo_disciplina, nome_disciplina: disciplina.nome_disciplina }, status: this.form.status, tipo: this.form.tipo, serie: Number(this.form.serie), bimestre: this.form.bimestre, data_de_aplicacao: this.form.data_de_aplicacao, questoes: this.form.questoes };
    },
    async salvar() {
      this.erro = "";
      if (!this.disciplinaSelecionada()) { this.erro = "Selecione uma disciplina."; return; }
      if (this.form.questoes.length < 5) { this.erro = "Selecione ao menos cinco questões."; return; }
      try {
        if (this.provaId) await atualizarProva(this.provaId, this.payload());
        else await criarProva(this.payload());
        this.draftStore.limpar();
        this.$emit("salvo");
      } catch (error) {
        this.erro = error.details || error.message;
      }
    },
    fechar() {
      this.$emit("fechar");
    },
  },
};
</script>
<style scoped>
.editor-container {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 1000px;
  margin: 0 auto;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
}

.tema-escuro .editor-container {
  background: #2a2a2a;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e0e0e0;
}

.tema-escuro .editor-header {
  border-bottom-color: #404040;
}

.editor-header h2 {
  font-size: 20px;
  font-weight: 600;
  margin: 0;
  color: inherit;
}

.editor-actions {
  display: flex;
  gap: 12px;
}

.btn-salvar {
  padding: 8px 16px;
  background: #28a745;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.btn-salvar:hover {
  background: #218838;
}

.btn-fechar {
  padding: 8px 16px;
  background: #dc3545;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.btn-fechar:hover {
  background: #c82333;
}

.quill-editor {
  flex: 1;
  overflow: hidden;
  border-radius: 8px;
}

:deep(.ql-toolbar) {
  border-radius: 8px 8px 0 0;
  border-color: #e0e0e0;
}

:deep(.ql-container) {
  border-radius: 0 0 8px 8px;
  border-color: #e0e0e0;
  min-height: 400px;
}

.tema-escuro :deep(.ql-toolbar) {
  border-color: #404040;
  background: #1a1a1a;
}

.tema-escuro :deep(.ql-container) {
  border-color: #404040;
  background: #1a1a1a;
  color: #e5e5e5;
}

.tema-escuro :deep(.ql-picker-label) {
  color: #e5e5e5;
}

.tema-escuro :deep(.ql-stroke) {
  stroke: #e5e5e5;
}

.tema-escuro :deep(.ql-fill) {
  fill: #e5e5e5;
}

@media (max-width: 768px) {
  .editor-container {
    padding: 12px;
    max-height: 95vh;
  }

  .editor-header {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }

  .editor-actions {
    justify-content: flex-end;
  }
}
</style>
