import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './assets/css/estilos_globais.css'

const pinia = createPinia()
const app = createApp(App)

const usuariosPadrao = [
  {
    id: 1,
    nome: 'Professor Silva',
    registro: '123456',
    senha: '123456',
    tipo: 'professor'
  },
  {
    id: 2,
    nome: 'Professor Oliveira',
    registro: '789012',
    senha: '789012',
    tipo: 'professor'
  },
  {
    id: 3,
    nome: 'Processo Pedagógico',
    registro: '654321',
    senha: '654321',
    tipo: 'processo_pedagogico'
  }
]

// Verifica se já existem usuários salvos
const usuariosSalvos = localStorage.getItem('usuarios')
if (!usuariosSalvos) {
  localStorage.setItem('usuarios', JSON.stringify(usuariosPadrao))
  console.log('Usuários de teste criados no localStorage!')
} else {
  console.log('Usuários já existem no localStorage')
}

app.use(pinia)
app.use(router)
app.mount('#app')