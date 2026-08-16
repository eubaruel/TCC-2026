import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './assets/css/estilos_globais.css'

const pinia = createPinia()
const app = createApp(App)

// Criar usuários de teste no localStorage se não existirem
const usuariosPadrao = [
  {
    id: 1,
    nome: 'Professor Silva',
    registro: 123456,
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
    nome: 'Professor Oliveira',
    registro: 789012,
    email: 'professor.oliveira@escola.com',
    senha: '789012',
    role: 'Professor',
    disciplina: 'Português',
    ativo: true,
    primeiroAcesso: true,
    dataNascimento: '1982-03-10',
    createdAt: '2024-01-01',
    updatedAt: '2024-01-01',
    deletedAt: null
  },
  {
    id: 3,
    nome: 'Processo Pedagógico',
    registro: 654321,
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

// Verifica se já existem usuários salvos
const usuariosSalvos = localStorage.getItem('users')
if (!usuariosSalvos) {
  localStorage.setItem('users', JSON.stringify(usuariosPadrao))
  console.log('Usuários de teste criados no localStorage!')
} else {
  console.log('Usuários já existem no localStorage')
}

app.use(pinia)
app.use(router)
app.mount('#app')