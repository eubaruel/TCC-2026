<template>
  <div class="configuracoes-container">
    <div class="config-header">
      <h2 class="titulo-pagina">Configurações</h2>
      <div class="header-line"></div>
    </div>
    
    <div class="configuracoes-grid">
      <!-- Card de Tema -->
      <div class="card-configuracao">
        <div class="card-header">
          <div class="card-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="12" cy="12" r="5" stroke="currentColor" stroke-width="2"/>
              <path d="M12 3V1M12 23V21M21 12H23M1 12H3M18.36 5.64L19.78 4.22M4.22 19.78L5.64 18.36M18.36 18.36L19.78 19.78M4.22 4.22L5.64 5.64" stroke="currentColor" stroke-width="2"/>
            </svg>
          </div>
          <h3>Aparência</h3>
        </div>
        <div class="card-conteudo">
          <div class="opcoes-tema">
            <button 
              @click="selecionarTema('tema-claro')" 
              class="botao-tema"
              :class="{ ativo: temaSelecionado === 'tema-claro' }"
            >
              <div class="tema-preview claro"></div>
              <span>Claro</span>
            </button>
            <button 
              @click="selecionarTema('tema-escuro')" 
              class="botao-tema"
              :class="{ ativo: temaSelecionado === 'tema-escuro' }"
            >
              <div class="tema-preview escuro"></div>
              <span>Escuro</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Card de Notificações -->
      <div class="card-configuracao">
        <div class="card-header">
          <div class="card-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 22C13.1 22 14 21.1 14 20H10C10 21.1 10.9 22 12 22ZM18 16V11C18 7.93 16.36 5.36 13.5 4.68V4C13.5 3.17 12.83 2.5 12 2.5C11.17 2.5 10.5 3.17 10.5 4V4.68C7.63 5.36 6 7.92 6 11V16L4 18V19H20V18L18 16Z" fill="currentColor"/>
            </svg>
          </div>
          <h3>Notificações</h3>
        </div>
        <div class="card-conteudo">
          <div class="opcao-config">
            <label class="switch">
              <input type="checkbox" v-model="notificacoesEmailSelecionado">
              <span class="slider round"></span>
            </label>
            <span>Receber notificações por email</span>
          </div>
          <div class="opcao-config">
            <label class="switch">
              <input type="checkbox" v-model="notificacoesSistemaSelecionado">
              <span class="slider round"></span>
            </label>
            <span>Notificações do sistema</span>
          </div>
        </div>
      </div>
    </div>

    <div class="acoes-container">
      <button @click="salvarConfiguracoes" class="btn-salvar">
        Salvar Configurações
      </button>
      <button @click="cancelarAlteracoes" class="btn-cancelar">
        Cancelar
      </button>
    </div>

    <div v-if="mostrarModal" class="modal-overlay">
      <div class="modal-container">
        <div class="modal-header">
          <h3>Configurações não salvas</h3>
        </div>
        <div class="modal-body">
          <p>Há configurações que não foram salvas. O que você deseja fazer?</p>
        </div>
        <div class="modal-footer">
          <button @click="salvarESair" class="btn-modal-salvar">Salvar</button>
          <button @click="descartarESair" class="btn-modal-descartar">Não Salvar</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ConfiGuracoes',
  data() {
    return {
      temaAtual: 'tema-claro',
      notificacoesEmail: true,
      notificacoesSistema: true,
      temaSelecionado: 'tema-claro',
      notificacoesEmailSelecionado: true,
      notificacoesSistemaSelecionado: true,
      mostrarModal: false,
      temAlteracoes: false,
      navegacaoPendente: null
    }
  },
  mounted() {
    this.carregarConfiguracoes()
    window.addEventListener('beforeunload', this.handleBeforeUnload)
  },
  beforeUnmount() {
    window.removeEventListener('beforeunload', this.handleBeforeUnload)
  },
  watch: {
    temaSelecionado() { this.verificarAlteracoes() },
    notificacoesEmailSelecionado() { this.verificarAlteracoes() },
    notificacoesSistemaSelecionado() { this.verificarAlteracoes() }
  },
  methods: {
    carregarConfiguracoes() {
      const temaSalvo = localStorage.getItem('tema')
      if (temaSalvo) {
        this.temaAtual = temaSalvo
        this.temaSelecionado = temaSalvo
      }
      
      const notificacoesEmailSalvas = localStorage.getItem('notificacoesEmail')
      if (notificacoesEmailSalvas !== null) {
        this.notificacoesEmail = JSON.parse(notificacoesEmailSalvas)
        this.notificacoesEmailSelecionado = JSON.parse(notificacoesEmailSalvas)
      }
      
      const notificacoesSistemaSalvas = localStorage.getItem('notificacoesSistema')
      if (notificacoesSistemaSalvas !== null) {
        this.notificacoesSistema = JSON.parse(notificacoesSistemaSalvas)
        this.notificacoesSistemaSelecionado = JSON.parse(notificacoesSistemaSalvas)
      }
    },
    
    verificarAlteracoes() {
      this.temAlteracoes = 
        this.temaSelecionado !== this.temaAtual ||
        this.notificacoesEmailSelecionado !== this.notificacoesEmail ||
        this.notificacoesSistemaSelecionado !== this.notificacoesSistema
      
      this.$emit('configuracao-alterada', this.temAlteracoes)
    },
    
    selecionarTema(tema) {
      this.temaSelecionado = tema
    },
    
    salvarConfiguracoes() {
      this.temaAtual = this.temaSelecionado
      this.notificacoesEmail = this.notificacoesEmailSelecionado
      this.notificacoesSistema = this.notificacoesSistemaSelecionado
      
      localStorage.setItem('tema', this.temaAtual)
      localStorage.setItem('notificacoesEmail', JSON.stringify(this.notificacoesEmail))
      localStorage.setItem('notificacoesSistema', JSON.stringify(this.notificacoesSistema))
      
      window.dispatchEvent(new CustomEvent('tema-mudou', { detail: { tema: this.temaAtual } }))
      
      this.temAlteracoes = false
      this.$emit('configuracao-alterada', false)
      alert('Configurações salvas com sucesso!')
    },
    
    cancelarAlteracoes() {
      this.temaSelecionado = this.temaAtual
      this.notificacoesEmailSelecionado = this.notificacoesEmail
      this.notificacoesSistemaSelecionado = this.notificacoesSistema
      this.temAlteracoes = false
      this.$emit('configuracao-alterada', false)
    },
    
    handleBeforeUnload(event) {
      if (this.temAlteracoes) {
        event.preventDefault()
        event.returnValue = 'Há configurações que não foram salvas.'
      }
    },
    
    salvarESair() {
      this.salvarConfiguracoes()
      this.mostrarModal = false
      if (this.navegacaoPendente) {
        this.navegacaoPendente.next()
        this.navegacaoPendente = null
      }
    },
    
    descartarESair() {
      this.mostrarModal = false
      if (this.navegacaoPendente) {
        this.navegacaoPendente.next()
        this.navegacaoPendente = null
      }
    }
  },
  beforeRouteLeave(to, from, next) {
    if (this.temAlteracoes) {
      this.mostrarModal = true
      this.navegacaoPendente = { to, next }
    } else {
      next()
    }
  }
}
</script>

