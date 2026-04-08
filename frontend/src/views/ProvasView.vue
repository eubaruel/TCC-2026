<template>
  <div class="provas-container">
    <div class="page-header">
      <h2>Provas</h2>
      <div class="header-line"></div>
    </div>
    
    <div class="alerts-section">
      <h3>Avisos de Provas</h3>
      <div v-if="alerts.length === 0" class="sem-alerts">
        Nenhum aviso de prova no momento.
      </div>
      <div v-else>
        <AlertProva
          v-for="alert in alerts"
          :key="alert.id"
          :id="alert.id"
          :titulo="alert.titulo"
          :mensagem="alert.mensagem"
          :dataEntrega="alert.dataEntrega"
          :disciplina="alert.disciplina"
          :turma="alert.turma"
          :bimestre="alert.bimestre"
          :semana="alert.semana"
          :tipoUsuario="userType"
          :entregueInicial="alert.entregue"
          @confirmado="onConfirmado"
        />
      </div>
    </div>
  </div>
</template>

<script>
import AlertProva from '@/components/AlertProva.vue'
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'ProvasView',
  components: {
    AlertProva
  },
  setup() {
    const authStore = useAuthStore()
    return { authStore }
  },
  data() {
    return {
      alerts: []
    }
  },
  computed: {
    userType() {
      return this.authStore.userType
    }
  },
  mounted() {
    this.carregarAlerts()
  },
  methods: {
    carregarAlerts() {
      const alertsSalvos = localStorage.getItem('alerts')
      if (alertsSalvos) {
        const todosAlerts = JSON.parse(alertsSalvos)
        
        if (this.userType === 'professor') {
          const entregues = JSON.parse(localStorage.getItem('entregues') || '{}')
          this.alerts = todosAlerts.map(alert => ({
            ...alert,
            entregue: entregues[alert.id] || false
          }))
        } else {
          this.alerts = todosAlerts
        }
      } else {
        this.alerts = [
          {
            id: 1,
            titulo: 'Prova Bimestral - Matemática',
            mensagem: 'A prova bimestral de Matemática deve ser entregue até o prazo estipulado.',
            dataEntrega: '15/04/2026',
            disciplina: 'Matemática',
            turma: '1° Ano A',
            bimestre: '1° Bimestre',
            semana: 'G1 Objetiva',
            entregue: false
          },
          {
            id: 2,
            titulo: 'Prova Final - Português',
            mensagem: 'Entrega da prova final de Português para correção.',
            dataEntrega: '22/04/2026',
            disciplina: 'Português',
            turma: '2° Ano B',
            bimestre: '2° Bimestre',
            semana: 'G2 Dissertativa',
            entregue: false
          }
        ]
        localStorage.setItem('alerts', JSON.stringify(this.alerts))
      }
    },
    
    onConfirmado(id) {
      const entregues = JSON.parse(localStorage.getItem('entregues') || '{}')
      entregues[id] = true
      localStorage.setItem('entregues', JSON.stringify(entregues))
      
      const alert = this.alerts.find(a => a.id === id)
      if (alert) {
        alert.entregue = true
      }
    }
  }
}
</script>

<style scoped>
.provas-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 0 20px;
}

.page-header {
  margin-bottom: 30px;
}

.page-header h2 {
  font-size: 28px;
  font-weight: 600;
  margin-bottom: 15px;
  margin-top: 20px;
  color: inherit;
}

.header-line {
  height: 2px;
  background: linear-gradient(90deg, #00488b 0%, #00488b 50%, transparent 100%);
  width: 100%;
}

.alerts-section h3 {
  font-size: 20px;
  margin-bottom: 20px;
  color: inherit;
}

.sem-alerts {
  text-align: center;
  padding: 40px;
  color: #888;
  background: #f5f5f5;
  border-radius: 12px;
}

.tema-escuro .sem-alerts {
  background: #2a2a2a;
}
</style>