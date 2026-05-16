<template>
  <div class="avisos-container">
    <div class="page-header">
      <h2>{{ isProcessoPedagogico ? 'Gerenciar Avisos' : 'Avisos' }}</h2>
      <div class="header-line"></div>
    </div>

    <!-- Para Processo Pedagógico: Formulário de criação -->
    <div v-if="isProcessoPedagogico" class="criar-aviso">
      <h3>Criar Novo Aviso</h3>
      <form @submit.prevent="criarAviso" class="form-aviso">
        <div class="form-group">
          <label>Título do Aviso *</label>
          <input type="text" v-model="novoAviso.titulo" required placeholder="Ex: Alteração de data da prova" />
        </div>
        
        <div class="form-group">
          <label>Mensagem *</label>
          <textarea v-model="novoAviso.mensagem" rows="4" required placeholder="Digite o conteúdo do aviso..."></textarea>
        </div>
        
        <div class="form-group">
          <label>Para qual turma? (opcional)</label>
          <select v-model="novoAviso.turma">
            <option value="">Todas as turmas</option>
            <option v-for="turma in turmas" :key="turma" :value="turma">
              {{ turma }}
            </option>
          </select>
        </div>
        
        <button type="submit" class="btn-criar">Publicar Aviso</button>
      </form>
    </div>

    <!-- Lista de Avisos (para ambos os tipos) -->
    <div class="avisos-lista">
      <h3>Avisos Publicados</h3>
      <div v-if="avisos.length === 0" class="sem-avisos">
        Nenhum aviso publicado ainda.
      </div>
      <div v-else>
        <div v-for="aviso in avisos" :key="aviso.id" class="aviso-card" :class="{ lido: aviso.lido }">
          <div class="aviso-header">
            <h4>{{ aviso.titulo }}</h4>
            <span class="aviso-data">{{ aviso.dataCriacao }}</span>
            <span v-if="aviso.turma" class="aviso-turma">🎯 {{ aviso.turma }}</span>
          </div>
          <p class="aviso-mensagem">{{ aviso.mensagem }}</p>
          
          <!-- Botão Marcar como Lido (apenas para Professor) -->
          <div class="aviso-actions" v-if="isProfessor && !aviso.lido">
            <button @click="marcarComoLido(aviso.id)" class="btn-marcar-lido">
              ✓ Marcar como Lido
            </button>
          </div>
          
          <!-- Status Lido (para Processo Pedagógico) -->
          <div class="aviso-status" v-if="isProcessoPedagogico">
            <span class="status-lido" v-if="aviso.lido">✓ Lido por {{ aviso.lidoPor?.length || 0 }} professor(es)</span>
            <span class="status-nao-lido" v-else>⏳ Aguardando leitura</span>
          </div>
          
          <!-- Botão Excluir (apenas para Processo Pedagógico) -->
          <div class="aviso-actions" v-if="isProcessoPedagogico">
            <button @click="excluirAviso(aviso.id)" class="btn-excluir-aviso">Excluir Aviso</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'AvisosView',
  setup() {
    const authStore = useAuthStore()
    return { authStore }
  },
  data() {
    return {
      avisos: [],
      turmas: [],
      novoAviso: {
        titulo: '',
        mensagem: '',
        turma: ''
      }
    }
  },
  computed: {
    isProfessor() {
      return this.authStore.isProfessor
    },
    isProcessoPedagogico() {
      return this.authStore.isProcessoPedagogico
    }
  },
  mounted() {
    this.carregarAvisos()
    this.gerarTurmas()
  },
  methods: {
    gerarTurmas() {
      const turmasLista = []
      const primeiroAno = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N']
      for (const letra of primeiroAno) {
        turmasLista.push(`1° Ano ${letra}`)
      }
      const segundoAno = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L']
      for (const letra of segundoAno) {
        turmasLista.push(`2° Ano ${letra}`)
      }
      const terceiroAno = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L']
      for (const letra of terceiroAno) {
        turmasLista.push(`3° Ano ${letra}`)
      }
      this.turmas = turmasLista
    },
    
    carregarAvisos() {
      const salvos = localStorage.getItem('avisos')
      if (salvos) {
        this.avisos = JSON.parse(salvos)
      } else {
        this.avisos = []
        localStorage.setItem('avisos', JSON.stringify(this.avisos))
      }
    },
    
    criarAviso() {
      if (!this.novoAviso.titulo || !this.novoAviso.mensagem) {
        window.$modal.abrir({
          titulo: "Atenção",
          mensagem: "Preencha título e mensagem!",
          tipo: "alerta"
        });
        return
      }
      
      const novo = {
        id: Date.now(),
        titulo: this.novoAviso.titulo,
        mensagem: this.novoAviso.mensagem,
        turma: this.novoAviso.turma || null,
        dataCriacao: new Date().toLocaleDateString('pt-BR'),
        lido: false,
        lidoPor: []
      }
      
      this.avisos.unshift(novo)
      localStorage.setItem('avisos', JSON.stringify(this.avisos))
      
      this.resetarFormulario()
      
      window.$modal.abrir({
        titulo: "Sucesso",
        mensagem: "Aviso publicado com sucesso!",
        tipo: "alerta"
      });
    },
    
    marcarComoLido(id) {
      const index = this.avisos.findIndex(a => a.id === id)
      if (index !== -1) {
        const professorNome = this.authStore.user?.nome || 'Professor'
        
        if (!this.avisos[index].lidoPor) {
          this.avisos[index].lidoPor = []
        }
        
        if (!this.avisos[index].lidoPor.includes(professorNome)) {
          this.avisos[index].lidoPor.push(professorNome)
        }
        
        this.avisos[index].lido = true
        localStorage.setItem('avisos', JSON.stringify(this.avisos))
        
        window.$modal.abrir({
          titulo: "Sucesso",
          mensagem: "Aviso marcado como lido!",
          tipo: "alerta"
        });
      }
    },
    
    resetarFormulario() {
      this.novoAviso = {
        titulo: '',
        mensagem: '',
        turma: ''
      }
    },
    
    excluirAviso(id) {
      window.$modal.abrir({
        titulo: "Confirmar Exclusão",
        mensagem: "Tem certeza que deseja excluir este aviso?",
        tipo: "confirmacao",
        onConfirm: () => {
          this.avisos = this.avisos.filter(a => a.id !== id)
          localStorage.setItem('avisos', JSON.stringify(this.avisos))
          window.$modal.abrir({
            titulo: "Sucesso",
            mensagem: "Aviso excluído com sucesso!",
            tipo: "alerta"
          });
        }
      });
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

.aviso-card.lido {
  opacity: 0.7;
  background: #f5f5f5;
}

.tema-escuro .aviso-card {
  background: #2a2a2a;
  border-color: #404040;
}

.tema-escuro .aviso-card.lido {
  background: #1a1a1a;
}

.aviso-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.aviso-header h4 {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
  flex: 1;
}

.aviso-data {
  font-size: 12px;
  color: #888;
}

.aviso-turma {
  font-size: 12px;
  background: #e9ecef;
  padding: 2px 8px;
  border-radius: 12px;
  color: #495057;
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

.aviso-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.aviso-status {
  margin-top: 12px;
  font-size: 12px;
}

.status-lido {
  color: #28a745;
}

.status-nao-lido {
  color: #ffc107;
}

.btn-marcar-lido {
  padding: 6px 12px;
  background: #28a745;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
}

.btn-marcar-lido:hover {
  background: #218838;
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

.btn-excluir-aviso:hover {
  background: #c82333;
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

@media (max-width: 768px) {
  .aviso-header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>