import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './assets/css/estilos_globais.css' // Caminho corrigido para assets/css

const app = createApp(App)
app.use(router)
app.mount('#app')