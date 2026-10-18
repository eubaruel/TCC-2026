<template>
  <div v-if="visivel" class="modal-overlay" @click.self="$emit('cancelar')">
    <div class="modal-container">
      <div class="modal-header">
        <h3>Sair da edição</h3>
        <button class="modal-close" :disabled="salvando" @click="$emit('cancelar')">&times;</button>
      </div>
      <div class="modal-body">
        <p>Deseja salvar o progresso de edição da prova antes de sair?</p>
        <p v-if="!provaSalva" class="aviso">Esta prova ainda não foi salva: se sair sem salvar, ela será descartada.</p>
      </div>
      <div class="modal-footer">
        <button class="btn-modal-cancelar" :disabled="salvando" @click="$emit('cancelar')">Cancelar</button>
        <button class="btn-modal-descartar" :disabled="salvando" @click="$emit('sair-sem-salvar')">Sair sem salvar</button>
        <button class="btn-modal-confirmar" :disabled="salvando" @click="$emit('salvar-e-sair')">
          {{ salvando ? "Salvando..." : "Salvar e sair" }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "ModalSairEdicao",
  props: {
    visivel: { type: Boolean, default: false },
    salvando: { type: Boolean, default: false },
    provaSalva: { type: Boolean, default: false },
  },
  emits: ["cancelar", "sair-sem-salvar", "salvar-e-sair"],
};
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 3000;
  padding: 20px;
}

.modal-container {
  background: white;
  border-radius: 12px;
  width: 100%;
  max-width: 460px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  animation: fadeIn 0.2s ease;
}

.tema-escuro .modal-container {
  background: #2a2a2a;
  color: #e5e5e5;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e0e0e0;
}

.tema-escuro .modal-header {
  border-bottom-color: #404040;
}

.modal-header h3 {
  font-size: 18px;
  font-weight: 600;
}

.modal-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #888;
}

.modal-body {
  padding: 20px;
  font-size: 14px;
}

.aviso {
  margin-top: 10px;
  font-size: 13px;
  color: #b42318;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 0 20px 20px;
  flex-wrap: wrap;
}

.modal-footer button {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
}

.modal-footer button:disabled {
  opacity: 0.65;
  cursor: wait;
}

.btn-modal-confirmar {
  background: #00488b;
  color: white;
}

.btn-modal-confirmar:hover:not(:disabled) {
  background: #0066cc;
}

.btn-modal-descartar {
  background: #dc3545;
  color: white;
}

.btn-modal-descartar:hover:not(:disabled) {
  background: #c82333;
}

.btn-modal-cancelar {
  background: #e0e0e0;
  color: #333;
}

.tema-escuro .btn-modal-cancelar {
  background: #404040;
  color: #e5e5e5;
}
</style>
