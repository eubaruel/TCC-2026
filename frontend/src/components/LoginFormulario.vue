<template>
  <div class="card_unico">
    <div class="logo-section">
      <img src="@/assets/univaplogo.png" alt="Logo Univap" class="logo" />
    </div>
    
    <form @submit.prevent="processarLogin" class="formulario_login">
      <div class="campo_email">
        <label for="email_usuario">Email</label>
        <input
          id="email_usuario"
          v-model="email_usuario"
          type="email"
          required
          autocomplete="email"
          placeholder="Digite seu email"
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
        Entrar
      </button>
    </form>
  </div>
</template>

<script>
export default {
  name: 'LoginFormulario',
  data() {
    return {
      email_usuario: '',
      senha_usuario: ''
    }
  },
  methods: {
    processarLogin() {
      const credenciais = {
        email: this.email_usuario,
        senha: this.senha_usuario
      }
      
      console.log('Credenciais:', credenciais)
      
      // Simulação de login
      const usuarioSimulado = {
        nome: this.email_usuario.split('@')[0],
        email: this.email_usuario,
        tipo: 'professor'
      }
      
      localStorage.setItem('usuarioLogado', JSON.stringify(usuarioSimulado))
      localStorage.setItem('token', 'simulated-token-123')
      
      this.$emit('login-enviado', credenciais)
      
      // Redireciona para a tela principal
      this.$router.push('/acessar-provas')
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

.campo_email,
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
  
  input {
    padding: 12px;
    font-size: 15px;
  }
  
  .botao_entrar {
    padding: 14px;
    font-size: 16px;
  }
}

@media (max-width: 360px) {
  .logo-section {
    padding: 25px 20px 10px 20px;
  }
  
  .logo {
    max-width: 120px;
  }
  
  .formulario_login {
    padding: 10px 20px 20px 20px;
  }
}
</style>