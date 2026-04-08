import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    userType: null
  }),
  
  actions: {
    login(registro, senha) {
      // TODO: Substituir por chamada API real
      const usuariosSalvos = JSON.parse(localStorage.getItem('usuarios') || '[]')
      const usuario = usuariosSalvos.find(u => u.registro === registro && u.senha === senha)
      
      if (usuario) {
        this.user = {
          id: parseInt(registro),
          nome: usuario.nome,
          registro: registro,
          tipo: usuario.tipo
        }
        this.userType = usuario.tipo
        
        localStorage.setItem('usuarioLogado', JSON.stringify(this.user))
        localStorage.setItem('userType', this.userType)
        
        return { success: true, user: this.user, userType: this.userType }
      }
      
      return { success: false, message: 'Registro ou senha inválidos' }
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