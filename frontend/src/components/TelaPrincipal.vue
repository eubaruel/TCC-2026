<template>
  <div class="app-container">
    <BarraLateral />
    <div class="conteudo-principal" :class="temaAtual">
      <div class="header" v-if="mostrarHeader">
        <h1>Seja Bem Vindo(a) {{ nomeProfessor }}!</h1>
      </div>

      <div class="conteudo">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script>
import BarraLateral from "@/components/BarraLateral.vue";

export default {
  name: "TelaPrincipal",
  components: {
    BarraLateral,
  },
  data() {
    return {
      nomeProfessor: "Professor",
      temaAtual: "tema-claro",
      configuracaoAlterada: false,
      mostrarHeader: true,
    };
  },
  mounted() {
    console.log("TelaPrincipal montada, rota:", this.$route.path);
    this.carregarDadosUsuario();
    this.carregarTema();
    this.verificarRota();

    window.addEventListener("tema-mudou", this.atualizarTema);
  },
  beforeUnmount() {
    window.removeEventListener("tema-mudou", this.atualizarTema);
  },
  watch: {
    "$route.path"() {
      this.verificarRota();
    },
  },
  methods: {
    carregarDadosUsuario() {
      const usuarioSalvo = localStorage.getItem("usuarioLogado");
      if (usuarioSalvo) {
        try {
          const usuario = JSON.parse(usuarioSalvo);
          this.nomeProfessor =
            usuario.nome || usuario.email?.split("@")[0] || "Professor";
        } catch (error) {
          console.error("Erro ao carregar dados do usuário:", error);
        }
      }
    },

    carregarTema() {
      const temaSalvo = localStorage.getItem("tema");
      if (temaSalvo) {
        this.temaAtual = temaSalvo;
      } else {
        this.temaAtual = "tema-claro";
      }
    },

    atualizarTema(event) {
      this.temaAtual = event.detail.tema;
    },

    verificarRota() {
      if (this.$route.path === "/configuracoes") {
        this.mostrarHeader = false;
      } else {
        this.mostrarHeader = true;
      }
    },
  },
};
</script>

<style scoped>
.app-container {
  display: flex;
  min-height: 100vh;
}

.conteudo-principal {
  flex: 1;
  margin-left: 70px;
  transition: margin-left 0.3s ease, background-color 0.3s ease, color 0.3s ease;
  min-height: 100vh;
}

.conteudo-principal.tema-claro {
  background-color: #f5f5f5;
  color: #333;
}

.conteudo-principal.tema-escuro {
  background-color: #1a1a1a;
  color: #e5e5e5;
}

.header {
  padding: 30px 40px;
  border-bottom: 2px solid rgba(0, 0, 0, 0.1);
}

.tema-escuro .header {
  border-bottom-color: rgba(255, 255, 255, 0.1);
}

.header h1 {
  font-size: 28px;
  font-weight: 600;
  margin: 0;
}

.conteudo {
  padding: 30px 40px;
}

@media (min-width: 769px) {
  .sidebar:hover ~ .conteudo-principal {
    margin-left: 250px;
  }
}

@media (max-width: 768px) {
  .conteudo-principal {
    margin-left: 70px;
  }

  .header {
    padding: 20px;
  }

  .header h1 {
    font-size: 24px;
  }

  .conteudo {
    padding: 20px;
  }
}
</style>
