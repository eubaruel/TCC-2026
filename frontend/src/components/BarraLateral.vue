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
      </div>
      
      <nav class="nav-menu">
        <router-link 
          to="/acessar-provas" 
          class="nav-item"
          :class="{ 'nav-item-expandido': hoverActive }"
          active-class="nav-item-ativo"
        >
          <div class="nav-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M4 4H20V20H4V4Z" stroke="white" stroke-width="2" fill="none"/>
              <path d="M8 8H16V10H8V8Z" fill="white"/>
              <path d="M8 12H14V14H8V12Z" fill="white"/>
              <path d="M8 16H12V18H8V16Z" fill="white"/>
            </svg>
          </div>
          <span v-show="hoverActive" class="nav-texto">Acessar Provas</span>
        </router-link>

        <router-link 
          to="/montar-prova" 
          class="nav-item"
          :class="{ 'nav-item-expandido': hoverActive }"
          active-class="nav-item-ativo"
        >
          <div class="nav-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M14 4H6C5.46957 4 4.96086 4.21071 4.58579 4.58579C4.21071 4.96086 4 5.46957 4 6V18C4 18.5304 4.21071 19.0391 4.58579 19.4142C4.96086 19.7893 5.46957 20 6 20H18C18.5304 20 19.0391 19.7893 19.4142 19.4142C19.7893 19.0391 20 18.5304 20 18V10" stroke="white" stroke-width="2" fill="none"/>
              <path d="M15 4L20 9" stroke="white" stroke-width="2"/>
              <path d="M12 12H8V16H12V12Z" stroke="white" stroke-width="2" fill="none"/>
            </svg>
          </div>
          <span v-show="hoverActive" class="nav-texto">Montar Prova</span>
        </router-link>

        <router-link 
          to="/configuracoes" 
          class="nav-item"
          :class="{ 'nav-item-expandido': hoverActive }"
          active-class="nav-item-ativo"
        >
          <div class="nav-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="12" cy="12" r="3" stroke="white" stroke-width="2" fill="none"/>
              <path d="M19.4 15.5L18.2 16.7C17.9 17 17.5 17.2 17.1 17.2C16.7 17.2 16.3 17 16 16.7L12 12.7L8 16.7C7.7 17 7.3 17.2 6.9 17.2C6.5 17.2 6.1 17 5.8 16.7L4.6 15.5C4.3 15.2 4.1 14.8 4.1 14.4C4.1 14 4.3 13.6 4.6 13.3L8.6 9.3L4.6 5.3C4.3 5 4.1 4.6 4.1 4.2C4.1 3.8 4.3 3.4 4.6 3.1L5.8 1.9C6.1 1.6 6.5 1.4 6.9 1.4C7.3 1.4 7.7 1.6 8 1.9L12 5.9L16 1.9C16.3 1.6 16.7 1.4 17.1 1.4C17.5 1.4 17.9 1.6 18.2 1.9L19.4 3.1C19.7 3.4 19.9 3.8 19.9 4.2C19.9 4.6 19.7 5 19.4 5.3L15.4 9.3L19.4 13.3C19.7 13.6 19.9 14 19.9 14.4C19.9 14.8 19.7 15.2 19.4 15.5Z" stroke="white" stroke-width="2" fill="none"/>
            </svg>
          </div>
          <span v-show="hoverActive" class="nav-texto">Configurações</span>
        </router-link>
      </nav>
    </div>
  </div>
</template>

<script>
export default {
  name: 'BarraLateral',
  data() {
    return {
      hoverActive: false
    }
  }
}
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
  padding: 20px 0;
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

/* Efeito apenas quando passar o mouse */
.nav-item:hover {
  background-color: rgba(255, 255, 255, 0.1);
  transform: translateX(5px);
}

/* Estilo apenas para o item que está ativo (página atual) */
.nav-item-ativo {
  background-color: rgba(255, 255, 255, 0.2);
  border-left: 3px solid white;
}
</style>