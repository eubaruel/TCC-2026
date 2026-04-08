<template>
  <div class="questoes-container">
    <div class="page-header">
      <h2>Questões</h2>
      <div class="header-line"></div>
    </div>
    
    <div class="questoes-tabs">
      <button 
        @click="abaAtiva = 'buscar'" 
        class="tab-btn"
        :class="{ ativo: abaAtiva === 'buscar' }"
      >
        Buscar Questão
      </button>
      <button 
        @click="abaAtiva = 'cadastrar'" 
        class="tab-btn"
        :class="{ ativo: abaAtiva === 'cadastrar' }"
      >
        Cadastrar Questão
      </button>
      <button 
        @click="abaAtiva = 'minhas'" 
        class="tab-btn"
        :class="{ ativo: abaAtiva === 'minhas' }"
      >
        Minhas Questões
      </button>
    </div>
    
    <div class="tab-content">
      <!-- Buscar Questões -->
      <div v-if="abaAtiva === 'buscar'" class="buscar-questoes">
        <div class="search-box">
          <input 
            type="text" 
            v-model="busca" 
            placeholder="Buscar por disciplina, assunto, autor ou texto..."
            class="search-input"
          />
          <button @click="buscarQuestoes" class="btn-buscar">Buscar</button>
        </div>
        
        <div class="resultados" v-if="resultados.length > 0">
          <div v-for="questao in resultados" :key="questao.id" class="questao-card">
            <div class="questao-header">
              <span class="disciplina">{{ questao.disciplina }}</span>
              <span class="tipo-questao" :class="questao.tipo">
                {{ questao.tipo === 'objetiva' ? 'Objetiva' : 'Dissertativa' }}
              </span>
              <span class="dificuldade" :class="questao.dificuldade">
                {{ questao.dificuldade }}
              </span>
            </div>
            <div class="questao-metadata">
              <span v-if="questao.autor" class="autor">Autor: {{ questao.autor }}</span>
              <span class="data-criacao">Criada em: {{ questao.dataCriacao }}</span>
            </div>
            <p class="questao-texto">{{ questao.texto }}</p>
            <div v-if="questao.tipo === 'objetiva'" class="alternativas">
              <p><strong>Alternativas:</strong></p>
              <ul>
                <li v-for="alt in questao.alternativas" :key="alt.letra" 
                    :class="{ correta: alt.letra === 'A' }">
                  {{ alt.letra }}) {{ alt.texto }}
                </li>
              </ul>
            </div>
            <div v-else class="linhas-resposta">
              <p><strong>Linhas para resposta:</strong> {{ questao.linhasResposta }} linhas</p>
            </div>
            <div class="questao-footer">
              <button v-if="isProfessor" @click="usarQuestao(questao)" class="btn-usar">
                Usar em Prova
              </button>
            </div>
          </div>
        </div>
        <div v-else-if="buscou" class="sem-resultados">
          Nenhuma questão encontrada.
        </div>
      </div>
      
      <!-- Cadastrar Questão -->
      <div v-if="abaAtiva === 'cadastrar'" class="cadastrar-questao">
        <form @submit.prevent="salvarQuestao" class="form-questao">
          <div class="form-group">
            <label>Disciplina *</label>
            <select v-model="novaQuestao.disciplina" required>
              <option value="">Selecione a disciplina</option>
              <option v-for="disciplina in disciplinas" :key="disciplina" :value="disciplina">
                {{ disciplina }}
              </option>
            </select>
          </div>
          
          <div class="form-group">
            <label>Assunto *</label>
            <input type="text" v-model="novaQuestao.assunto" required />
          </div>
          
          <div class="form-group">
            <label>Autor (opcional)</label>
            <input 
              type="text" 
              v-model="novaQuestao.autor" 
              placeholder="Ex: ENEM, Unicamp, ITA, etc"
            />
            <small class="helper-text">
              Coloque a fonte da questão se não foi você que a criou. 
              Se foi você que escreveu, deixe em branco.
            </small>
          </div>
          
          <div class="form-group">
            <label>Tipo de Questão *</label>
            <div class="radio-group">
              <label class="radio-label">
                <input type="radio" value="objetiva" v-model="novaQuestao.tipo" />
                Objetiva
              </label>
              <label class="radio-label">
                <input type="radio" value="dissertativa" v-model="novaQuestao.tipo" />
                Dissertativa
              </label>
            </div>
          </div>
          
          <div class="form-group">
            <label>Enunciado da Questão *</label>
            <textarea v-model="novaQuestao.texto" rows="5" required></textarea>
          </div>
          
          <!-- Campo para questão objetiva -->
          <div v-if="novaQuestao.tipo === 'objetiva'" class="objetiva-fields">
            <div class="form-group">
              <label>Alternativa Correta *</label>
              <input 
                type="text" 
                v-model="novaQuestao.alternativaCorreta" 
                placeholder="Digite o texto da alternativa correta"
                required
              />
            </div>
            
            <div class="form-group">
              <label>Alternativas</label>
              <div v-for="(alt, idx) in novaQuestao.alternativasDistratores" :key="idx" class="alternativa-item">
                <input 
                  type="text" 
                  v-model="alt.texto" 
                  :placeholder="`Digite o texto da alternativa ${idx + 1}`" 
                  required
                />
              </div>
            </div>
          </div>
          
          <!-- Campo para questão dissertativa -->
          <div v-if="novaQuestao.tipo === 'dissertativa'" class="dissertativa-fields">
            <div class="form-group">
              <label>Quantidade de Linhas para Resposta *</label>
              <input 
                type="number" 
                v-model.number="novaQuestao.linhasResposta" 
                min="1" 
                max="100"
                step="1"
                required
                class="input-linhas"
              />
              <small class="helper-text">Digite um número inteiro entre 1 e 100 linhas</small>
            </div>
          </div>
          
          <div class="form-group">
            <label>Dificuldade *</label>
            <select v-model="novaQuestao.dificuldade">
              <option value="Muito Fácil">Muito Fácil</option>
              <option value="Fácil">Fácil</option>
              <option value="Médio">Médio</option>
              <option value="Difícil">Difícil</option>
              <option value="Muito Difícil">Muito Difícil</option>
            </select>
          </div>
          
          <button type="submit" class="btn-salvar-questao">Salvar Questão</button>
        </form>
      </div>
      
      <!-- Minhas Questões -->
      <div v-if="abaAtiva === 'minhas'" class="minhas-questoes">
        <div v-if="minhasQuestoes.length === 0" class="sem-questoes">
          Você ainda não cadastrou nenhuma questão.
        </div>
        <div v-else>
          <div v-for="questaoItem in minhasQuestoes" :key="questaoItem.id" class="questao-card minhas">
            <div class="questao-header">
              <span class="disciplina">{{ questaoItem.disciplina }}</span>
              <span class="tipo-questao" :class="questaoItem.tipo">
                {{ questaoItem.tipo === 'objetiva' ? 'Objetiva' : 'Dissertativa' }}
              </span>
              <span class="dificuldade" :class="questaoItem.dificuldade">
                {{ questaoItem.dificuldade }}
              </span>
            </div>
            <div class="questao-metadata">
              <span v-if="questaoItem.autor" class="autor">Autor: {{ questaoItem.autor }}</span>
              <span class="data-criacao">Criada em: {{ questaoItem.dataCriacao }}</span>
            </div>
            <p class="questao-texto">{{ questaoItem.texto }}</p>
            <div v-if="questaoItem.tipo === 'objetiva'" class="alternativas">
              <p><strong>Alternativas:</strong></p>
              <ul>
                <li v-for="alt in questaoItem.alternativas" :key="alt.letra" 
                    :class="{ correta: alt.letra === 'A' }">
                  {{ alt.letra }}) {{ alt.texto }}
                </li>
              </ul>
            </div>
            <div v-else class="linhas-resposta">
              <p><strong>Linhas para resposta:</strong> {{ questaoItem.linhasResposta }} linhas</p>
            </div>
            <div class="questao-actions">
              <button @click="editarQuestao(questaoItem)" class="btn-editar">Editar</button>
              <button @click="excluirQuestao(questaoItem.id)" class="btn-excluir">Excluir</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'QuestoesView',
  setup() {
    const authStore = useAuthStore()
    return { authStore }
  },
  data() {
    return {
      abaAtiva: 'buscar',
      busca: '',
      buscou: false,
      resultados: [],
      minhasQuestoes: [],
      // Lista de disciplinas definida pelo sistema
      disciplinas: [
        'Matemática FGB',
        'Matemática AP',
        'Português',
        'Literatura',
        'Inglês',
        'Projeto de Vida',
        'Eletiva',
        'Física FGB',
        'Física AP',
        'Química FGB',
        'Química AP',
        'Biologia FGB',
        'Biologia AP',
        'História',
        'Geografia',
        'Filosofia/Sociologia',
        'Arte',
        'Educação Física',
        'Redação'
      ],
      novaQuestao: {
        disciplina: '',
        assunto: '',
        autor: '',
        tipo: 'objetiva',
        texto: '',
        alternativaCorreta: '',
        alternativasDistratores: [
          { texto: '' },
          { texto: '' },
          { texto: '' },
          { texto: '' }
        ],
        linhasResposta: 10,
        dificuldade: 'Médio'
      }
    }
  },
  computed: {
    isProfessor() {
      return this.authStore.isProfessor
    }
  },
  mounted() {
    this.carregarMinhasQuestoes()
  },
  methods: {
    carregarMinhasQuestoes() {
      const salvas = localStorage.getItem('questoes')
      if (salvas) {
        const todas = JSON.parse(salvas)
        const usuario = this.authStore.user
        this.minhasQuestoes = todas.filter(q => q.autorId === usuario?.id)
      }
    },
    
    buscarQuestoes() {
      this.buscou = true
      const todas = JSON.parse(localStorage.getItem('questoes') || '[]')
      const termoBusca = this.busca.toLowerCase()
      this.resultados = todas.filter(q => 
        q.disciplina?.toLowerCase().includes(termoBusca) ||
        q.assunto?.toLowerCase().includes(termoBusca) ||
        q.autor?.toLowerCase().includes(termoBusca) ||
        q.texto?.toLowerCase().includes(termoBusca)
      )
    },
    
    validarAlternativasObjetiva() {
      if (!this.novaQuestao.alternativaCorreta.trim()) {
        alert('Preencha a alternativa correta!')
        return false
      }
      
      const alternativasVazias = this.novaQuestao.alternativasDistratores.filter(a => !a.texto.trim())
      if (alternativasVazias.length > 0) {
        alert('Preencha todas as alternativas!')
        return false
      }
      return true
    },
    
    validarLinhasResposta() {
      const linhas = this.novaQuestao.linhasResposta
      if (!Number.isInteger(linhas) || linhas < 1 || linhas > 100) {
        alert('A quantidade de linhas deve ser um número inteiro entre 1 e 100!')
        return false
      }
      return true
    },
    
    montarAlternativasCompletas() {
      const alternativas = [
        { letra: 'A', texto: this.novaQuestao.alternativaCorreta },
        { letra: 'B', texto: this.novaQuestao.alternativasDistratores[0].texto },
        { letra: 'C', texto: this.novaQuestao.alternativasDistratores[1].texto },
        { letra: 'D', texto: this.novaQuestao.alternativasDistratores[2].texto },
        { letra: 'E', texto: this.novaQuestao.alternativasDistratores[3].texto }
      ]
      return alternativas
    },
    
    salvarQuestao() {
      if (!this.novaQuestao.disciplina || !this.novaQuestao.assunto || !this.novaQuestao.texto) {
        alert('Preencha todos os campos obrigatórios!')
        return
      }
      
      if (this.novaQuestao.tipo === 'objetiva') {
        if (!this.validarAlternativasObjetiva()) {
          return
        }
      }
      
      if (this.novaQuestao.tipo === 'dissertativa') {
        if (!this.validarLinhasResposta()) {
          return
        }
      }
      
      const nova = {
        id: Date.now(),
        disciplina: this.novaQuestao.disciplina,
        assunto: this.novaQuestao.assunto,
        autor: this.novaQuestao.autor,
        tipo: this.novaQuestao.tipo,
        texto: this.novaQuestao.texto,
        dificuldade: this.novaQuestao.dificuldade,
        autorId: this.authStore.user?.id,
        autorNome: this.authStore.user?.nome,
        dataCriacao: new Date().toLocaleDateString('pt-BR'),
        alternativas: this.novaQuestao.tipo === 'objetiva' 
          ? this.montarAlternativasCompletas()
          : [],
        linhasResposta: this.novaQuestao.tipo === 'dissertativa' 
          ? this.novaQuestao.linhasResposta 
          : null
      }
      
      const todas = JSON.parse(localStorage.getItem('questoes') || '[]')
      todas.push(nova)
      localStorage.setItem('questoes', JSON.stringify(todas))
      
      alert('Questão salva com sucesso!')
      this.carregarMinhasQuestoes()
      this.resetarFormulario()
      this.abaAtiva = 'minhas'
    },
    
    resetarFormulario() {
      this.novaQuestao = {
        disciplina: '',
        assunto: '',
        autor: '',
        tipo: 'objetiva',
        texto: '',
        alternativaCorreta: '',
        alternativasDistratores: [
          { texto: '' },
          { texto: '' },
          { texto: '' },
          { texto: '' }
        ],
        linhasResposta: 10,
        dificuldade: 'Médio'
      }
    },
    
    editarQuestao(questaoItem) {
      alert(`Editar questão: ${questaoItem.texto.substring(0, 50)}...`)
    },
    
    excluirQuestao(id) {
      if (confirm('Tem certeza que deseja excluir esta questão?')) {
        const todas = JSON.parse(localStorage.getItem('questoes') || '[]')
        const filtradas = todas.filter(q => q.id !== id)
        localStorage.setItem('questoes', JSON.stringify(filtradas))
        this.carregarMinhasQuestoes()
        alert('Questão excluída com sucesso!')
      }
    },
    
    usarQuestao(questaoItem) {
      alert(`Questão "${questaoItem.texto.substring(0, 50)}..." adicionada à prova!`)
    }
  }
}
</script>

