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
              <span class="dificuldade" :class="getDificuldadeClass(questao.dificuldade)">
                {{ questao.dificuldade }}
              </span>
            </div>
            <div class="questao-metadata">
              <span v-if="questao.autor" class="autor">Autor: {{ questao.autor }}</span>
              <span class="data-criacao">Criada em: {{ questao.dataCriacao }}</span>
            </div>
            <p class="questao-texto">{{ questao.texto }}</p>
            <div v-if="questao.tipo === 'objetiva'" class="alternativas">
              <p><strong>Texto das Alternativas:</strong></p>
              <ul>
                <li v-for="alt in questao.alternativas" :key="alt.letra" 
                    :class="{ correta: alt.letra === questao.alternativaCorreta }">
                  {{ alt.letra }}) {{ alt.texto }}
                </li>
              </ul>
              <p class="correta-destaque">✅ Alternativa correta: {{ questao.alternativaCorreta }}</p>
            </div>
            <div v-else class="linhas-resposta">
              <p><strong>Linhas para resposta:</strong> {{ questao.linhasResposta_json }} linhas</p>
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
            <select
              v-if="!carregandoDisciplinas && disciplinas.length"
              v-model="novaQuestao.disciplina"
              required
            >
              <option value="">Selecione a disciplina</option>
              <option
                v-for="disc in disciplinas"
                :key="disc.codigo_disciplina"
                :value="disc.nome_disciplina"
              >
                {{ disc.nome_disciplina }} ({{ disc.codigo_disciplina }})
              </option>
            </select>
            <input
              v-else-if="!carregandoDisciplinas"
              v-model="novaQuestao.disciplina"
              type="text"
              required
              minlength="2"
              placeholder="Digite o nome da disciplina"
            />
            <p v-else class="estado-disciplina">Carregando disciplinas...</p>
            <small v-if="erroDisciplinas" class="mensagem-erro">
              {{ erroDisciplinas }} Você ainda pode informar a disciplina manualmente.
            </small>
            <small v-else-if="!carregandoDisciplinas && !disciplinas.length" class="helper-text">
              Nenhuma disciplina cadastrada foi encontrada. Informe a disciplina manualmente.
            </small>
            <button
              v-if="erroDisciplinas"
              type="button"
              class="btn-recarregar"
              @click="carregarDisciplinas"
            >
              Tentar carregar novamente
            </button>
          </div>
          
          <div class="form-group">
            <label>Assunto *</label>
            <input type="text" v-model="novaQuestao.assunto" required placeholder="Ex: Equações do 2º grau" />
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
            <textarea v-model="novaQuestao.texto" rows="5" required placeholder="Digite o enunciado da questão..."></textarea>
          </div>
          
          <!-- Campo para questão objetiva -->
          <div v-if="novaQuestao.tipo === 'objetiva'" class="objetiva-fields">
            <div class="form-group">
              <label>Texto das Alternativas</label>
              <div v-for="(alt, idx) in novaQuestao.alternativas" :key="idx" class="alternativa-item">
                <span class="letra-alt">{{ alt.letra }})</span>
                <input 
                  type="text" 
                  v-model="alt.texto" 
                  :placeholder="`Texto da alternativa ${alt.letra}`" 
                  required
                />
              </div>
            </div>

            <div class="form-group">
              <label>Alternativa Correta *</label>
              <select v-model="novaQuestao.alternativaCorreta" required class="select-correta">
                <option value="A">Alternativa A</option>
                <option value="B">Alternativa B</option>
                <option value="C">Alternativa C</option>
                <option value="D">Alternativa D</option>
                <option value="E">Alternativa E</option>
              </select>
              <small class="helper-text">Selecione qual alternativa é a correta</small>
            </div>
          </div>
          
          <!-- Campo para questão dissertativa -->
          <div v-if="novaQuestao.tipo === 'dissertativa'" class="dissertativa-fields">
            <div class="form-group">
              <label>Quantidade de Linhas para Resposta_json *</label>
              <input 
                type="number" 
                v-model.number="novaQuestao.linhasResposta_json" 
                min="1" 
                max="10"
                step="1"
                required
                class="input-linhas"
              />
              <small class="helper-text">Digite um número inteiro entre 1 e 10 linhas</small>
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
          
          <button
            type="submit"
            class="btn-salvar-questao"
            :disabled="carregandoDisciplinas"
          >
            {{ carregandoDisciplinas ? "Carregando..." : "Salvar Questão" }}
          </button>
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
              <span class="dificuldade" :class="getDificuldadeClass(questaoItem.dificuldade)">
                {{ questaoItem.dificuldade }}
              </span>
            </div>
            <div class="questao-metadata">
              <span v-if="questaoItem.autor" class="autor">Autor: {{ questaoItem.autor }}</span>
              <span class="data-criacao">Criada em: {{ questaoItem.dataCriacao }}</span>
            </div>
            <p class="questao-texto">{{ questaoItem.texto }}</p>
            <div v-if="questaoItem.tipo === 'objetiva'" class="alternativas">
              <p><strong>Texto das Alternativas:</strong></p>
              <ul>
                <li v-for="alt in questaoItem.alternativas" :key="alt.letra" 
                    :class="{ correta: alt.letra === questaoItem.alternativaCorreta }">
                  {{ alt.letra }}) {{ alt.texto }}
                </li>
              </ul>
              <p class="correta-destaque">✅ Alternativa correta: {{ questaoItem.alternativaCorreta }}</p>
            </div>
            <div v-else class="linhas-resposta">
              <p><strong>Linhas para resposta:</strong> {{ questaoItem.linhasResposta_json }} linhas</p>
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
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import { useProvaDraftStore } from "@/stores/provaDraft";
import { listarDisciplinas } from "@/services/disciplinas";
import { atualizarQuestao, criarQuestao, excluirQuestao, listarQuestoes } from "@/services/questoes";

