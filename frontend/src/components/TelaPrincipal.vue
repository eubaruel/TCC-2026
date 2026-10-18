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

    <!-- Modal Primeiro Acesso (trocar senha) -->
    <div v-if="mostrarModalTrocarSenha" class="modal-overlay">
      <div class="modal-container">
        <div class="modal-header">
          <h3>Primeiro Acesso</h3>
        </div>
        <div class="modal-body">
          <p>Por segurança, você precisa alterar sua senha antes de continuar.</p>
          <div class="form-group-modal">
            <label>Nova Senha *</label>
            <input 
              type="password" 
              v-model="novaSenha" 
              placeholder="Digite sua nova senha" 
              @click.stop
            />
            <small class="helper-text">Mínimo 6 caracteres, 1 maiúscula, 1 número e 1 caractere especial</small>
          </div>
          <div class="form-group-modal">
            <label>Confirmar Nova Senha *</label>
            <input 
              type="password" 
              v-model="confirmarSenha" 
              placeholder="Confirme sua nova senha" 
              @click.stop
            />
          </div>
          <p v-if="erroSenha" class="mensagem-erro">{{ erroSenha }}</p>
        </div>
        <div class="modal-footer">
          <button @click="confirmarTrocaSenha" class="btn-modal-salvar">Alterar Senha</button>
          <button @click="fecharModalTrocarSenha" class="btn-modal-cancelar">Cancelar</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import BarraLateral from "@/components/BarraLateral.vue";
import { useAuthStore } from "@/stores/auth";

export default {
  name: "TelaPrincipal",
  components: { BarraLateral },
  setup() {
    return { authStore: useAuthStore() };
  },
  data: () => ({
    temaAtual: "tema-claro",
    mostrarHeader: true,
    mostrarModalTrocarSenha: false,
    novaSenha: "",
    confirmarSenha: "",
    erroSenha: "",
  }),
  computed: {
    nomeUsuario() {
      return this.authStore.user?.nome || "Usuário";
    },
  },
  watch: {
    "$route.path"() {
      this.mostrarHeader = this.$route.path !== "/configuracoes";
    },
  },
  mounted() {
    this.mostrarHeader = this.$route.path !== "/configuracoes";
  },
  methods: {
    confirmarTrocaSenha() {
      // A API não disponibiliza endpoint para alteração de senha.
    },
    fecharModalTrocarSenha() {
      this.mostrarModalTrocarSenha = false;
    },
  },
};
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
  z-index: 10000;
}

.modal-container {
  background: white;
  border-radius: 12px;
  max-width: 450px;
  width: 90%;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
}

.tema-escuro .modal-container {
  background: #2a2a2a;
  color: #e5e5e5;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
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

.tema-escuro .form-group-modal input {
  background: #1a1a1a;
  border-color: #404040;
  color: #e5e5e5;
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

.tema-escuro .modal-footer {
  border-top-color: #404040;
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
