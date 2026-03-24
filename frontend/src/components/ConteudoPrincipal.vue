<template>
  <div class="conteudo-principal" :class="temaAtual">
    <div class="header">
      <h1>Seja Bem Vindo(a) {{ nomeProfessor }}!</h1>
    </div>
    
    <div class="conteudo">
      <router-view />
    </div>
  </div>
</template>

<script>
export default {
  name: 'ConteudoPrincipal',
  data() {
    return {
      nomeProfessor: 'Professor',
      temaAtual: 'tema-claro'
    }
  },
  mounted() {
    this.carregarDadosUsuario()
    this.carregarTema()
    
    window.addEventListener('tema-mudou', this.atualizarTema)
  },
  beforeUnmount() {
    window.removeEventListener('tema-mudou', this.atualizarTema)
  },
  methods: {
    carregarDadosUsuario() {
      const usuarioSalvo = localStorage.getItem('usuarioLogado')
      if (usuarioSalvo) {
        try {
          const usuario = JSON.parse(usuarioSalvo)
          this.nomeProfessor = usuario.nome || usuario.email?.split('@')[0] || 'Professor'
        } catch (error) {
          console.error('Erro ao carregar dados do usuário:', error)
        }
      }
    },
    
    carregarTema() {
      const temaSalvo = localStorage.getItem('tema')
      if (temaSalvo) {
        this.temaAtual = temaSalvo
      }
    },
    
    atualizarTema(event) {
      this.temaAtual = event.detail.tema
    }
  }
}
</script>

<style scoped>
.conteudo-principal {
  min-height: 100vh;
  transition: background-color 0.3s ease, color 0.3s ease;
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
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
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

@media (max-width: 768px) {
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