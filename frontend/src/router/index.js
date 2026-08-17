import { createRouter, createWebHistory } from "vue-router";
import LoginTelaPrincipal from "@/views/LoginTelaPrincipal.vue";
import TelaPrincipal from "@/components/TelaPrincipal.vue";
import AvisosView from "@/views/AvisosView.vue";
import ProvasView from "@/views/ProvasView.vue";
import QuestoesView from "@/views/QuestoesView.vue";
import GestaoUsuarios from "@/views/GestaoUsuarios.vue";
import ConfiGuracoes from "@/views/ConfiGuracoes.vue";
import { useAuthStore } from "@/stores/auth";

const routes = [
  {
    path: "/",
    name: "Login",
    component: LoginTelaPrincipal,
  },
  {
    path: "/",
    component: TelaPrincipal,
    meta: { requiresAuth: true },
    children: [
      {
        path: "avisos",
        name: "AvisosView",
        component: AvisosView,
      },
      {
        path: "provas",
        name: "ProvasView",
        component: ProvasView,
      },
      {
        path: "questoes",
        name: "QuestoesView",
        component: QuestoesView,
        meta: { requiresProfessor: true },
      },
      {
        path: "usuarios",
        name: "GestaoUsuarios",
        component: GestaoUsuarios,
        meta: { requiresProcesso: true },
      },
      {
        path: "configuracoes",
        name: "ConfiGuracoes",
        component: ConfiGuracoes,
      },
      {
        path: "",
        redirect: "/avisos",
      },
    ],
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();

  if (to.meta.requiresAuth && !authStore.isLoggedIn) {
    next("/");
  } else if (to.meta.requiresProfessor && !authStore.isProfessor) {
    next("/avisos");
  } else if (to.meta.requiresProcesso && !authStore.isProcessoPedagogico) {
    next("/avisos");
  } else {
    next();
  }
});

export default router;
