<template>
  <div class="card_unico">
    <div class="logo-section">
      <img src="@/assets/univaplogo.png" alt="Logo Univap" class="logo" />
    </div>
    
    <form @submit.prevent="processarLogin" class="formulario_login">
      <div class="campo_registro">
        <label for="registro_usuario">Registro</label>
        <input
          id="registro_usuario"
          v-model="registro_usuario"
          type="text"
          required
          autocomplete="username"
          placeholder="Digite seu registro"
          maxlength="10"
          @input="validarRegistro"
        />
        <small v-if="erroRegistro" class="mensagem-erro">{{ erroRegistro }}</small>
      </div>

      <div class="campo_senha">
        <label for="senha_usuario">Senha</label>
        <input
          id="senha_usuario"
          v-model="senha_usuario"
          type="password"
          required
          autocomplete="current-password"
          placeholder="Digite sua senha"
        />
      </div>

      <div class="links-container">
        <a href="#" @click.prevent="abrirModalEsqueciSenha" class="link-esqueci-senha">
          Esqueci minha senha
        </a>
      </div>

      <button
        type="submit"
        class="botao_entrar"
        :disabled="authStore.loading"
        :aria-busy="authStore.loading"
        :aria-label="authStore.loading ? 'Entrando' : 'Entrar'"
      >
        <span v-if="authStore.loading" class="indicador-carregamento" aria-hidden="true"></span>
        <span v-else>Entrar</span>
      </button>
    </form>

    <!-- Modal Esqueci minha senha (mantém na tela de login) -->
    <div v-if="modalEsqueciSenha" class="modal-overlay" @click="fecharModal">
      <div class="modal-container">
        <div class="modal-header">
          <h3>Recuperar Senha</h3>
          <button @click="fecharModal" class="modal-close">&times;</button>
        </div>
        <div class="modal-body">
          <p>Para recuperar sua senha, procure o processo pedagógico e solicite a recuperação do seu acesso.</p>
        </div>
        <div class="modal-footer">
          <button @click="fecharModal" class="btn-modal-fechar">Entendi</button>
        </div>
      </div>
    </div>

    <!-- REMOVIDO: Modal Primeiro Acesso - AGORA VAI FICAR NA TELA PRINCIPAL -->
  </div>
</template>

<script>
import { useAuthStore } from "@/stores/auth";
import { useRouter } from "vue-router";

export default {
  name: "LoginFormulario",
  setup() { return { authStore: useAuthStore(), router: useRouter() }; },
  data: () => ({
    registro_usuario: "",
    senha_usuario: "",
    erroRegistro: "",
    modalEsqueciSenha: false,
  }),
  methods: {
    validarRegistro() {
      this.registro_usuario = this.registro_usuario.replace(/\D/g, "").slice(0, 10);
      this.erroRegistro = "";
    },
    async processarLogin() {
      if (this.authStore.loading) return;
      this.erroRegistro = "";
      if (!this.registro_usuario) {
        this.erroRegistro = "Informe o registro.";
        return;
      }
      const resultado = await this.authStore.login(Number(this.registro_usuario), this.senha_usuario);
      if (!resultado.success) {
        this.erroRegistro = resultado.message;
        return;
      }
      this.router.push("/provas");
    },
    abrirModalEsqueciSenha() {
      this.modalEsqueciSenha = true;
    },
    fecharModal() {
      this.modalEsqueciSenha = false;
    },
  },
};
</script>

<style scoped>
/* Estilos mantidos iguais */
.card_unico {
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  width: 100%;
  max-width: 400px;
  overflow: hidden;
}

.logo-section {
  padding: 40px 40px 20px 40px;
  display: flex;
  justify-content: center;
  align-items: center;
  border-bottom: 1px solid #e0e0e0;
}

.logo {
  max-width: 180px;
  height: auto;
  display: block;
}

.formulario_login {
  padding: 20px 40px 40px 40px;
}

.campo_registro,
.campo_senha {
  margin-bottom: 25px;
}

label {
  display: block;
  color: #000000;
  font-weight: 600;
  margin-bottom: 8px;
  font-size: 16px;
}

input {
  width: 100%;
  padding: 14px;
  border: 2px solid #000000;
  border-radius: 8px;
  font-size: 16px;
  box-sizing: border-box;
  transition: all 0.3s ease;
}

input:focus {
  outline: none;
  border-color: #00488b;
  box-shadow: 0 0 0 3px rgba(0, 72, 139, 0.1);
}

input::placeholder {
  color: #999;
  font-size: 14px;
}

.mensagem-erro {
  display: block;
  margin-top: 5px;
  font-size: 12px;
  color: #dc3545;
}

.links-container {
  text-align: center;
  margin-bottom: 20px;
}

.link-esqueci-senha {
  font-size: 14px;
  color: #00488b;
  text-decoration: none;
}

.link-esqueci-senha:hover {
  text-decoration: underline;
}

.botao_entrar {
  width: 100%;
  padding: 16px;
  background-color: #00488b;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 18px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.3s ease;
  margin-top: 10px;
}

.botao_entrar:hover:not(:disabled) {
  background-color: #002d58;
}

.botao_entrar:disabled {
  cursor: wait;
  opacity: 0.8;
}

.indicador-carregamento {
  display: inline-block;
  width: 1em;
  height: 1em;
  box-sizing: border-box;
  vertical-align: middle;
  border: 2px solid currentColor;
  border-right-color: transparent;
  border-radius: 50%;
  animation: girar-carregamento 0.8s linear infinite;
}

@keyframes girar-carregamento {
  to { transform: rotate(360deg); }
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

.modal-footer {
  display: flex;
  gap: 12px;
  padding: 20px 24px;
  border-top: 1px solid #e0e0e0;
  justify-content: flex-end;
}

.btn-modal-fechar {
  padding: 10px 20px;
  background: #00488b;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

@media (max-width: 480px) {
  .logo-section {
    padding: 30px 30px 15px 30px;
  }
  
  .logo {
    max-width: 140px;
  }
  
  .formulario_login {
    padding: 15px 30px 30px 30px;
  }
  
  input {
    padding: 12px;
    font-size: 15px;
  }
  
  .botao_entrar {
    padding: 14px;
    font-size: 16px;
  }
}
</style>
