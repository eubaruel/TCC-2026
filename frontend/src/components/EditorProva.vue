<template>
  <div class="editor-container">
    <div class="editor-header">
      <h2>{{ titulo }}</h2>
      <div class="editor-actions">
        <button type="submit" form="form-prova" class="btn-salvar" :disabled="salvando || carregando">
          {{ salvando ? "Salvando..." : "💾 Salvar" }}
        </button>
        <button type="button" @click="fechar" class="btn-fechar" :disabled="salvando">✕ Fechar</button>
      </div>
    </div>
    <form id="form-prova" class="quill-editor" @submit.prevent="salvar">
      <p v-if="carregando">Carregando dados da prova...</p>
      <table>
        <tbody>
          <tr>
            <td><label for="turmas">Turma(s)</label></td>
            <td>
              <textarea id="turmas" v-model="form.turmasTexto" required rows="2" placeholder="Uma turma por linha, por exemplo:&#10;Turma 2026 A"></textarea>
              <small>Informe uma turma por linha. Cada turma deve ter ao menos 10 caracteres.</small>
            </td>
          </tr>
          <tr>
            <td><label for="disciplina">Disciplina</label></td>
            <td>
              <select
                v-if="!modoDisciplinaManual"
                id="disciplina"
                v-model="form.codigo_disciplina"
                required
                @change="aoAlterarCriterios"
              >
                <option value="">Selecione</option>
                <option v-for="disciplina in disciplinas" :key="disciplina.codigo_disciplina" :value="disciplina.codigo_disciplina">
                  {{ disciplina.nome_disciplina }} ({{ disciplina.codigo_disciplina }})
                </option>
              </select>
              <div v-else class="disciplina-manual">
                <input v-model.trim="form.codigo_disciplina" required placeholder="Código, por exemplo: MAT" @input="aoAlterarCriterios" />
                <input v-model.trim="form.nome_disciplina" required minlength="3" placeholder="Nome, por exemplo: Matemática" @input="aoAlterarCriterios" />
              </div>
              <button v-if="disciplinas.length" type="button" class="btn-alternar-disciplina" @click="alternarModoDisciplina">
                {{ modoDisciplinaManual ? "Selecionar disciplina cadastrada" : "Informar disciplina manualmente" }}
              </button>
              <small v-if="!disciplinas.length">Nenhuma disciplina cadastrada foi encontrada. Informe código e nome manualmente.</small>
            </td>
          </tr>
          <tr><td><label for="tipo">Tipo</label></td><td><select id="tipo" v-model="form.tipo" @change="aoAlterarCriterios"><option>Objetiva</option><option>Dissertativa</option></select></td></tr>
          <tr><td><label for="serie">Série</label></td><td><input id="serie" v-model.number="form.serie" type="number" min="1" required /></td></tr>
          <tr><td><label for="bimestre">Bimestre</label></td><td><input id="bimestre" v-model.trim="form.bimestre" required placeholder="1° bimestre" /></td></tr>
          <tr><td><label for="dataAplicacao">Data de aplicação</label></td><td><input id="dataAplicacao" v-model="form.data_de_aplicacao" type="date" required /></td></tr>
          <tr><td><label for="status">Status</label></td><td><select id="status" v-model="form.status"><option>Não Corrigida</option><option>Corrigida</option></select></td></tr>
        </tbody>
      </table>
      <label for="questoes">Questões (selecione pelo menos cinco)</label>
      <select id="questoes" v-model="form.questoes" multiple size="8" required @change="aoSelecionarQuestoes">
        <option v-for="questao in questoesDisponiveis" :key="questao._id" :value="questao._id">{{ questao.enunciado }}</option>
      </select>
      <small>{{ form.questoes.length }} selecionada(s) de {{ questoesDisponiveis.length }} compatível(is).</small>
      <p v-if="idsQuestoesIndisponiveis.length" class="mensagem-erro">
        {{ idsQuestoesIndisponiveis.length }} questão(ões) da prova não está(ão) mais disponível(is). Substitua-as antes de salvar.
      </p>
      <p v-if="erro" class="mensagem-erro">{{ erro }}</p>
      <button v-if="erroCarregamento" type="button" class="btn-alternar-disciplina" @click="carregarDados">Tentar carregar novamente</button>
    </form>
  </div>
</template>

<script>
import { useAuthStore } from "@/stores/auth";
import { useProvaDraftStore } from "@/stores/provaDraft";
import { listarDisciplinas } from "@/services/disciplinas";
import { listarQuestoes } from "@/services/questoes";
import { atualizarProva, criarProva, listarProvas } from "@/services/provas";

