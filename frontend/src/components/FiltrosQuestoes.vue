<template>
  <div class="filtros-questoes">
    <label class="filtro">
      Disciplina
      <select :value="modelValue.disciplina" :disabled="desabilitado" @change="atualizar('disciplina', $event.target.value)">
        <option value="">Todas as disciplinas</option>
        <option v-for="disciplina in opcoes" :key="disciplina.codigo_disciplina || disciplina.nome_disciplina" :value="disciplina.codigo_disciplina || disciplina.nome_disciplina">{{ disciplina.nome_disciplina }}</option>
      </select>
    </label>
    <label class="filtro">
      Dificuldade
      <select :value="modelValue.dificuldade" :disabled="desabilitado" @change="atualizar('dificuldade', $event.target.value)">
        <option value="">Todas as dificuldades</option>
        <option v-for="dificuldade in dificuldades" :key="dificuldade" :value="dificuldade">{{ dificuldade }}</option>
      </select>
    </label>
    <label class="filtro">
      Autor
      <input :value="modelValue.autor" :disabled="desabilitado" type="text" placeholder="Nome do autor..." @input="atualizar('autor', $event.target.value)" />
    </label>
    <label class="filtro filtro-enunciado">
      Enunciado
      <textarea :value="modelValue.enunciado" :disabled="desabilitado" rows="2" placeholder="Buscar no enunciado..." @input="atualizar('enunciado', $event.target.value)"></textarea>
    </label>
  </div>
</template>

<script>
import { opcoesDisciplinas } from "@/utils/filtrosQuestoes";

export default {
  name: "FiltrosQuestoes",
  props: {
    modelValue: { type: Object, required: true },
    disciplinas: { type: Array, default: () => [] },
    questoes: { type: Array, default: () => [] },
    desabilitado: { type: Boolean, default: false },
  },
  emits: ["update:modelValue"],
  data: () => ({ dificuldades: ["Muito Fácil", "Fácil", "Médio", "Difícil", "Muito Difícil"] }),
  computed: { opcoes() { return opcoesDisciplinas(this.questoes, this.disciplinas); } },
  methods: { atualizar(campo, valor) { this.$emit("update:modelValue", { ...this.modelValue, [campo]: valor }); } },
};
</script>

<style scoped>
.filtros-questoes {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 16px;
}
.filtro {
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-width: 0;
  font-size: 13px;
  font-weight: 500;
}
.filtro-enunciado { grid-column: 1 / -1; }
input, select, textarea {
  box-sizing: border-box;
  width: 100%;
  min-width: 0;
  padding: 10px;
  border: 1px solid #d8d8d8;
  border-radius: 6px;
  background: white;
  color: inherit;
  font: inherit;
}
textarea { resize: vertical; }
:global(.tema-escuro .filtros-questoes input),
:global(.tema-escuro .filtros-questoes select),
:global(.tema-escuro .filtros-questoes textarea) {
  background: #2a2a2a;
  border-color: #404040;
}
@media (max-width: 600px) {
  .filtros-questoes { grid-template-columns: 1fr; }
}
</style>
