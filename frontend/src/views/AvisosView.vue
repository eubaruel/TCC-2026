<template>
  <div class="avisos-container">
    <div class="page-header">
      <h2>Avisos de Provas</h2>
      <div class="header-line"></div>
    </div>
    
    <div class="criar-aviso">
      <h3>Criar Novo Aviso</h3>
      <form @submit.prevent="criarAviso" class="form-aviso">
        <div class="form-group">
          <label>Título do Aviso *</label>
          <input type="text" v-model="novoAviso.titulo" required placeholder="Ex: Prova Bimestral - Matemática" />
        </div>
        
        <div class="form-group">
          <label>Mensagem *</label>
          <textarea v-model="novoAviso.mensagem" rows="3" required placeholder="Detalhes sobre a prova..."></textarea>
        </div>
        
        <div class="form-row">
          <div class="form-group">
            <label>Matéria *</label>
            <input type="text" v-model="novoAviso.materia" required placeholder="Ex: Matemática" />
          </div>
          <div class="form-group">
            <label>Turma *</label>
            <input type="text" v-model="novoAviso.turma" required placeholder="Ex: 9° Ano A" />
          </div>
        </div>
        
        <div class="form-row">
          <div class="form-group">
            <label>Data de Entrega *</label>
            <input type="date" v-model="novoAviso.dataEntrega" required />
          </div>
          <div class="form-group">
            <label>Semana da Prova *</label>
            <select v-model="novoAviso.semana">
              <option value="">Selecione a semana</option>
              <option value="1ª Semana">1ª Semana do mês</option>
              <option value="2ª Semana">2ª Semana do mês</option>
              <option value="3ª Semana">3ª Semana do mês</option>
              <option value="4ª Semana">4ª Semana do mês</option>
              <option value="5ª Semana">5ª Semana do mês</option>
            </select>
          </div>
        </div>
        
        <button type="submit" class="btn-criar">📢 Publicar Aviso</button>
      </form>
    </div>
    
    <div class="avisos-lista">
      <h3>Avisos Publicados</h3>
      <div v-if="avisos.length === 0" class="sem-avisos">
        Nenhum aviso publicado ainda.
      </div>
      <div v-else>
        <div v-for="aviso in avisos" :key="aviso.id" class="aviso-card">
          <div class="aviso-header">
            <h4>{{ aviso.titulo }}</h4>
            <span class="aviso-data">{{ aviso.dataCriacao }}</span>
          </div>
          <p class="aviso-mensagem">{{ aviso.mensagem }}</p>
          <div class="aviso-detalhes">
            <span>📚 {{ aviso.materia }}</span>
            <span>🏫 {{ aviso.turma }}</span>
            <span>📅 Entrega: {{ aviso.dataEntregaFormatada || aviso.dataEntrega }}</span>
            <span>📆 {{ aviso.semana }}</span>
          </div>
          <div class="aviso-actions">
            <button @click="excluirAviso(aviso.id)" class="btn-excluir-aviso">🗑️ Excluir</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'AvisosView', // Nome do componente
  setup() {
    const authStore = useAuthStore()
    return { authStore }
  },
  data() {
    return {
      avisos: [],
      novoAviso: {
        titulo: '',
        mensagem: '',
        materia: '',
        turma: '',
        dataEntrega: '',
        semana: ''
      }
    }
  },
  mounted() {
    this.carregarAvisos()
  },
  methods: {
    carregarAvisos() {
      const salvos = localStorage.getItem('avisos')
      if (salvos) {
        this.avisos = JSON.parse(salvos).map(aviso => ({
          ...aviso,
          dataEntregaFormatada: this.formatarData(aviso.dataEntrega)
        }))
      } else {
        this.avisos = [
          {
            id: 1,
            titulo: 'Prova Bimestral - Matemática',
            mensagem: 'A prova bimestral de Matemática deve ser entregue até o prazo estipulado. A prova será sobre equações do 2º grau e geometria plana.',
            materia: 'Matemática',
            turma: '9° Ano A',
            dataEntrega: '2026-04-15',
            dataEntregaFormatada: '15/04/2026',
            semana: '2ª Semana',
            dataCriacao: '10/04/2026'
          },
          {
            id: 2,
            titulo: 'Prova Final - Português',
            mensagem: 'Entrega da prova final de Português para correção. Conteúdo: análise sintática e interpretação de texto.',
            materia: 'Português',
            turma: '8° Ano B',
            dataEntrega: '2026-04-22',
            dataEntregaFormatada: '22/04/2026',
            semana: '3ª Semana',
            dataCriacao: '12/04/2026'
          }
        ]
        localStorage.setItem('avisos', JSON.stringify(this.avisos))
      }
    },
    
    criarAviso() {
      if (!this.novoAviso.titulo || !this.novoAviso.mensagem || !this.novoAviso.materia || !this.novoAviso.turma || !this.novoAviso.dataEntrega) {
        alert('Preencha todos os campos obrigatórios!')
        return
      }
      
      const novo = {
        id: Date.now(),
        ...this.novoAviso,
        dataEntregaFormatada: this.formatarData(this.novoAviso.dataEntrega),
        dataCriacao: new Date().toLocaleDateString('pt-BR'),
        entregue: false
      }
      
      this.avisos.unshift(novo)
      localStorage.setItem('avisos', JSON.stringify(this.avisos))
      
      const alerts = JSON.parse(localStorage.getItem('alerts') || '[]')
      alerts.push({
        id: novo.id,
        titulo: novo.titulo,
        mensagem: novo.mensagem,
        dataEntrega: this.formatarData(novo.dataEntrega),
        materia: novo.materia,
        turma: novo.turma,
        semana: novo.semana
      })
      localStorage.setItem('alerts', JSON.stringify(alerts))
      
      this.resetarFormulario()
      alert('Aviso publicado com sucesso!')
    },
    
    formatarData(data) {
      if (!data) return ''
      const [ano, mes, dia] = data.split('-')
      return `${dia}/${mes}/${ano}`
    },
    
    resetarFormulario() {
      this.novoAviso = {
        titulo: '',
        mensagem: '',
        materia: '',
        turma: '',
        dataEntrega: '',
        semana: ''
      }
    },
    
    excluirAviso(id) {
      if (confirm('Tem certeza que deseja excluir este aviso?')) {
        this.avisos = this.avisos.filter(a => a.id !== id)
        localStorage.setItem('avisos', JSON.stringify(this.avisos))
        
        const alerts = JSON.parse(localStorage.getItem('alerts') || '[]')
        const novosAlerts = alerts.filter(a => a.id !== id)
        localStorage.setItem('alerts', JSON.stringify(novosAlerts))
        
        alert('Aviso excluído com sucesso!')
      }
    }
  }
}
</script>