const novoFormulario = () => ({ turmasTexto: "", codigo_disciplina: "", nome_disciplina: "", tipo: "Objetiva", serie: 3, bimestre: "", data_de_aplicacao: "", status: "Não Corrigida", questoes: [] });

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
  data: () => ({
    form: novoFormulario(),
    disciplinas: [],
    questoes: [],
    modoDisciplinaManual: false,
    carregando: true,
    salvando: false,
    erro: "",
    erroCarregamento: "",
    idsQuestoesIndisponiveis: [],
  }),
  computed: {
    disciplinaAtual() {
      if (this.modoDisciplinaManual) {
        const codigo = this.form.codigo_disciplina.trim();
        const nome = this.form.nome_disciplina.trim();
        return codigo && nome ? { codigo_disciplina: codigo, nome_disciplina: nome } : null;
      }
      return this.disciplinas.find((item) => item.codigo_disciplina === this.form.codigo_disciplina) || null;
    },
    questoesDisponiveis() {
      const disciplina = this.disciplinaAtual;
      if (!disciplina) return [];
      const referencias = [disciplina.codigo_disciplina.toLowerCase(), disciplina.nome_disciplina.toLowerCase()];
      return this.questoes.filter((questao) =>
        questao.tipo_questao === this.form.tipo
        && Array.isArray(questao.disciplina)
        && questao.disciplina.some((item) => referencias.includes(String(item).trim().toLowerCase())),
      );
    },
  },
  async mounted() {
    await this.carregarDados();
  },
  methods: {
    mensagemErro(error) {
      return error?.details || error?.message || "Não foi possível carregar os dados.";
    },
    async carregarDados() {
      this.carregando = true;
      this.erro = "";
      this.erroCarregamento = "";
      const [resultadoDisciplinas, resultadoQuestoes] = await Promise.allSettled([listarDisciplinas(), listarQuestoes()]);
      if (resultadoDisciplinas.status === "fulfilled") {
        this.disciplinas = Array.isArray(resultadoDisciplinas.value?.disciplinas) ? resultadoDisciplinas.value.disciplinas : [];
      } else {
        this.disciplinas = [];
        this.erroCarregamento = this.mensagemErro(resultadoDisciplinas.reason);
      }
      if (resultadoQuestoes.status === "fulfilled") {
        this.questoes = Array.isArray(resultadoQuestoes.value?.questoes) ? resultadoQuestoes.value.questoes : [];
      } else {
        this.questoes = [];
        this.erroCarregamento = [this.erroCarregamento, this.mensagemErro(resultadoQuestoes.reason)].filter(Boolean).join(" ");
      }
      this.modoDisciplinaManual = !this.disciplinas.length;
      if (this.provaId) await this.carregarProva();
      else this.carregarRascunho();
      this.carregando = false;
    },
    async carregarProva() {
      try {
        const provas = (await listarProvas({ id: this.provaId })).provas;
        const prova = provas?.[0];
        if (!prova) {
          this.erro = "A prova não foi encontrada ou está inativa.";
          return;
        }
        const disciplinaCadastrada = this.disciplinas.some((item) => item.codigo_disciplina === prova.disciplina.codigo_disciplina);
        this.modoDisciplinaManual = !disciplinaCadastrada;
        const idsAtivos = new Set(this.questoes.map((questao) => questao._id));
        this.idsQuestoesIndisponiveis = prova.questoes.filter((id) => !idsAtivos.has(id));
        this.form = {
          turmasTexto: (Array.isArray(prova.id_turma) ? prova.id_turma : [prova.id_turma]).join("\n"),
          codigo_disciplina: prova.disciplina.codigo_disciplina,
          nome_disciplina: prova.disciplina.nome_disciplina,
          tipo: prova.tipo,
          serie: prova.serie,
          bimestre: prova.bimestre,
          data_de_aplicacao: prova.data_de_aplicacao,
          status: prova.status,
          questoes: prova.questoes.filter((id) => idsAtivos.has(id)),
        };
      } catch (error) {
        this.erro = this.mensagemErro(error);
      }
    },
    carregarRascunho() {
      const rascunho = this.draftStore.questoes;
      this.form.questoes = rascunho.map((questao) => questao._id);
      const primeira = rascunho[0];
      if (!primeira) return;
      this.form.tipo = primeira.tipo_questao || (primeira.tipo === "objetiva" ? "Objetiva" : "Dissertativa");
      const referencias = primeira.disciplinasOriginais || (Array.isArray(primeira.disciplina) ? primeira.disciplina : []);
      const disciplina = this.disciplinas.find((item) =>
        referencias.some((referencia) => [item.codigo_disciplina, item.nome_disciplina].some((valor) => valor.toLowerCase() === String(referencia).toLowerCase())),
      );
      if (disciplina) {
        this.form.codigo_disciplina = disciplina.codigo_disciplina;
        this.modoDisciplinaManual = false;
      } else if (referencias.length) {
        this.form.nome_disciplina = [...referencias].sort((a, b) => String(b).length - String(a).length)[0];
        this.modoDisciplinaManual = true;
      }
      this.aoAlterarCriterios();
    },
    alternarModoDisciplina() {
      this.modoDisciplinaManual = !this.modoDisciplinaManual;
      this.form.codigo_disciplina = "";
      this.form.nome_disciplina = "";
      this.aoAlterarCriterios();
    },
    aoAlterarCriterios() {
      const idsCompativeis = new Set(this.questoesDisponiveis.map((questao) => questao._id));
      const quantidadeAnterior = this.form.questoes.length;
      this.form.questoes = this.form.questoes.filter((id) => idsCompativeis.has(id));
      if (quantidadeAnterior !== this.form.questoes.length) this.erro = "Questões incompatíveis com o novo tipo ou disciplina foram removidas.";
    },
    aoSelecionarQuestoes() {
      if (this.form.questoes.length >= 5) this.idsQuestoesIndisponiveis = [];
    },
    turmas() {
      return this.form.turmasTexto.split(/\r?\n/).map((turma) => turma.trim()).filter(Boolean);
    },
    payload() {
      const turmas = this.turmas();
      return { id_turma: turmas.length === 1 ? turmas[0] : turmas, professor: { nome: this.authStore.user.nome }, disciplina: { codigo_disciplina: this.disciplinaAtual.codigo_disciplina, nome_disciplina: this.disciplinaAtual.nome_disciplina }, status: this.form.status, tipo: this.form.tipo, serie: Number(this.form.serie), bimestre: this.form.bimestre, data_de_aplicacao: this.form.data_de_aplicacao, questoes: [...this.form.questoes] };
    },
    async salvar() {
      this.erro = "";
      if (this.salvando) return;
      const turmas = this.turmas();
      if (!turmas.length || turmas.some((turma) => turma.length < 10)) { this.erro = "Cada turma deve possuir ao menos 10 caracteres."; return; }
      if (!this.disciplinaAtual) { this.erro = "Selecione uma disciplina ou informe seu código e nome."; return; }
      if (this.form.questoes.length < 5) { this.erro = "Selecione ao menos cinco questões."; return; }
      this.salvando = true;
      try {
        if (this.provaId) await atualizarProva(this.provaId, this.payload());
        else await criarProva(this.payload());
        this.draftStore.limpar();
        this.$emit("salvo");
      } catch (error) {
        this.erro = this.mensagemErro(error);
      } finally {
        this.salvando = false;
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

.btn-salvar:disabled,
.btn-fechar:disabled {
  cursor: wait;
  opacity: 0.65;
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
  overflow: auto;
  border-radius: 8px;
}

.quill-editor table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0 10px;
}

.quill-editor td:first-child {
  width: 160px;
  vertical-align: top;
  padding-top: 10px;
}

.quill-editor input,
.quill-editor select,
.quill-editor textarea {
  box-sizing: border-box;
  width: 100%;
  padding: 10px;
  border: 1px solid #d8d8d8;
  border-radius: 6px;
  font: inherit;
}

.quill-editor select[multiple] {
  min-height: 180px;
  margin: 8px 0;
}

.quill-editor small {
  display: block;
  margin-top: 5px;
  color: #666;
}

.disciplina-manual {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 8px;
}

.btn-alternar-disciplina {
  margin-top: 8px;
  padding: 7px 10px;
  border: 1px solid #00488b;
  border-radius: 6px;
  background: transparent;
  color: #00488b;
  cursor: pointer;
}

.mensagem-erro {
  color: #b42318;
  font-weight: 500;
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

  .quill-editor table,
  .quill-editor tbody,
  .quill-editor tr,
  .quill-editor td {
    display: block;
    width: 100%;
  }

  .quill-editor td:first-child {
    padding-top: 0;
  }

  .disciplina-manual {
    grid-template-columns: 1fr;
  }
}
</style>