<style scoped>
.questoes-container {
  max-width: 1200px;
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

.questoes-tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 30px;
  border-bottom: 1px solid #e0e0e0;
}

.tab-btn {
  padding: 12px 24px;
  background: transparent;
  border: none;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  color: #666;
  transition: all 0.3s ease;
}

.tab-btn.ativo {
  color: #00488b;
  border-bottom: 2px solid #00488b;
}

.tema-escuro .tab-btn {
  color: #aaa;
}

.tema-escuro .tab-btn.ativo {
  color: #0066cc;
  border-bottom-color: #0066cc;
}

.search-box {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
}

.search-input {
  flex: 1;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 16px;
}

.btn-buscar {
  padding: 12px 24px;
  background: #00488b;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
}

.questao-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 16px;
  border: 1px solid #e0e0e0;
  transition: all 0.3s ease;
}

.tema-escuro .questao-card {
  background: #2a2a2a;
  border-color: #404040;
}

.questao-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.questao-header {
  display: flex;
  gap: 12px;
  margin-bottom: 8px;
  flex-wrap: wrap;
}

.questao-metadata {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
  font-size: 12px;
  color: #888;
  flex-wrap: wrap;
}

.autor {
  background: #e9ecef;
  padding: 2px 8px;
  border-radius: 12px;
  color: #495057;
}

