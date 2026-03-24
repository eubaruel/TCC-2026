<template>
  <router-view />
</template>

<script>
export default {
  name: 'App',
  mounted() {
    this.aplicarTemaSalvo()
    this.verificarRotaLogin()
    
    window.addEventListener('tema-mudou', this.handleTemaMudou)
    this.$watch('$route', () => {
      this.verificarRotaLogin()
    })
  },
  beforeUnmount() {
    window.removeEventListener('tema-mudou', this.handleTemaMudou)
  },
  methods: {
    aplicarTemaSalvo() {
      const temaSalvo = localStorage.getItem('tema')
      if (temaSalvo === 'tema-escuro') {
        document.body.classList.add('tema-escuro')
        document.body.classList.remove('tema-claro')
      } else {
        document.body.classList.add('tema-claro')
        document.body.classList.remove('tema-escuro')
      }
    },
    
    handleTemaMudou(event) {
      const novoTema = event.detail.tema
      if (novoTema === 'tema-escuro') {
        document.body.classList.add('tema-escuro')
        document.body.classList.remove('tema-claro')
      } else {
        document.body.classList.add('tema-claro')
        document.body.classList.remove('tema-escuro')
      }
    },
    
    verificarRotaLogin() {
      if (this.$route.path === '/' || this.$route.path === '/login') {
        document.body.classList.add('pagina-login')
      } else {
        document.body.classList.remove('pagina-login')
      }
    }
  }
}
</script>

<style>
/* Estilos adicionais específicos do App se necessário */
</style>