<template>
  <div class="questao-editor">
    <div class="questao-cabecalho">
      <h4 class="texto-questao">Questão {{ numero }}</h4>
      <div v-if="!bloqueada" class="questao-acoes">
        <button type="button" title="Mover para cima" :disabled="primeira" @click="$emit('mover', -1)">↑</button>
        <button type="button" title="Mover para baixo" :disabled="ultima" @click="$emit('mover', 1)">↓</button>
        <button type="button" class="btn-remover" title="Remover questão" @click="$emit('remover')">🗑️</button>
      </div>
    </div>
    <div class="linha-campos">
      <div class="campo"><label>Assunto</label><p>{{ questao.assunto }}</p></div>
      <div class="campo"><label>Dificuldade</label><p>{{ questao.dificuldade }}</p></div>
    </div>
    <div class="campo">
      <label>Enunciado</label>
      <!-- eslint-disable-next-line vue/no-v-html -->
      <div class="texto-questao" v-html="sanitizar(questao.enunciado)"></div>
    </div>
    <div class="campo">
      <label>Alternativas — correta destacada</label>
      <div v-for="(alternativa, index) in questao.alternativas" :key="index" class="alternativa">
        <span class="marcador texto-questao" :class="{ correta: questao.indiceCorreta === index }">{{ letras[index] }}</span>
        <!-- eslint-disable-next-line vue/no-v-html -->
        <div class="alternativa-editor texto-questao" v-html="sanitizar(alternativa)"></div>
      </div>
    </div>
    <small class="aviso-banco">Conteúdo do banco de questões: somente seleção e ordenação nesta tela.</small>
  </div>
</template>

<script>
import { LETRAS } from "@/stores/provaDraft";
import { sanitizar } from "@/utils/html";

export default {
  name: "QuestaoEditor",
  props: {
    questao: { type: Object, required: true },
    numero: { type: Number, required: true },
    primeira: { type: Boolean, default: false },
    ultima: { type: Boolean, default: false },
    bloqueada: { type: Boolean, default: false },
  },
  emits: ["mover", "remover"],
  data: () => ({ letras: LETRAS }),
  methods: { sanitizar },
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
}

.campo :deep(img) { max-width: 100%; height: auto; }

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