<style scoped>
.avisos-container {
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

.criar-aviso {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 40px;
  border: 1px solid #e0e0e0;
}

.tema-escuro .criar-aviso {
  background: #2a2a2a;
  border-color: #404040;
}

.criar-aviso h3 {
  font-size: 20px;
  margin-bottom: 20px;
}

.form-aviso {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-weight: 500;
  font-size: 14px;
}

.form-group input, .form-group textarea, .form-group select {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.btn-criar {
  padding: 12px;
  background: #00488b;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  margin-top: 8px;
}

.btn-criar:hover {
  background: #0066cc;
}

.avisos-lista h3 {
  font-size: 20px;
  margin-bottom: 20px;
}

.aviso-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 16px;
  border: 1px solid #e0e0e0;
  transition: all 0.3s ease;
}

.tema-escuro .aviso-card {
  background: #2a2a2a;
  border-color: #404040;
}

.aviso-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.aviso-header h4 {
  font-size: 18px;
  font-weight: 600;
}

.aviso-data {
  font-size: 12px;
  color: #888;
}

.aviso-mensagem {
  font-size: 14px;
  line-height: 1.5;
  margin-bottom: 16px;
  color: #666;
}

.tema-escuro .aviso-mensagem {
  color: #aaa;
}

.aviso-detalhes {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  font-size: 12px;
  color: #888;
  margin-bottom: 16px;
}

.aviso-actions {
  display: flex;
  justify-content: flex-end;
}

.btn-excluir-aviso {
  padding: 6px 12px;
  background: #dc3545;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
}

.sem-avisos {
  text-align: center;
  padding: 40px;
  color: #888;
  background: #f5f5f5;
  border-radius: 12px;
}

.tema-escuro .sem-avisos {
  background: #2a2a2a;
}
</style>