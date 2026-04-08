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

      <button type="submit" class="botao_entrar">
        Entrar
      </button>
    </form>
  </div>
</template>

<script>
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

export default {
  name: 'LoginFormulario',
  setup() {
    const authStore = useAuthStore()
    const router = useRouter()
    return { authStore, router }
  },
  data() {
    return {
      registro_usuario: '',
      senha_usuario: '',
      erroRegistro: ''
    }
  },
  methods: {
    validarRegistro() {
      // Remove qualquer caractere que não seja número
      this.registro_usuario = this.registro_usuario.replace(/[^0-9]/g, '')
      
      // Verifica se tem mais de 10 caracteres
      if (this.registro_usuario.length > 10) {
        this.registro_usuario = this.registro_usuario.slice(0, 10)
      }
      
      // Verifica se está vazio
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
      
      // TODO: Substituir pela chamada real da API
      // Por enquanto, simula o login buscando o usuário no localStorage
      const usuariosSalvos = JSON.parse(localStorage.getItem('usuarios') || '[]')
      const usuarioEncontrado = usuariosSalvos.find(
        u => u.registro === this.registro_usuario && u.senha === this.senha_usuario
      )
      
      if (usuarioEncontrado) {
        const usuario = {
          id: parseInt(this.registro_usuario),
          nome: usuarioEncontrado.nome,
          registro: this.registro_usuario,
          tipo: usuarioEncontrado.tipo
        }
        
        this.authStore.user = usuario
        this.authStore.userType = usuario.tipo
        
        localStorage.setItem('usuarioLogado', JSON.stringify(usuario))
        localStorage.setItem('userType', usuario.tipo)
        
        this.router.push('/provas')
      } else {
        alert('Registro ou senha inválidos!')
      }
    }
  }
}
</script>

<style scoped>
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