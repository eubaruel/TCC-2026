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
      <FiltrosQuestoes v-if="abaAtiva !== 'cadastrar'" v-model="filtrosQuestoes" :disciplinas="disciplinas" :questoes="todasQuestoes" />
      <!-- Buscar Questões -->
      <div v-if="abaAtiva === 'buscar'" class="buscar-questoes">
        <p v-if="carregandoQuestoes" class="sem-resultados">Carregando questões...</p>
        
        <div class="resultados" v-if="resultados.length > 0">
          <div v-for="questao in resultados" :key="questao.id" class="questao-card">
            <div class="questao-header">
              <span class="disciplina">{{ questao.disciplina }}</span>
              <span class="tipo-questao objetiva">
                Objetiva
              </span>
              <span class="dificuldade" :class="getDificuldadeClass(questao.dificuldade)">
                {{ questao.dificuldade }}
              </span>
            </div>
            <div class="questao-metadata">
              <span v-if="questao.autor" class="autor">Autor: {{ questao.autor }}</span>
              <span class="data-criacao">Criada em: {{ questao.dataCriacao }}</span>
            </div>
            <!-- eslint-disable-next-line vue/no-v-html -->
            <div class="questao-texto texto-questao" v-html="sanitizar(questao.texto)"></div>
            <div class="alternativas texto-questao">
              <p><strong>Texto das Alternativas:</strong></p>
              <ul>
                <li v-for="alt in questao.alternativas" :key="alt.letra" 
                    :class="{ correta: alt.letra === questao.alternativaCorreta }">
                  <span class="letra-alternativa">{{ alt.letra }})</span>
                  <!-- eslint-disable-next-line vue/no-v-html -->
                  <span class="texto-alternativa" v-html="sanitizar(alt.texto)"></span>
                </li>
              </ul>
              <p class="correta-destaque">✅ Alternativa correta: {{ questao.alternativaCorreta }}</p>
            </div>
            <div class="questao-footer">
              <button v-if="isProfessor" @click="usarQuestao(questao)" class="btn-usar">
                Usar em Prova
              </button>
            </div>
          </div>
        </div>
        <div v-else-if="!carregandoQuestoes" class="sem-resultados">
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
            <label>Dificuldade *</label>
            <select v-model="novaQuestao.dificuldade">
              <option value="Muito Fácil">Muito Fácil</option>
              <option value="Fácil">Fácil</option>
              <option value="Médio">Médio</option>
              <option value="Difícil">Difícil</option>
              <option value="Muito Difícil">Muito Difícil</option>
            </select>
          </div>
          
          <div class="form-group">
            <label for="enunciado-questao">Enunciado da Questão *</label>
            <EditorQuill id="enunciado-questao" v-model="novaQuestao.texto" rotulo="Enunciado da questão" :limite-caracteres="limitesCaracteres.enunciado" obrigatorio placeholder="Digite o enunciado da questão..." />
          </div>
          
          <!-- Campo para questão objetiva -->
          <div class="objetiva-fields">
            <template v-for="(alt, idx) in novaQuestao.alternativas" :key="alt.letra">
              <h3 v-if="idx === 0" class="titulo-alternativas">Alternativa correta *</h3>
              <h3 v-else-if="idx === 1" class="titulo-alternativas">Demais alternativas *</h3>
              <div class="form-group alternativa-item">
                <label :for="`alternativa-${alt.letra}`" class="letra-alt">{{ alt.letra }})</label>
                <EditorQuill
                  :id="`alternativa-${alt.letra}`"
                  v-model="alt.texto"
                  :rotulo="`Alternativa ${alt.letra}${idx === 0 ? ' - correta' : ''}`"
                  :placeholder="`Texto da alternativa ${alt.letra}`"
                  :limite-caracteres="limitesCaracteres.alternativa"
                  compacto obrigatorio
                />
              </div>
            </template>
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
          Nenhuma questão sua encontrada com os filtros atuais.
        </div>
        <div v-else>
          <div v-for="questaoItem in minhasQuestoes" :key="questaoItem.id" class="questao-card minhas">
            <div class="questao-header">
              <span class="disciplina">{{ questaoItem.disciplina }}</span>
              <span class="tipo-questao objetiva">
                Objetiva
              </span>
              <span class="dificuldade" :class="getDificuldadeClass(questaoItem.dificuldade)">
                {{ questaoItem.dificuldade }}
              </span>
            </div>
            <div class="questao-metadata">
              <span v-if="questaoItem.autor" class="autor">Autor: {{ questaoItem.autor }}</span>
              <span class="data-criacao">Criada em: {{ questaoItem.dataCriacao }}</span>
            </div>
            <!-- eslint-disable-next-line vue/no-v-html -->
            <div class="questao-texto texto-questao" v-html="sanitizar(questaoItem.texto)"></div>
            <div class="alternativas texto-questao">
              <p><strong>Texto das Alternativas:</strong></p>
              <ul>
                <li v-for="alt in questaoItem.alternativas" :key="alt.letra" 
                    :class="{ correta: alt.letra === questaoItem.alternativaCorreta }">
                  <span class="letra-alternativa">{{ alt.letra }})</span>
                  <!-- eslint-disable-next-line vue/no-v-html -->
                  <span class="texto-alternativa" v-html="sanitizar(alt.texto)"></span>
                </li>
              </ul>
              <p class="correta-destaque">✅ Alternativa correta: {{ questaoItem.alternativaCorreta }}</p>
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
import { contarCaracteres, contarImagens, htmlVazio, sanitizar } from "@/utils/html";
import { LIMITE_IMAGENS } from "@/utils/imagensQuestao";
import EditorQuill from "@/components/EditorQuill.vue";
import FiltrosQuestoes from "@/components/FiltrosQuestoes.vue";
import { filtrarQuestoes, novosFiltrosQuestoes } from "@/utils/filtrosQuestoes";

