<template>
  <router-view />
  <ModalGlobal ref="$modal" />
</template>

<script>
import ModalGlobal from "@/components/ModalGlobal.vue";

export default {
  name: "App",
  components: { ModalGlobal },
  mounted() { window.$modal = this.$refs.$modal; },
};
</script>
<style>
/* Estilos adicionais */
</style>