<style scoped>
.configuracoes-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.config-header {
  margin-bottom: 30px;
}

.titulo-pagina {
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

.configuracoes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 24px;
  margin-bottom: 40px;
}

.card-configuracao {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid #e0e0e0;
}

.tema-escuro .card-configuracao {
  background: #2a2a2a;
  border-color: #404040;
  color: #e5e5e5;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px 24px;
  border-bottom: 1px solid #e0e0e0;
}

.tema-escuro .card-header {
  border-bottom-color: #404040;
}

.card-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: inherit;
}

.card-header h3 {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
}

.card-conteudo {
  padding: 24px;
}

.opcoes-tema {
  display: flex;
  gap: 20px;
}

.botao-tema {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: transparent;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  color: inherit;
}

.tema-escuro .botao-tema {
  border-color: #404040;
}

.botao-tema.ativo {
  border-color: #00488b;
  background: rgba(0, 72, 139, 0.1);
}

.tema-preview {
  width: 80px;
  height: 80px;
  border-radius: 8px;
}

.tema-preview.claro {
  background: linear-gradient(135deg, #f5f5f5 0%, #ffffff 100%);
  border: 1px solid #ddd;
}

.tema-preview.escuro {
  background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
  border: 1px solid #404040;
}

.opcao-config {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
}

.switch {
  position: relative;
  display: inline-block;
  width: 50px;
  height: 24px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  transition: 0.4s;
}

.slider:before {
  position: absolute;
  content: "";
  height: 16px;
  width: 16px;
  left: 4px;
  bottom: 4px;
  background-color: white;
  transition: 0.4s;
}

input:checked + .slider {
  background-color: #00488b;
}

input:checked + .slider:before {
  transform: translateX(26px);
}

.slider.round {
  border-radius: 34px;
}

.slider.round:before {
  border-radius: 50%;
}

.acoes-container {
  display: flex;
  gap: 16px;
  justify-content: flex-end;
  padding: 20px 0;
  border-top: 1px solid #e0e0e0;
}

.btn-salvar {
  padding: 12px 24px;
  background: #00488b;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
}

.btn-cancelar {
  padding: 12px 24px;
  background: transparent;
  color: inherit;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
}

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
  z-index: 2000;
}

.modal-container {
  background: white;
  border-radius: 12px;
  max-width: 400px;
  width: 90%;
}

.tema-escuro .modal-container {
  background: #2a2a2a;
}

.modal-header {
  padding: 20px 24px;
  border-bottom: 1px solid #e0e0e0;
}

.modal-body {
  padding: 24px;
}

.modal-footer {
  display: flex;
  gap: 12px;
  padding: 20px 24px;
  border-top: 1px solid #e0e0e0;
  justify-content: flex-end;
}

.btn-modal-salvar {
  padding: 10px 20px;
  background: #00488b;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.btn-modal-descartar {
  padding: 10px 20px;
  background: transparent;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  cursor: pointer;
}
</style>