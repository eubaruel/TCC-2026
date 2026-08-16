import { defineStore } from 'pinia'
import { useUsersStore } from './users'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    userType: null,
    precisaTrocarSenha: false
  }),
  
  actions: {
    async login(registro, senha) {
      const usersStore = useUsersStore()
      await usersStore.fetchUsers()
      
      const usuario = usersStore.users.find(u => 
        u.registro === registro && 
        u.ativo === true
      )
      
      console.log('Usuário encontrado:', usuario) // Debug
      
      if (!usuario) {
        return { success: false, message: 'Registro não encontrado' }
      }
      
      if (usuario.senha !== senha) {
        return { success: false, message: 'Senha inválida' }
      }
      
      this.user = usuario
      this.userType = usuario.role === 'Professor' ? 'professor' : 'processo_pedagogico'
      this.precisaTrocarSenha = usuario.primeiroAcesso || false
      
      localStorage.setItem('usuarioLogado', JSON.stringify(usuario))
      localStorage.setItem('userType', this.userType)
      localStorage.setItem('precisaTrocarSenha', this.precisaTrocarSenha)
      
      return { 
        success: true, 
        user: usuario, 
        userType: this.userType,
        precisaTrocarSenha: this.precisaTrocarSenha
      }
    },
    
    logout() {
      console.log('Executando logout na store') // Debug
      this.user = null
      this.userType = null
      this.precisaTrocarSenha = false
      localStorage.removeItem('usuarioLogado')
      localStorage.removeItem('userType')
      localStorage.removeItem('precisaTrocarSenha')
      console.log('Dados do localStorage removidos') // Debug
    },
    
    loadUser() {
      const usuarioSalvo = localStorage.getItem('usuarioLogado')
      const tipoSalvo = localStorage.getItem('userType')
      const precisaTrocar = localStorage.getItem('precisaTrocarSenha') === 'true'
      
      if (usuarioSalvo) {
        this.user = JSON.parse(usuarioSalvo)
        this.userType = tipoSalvo
        this.precisaTrocarSenha = precisaTrocar
        console.log('Usuário carregado:', this.user) // Debug
      }
    },
    
    async trocarSenha(novaSenha) {
      if (!this.user) return false
      
      const usersStore = useUsersStore()
      usersStore.resetarSenha(this.user.id, novaSenha)
      
      this.precisaTrocarSenha = false
      this.user.primeiroAcesso = false
      localStorage.setItem('precisaTrocarSenha', 'false')
      localStorage.setItem('usuarioLogado', JSON.stringify(this.user))
      
      return true
    }
  },
  
  getters: {
    isProfessor: (state) => state.userType === 'professor',
    isProcessoPedagogico: (state) => state.userType === 'processo_pedagogico',
    isLoggedIn: (state) => !!state.user
  }
})