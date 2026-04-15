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

      <button type="submit" class="botao_entrar">
        Entrar
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
          <p>Digite seu email para receber instruções de recuperação de senha.</p>
          <div class="form-group-modal">
            <label>Email</label>
            <input type="email" v-model="recuperarEmail" placeholder="Digite seu email cadastrado" />
          </div>
        </div>
        <div class="modal-footer">
          <button @click="enviarRecuperacao" class="btn-modal-enviar">Enviar</button>
          <button @click="fecharModal" class="btn-modal-cancelar">Cancelar</button>
        </div>
      </div>
    </div>

    <!-- REMOVIDO: Modal Primeiro Acesso - AGORA VAI FICAR NA TELA PRINCIPAL -->
  </div>
</template>

<script>
import { useAuthStore } from '@/stores/auth'
import { useUsersStore } from '@/stores/users'
import { useRouter } from 'vue-router'

export default {
  name: 'LoginFormulario',
  setup() {
    const authStore = useAuthStore()
    const usersStore = useUsersStore()
    const router = useRouter()
    return { authStore, usersStore, router }
  },
  data() {
    return {
      registro_usuario: '',
      senha_usuario: '',
      erroRegistro: '',
      modalEsqueciSenha: false,
      recuperarEmail: ''
    }
  },
  mounted() {
    this.usersStore.fetchUsers()
  },
  methods: {
    validarRegistro() {
      this.registro_usuario = this.registro_usuario.replace(/[^0-9]/g, '')
      
      if (this.registro_usuario.length > 10) {
        this.registro_usuario = this.registro_usuario.slice(0, 10)
      }
      
      if (this.registro_usuario.length === 0) {
        this.erroRegistro = ''
      } else if (this.registro_usuario.length > 10) {
        this.erroRegistro = 'O registro não pode ter mais de 10 dígitos'
      } else {
        this.erroRegistro = ''
      }
    },
    
    validarCampos() {
      if (!this.registro_usuario) {
        this.erroRegistro = 'Campo registro é obrigatório'
        return false
      }
      
      if (this.registro_usuario.length < 1) {
        this.erroRegistro = 'O registro deve ter pelo menos 1 dígito'
        return false
      }
      
      if (this.registro_usuario.length > 10) {
        this.erroRegistro = 'O registro não pode ter mais de 10 dígitos'
        return false
      }
      
      if (!/^\d+$/.test(this.registro_usuario)) {
        this.erroRegistro = 'O registro deve conter apenas números'
        return false
      }
      
      return true
    },
    
    async processarLogin() {
      this.erroRegistro = ''
      
      if (!this.validarCampos()) {
        return
      }
      
      const registroNum = parseInt(this.registro_usuario)
      const resultado = await this.authStore.login(registroNum, this.senha_usuario)
      
      if (!resultado.success) {
        alert(resultado.message)
        return
      }
      
      // Redireciona para a tela principal, que exibirá o modal se necessário
      this.router.push('/provas')
    },
    
    abrirModalEsqueciSenha() {
      this.modalEsqueciSenha = true
      this.recuperarEmail = ''
    },
    
    fecharModal() {
      this.modalEsqueciSenha = false
    },
    
    enviarRecuperacao() {
      if (!this.recuperarEmail) {
        alert('Digite seu email')
        return
      }
      
      const usuario = this.usersStore.users.find(u => 
        u.email === this.recuperarEmail && u.ativo === true
      )
      
      if (!usuario) {
        alert('Email não encontrado')
        return
      }
      
      let senhaTemporaria = '123456'
      if (usuario.dataNascimento) {
        senhaTemporaria = usuario.dataNascimento.replace(/-/g, '')
      }
      
      this.usersStore.resetarSenha(usuario.id, senhaTemporaria)
      
      alert(`Sua senha foi redefinida. Use sua data de nascimento como senha.`)
      this.fecharModal()
    }
  }
}
</script>

<style scoped>
/* Estilos mantidos iguais */
.card_unico {
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  width: 100%;
  max-width: 400px;
  border: 2px solid #000000;
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
  background-color: #000000;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 18px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.3s ease;
  margin-top: 10px;
}

.botao_entrar:hover {
  background-color: #00488b;
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

.modal-footer {
  display: flex;
  gap: 12px;
  padding: 20px 24px;
  border-top: 1px solid #e0e0e0;
  justify-content: flex-end;
}

.btn-modal-enviar {
  padding: 10px 20px;
  background: #00488b;
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