const letras = ["A", "B", "C", "D", "E"];
const novaQuestao = () => ({
  disciplina: "",
  assunto: "",
  autor: "",
  tipo: "objetiva",
  texto: "",
  alternativas: letras.map((letra) => ({ letra, texto: "" })),
  alternativaCorreta: "A",
  linhasResposta_json: 10,
  dificuldade: "Médio",
});

export default {
  name: "QuestoesView",
  setup() {
    return { authStore: useAuthStore(), draftStore: useProvaDraftStore(), router: useRouter() };
  },
  data: () => ({
    abaAtiva: "buscar",
    busca: "",
    buscou: false,
    resultados: [],
    minhasQuestoes: [],
    todasQuestoes: [],
    disciplinas: [],
    carregandoDisciplinas: true,
    erroDisciplinas: "",
    novaQuestao: novaQuestao(),
    editandoId: null,
    erro: "",
  }),
  computed: {
    isProfessor() {
      return this.authStore.isProfessor;
    },
  },
  async mounted() {
    await Promise.all([this.carregarDisciplinas(), this.carregarQuestoes()]);
  },
  methods: {
    getDificuldadeClass(dificuldade) {
      return { "Muito Fácil": "muito-facil", "Fácil": "facil", "Médio": "medio", "Difícil": "dificil", "Muito Difícil": "muito-dificil" }[dificuldade] || "medio";
    },
    adaptarQuestao(questao) {
      const indiceCorreta = questao.alternativas?.findIndex((alternativa) => alternativa.id === questao.alternativa_correta) ?? -1;
      const disciplinasOriginais = Array.isArray(questao.disciplina) ? [...questao.disciplina] : [];
      return {
        ...questao,
        id: questao._id,
        disciplina: disciplinasOriginais.join(", "),
        disciplinasOriginais,
        tipo: questao.tipo_questao.toLowerCase(),
        texto: questao.enunciado,
        dataCriacao: "—",
        alternativas: questao.alternativas?.map((alternativa, index) => ({ ...alternativa, letra: letras[index] })) || [],
        alternativaCorreta: indiceCorreta >= 0 ? letras[indiceCorreta] : "",
        linhasResposta_json: questao.numero_linhas,
      };
    },
    async carregarDisciplinas() {
      this.carregandoDisciplinas = true;
      this.erroDisciplinas = "";
      try {
        const resposta = await listarDisciplinas();
        this.disciplinas = Array.isArray(resposta?.disciplinas)
          ? resposta.disciplinas.filter(
              (disciplina) => disciplina?.codigo_disciplina && disciplina?.nome_disciplina,
            )
          : [];
      } catch (error) {
        this.disciplinas = [];
        this.erroDisciplinas = error.details || error.message;
      } finally {
        this.carregandoDisciplinas = false;
      }
    },
    async carregarQuestoes() {
      try {
        const questoes = (await listarQuestoes()).questoes;
        this.todasQuestoes = questoes.map(this.adaptarQuestao);
        this.resultados = [...this.todasQuestoes];
        this.minhasQuestoes = this.todasQuestoes.filter((questao) => questao.professor?.nome === this.authStore.user?.nome);
      } catch (error) {
        this.erro = error.details || error.message;
      }
    },
    buscarQuestoes() {
      this.buscou = true;
      const termo = this.busca.toLowerCase();
      this.resultados = this.todasQuestoes.filter((questao) => [questao.disciplina, questao.assunto, questao.autor, questao.texto].some((campo) => campo?.toLowerCase().includes(termo)));
    },
    payloadQuestao() {
      const disciplinaInformada = this.novaQuestao.disciplina.trim();
      const disciplinaCadastrada = this.disciplinas.find(
        (disciplina) => disciplina.nome_disciplina === disciplinaInformada,
      );
      const referenciasDisciplina = disciplinaCadastrada
        ? [disciplinaCadastrada.codigo_disciplina, disciplinaCadastrada.nome_disciplina]
        : [disciplinaInformada];
      const payload = {
        professor: { nome: this.authStore.user.nome },
        assunto: this.novaQuestao.assunto,
        disciplina: [...new Set(referenciasDisciplina.filter(Boolean))],
        tipo_questao: this.novaQuestao.tipo === "objetiva" ? "Objetiva" : "Dissertativa",
        dificuldade: this.novaQuestao.dificuldade,
        enunciado: this.novaQuestao.texto,
      };
      if (this.novaQuestao.autor) payload.autor = this.novaQuestao.autor;
      if (this.novaQuestao.tipo === "objetiva") {
        payload.alternativas = this.novaQuestao.alternativas.map((alternativa) => alternativa.texto);
        payload.alternativa_correta = this.novaQuestao.alternativas.find((alternativa) => alternativa.letra === this.novaQuestao.alternativaCorreta)?.texto;
      } else {
        payload.numero_linhas = Number(this.novaQuestao.linhasResposta_json);
      }
      return payload;
    },
    async salvarQuestao() {
      try {
        if (!this.novaQuestao.disciplina?.trim()) {
          window.$modal.abrir({ titulo: "Atenção", mensagem: "Informe uma disciplina.", tipo: "alerta" });
          return;
        }
        const payload = this.payloadQuestao();
        if (this.editandoId) await atualizarQuestao(this.editandoId, payload);
        else await criarQuestao(payload);
        await this.carregarQuestoes();
        this.resetarFormulario();
        this.abaAtiva = "minhas";
        window.$modal.abrir({ titulo: "Sucesso", mensagem: "Questão salva com sucesso.", tipo: "alerta" });
      } catch (error) {
        window.$modal.abrir({ titulo: "Erro", mensagem: error.details || error.message, tipo: "alerta" });
      }
    },
    resetarFormulario() {
      this.novaQuestao = novaQuestao();
      this.editandoId = null;
    },
    editarQuestao(questao) {
      this.editandoId = questao._id;
      const referencias = (questao.disciplinasOriginais || []).map((item) => item.toLowerCase());
      const disciplinaCadastrada = this.disciplinas.find((disciplina) =>
        [disciplina.codigo_disciplina, disciplina.nome_disciplina]
          .map((item) => item.toLowerCase())
          .some((item) => referencias.includes(item)),
      );
      const disciplinaLegada = [...(questao.disciplinasOriginais || [])]
        .sort((primeira, segunda) => segunda.length - primeira.length)[0] || "";
      this.novaQuestao = { disciplina: disciplinaCadastrada?.nome_disciplina || disciplinaLegada, assunto: questao.assunto, autor: questao.autor, tipo: questao.tipo, texto: questao.texto, alternativas: questao.alternativas.map((alternativa) => ({ letra: alternativa.letra, texto: alternativa.texto })), alternativaCorreta: questao.alternativaCorreta, linhasResposta_json: questao.linhasResposta_json || 10, dificuldade: questao.dificuldade };
      this.abaAtiva = "cadastrar";
    },
    excluirQuestao(id) {
      window.$modal.abrir({ titulo: "Excluir questão", mensagem: "Deseja excluir esta questão?", tipo: "confirmacao", onConfirm: async () => { try { await excluirQuestao(id); await this.carregarQuestoes(); } catch (error) { this.erro = error.details || error.message; } } });
    },
    usarQuestao(questao) {
      this.draftStore.adicionar(questao);
      this.router.push("/provas");
    },
  },
};
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

