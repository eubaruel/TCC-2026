import { createRouter, createWebHistory } from 'vue-router'
import LoginTelaPrincipal from '@/views/LoginTelaPrincipal.vue'
import TelaPrincipal from '@/components/TelaPrincipal.vue'
import ProvasView from '@/views/ProvasView.vue'
import QuestoesView from '@/views/QuestoesView.vue'
import AvisosView from '@/views/AvisosView.vue'
import ConfiGuracoes from '@/views/ConfiGuracoes.vue'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/',
    name: 'Login',
    component: LoginTelaPrincipal
  },
  {
    path: '/',
    component: TelaPrincipal,
    meta: { requiresAuth: true },
    children: [
      {
        path: 'provas',
        name: 'ProvasView',
        component: ProvasView
      },
      {
        path: 'questoes',
        name: 'QuestoesView',
        component: QuestoesView,
        meta: { requiresProfessor: true }
      },
      {
        path: 'avisos',
        name: 'AvisosView',
        component: AvisosView,
        meta: { requiresProcesso: true }
      },
      {
        path: 'configuracoes',
        name: 'ConfiGuracoes',
        component: ConfiGuracoes
      },
      {
        path: '',
        redirect: '/provas'
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  authStore.loadUser()
  
  const usuarioLogado = localStorage.getItem('usuarioLogado')
  
  if (to.meta.requiresAuth && !usuarioLogado) {
    next('/')
  } else if (to.meta.requiresProfessor && !authStore.isProfessor) {
    next('/provas')
  } else if (to.meta.requiresProcesso && !authStore.isProcessoPedagogico) {
    next('/provas')
  } else {
    next()
  }
})

export default router