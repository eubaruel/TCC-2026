<template>
  <div class="modal-overlay">
    <div class="modal-container" role="dialog" aria-modal="true" aria-labelledby="titulo-prova-base">
      <div class="modal-header">
        <h3 id="titulo-prova-base">Criar prova-base</h3>
        <button type="button" class="modal-close" :disabled="salvando" aria-label="Fechar" @click="fechar">&times;</button>
      </div>

      <form @submit.prevent="salvar">
        <div class="modal-body">
          <p class="info-text">Defina os dados da prova. O professor responsável adicionará as questões depois.</p>
          <p v-if="carregando" class="info-text">Carregando professores e disciplinas...</p>
          <div v-else class="form-grid">
            <div class="form-group-modal campo-largo">
              <label for="base-professor">Professor responsável *</label>
              <input id="base-professor" v-model="buscaProfessor" list="base-professores" autocomplete="off" required :disabled="salvando" placeholder="Digite ou selecione o professor" @input="selecionarProfessor" />
              <datalist id="base-professores">
                <option v-for="professor in professores" :key="professor.registro" :value="rotuloProfessor(professor)" />
              </datalist>
              <small v-if="!professores.length" class="info-text">Nenhum professor ativo cadastrado.</small>
            </div>

            <div class="form-group-modal">
              <label for="base-disciplina">Disciplina *</label>
              <select id="base-disciplina" v-model="formulario.codigoDisciplina" required :disabled="salvando" @change="selecionarDisciplina">
                <option value="">Selecione</option>
                <option v-for="disciplina in disciplinas" :key="disciplina.codigo_disciplina" :value="disciplina.codigo_disciplina">
                  {{ disciplina.nome_disciplina }} ({{ disciplina.codigo_disciplina }})
                </option>
              </select>
              <small v-if="!disciplinas.length" class="info-text">Nenhuma disciplina cadastrada.</small>
            </div>

            <div class="form-group-modal">
              <label for="base-turmas">Turma(s) *</label>
              <input id="base-turmas" v-model="buscaTurma" list="base-turmas-opcoes" autocomplete="off" :required="!turmasSelecionadas.length" :disabled="salvando" placeholder="Digite ou selecione uma turma" @change="adicionarTurma" @keydown.enter.prevent="adicionarTurma" />
              <datalist id="base-turmas-opcoes">
                <option v-for="turma in turmasDisponiveis" :key="turma" :value="turma" />
              </datalist>
              <div v-if="turmasSelecionadas.length" class="turmas-selecionadas">
                <span v-for="turma in turmasSelecionadas" :key="turma" class="turma-selecionada">
                  {{ turma }}
                  <button type="button" :disabled="salvando" :aria-label="`Remover turma ${turma}`" @click="removerTurma(turma)">&times;</button>
                </span>
              </div>
            </div>
            <div class="form-group-modal">
              <label for="base-serie">Série *</label>
              <select id="base-serie" v-model.number="formulario.serie" required :disabled="salvando">
                <option v-for="serie in 3" :key="serie" :value="serie">{{ serie }}ª série</option>
              </select>
            </div>
            <div class="form-group-modal">
              <label for="base-periodo-letivo">Período letivo *</label>
              <select id="base-periodo-letivo" v-model="formulario.periodo_letivo" required :disabled="salvando">
                <option value="">Selecione</option>
                <option v-for="periodo in 4" :key="periodo" :value="`${periodo}º período letivo`">{{ periodo }}º período letivo</option>
              </select>
            </div>
            <div class="form-group-modal">
              <label for="base-data">Data de aplicação *</label>
              <input id="base-data" v-model="formulario.data" type="date" required :disabled="salvando" />
            </div>
            <div class="form-group-modal">
              <label for="base-quantidade">Quantidade de questões *</label>
              <input id="base-quantidade" v-model.number="formulario.quantidade_questoes" type="number" min="2" max="10" step="1" inputmode="numeric" required :disabled="salvando" placeholder="Ex.: 5" aria-describedby="base-quantidade-ajuda" />
              <small id="base-quantidade-ajuda" class="info-text">De 2 a 10 questões.</small>
            </div>
          </div>
          <p v-if="erro" class="mensagem-erro" role="alert">{{ erro }}</p>
          <button v-if="erro && (!professores.length || !disciplinas.length)" type="button" class="btn-modal-cancelar" :disabled="carregando" @click="carregar">Tentar carregar novamente</button>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn-modal-cancelar" :disabled="salvando" @click="fechar">Cancelar</button>
          <button type="submit" class="btn-modal-salvar" :disabled="carregando || salvando || !professores.length || !disciplinas.length">
            {{ salvando ? "Salvando..." : "Criar prova-base" }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { listarUsuarios } from "@/services/usuarios";
import { listarDisciplinas } from "@/services/disciplinas";
import { criarProva } from "@/services/provas";

export default {
  name: "CriarProvaBase",
  emits: ["fechar", "criada"],
  data: () => ({
    formulario: { registroProfessor: "", codigoDisciplina: "", turmasTexto: "", serie: 3, periodo_letivo: "", data: "", quantidade_questoes: "" },
    professores: [],
    disciplinas: [],
    buscaProfessor: "",
    buscaTurma: "",
    carregando: true,
    salvando: false,
    erro: "",
  }),
  computed: {
    turmasSelecionadas() {
      return [...new Set(this.formulario.turmasTexto.split(/\r?\n/).map((turma) => turma.trim()).filter(Boolean))];
    },
    turmasCadastradas() {
      return [...new Set(this.disciplinas.map((disciplina) => disciplina.turma?.trim()).filter(Boolean))].sort((a, b) => a.localeCompare(b, "pt-BR"));
    },
    turmasDisponiveis() {
      return this.turmasCadastradas.filter((turma) => !this.turmasSelecionadas.includes(turma));
    },
  },
  mounted() {
    this.carregar();
  },
  methods: {
    async carregar() {
      this.carregando = true;
      this.erro = "";
      try {
        const [usuarios, disciplinas] = await Promise.all([
          listarUsuarios({ role: "Professor", ativo: true }),
          listarDisciplinas(),
        ]);
        this.professores = usuarios.usuarios;
        this.disciplinas = disciplinas.disciplinas;
      } catch (error) {
        this.erro = error.details || error.message;
      } finally {
        this.carregando = false;
      }
    },
    rotuloProfessor(professor) { return `${professor.nome} (${professor.registro})`; },
    selecionarProfessor() {
      if (this.salvando) return;
      const professor = this.professores.find((item) => this.rotuloProfessor(item) === this.buscaProfessor.trim());
      this.formulario.registroProfessor = professor?.registro ?? "";
    },
    adicionarTurma() {
      if (this.salvando || !this.buscaTurma.trim()) return;
      const turma = this.buscaTurma.trim();
      if (!this.turmasCadastradas.includes(turma)) {
        this.erro = "Selecione uma turma cadastrada na lista de sugestões.";
        return;
      }
      this.formulario.turmasTexto = [...new Set([...this.turmasSelecionadas, turma])].join("\n");
      this.buscaTurma = "";
      this.erro = "";
    },
    removerTurma(turma) {
      if (!this.salvando) this.formulario.turmasTexto = this.turmasSelecionadas.filter((item) => item !== turma).join("\n");
    },
    selecionarDisciplina() {
      const disciplina = this.disciplinas.find((item) => item.codigo_disciplina === this.formulario.codigoDisciplina);
      this.formulario.turmasTexto = disciplina?.turma || "";
      this.buscaTurma = "";
      const professor = this.professores.find((item) => item.registro === disciplina?.professor?.registro);
      if (professor) {
        this.formulario.registroProfessor = professor.registro;
        this.buscaProfessor = this.rotuloProfessor(professor);
      }
    },
    fechar() {
      if (!this.salvando) this.$emit("fechar");
    },
    async salvar() {
      if (this.carregando || this.salvando) return;
      this.erro = "";
      this.selecionarProfessor();
      if (this.buscaTurma.trim()) {
        this.adicionarTurma();
        if (this.buscaTurma.trim()) return;
      }
      const professor = this.professores.find((item) => item.registro === this.formulario.registroProfessor);
      const disciplina = this.disciplinas.find((item) => item.codigo_disciplina === this.formulario.codigoDisciplina);
      const turmas = this.turmasSelecionadas;
      if (!professor || !disciplina || !turmas.length || !this.formulario.periodo_letivo || !this.formulario.data
          || !Number.isInteger(this.formulario.quantidade_questoes) || this.formulario.quantidade_questoes < 2 || this.formulario.quantidade_questoes > 10
          || ![1, 2, 3].includes(this.formulario.serie) || ![1, 2, 3, 4].some((numero) => this.formulario.periodo_letivo === `${numero}º período letivo`)) {
        this.erro = "Preencha todos os dados da prova corretamente.";
        return;
      }

      this.salvando = true;
      try {
        const resposta = await criarProva({
          professor: { registro: professor.registro, nome: professor.nome },
          disciplina: { codigo_disciplina: disciplina.codigo_disciplina, nome_disciplina: disciplina.nome_disciplina },
          id_turma: turmas.length === 1 ? turmas[0] : turmas,
          tipo: "Objetiva",
          serie: this.formulario.serie,
          periodo_letivo: this.formulario.periodo_letivo,
          data_de_aplicacao: this.formulario.data,
          quantidade_questoes: this.formulario.quantidade_questoes,
        });
        this.$emit("criada", resposta.prova);
      } catch (error) {
        this.erro = error.details || error.message;
      } finally {
        this.salvando = false;
      }
    },
  },
};
</script>

<style scoped>
/* Mesmo padrão dos modais da Gestão de Usuários. */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
}
.modal-container {
  background: white;
  border-radius: 12px;
  max-width: 700px;
  width: 90%;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
  max-height: 90vh;
  overflow-y: auto;
}
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e0e0e0;
}
.modal-header h3 { font-size: 18px; font-weight: 600; margin: 0; }
.modal-close { background: none; border: none; font-size: 24px; cursor: pointer; color: #999; }
.modal-body { padding: 24px; }
.form-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }
.form-group-modal { min-width: 0; }
.campo-largo { grid-column: 1 / -1; }
.form-group-modal label { display: block; margin-bottom: 8px; font-weight: 500; font-size: 14px; }
.form-group-modal input, .form-group-modal select {
  box-sizing: border-box;
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font: inherit;
  font-size: 14px;
}
.turmas-selecionadas { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px; }
.turma-selecionada { display: inline-flex; align-items: center; gap: 6px; max-width: 100%; overflow-wrap: anywhere; padding: 4px 8px; background: #eef5fc; color: #00488b; border: 1px solid #c9ddf0; border-radius: 6px; font-size: 12px; }
.turma-selecionada button { flex-shrink: 0; padding: 0 2px; border: 0; background: transparent; color: inherit; font-size: 18px; cursor: pointer; }
.info-text { font-size: 12px; color: #888; margin-bottom: 16px; }
.mensagem-erro { color: #dc3545; font-size: 13px; margin-top: 16px; }
.modal-footer { display: flex; gap: 12px; padding: 20px 24px; border-top: 1px solid #e0e0e0; justify-content: flex-end; }
.btn-modal-salvar { padding: 10px 20px; background: #28a745; color: white; border: none; border-radius: 6px; cursor: pointer; }
.btn-modal-salvar:hover:not(:disabled) { background: #218838; }
.btn-modal-cancelar { padding: 10px 20px; background: transparent; border: 1px solid #ddd; border-radius: 6px; cursor: pointer; color: inherit; }
button:disabled { opacity: 0.6; cursor: not-allowed; }
.tema-escuro .modal-container { background: #2a2a2a; }
.tema-escuro .modal-header, .tema-escuro .modal-footer { border-bottom-color: #404040; border-top-color: #404040; }
.tema-escuro input, .tema-escuro select, .tema-escuro textarea { background: #1a1a1a; border-color: #404040; color: #e5e5e5; }
@media (max-width: 768px) { .form-grid { grid-template-columns: 1fr; } }
</style>