/* Estilos de dificuldade */
.dificuldade {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
}

.dificuldade.muito-facil {
  background: #28a74520;
  color: #28a745;
}

.dificuldade.facil {
  background: #28a74520;
  color: #28a745;
}

.dificuldade.medio {
  background: #ffc10720;
  color: #ffc107;
}

.dificuldade.dificil {
  background: #dc354520;
  color: #dc3545;
}

.dificuldade.muito-dificil {
  background: #8b000020;
  color: #8b0000;
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

.correta-destaque {
  margin-top: 10px;
  font-size: 13px;
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

.form-group input, 
.form-group textarea, 
.form-group select {
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
  background-color: #1a1a1a;
  border-color: #404040;
  color: #e5e5e5;
}

.helper-text {
  display: block;
  margin-top: 5px;
  font-size: 11px;
  color: #888;
}

.estado-disciplina,
.mensagem-erro {
  display: block;
  margin: 6px 0 0;
  font-size: 12px;
}

.estado-disciplina {
  color: #666;
}

.mensagem-erro {
  color: #b42318;
}

.btn-recarregar {
  margin-top: 8px;
  padding: 7px 12px;
  border: 1px solid #00488b;
  border-radius: 6px;
  background: transparent;
  color: #00488b;
  cursor: pointer;
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
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
  align-items: center;
}

.letra-alt {
  width: 35px;
  font-weight: 600;
  color: #666;
}

.alternativa-item input[type="text"] {
  flex: 1;
}

.select-correta {
  width: 200px;
  cursor: pointer;
}

.input-linhas {
  width: 200px;
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

.btn-salvar-questao:hover:not(:disabled) {
  background: #218838;
}

.btn-salvar-questao:disabled {
  background: #8a9a8e;
  cursor: wait;
  opacity: 0.75;
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
  
  .alternativa-item {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .letra-alt {
    width: auto;
  }
  
  .select-correta, 
  .input-linhas {
    width: 100%;
  }
}
</style>
