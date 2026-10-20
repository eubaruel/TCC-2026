<template>
  <div
    class="sidebar"
    :class="{ 'sidebar-retraida': !hoverActive }"
    @mouseenter="hoverActive = true"
    @mouseleave="hoverActive = false"
  >
    <div class="sidebar-content">
      <div class="logo-sidebar">
        <img src="/logo_univap.ico" alt="Logo" class="logo-mini" />
        <span v-show="hoverActive" class="logo-texto">UNIVAP</span>
      </div>

      <nav class="nav-menu">
        <!-- Menu para Professor -->
        <template v-if="isProfessor">
          <router-link
            to="/provas"
            class="nav-item"
            :class="{ 'nav-item-expandido': hoverActive }"
            active-class="nav-item-ativo"
          >
            <div class="nav-icon">
              <svg
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M4 4H20V20H4V4Z"
                  stroke="white"
                  stroke-width="2"
                  fill="none"
                />
                <path d="M8 8H16V10H8V8Z" fill="white" />
                <path d="M8 12H14V14H8V12Z" fill="white" />
                <path d="M8 16H12V18H8V16Z" fill="white" />
              </svg>
            </div>
            <span v-show="hoverActive" class="nav-texto">Provas</span>
          </router-link>

          <router-link
            to="/questoes"
            class="nav-item"
            :class="{ 'nav-item-expandido': hoverActive }"
            active-class="nav-item-ativo"
          >
            <div class="nav-icon">
              <svg
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M14 4H6C5.46957 4 4.96086 4.21071 4.58579 4.58579C4.21071 4.96086 4 5.46957 4 6V18C4 18.5304 4.21071 19.0391 4.58579 19.4142C4.96086 19.7893 5.46957 20 6 20H18C18.5304 20 19.0391 19.7893 19.4142 19.4142C19.7893 19.0391 20 18.5304 20 18V10"
                  stroke="white"
                  stroke-width="2"
                  fill="none"
                />
                <path d="M15 4L20 9" stroke="white" stroke-width="2" />
                <path
                  d="M12 12H8V16H12V12Z"
                  stroke="white"
                  stroke-width="2"
                  fill="none"
                />
              </svg>
            </div>
            <span v-show="hoverActive" class="nav-texto">Questões</span>
          </router-link>
        </template>

        <!-- Menu para Processo Pedagógico -->
        <template v-if="isProcessoPedagogico">
          <router-link
            to="/provas"
            class="nav-item"
            :class="{ 'nav-item-expandido': hoverActive }"
            active-class="nav-item-ativo"
          >
            <div class="nav-icon">
              <svg
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M4 4H20V20H4V4Z"
                  stroke="white"
                  stroke-width="2"
                  fill="none"
                />
                <path d="M8 8H16V10H8V8Z" fill="white" />
                <path d="M8 12H14V14H8V12Z" fill="white" />
                <path d="M8 16H12V18H8V16Z" fill="white" />
              </svg>
            </div>
            <span v-show="hoverActive" class="nav-texto">Provas</span>
          </router-link>

          <router-link
            to="/usuarios"
            class="nav-item"
            :class="{ 'nav-item-expandido': hoverActive }"
            active-class="nav-item-ativo"
          >
            <div class="nav-icon">
              <svg
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M12 12C14.21 12 16 10.21 16 8C16 5.79 14.21 4 12 4C9.79 4 8 5.79 8 8C8 10.21 9.79 12 12 12Z"
                  stroke="white"
                  stroke-width="2"
                  fill="none"
                />
                <path
                  d="M5 20V19C5 15.13 8.13 12 12 12C15.87 12 19 15.13 19 19V20"
                  stroke="white"
                  stroke-width="2"
                />
              </svg>
            </div>
            <span v-show="hoverActive" class="nav-texto">Usuários</span>
          </router-link>
        </template>

        <!-- Informações (para todos os usuários) -->
        <router-link
          to="/informacoes"
          aria-label="Informações"
          title="Informações"
          class="nav-item"
          :class="{ 'nav-item-expandido': hoverActive }"
          active-class="nav-item-ativo"
        >
          <div class="nav-icon">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke-width="1.5"
              stroke="currentColor"
              class="size-6"
              aria-hidden="true"
            >
              <circle cx="12" cy="12" r="9" />
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M12 11v6m0-10v.01"
              />
            </svg>
          </div>
          <span v-show="hoverActive" class="nav-texto">Informações</span>
        </router-link>
      </nav>

      <!-- Botão Sair na parte inferior -->
      <div class="logout-section">
        <button
          @click="logout"
          class="logout-btn"
          :class="{ 'logout-btn-expandido': hoverActive }"
        >
          <div class="nav-icon">
            <svg
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M9 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V5C3 4.46957 3.21071 3.96086 3.58579 3.58579C3.96086 3.21071 4.46957 3 5 3H9"
                stroke="white"
                stroke-width="2"
                fill="none"
              />
              <path d="M16 17L21 12L16 7" stroke="white" stroke-width="2" />
              <path d="M21 12H9" stroke="white" stroke-width="2" />
            </svg>
          </div>
          <span v-show="hoverActive" class="nav-texto">Sair</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { useAuthStore } from "@/stores/auth";
