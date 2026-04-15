<template>
  <div class="app-container">
    <BarraLateral />
    <div class="conteudo-principal" :class="temaAtual">
      <div class="header" v-if="mostrarHeader">
        <h1>Seja Bem Vindo(a) {{ nomeUsuario }}!</h1>
      </div>
      
      <div class="conteudo">
        <router-view />
      </div>
    </div>

    <!-- Modal Primeiro Acesso (trocar senha) - AGORA NA TELA PRINCIPAL -->
    <div v-if="mostrarModalTrocarSenha" class="modal-overlay" @click="fecharModalTrocarSenha">
      <div class="modal-container">
        <div class="modal-header">
          <h3>Primeiro Acesso</h3>
          <button @click="fecharModalTrocarSenha" class="modal-close">&times;</button>
        </div>
        <div class="modal-body">
          <p>Por segurança, você precisa alterar sua senha antes de continuar.</p>
          <div class="form-group-modal">
            <label>Nova Senha *</label>
            <input type="password" v-model="novaSenha" placeholder="Digite sua nova senha" />
            <small class="helper-text">Mínimo 6 caracteres, 1 maiúscula, 1 número e 1 caractere especial</small>
          </div>
          <div class="form-group-modal">
            <label>Confirmar Nova Senha *</label>
            <input type="password" v-model="confirmarSenha" placeholder="Confirme sua nova senha" />
          </div>
          <p v-if="erroSenha" class="mensagem-erro">{{ erroSenha }}</p>
        </div>
        <div class="modal-footer">
          <button @click="confirmarTrocaSenha" class="btn-modal-salvar">Alterar Senha</button>
          <button @click="fecharModalTrocarSenha" class="btn-modal-cancelar">Sair</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import BarraLateral from '@/components/BarraLateral.vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

export default {
  name: 'TelaPrincipal',
  components: {
    BarraLateral
  },
  setup() {
    const authStore = useAuthStore()
    const router = useRouter()
    return { authStore, router }
  },
  data() {
    return {
      temaAtual: 'tema-claro',
      mostrarHeader: true,
      mostrarModalTrocarSenha: false,
      novaSenha: '',
      confirmarSenha: '',
      erroSenha: ''
    }
  },
  computed: {
    nomeUsuario() {
      return this.authStore.user?.nome || 'Usuário'
    }
  },
  mounted() {
    this.carregarTema()
    this.verificarRota()
    this.verificarPrimeiroAcesso()
    
    window.addEventListener('tema-mudou', this.atualizarTema)
  },
  beforeUnmount() {
    window.removeEventListener('tema-mudou', this.atualizarTema)
  },
  watch: {
    '$route.path'() {
      this.verificarRota()
    }
  },
  methods: {
    carregarTema() {
      const temaSalvo = localStorage.getItem('tema')
      if (temaSalvo) {
        this.temaAtual = temaSalvo
      } else {
        this.temaAtual = 'tema-claro'
      }
    },
    
    atualizarTema(event) {
      this.temaAtual = event.detail.tema
    },
    
    verificarRota() {
      if (this.$route.path === '/configuracoes') {
        this.mostrarHeader = false
      } else {
        this.mostrarHeader = true
      }
    },
    
    verificarPrimeiroAcesso() {
      const precisaTrocar = localStorage.getItem('precisaTrocarSenha') === 'true'
      if (precisaTrocar) {
        this.mostrarModalTrocarSenha = true
      }
    },
    
    async confirmarTrocaSenha() {
      this.erroSenha = ''
      
      if (this.novaSenha !== this.confirmarSenha) {
        this.erroSenha = 'As senhas não coincidem'
        return
      }
      
      if (this.novaSenha.length < 6) {
        this.erroSenha = 'A senha deve ter pelo menos 6 caracteres'
        return
      }
      
      if (!/[A-Z]/.test(this.novaSenha)) {
        this.erroSenha = 'A senha deve conter pelo menos uma letra maiúscula'
        return
      }
      
      if (!/\d/.test(this.novaSenha)) {
        this.erroSenha = 'A senha deve conter pelo menos um número'
        return
      }
      
      if (!/[!@#$%^&*(),.?":{}|<>]/.test(this.novaSenha)) {
        this.erroSenha = 'A senha deve conter pelo menos um caractere especial'
        return
      }
      
      const sucesso = await this.authStore.trocarSenha(this.novaSenha)
      
      if (sucesso) {
        this.mostrarModalTrocarSenha = false
        this.novaSenha = ''
        this.confirmarSenha = ''
      } else {
        this.erroSenha = 'Erro ao alterar senha'
      }
    },
    
    fecharModalTrocarSenha() {
      this.mostrarModalTrocarSenha = false
      this.authStore.logout()
      this.router.push('/')
    }
  }
}
</script>

<style scoped>
.app-container {
  display: flex;
  min-height: 100vh;
}

.conteudo-principal {
  flex: 1;
  margin-left: 70px;
  transition: margin-left 0.3s ease, background-color 0.3s ease, color 0.3s ease;
  min-height: 100vh;
}

.conteudo-principal.tema-claro {
  background-color: #f5f5f5;
  color: #333;
}

.conteudo-principal.tema-escuro {
  background-color: #1a1a1a;
  color: #e5e5e5;
}

.header {
  padding: 30px 40px;
  border-bottom: 2px solid rgba(0, 0, 0, 0.1);
}

.tema-escuro .header {
  border-bottom-color: rgba(255, 255, 255, 0.1);
}

.header h1 {
  font-size: 28px;
  font-weight: 600;
  margin: 0;
}

.conteudo {
  padding: 30px 40px;
}

/* Modal styles */
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
  max-width: 450px;
  width: 90%;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e0e0e0;
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
  padding: 24px;
}

.form-group-modal {
  margin-bottom: 16px;
}

.form-group-modal label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  font-size: 14px;
}

.form-group-modal input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
}

.helper-text {
  display: block;
  margin-top: 5px;
  font-size: 11px;
  color: #888;
}

.mensagem-erro {
  color: #dc3545;
  font-size: 12px;
  margin-top: 8px;
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
  background: #28a745;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.btn-modal-cancelar {
  padding: 10px 20px;
  background: transparent;
  border: 1px solid #ddd;
  border-radius: 6px;
  cursor: pointer;
}

@media (min-width: 769px) {
  .sidebar:hover ~ .conteudo-principal {
    margin-left: 250px;
  }
}

@media (max-width: 768px) {
  .conteudo-principal {
    margin-left: 70px;
  }
  
  .header {
    padding: 20px;
  }
  
  .header h1 {
    font-size: 24px;
  }
  
  .conteudo {
    padding: 20px;
  }
}
</style>