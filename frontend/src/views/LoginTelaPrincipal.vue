<template>
  <div class="login_container_principal">
    <LoginFormulario />
  </div>
</template>

<script>
import LoginFormulario from "@/components/LoginFormulario.vue";

export default {
  name: "LoginTelaPrincipal",
  components: {
    LoginFormulario,
  },
};
</script>

<style scoped>
.login_container_principal {
  position: fixed;
  inset: 0;
  width: 100%;
  min-height: 100vh;
  min-height: 100dvh;
  background-color: #00488b;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
  box-sizing: border-box;
  overflow-y: auto;
}

@media (max-width: 768px) {
  .login_container_principal {
    padding: 15px;
  }
}
</style>
