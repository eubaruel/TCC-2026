import { defineStore } from 'pinia'

export const useUsersStore = defineStore('users', {
  state: () => ({
    users: [],
    loading: false,
    error: null
  }),

  getters: {
    activeUsers: (state) => {
      return state.users.filter(u => u.ativo === true)
    },
    
    professores: (state) => {
      return state.users.filter(u => u.role === 'Professor' && u.ativo === true)
    },
    
    processoPedagogico: (state) => {
      return state.users.filter(u => u.role === 'Processo pedagógico' && u.ativo === true)
    },
    
    getByRegistro: (state) => (registro) => {
      if (!registro) return []
      return state.users.filter(u => 
        u.registro && u.registro.toString().includes(registro.toString()) && u.ativo === true
      )
    },
    
    getByNome: (state) => (nome) => {
      if (!nome) return []
      const termo = nome.toLowerCase()
      return state.users.filter(u => 
        u.nome && u.nome.toLowerCase().includes(termo) && u.ativo === true
      )
    },
    
    getByEmail: (state) => (email) => {
      if (!email) return []
      const termo = email.toLowerCase()
      return state.users.filter(u => 
        u.email && u.email.toLowerCase().includes(termo) && u.ativo === true
      )
    },
    
    getByDisciplina: (state) => (disciplina) => {
      if (!disciplina) return []
      return state.users.filter(u => 
        u.role === 'Professor' && 
        u.disciplina === disciplina && 
        u.ativo === true
      )
    }
  },

  actions: {
    fetchUsers() {
      this.loading = true
      this.error = null
      
      try {
        const saved = localStorage.getItem('users')
        console.log('Dados salvos no localStorage:', saved) // Debug
        
        if (saved) {
          this.users = JSON.parse(saved)
          console.log('Usuários carregados:', this.users) // Debug
        } else {
          // Usuários padrão para primeiro acesso
          this.users = [
            {
              id: 1,
              registro: 123456,
              nome: 'Professor Silva',
              email: 'professor.silva@escola.com',
              senha: '123456',
              role: 'Professor',
              disciplina: 'Matemática FGB',
              ativo: true,
              primeiroAcesso: true,
              dataNascimento: '1980-05-15',
              createdAt: '2024-01-01',
              updatedAt: '2024-01-01',
              deletedAt: null
            },
            {
              id: 2,
              registro: 654321,
              nome: 'Processo Pedagógico',
              email: 'processo@escola.com',
              senha: '654321',
              role: 'Processo pedagógico',
              disciplina: null,
              ativo: true,
              primeiroAcesso: false,
              dataNascimento: '1975-10-20',
              createdAt: '2024-01-01',
              updatedAt: '2024-01-01',
              deletedAt: null
            }
          ]
          this.saveToLocalStorage()
          console.log('Usuários padrão criados:', this.users) // Debug
        }
      } catch (error) {
        console.error('Erro ao carregar usuários:', error)
        this.error = error.message
        this.users = []
      } finally {
        this.loading = false
      }
    },

    saveToLocalStorage() {
      try {
        localStorage.setItem('users', JSON.stringify(this.users))
        console.log('Usuários salvos no localStorage') // Debug
      } catch (error) {
        console.error('Erro ao salvar usuários:', error)
        this.error = error.message
      }
    },

    createUser(userData) {
      // Validações
      if (!userData.registro || !Number.isInteger(userData.registro)) {
        throw new Error('Registro deve ser um número inteiro')
      }
      
      if (this.users.some(u => u.registro === userData.registro)) {
        throw new Error('Registro já cadastrado')
      }
      
      if (!userData.nome || userData.nome.length < 5) {
        throw new Error('Nome deve ter ao menos 5 caracteres')
      }
      
      if (userData.nome.split(' ').length < 2) {
        throw new Error('Nome deve ter ao menos um sobrenome')
      }
      
      const emailRegex = /^[a-zA-Z0-9][a-zA-Z0-9._%+-]{0,63}@[a-zA-Z0-9][a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
      if (!emailRegex.test(userData.email)) {
        throw new Error('Email inválido')
      }
      
      if (!userData.role || !['Professor', 'Processo pedagógico'].includes(userData.role)) {
        throw new Error('Role inválido')
      }
      
      if (userData.role === 'Professor' && !userData.disciplina) {
        throw new Error('Professor deve ter uma disciplina associada')
      }
      
      const newUser = {
        id: Date.now(),
        registro: userData.registro,
        nome: userData.nome,
        email: userData.email.toLowerCase(),
        senha: userData.senha || this.gerarSenhaTemporaria(userData.dataNascimento),
        role: userData.role,
        disciplina: userData.role === 'Professor' ? userData.disciplina : null,
        ativo: true,
        primeiroAcesso: true,
        dataNascimento: userData.dataNascimento || null,
        createdAt: new Date().toISOString().split('T')[0],
        updatedAt: new Date().toISOString().split('T')[0],
        deletedAt: null
      }
      
      this.users.push(newUser)
      this.saveToLocalStorage()
      return newUser
    },

    updateUser(id, updates) {
      const index = this.users.findIndex(u => u.id === id)
      if (index === -1) throw new Error('Usuário não encontrado')
      
      // Não permite alterar registro e id
      delete updates.registro
      delete updates.id
      
      if (updates.email) {
        const emailRegex = /^[a-zA-Z0-9][a-zA-Z0-9._%+-]{0,63}@[a-zA-Z0-9][a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
        if (!emailRegex.test(updates.email)) {
          throw new Error('Email inválido')
        }
        updates.email = updates.email.toLowerCase()
      }
      
      if (updates.disciplina !== undefined && this.users[index].role === 'Professor') {
        if (!updates.disciplina) {
          throw new Error('Professor deve ter uma disciplina associada')
        }
      }
      
      this.users[index] = {
        ...this.users[index],
        ...updates,
        updatedAt: new Date().toISOString().split('T')[0]
      }
      
      this.saveToLocalStorage()
      return this.users[index]
    },

    softDeleteUser(id) {
      const index = this.users.findIndex(u => u.id === id)
      if (index === -1) throw new Error('Usuário não encontrado')
      
      this.users[index].ativo = false
      this.users[index].deletedAt = new Date().toISOString().split('T')[0]
      this.saveToLocalStorage()
    },

    gerarSenhaTemporaria(dataNascimento) {
      if (dataNascimento) {
        return dataNascimento.replace(/-/g, '')
      }
      return '123456'
    },

    resetarSenha(id, novaSenha) {
      const index = this.users.findIndex(u => u.id === id)
      if (index === -1) throw new Error('Usuário não encontrado')
      
      if (novaSenha.length < 6) {
        throw new Error('Senha deve ter ao menos 6 caracteres')
      }
      
      if (!/[A-Z]/.test(novaSenha)) {
        throw new Error('Senha deve conter ao menos uma letra maiúscula')
      }
      
      if (!/\d/.test(novaSenha)) {
        throw new Error('Senha deve conter ao menos um número')
      }
      
      if (!/[!@#$%^&*(),.?":{}|<>]/.test(novaSenha)) {
        throw new Error('Senha deve conter ao menos um caractere especial')
      }
      
      this.users[index].senha = novaSenha
      this.users[index].primeiroAcesso = false
      this.saveToLocalStorage()
    },

    isPrimeiroAcesso(registro) {
      const user = this.users.find(u => u.registro === registro && u.ativo === true)
      return user ? user.primeiroAcesso : false
    }
  }
})