.tema-escuro .autor {
  background: #404040;
  color: #aaa;
}

.disciplina {
  background: #00488b20;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  color: #00488b;
}

.tipo-questao {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
}

.tipo-questao.objetiva {
  background: #17a2b820;
  color: #17a2b8;
}

.tipo-questao.dissertativa {
  background: #6c757d20;
  color: #6c757d;
}

.dificuldade {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
}

.dificuldade.Fácil {
  background: #28a74520;
  color: #28a745;
}

.dificuldade.Médio {
  background: #ffc10720;
  color: #ffc107;
}

.dificuldade.Difícil {
  background: #dc354520;
  color: #dc3545;
}

.questao-texto {
  font-size: 14px;
  line-height: 1.5;
  margin-bottom: 16px;
}

.alternativas ul {
  margin-top: 8px;
  padding-left: 20px;
}

.alternativas li {
  font-size: 13px;
  margin-bottom: 4px;
}

.alternativas li.correta {
  color: #28a745;
  font-weight: 500;
}

.linhas-resposta {
  margin-top: 8px;
  font-size: 13px;
  color: #666;
}

.questao-footer {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  font-size: 12px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #eee;
}

.btn-usar, .btn-editar, .btn-excluir {
  padding: 6px 12px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.3s ease;
}

.btn-usar {
  background: #00488b;
  color: white;
}