const letras = ["A", "B", "C", "D", "E"];
const LIMITES_CARACTERES = { enunciado: 7000, alternativa: 2000 };
const novaQuestao = () => ({
  disciplina: "",
  assunto: "",
  autor: "",
  texto: "",
  alternativas: letras.map((letra) => ({ letra, texto: "" })),
  dificuldade: "Médio",
});

export default {
  name: "QuestoesView",
  components: { FiltrosQuestoes, EditorQuill },
  setup() {
    return { authStore: useAuthStore(), draftStore: useProvaDraftStore(), router: useRouter() };
  },
  data: () => ({
    abaAtiva: "buscar",
    filtrosQuestoes: novosFiltrosQuestoes(),
    carregandoQuestoes: true,
    todasQuestoes: [],
    disciplinas: [],
    carregandoDisciplinas: true,
    erroDisciplinas: "",
    novaQuestao: novaQuestao(),
    limitesCaracteres: LIMITES_CARACTERES,
    editandoId: null,
    erro: "",
  }),
  computed: {
    isProfessor() {
      return this.authStore.isProfessor;
    },
    resultados() {
      return filtrarQuestoes(this.todasQuestoes, this.filtrosQuestoes, this.disciplinas);
    },
    minhasQuestoes() {
      const minhas = this.todasQuestoes.filter((questao) => questao.professor?.nome === this.authStore.user?.nome);
      return filtrarQuestoes(minhas, this.filtrosQuestoes, this.disciplinas);
    },
  },
  async mounted() {
    await Promise.all([this.carregarDisciplinas(), this.carregarQuestoes()]);
  },
  methods: {
    sanitizar,
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
        texto: questao.enunciado,
        dataCriacao: "—",
        alternativas: questao.alternativas?.map((alternativa, index) => ({ ...alternativa, letra: letras[index] })) || [],
        alternativaCorreta: indiceCorreta >= 0 ? letras[indiceCorreta] : "",
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
      this.carregandoQuestoes = true;
      try {
        const questoes = (await listarQuestoes()).questoes;
        this.todasQuestoes = questoes.map(this.adaptarQuestao);
      } catch (error) {
        this.erro = error.details || error.message;
      } finally {
        this.carregandoQuestoes = false;
      }
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
        tipo_questao: "Objetiva",
        dificuldade: this.novaQuestao.dificuldade,
        enunciado: sanitizar(this.novaQuestao.texto),
      };
      if (this.novaQuestao.autor) payload.autor = this.novaQuestao.autor;
      payload.alternativas = this.novaQuestao.alternativas.map((alternativa) => sanitizar(alternativa.texto));
      payload.alternativa_correta = payload.alternativas[0];
      return payload;
    },
    async salvarQuestao() {
      try {
        if (!this.novaQuestao.disciplina?.trim()) {
          window.$modal.abrir({ titulo: "Atenção", mensagem: "Informe uma disciplina.", tipo: "alerta" });
          return;
        }
        if (htmlVazio(this.novaQuestao.texto)) {
          window.$modal.abrir({ titulo: "Atenção", mensagem: "Preencha o enunciado da questão.", tipo: "alerta" });
          return;
        }
        const alternativaVazia = this.novaQuestao.alternativas.find((alternativa) => htmlVazio(alternativa.texto));
        if (alternativaVazia) {
          window.$modal.abrir({ titulo: "Atenção", mensagem: `Preencha a alternativa ${alternativaVazia.letra}.`, tipo: "alerta" });
          return;
        }
        if (contarCaracteres(this.novaQuestao.texto) > LIMITES_CARACTERES.enunciado) {
          window.$modal.abrir({ titulo: "Atenção", mensagem: "O enunciado deve ter no máximo 7.000 caracteres de texto, incluindo espaços e pontuação.", tipo: "alerta" });
          return;
        }
        const alternativaLonga = this.novaQuestao.alternativas.find((alternativa) => contarCaracteres(alternativa.texto) > LIMITES_CARACTERES.alternativa);
        if (alternativaLonga) {
          window.$modal.abrir({ titulo: "Atenção", mensagem: `A alternativa ${alternativaLonga.letra} deve ter no máximo 2.000 caracteres de texto, incluindo espaços e pontuação.`, tipo: "alerta" });
          return;
        }
        const payload = this.payloadQuestao();
        const campos = [{ nome: "O enunciado", texto: payload.enunciado }, ...payload.alternativas.map((texto, i) => ({ nome: `A alternativa ${letras[i]}`, texto }))];
        const excessoImagens = campos.find(campo => contarImagens(campo.texto) > LIMITE_IMAGENS);
        if (excessoImagens) {
          window.$modal.abrir({ titulo: "Atenção", mensagem: `${excessoImagens.nome} deve ter no máximo 3 imagens. Exclua as imagens excedentes para salvar.`, tipo: "alerta" });
          return;
        }
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
      const correta = questao.alternativas.find((alternativa) => alternativa.letra === questao.alternativaCorreta);
      if (!correta) {
        window.$modal.abrir({ titulo: "Atenção", mensagem: "Esta questão está sem uma alternativa correta válida. Confira o cadastro antes de editar.", tipo: "alerta" });
        return;
      }
      const alternativas = [correta, ...questao.alternativas.filter((alternativa) => alternativa !== correta)];
      this.editandoId = questao._id;
      const referencias = (questao.disciplinasOriginais || []).map((item) => item.toLowerCase());
      const disciplinaCadastrada = this.disciplinas.find((disciplina) =>
        [disciplina.codigo_disciplina, disciplina.nome_disciplina]
          .map((item) => item.toLowerCase())
          .some((item) => referencias.includes(item)),
      );
      const disciplinaLegada = [...(questao.disciplinasOriginais || [])]
        .sort((primeira, segunda) => segunda.length - primeira.length)[0] || "";
      this.novaQuestao = { disciplina: disciplinaCadastrada?.nome_disciplina || disciplinaLegada, assunto: questao.assunto, autor: questao.autor, texto: questao.texto, alternativas: alternativas.map((alternativa, index) => ({ letra: letras[index], texto: alternativa.texto })), dificuldade: questao.dificuldade };
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

.questao-texto :deep(img),
.texto-alternativa :deep(img) {
  max-width: 100%;
  height: auto;
  display: block;
  margin: 6px 0;
}

.letra-alternativa {
  margin-right: 4px;
}

.texto-alternativa,
.texto-alternativa :deep(p) {
  display: inline;
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

.alternativa-item .editor-quill {
  flex: 1;
  width: 100%;
}

.titulo-alternativas { font-size: 16px; font-weight: 500; margin: 20px 0 8px; }
.alternativa-item label { margin-bottom: 0; }

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
  .questoes-tabs {
    flex-wrap: wrap;
  }

  .tab-btn {
    padding: 10px 12px;
  }

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
  
}
</style>
