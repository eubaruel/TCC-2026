<template>
  <div class="questao-editor">
    <div class="questao-cabecalho">
      <h4>Questão {{ numero }}</h4>
      <div class="questao-acoes">
        <button type="button" title="Mover para cima" :disabled="primeira" @click="$emit('mover', -1)">↑</button>
        <button type="button" title="Mover para baixo" :disabled="ultima" @click="$emit('mover', 1)">↓</button>
        <button type="button" class="btn-remover" title="Remover questão" @click="$emit('remover')">🗑️</button>
      </div>
    </div>

    <div class="linha-campos">
      <div class="campo">
        <label>Assunto</label>
        <input :value="questao.assunto" placeholder="Ex.: Álgebra" @input="atualizar('assunto', $event.target.value)" />
      </div>
      <div class="campo">
        <label>Dificuldade</label>
        <select :value="questao.dificuldade" @change="atualizar('dificuldade', $event.target.value)">
          <option v-for="nivel in dificuldades" :key="nivel">{{ nivel }}</option>
        </select>
      </div>
    </div>

    <div class="campo">
      <label>Enunciado</label>
      <EditorQuill
        :modelValue="questao.enunciado"
        placeholder="Digite o enunciado da questão. Use o ícone de imagem para inserir figuras."
        @update:modelValue="atualizar('enunciado', $event)"
      />
    </div>

    <div v-if="tipo === 'Objetiva'" class="campo">
      <label>Alternativas (marque a correta)</label>
      <div v-for="(alternativa, index) in questao.alternativas" :key="index" class="alternativa">
        <label class="marcador" :class="{ correta: questao.indiceCorreta === index }">
          <input
            type="radio"
            :name="`correta-${questao._idLocal}`"
            :checked="questao.indiceCorreta === index"
            @change="atualizar('indiceCorreta', index)"
          />
          {{ letras[index] }}
        </label>
        <EditorQuill
          class="alternativa-editor"
          compacto
          :modelValue="alternativa"
          :placeholder="`Alternativa ${letras[index]}`"
          @update:modelValue="atualizarAlternativa(index, $event)"
        />
      </div>
    </div>

    <div v-else class="campo campo-linhas">
      <label>Número de linhas para resposta</label>
      <input
        type="number"
        min="1"
        :value="questao.numeroLinhas"
        @input="atualizar('numeroLinhas', Number($event.target.value))"
      />
    </div>

    <small v-if="questao._idBanco" class="aviso-banco">
      Questão já cadastrada no banco: alterações serão gravadas nela ao salvar.
    </small>
  </div>
</template>

<script>
import EditorQuill from "@/components/EditorQuill.vue";
import { LETRAS } from "@/stores/provaDraft";

export default {
  name: "QuestaoEditor",
  components: { EditorQuill },
  props: {
    questao: { type: Object, required: true },
    numero: { type: Number, required: true },
    tipo: { type: String, default: "Objetiva" },
    primeira: { type: Boolean, default: false },
    ultima: { type: Boolean, default: false },
  },
  emits: ["atualizar", "mover", "remover"],
  data: () => ({
    letras: LETRAS,
    dificuldades: ["Muito Fácil", "Fácil", "Médio", "Difícil", "Muito Difícil"],
  }),
  methods: {
    atualizar(campo, valor) {
      this.$emit("atualizar", { [campo]: valor });
    },
    atualizarAlternativa(index, valor) {
      const alternativas = [...this.questao.alternativas];
      alternativas[index] = valor;
      this.atualizar("alternativas", alternativas);
    },
  },
};
</script>

<style scoped>
.questao-editor {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  padding: 16px 20px;
  margin-bottom: 16px;
  transition: all 0.3s ease;
}

.tema-escuro .questao-editor {
  background: #2a2a2a;
  border-color: #404040;
}

.questao-cabecalho {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e0e0e0;
}

.tema-escuro .questao-cabecalho {
  border-bottom-color: #404040;
}

.questao-cabecalho h4 {
  font-size: 16px;
  font-weight: 600;
  color: #00488b;
}

.tema-escuro .questao-cabecalho h4 {
  color: #0066cc;
}

.questao-acoes {
  display: flex;
  gap: 6px;
}

.questao-acoes button {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 8px;
  background: transparent;
  cursor: pointer;
  font-size: 15px;
  color: inherit;
  transition: all 0.3s ease;
}

.questao-acoes button:hover:not(:disabled) {
  background: #f0f0f0;
}

.tema-escuro .questao-acoes button:hover:not(:disabled) {
  background: #3a3a3a;
}

.questao-acoes button:disabled {
  opacity: 0.35;
  cursor: default;
}

.questao-acoes .btn-remover:hover {
  background: #dc3545 !important;
}

.linha-campos {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 12px;
}

.campo {
  margin-bottom: 12px;
}

.campo > label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  margin-bottom: 6px;
  color: #666;
}

.tema-escuro .campo > label {
  color: #aaa;
}

.campo input,
.campo select {
  width: 100%;
  padding: 9px 10px;
  border: 1px solid #d8d8d8;
  border-radius: 6px;
  font: inherit;
}

.campo-linhas input {
  max-width: 160px;
}

.alternativa {
  display: flex;
  gap: 10px;
  align-items: flex-start;
  margin-bottom: 8px;
}

.alternativa-editor {
  flex: 1;
  min-width: 0;
}

.marcador {
  display: flex;
  align-items: center;
  gap: 4px;
  min-width: 48px;
  padding: 8px;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
  font-weight: 600;
  cursor: pointer;
}

.marcador input {
  width: auto;
}

.marcador.correta {
  background: #28a74520;
  border-color: #28a745;
  color: #28a745;
}

.tema-escuro .marcador {
  border-color: #404040;
}

.aviso-banco {
  display: block;
  font-size: 12px;
  color: #888;
}

@media (max-width: 768px) {
  .linha-campos {
    grid-template-columns: 1fr;
  }
}
</style>