import { useRouter } from "vue-router";

export default {
  name: "BarraLateral",
  setup() {
    const authStore = useAuthStore();
    const router = useRouter();

    const logout = () => {
      window.$modal.abrir({
        titulo: "Confirmar Saída",
        mensagem: "Tem certeza que deseja sair?",
        tipo: "confirmacao",
        onConfirm: () => {
          authStore.logout();
          router.push("/");
        },
      });
    };

    return {
      isProfessor: authStore.isProfessor,
      isProcessoPedagogico: authStore.isProcessoPedagogico,
      logout,
    };
  },
  data() {
    return {
      hoverActive: false,
    };
  },
};
</script>

<style scoped>
.sidebar {
  position: fixed;
  left: 0;
  top: 0;
  height: 100vh;
  background: linear-gradient(135deg, #00488b 0%, #003366 100%);
  transition: width 0.3s ease;
  overflow: hidden;
  z-index: 1000;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
}

.sidebar-retraida {
  width: 70px;
}

.sidebar:not(.sidebar-retraida) {
  width: 250px;
}

.sidebar-content {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 20px 0 0 0;
}

.logo-sidebar {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 15px;
  margin-bottom: 40px;
  gap: 10px;
}

.logo-mini {
  width: 40px;
  height: 40px;
  object-fit: contain;
}

.logo-texto {
  color: white;
  font-weight: bold;
  font-size: 18px;
  white-space: nowrap;
}

.nav-menu {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 0 10px;
  margin-bottom: 30px;
}

.logout-section {
  padding: 15px 10px 40px 10px;
  border-top: 1px solid rgba(255, 255, 255, 0.2);
  margin-top: auto;
}

.logout-btn {
  display: flex;
  align-items: center;
  padding: 12px;
  color: white;
  text-decoration: none;
  border-radius: 8px;
  transition: all 0.3s ease;
  white-space: nowrap;
  gap: 12px;
  background: transparent;
  border: none;
  width: 100%;
  cursor: pointer;
  margin-top: 12px;
}

.logout-btn-expandido {
  padding: 12px 15px;
}

.logout-btn:hover {
  background-color: rgba(255, 255, 255, 0.1);
  transform: translateX(5px);
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 12px;
  color: white;
  text-decoration: none;
  border-radius: 8px;
  transition: all 0.3s ease;
  white-space: nowrap;
  gap: 12px;
}

.nav-item-expandido {
  padding: 12px 15px;
}

.nav-icon {
  min-width: 24px;
  display: flex;
  justify-content: center;
}

.nav-texto {
  font-size: 14px;
  font-weight: 500;
}

.nav-item:hover {
  background-color: rgba(255, 255, 255, 0.1);
  transform: translateX(5px);
}

.nav-item-ativo {
  background-color: rgba(255, 255, 255, 0.2);
  border-left: 3px solid white;
}

@media (max-width: 768px) {
  .sidebar-retraida {
    width: 60px;
  }

  .sidebar:not(.sidebar-retraida) {
    width: 220px;
  }

  .logo-mini {
    width: 32px;
    height: 32px;
  }

  .logo-texto {
    font-size: 16px;
  }

  .nav-item {
    padding: 10px;
  }

  .nav-texto {
    font-size: 13px;
  }

  .logout-btn {
    padding: 10px;
  }
}
</style>
