import { createRouter, createWebHistory } from 'vue-router'
import LoginTelaPrincipal from '@/views/LoginTelaPrincipal.vue'
import TelaPrincipal from '@/components/TelaPrincipal.vue'
import AcessarProvas from '@/views/AcessarProvas.vue'
import MontarProva from '@/views/MontarProva.vue'
import ConfiGuracoes from '@/views/ConfiGuracoes.vue'

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
        path: 'acessar-provas',
        name: 'AcessarProvas',
        component: AcessarProvas
      },
      {
        path: 'montar-prova',
        name: 'MontarProva',
        component: MontarProva
      },
      {
        path: 'configuracoes',
        name: 'ConfiGuracoes',
        component: ConfiGuracoes
      },
      {
        path: '',
        redirect: '/acessar-provas'
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const usuarioLogado = localStorage.getItem('usuarioLogado')
  
  if (to.meta.requiresAuth && !usuarioLogado) {
    next('/')
  } else {
    next()
  }
})

export default router