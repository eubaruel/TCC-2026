<template>
  <div class="alert-prova" :class="{ entregue: entregue }">
    <div class="alert-content">
      <div class="alert-icon">
        <svg
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M12 8V12L15 15M12 22C6.477 22 2 17.523 2 12S6.477 2 12 2 22 6.477 22 12 17.523 22 12 22Z"
            stroke="currentColor"
            stroke-width="2"
          />
          <path d="M12 6V12L15 15" stroke="currentColor" stroke-width="2" />
        </svg>
      </div>
      <div class="alert-info">
        <h4>{{ titulo }}</h4>
        <p>{{ mensagem }}</p>
        <div class="alert-data">
          <span>📅 Data de entrega: {{ dataEntrega }}</span>
          <span>📚 Disciplina: {{ disciplina }}</span>
          <span>🏫 Turma: {{ turma }}</span>
          <span>📆 Bimestre: {{ bimestre }}</span>
          <span>📋 Semana: {{ semana }}</span>
        </div>
      </div>
      <button
        v-if="!entregue && tipoUsuario === 'professor'"
        @click="confirmarEntrega"
        class="btn-confirmar"
      >
        Confirmar Entrega
      </button>
      <span v-if="entregue" class="status-entregue">
        Entregue em {{ dataConfirmacao }}
      </span>
      <span
        v-if="tipoUsuario === 'processo_pedagogico'"
        class="status-aguardando"
      >
        Aguardando confirmação
      </span>
    </div>
  </div>
</template>

<script>
export default {
  name: "AlertProva",
  props: {
    id: {
      type: Number,
      required: true,
    },
    titulo: {
      type: String,
      required: true,
    },
    mensagem: {
      type: String,
      required: true,
    },
    dataEntrega: {
      type: String,
      required: true,
    },
    disciplina: {
      type: String,
      default: "Não especificada",
    },
    turma: {
      type: String,
      default: "Não especificada",
    },
    bimestre: {
      type: String,
      default: "Não especificado",
    },
    semana: {
      type: String,
      default: "Não especificada",
    },
    tipoUsuario: {
      type: String,
      required: true,
    },
    entregueInicial: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      entregue: this.entregueInicial,
      dataConfirmacao: null,
    };
  },
  mounted() {
    if (this.entregue) {
      const entregueSalvo = localStorage.getItem(`prova_${this.id}_entregue`);
      if (entregueSalvo) {
        const data = JSON.parse(entregueSalvo);
        this.dataConfirmacao = data.data;
      }
    }
  },
  methods: {
    confirmarEntrega() {
      window.$modal.abrir({
        titulo: "Confirmar Entrega",
        mensagem: "Tem certeza que deseja confirmar a entrega desta prova?",
        tipo: "confirmacao",
        onConfirm: () => {
          this.entregue = true;
          const dataAtual = new Date().toLocaleDateString("pt-BR");
          this.dataConfirmacao = dataAtual;

          localStorage.setItem(
            `prova_${this.id}_entregue`,
            JSON.stringify({
              entregue: true,
              data: dataAtual,
            }),
          );

          this.$emit("confirmado", this.id);

          window.$modal.abrir({
            titulo: "Sucesso",
            mensagem: "Prova confirmada com sucesso!",
            tipo: "alerta",
          });
        },
      });
    },
  },
};
</script>

<style scoped>
.alert-prova {
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 16px;
  border-left: 4px solid #00488b;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.alert-prova.entregue {
  border-left-color: #28a745;
  background: #f8fff8;
  opacity: 0.8;
}

.tema-escuro .alert-prova {
  background: #2a2a2a;
  border-left-color: #0066cc;
}

.tema-escuro .alert-prova.entregue {
  background: #1e3a2e;
  border-left-color: #28a745;
}

.alert-content {
  display: flex;
  gap: 16px;
  align-items: flex-start;
  flex-wrap: wrap;
}

.alert-icon {
  width: 40px;
  height: 40px;
  background: #00488b20;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #00488b;
}

.tema-escuro .alert-icon {
  background: #0066cc20;
  color: #0066cc;
}

.alert-info {
  flex: 1;
}

.alert-info h4 {
  font-size: 18px;
  margin-bottom: 8px;
  color: inherit;
}

.alert-info p {
  font-size: 14px;
  margin-bottom: 12px;
  color: #666;
}

.tema-escuro .alert-info p {
  color: #aaa;
}

.alert-data {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #888;
  flex-wrap: wrap;
}

.tema-escuro .alert-data {
  color: #aaa;
}

.btn-confirmar {
  padding: 10px 20px;
  background: #28a745;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
}

.btn-confirmar:hover {
  background: #218838;
  transform: scale(1.02);
}

.status-entregue {
  padding: 10px 20px;
  background: #28a74520;
  color: #28a745;
  border-radius: 8px;
  font-size: 14px;
}

.status-aguardando {
  padding: 10px 20px;
  background: #ffc10720;
  color: #ffc107;
  border-radius: 8px;
  font-size: 14px;
}
</style>
