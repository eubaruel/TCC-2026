<template>
  <div class="card_unico">
    <div class="logo-section">
      <img src="@/assets/univaplogo.png" alt="Logo Univap" class="logo" />
    </div>
    
    <form @submit.prevent="processarLogin" class="formulario_login">
      <div class="tipo-usuario">
        <label class="radio-label">
          <input type="radio" value="professor" v-model="tipoUsuario" />
          <span class="radio-custom"></span>
          Professor
        </label>
        <label class="radio-label">
          <input type="radio" value="processo_pedagogico" v-model="tipoUsuario" />
          <span class="radio-custom"></span>
          Processo Pedagógico
        </label>
      </div>

      <div class="campo_registro">
        <label for="registro_usuario">Registro</label>
        <input
          id="registro_usuario"
          v-model="registro_usuario"
          type="text"
          required
          autocomplete="username"
          placeholder="Digite seu registro"
        />
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
        Enviar
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
      tipoUsuario: 'professor',
      registro_usuario: '',
      senha_usuario: ''
    }
  },
  methods: {
    processarLogin() {
      // Simulação de login com base no tipo selecionado
      let usuario = null
      let tipo = null
      
      if (this.tipoUsuario === 'professor') {
        usuario = {
          id: 1,
          nome: this.registro_usuario || 'Professor',
          registro: this.registro_usuario,
          tipo: 'professor'
        }
        tipo = 'professor'
      } else if (this.tipoUsuario === 'processo_pedagogico') {
        usuario = {
          id: 2,
          nome: 'Processo Pedagógico',
          registro: this.registro_usuario,
          tipo: 'processo_pedagogico'
        }
        tipo = 'processo_pedagogico'
      }
      
      this.authStore.user = usuario
      this.authStore.userType = tipo
      
      localStorage.setItem('usuarioLogado', JSON.stringify(usuario))
      localStorage.setItem('userType', tipo)
      
      this.router.push('/provas')
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

.tipo-usuario {
  display: flex;
  gap: 30px;
  margin-bottom: 25px;
  justify-content: center;
}

.radio-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 14px;
  color: #333;
}

.radio-label input {
  width: auto;
  margin: 0;
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
  
  .tipo-usuario {
    gap: 20px;
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