<template>
  <div v-if="visivel" class="modal-overlay">
    <div class="modal-container" :class="{ 'pequeno': tipo === 'pequeno' }">
      <div class="modal-header" v-if="titulo">
        <h3>{{ titulo }}</h3>
        <button v-if="fecharBtn" @click="fechar" class="modal-close">&times;</button>
      </div>
      <div class="modal-body">
        <p>{{ mensagem }}</p>
      </div>
      <div class="modal-footer" v-if="tipo === 'confirmacao'">
        <button @click="confirmar" class="btn-modal-confirmar">Confirmar</button>
        <button @click="cancelar" class="btn-modal-cancelar">Cancelar</button>
      </div>
      <div class="modal-footer" v-else-if="tipo === 'alerta'">
        <button @click="fechar" class="btn-modal-confirmar">OK</button>
      </div>
      <div class="modal-footer" v-else-if="tipo === 'pequeno'">
        <button @click="fechar" class="btn-modal-confirmar">OK</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ModalGlobal',
  data() {
    return {
      visivel: false,
      titulo: '',
      mensagem: '',
      tipo: 'alerta',
      fecharBtn: true,
      onConfirm: null,
      onCancel: null
    }
  },
  methods: {
    abrir(opcoes) {
      this.titulo = opcoes.titulo || ''
      this.mensagem = opcoes.mensagem || ''
      this.tipo = opcoes.tipo || 'alerta'
      this.fecharBtn = opcoes.fecharBtn !== false
      this.onConfirm = opcoes.onConfirm || null
      this.onCancel = opcoes.onCancel || null
      this.visivel = true
    },
    fechar() {
      this.visivel = false
      this.onConfirm = null
      this.onCancel = null
    },
    confirmar() {
      if (this.onConfirm) {
        this.onConfirm()
      }
      this.fechar()
    },
    cancelar() {
      if (this.onCancel) {
        this.onCancel()
      }
      this.fechar()
    }
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
}

.modal-container {
  background: white;
  border-radius: 12px;
  min-width: 300px;
  max-width: 400px;
  width: 90%;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
  animation: fadeIn 0.2s ease;
}

.modal-container.pequeno {
  max-width: 250px;
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
  margin: 0;
}

.modal-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #999;
}

.modal-body {
  padding: 20px;
  font-size: 14px;
  line-height: 1.5;
}

.modal-footer {
  display: flex;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid #e0e0e0;
  justify-content: flex-end;
}

.tema-escuro .modal-footer {
  border-top-color: #404040;
}

.btn-modal-confirmar {
  padding: 8px 20px;
  background: #00488b;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-modal-confirmar:hover {
  background: #0066cc;
}

.btn-modal-cancelar {
  padding: 8px 20px;
  background: transparent;
  border: 1px solid #ddd;
  border-radius: 6px;
  cursor: pointer;
}

.tema-escuro .btn-modal-cancelar {
  border-color: #404040;
  color: #e5e5e5;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}
</style>