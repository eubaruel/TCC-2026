<template>
  <router-view />
  <ModalGlobal ref="$modal" />
</template>

<script>
import ModalGlobal from '@/components/ModalGlobal.vue'

export default {
  name: 'App',
  components: {
    ModalGlobal
  },
  mounted() {
    // Disponibiliza o modal globalmente
    window.$modal = this.$refs.$modal
    
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
/* Estilos adicionais */
</style>