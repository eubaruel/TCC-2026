import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    userType: null // 'professor' ou 'processo_pedagogico'
  }),
  
  actions: {
    login(email, senha) { // Mantém o parâmetro mas não usa ainda
      // TODO: Implementar validação de senha quando o backend estiver pronto
      // eslint-disable-next-line no-unused-vars
      const _senha = senha // Apenas para evitar o erro, pode ser removido depois
      
      // Simulação de login - substituir por chamada API
      let usuario = null
      let tipo = null
      
      if (email === 'professor@escola.com') {
        usuario = {
          id: 1,
          nome: email.split('@')[0],
          email: email,
          tipo: 'professor'
        }
        tipo = 'professor'
      } else if (email === 'processo@escola.com') {
        usuario = {
          id: 2,
          nome: 'Processo Pedagógico',
          email: email,
          tipo: 'processo_pedagogico'
        }
        tipo = 'processo_pedagogico'
      } else {
        // Fallback para teste
        usuario = {
          id: 1,
          nome: email.split('@')[0],
          email: email,
          tipo: 'professor'
        }
        tipo = 'professor'
      }
      
      this.user = usuario
      this.userType = tipo
      
      localStorage.setItem('usuarioLogado', JSON.stringify(usuario))
      localStorage.setItem('userType', tipo)
      
      return { success: true, user: usuario, userType: tipo }
    },
    
    logout() {
      this.user = null
      this.userType = null
      localStorage.removeItem('usuarioLogado')
      localStorage.removeItem('userType')
    },
    
    loadUser() {
      const usuarioSalvo = localStorage.getItem('usuarioLogado')
      const tipoSalvo = localStorage.getItem('userType')
      
      if (usuarioSalvo) {
        this.user = JSON.parse(usuarioSalvo)
        this.userType = tipoSalvo
      }
    }
  },
  
  getters: {
    isProfessor: (state) => state.userType === 'professor',
    isProcessoPedagogico: (state) => state.userType === 'processo_pedagogico',
    isLoggedIn: (state) => !!state.user
  }
})