.btn-editar {
  background: #ffc107;
  color: #333;
}

.btn-excluir {
  background: #dc3545;
  color: white;
}

.questao-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #eee;
}

.form-questao {
  max-width: 800px;
  margin: 0 auto;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
}

.form-group input, .form-group textarea, .form-group select {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
}

.form-group select {
  cursor: pointer;
  background-color: white;
}

.tema-escuro .form-group select {
  background-color: #2a2a2a;
  border-color: #404040;
  color: #e5e5e5;
}

.input-linhas {
  width: 200px;
}

.helper-text {
  display: block;
  margin-top: 5px;
  font-size: 12px;
  color: #888;
}

.radio-group {
  display: flex;
  gap: 30px;
}

.radio-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.radio-label input {
  width: auto;
  margin: 0;
}

.alternativa-item {
  margin-bottom: 12px;
}

.alternativa-item input[type="text"] {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
}

.btn-salvar-questao {
  width: 100%;
  padding: 14px;
  background: #28a745;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
}

.sem-resultados, .sem-questoes {
  text-align: center;
  padding: 40px;
  color: #888;
}

@media (max-width: 768px) {
  .questao-header {
    flex-direction: column;
    gap: 8px;
  }
  
  .questao-metadata {
    flex-direction: column;
    gap: 8px;
  }
  
  .radio-group {
    flex-direction: column;
    gap: 10px;
  }
  
  .input-linhas {
    width: 100%;
  }
}
</style>