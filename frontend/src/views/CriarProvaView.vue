<template>
  <div class="criar-prova" :class="temaAtual">
    <!-- Barra superior -->
    <header class="barra-superior">
      <button type="button" class="btn-voltar" title="Voltar" @click="voltar">
        <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M15 18L9 12L15 6" stroke-linecap="round" stroke-linejoin="round" />
        </svg>
      </button>
      <h1>{{ tituloTela }}</h1>
      <span v-if="draft.sujo" class="indicador-alteracoes">Alterações não salvas</span>
      <button type="button" class="btn-salvar" :disabled="salvando || carregando" @click="salvar()">
        {{ salvando ? "Salvando..." : "💾 Salvar" }}
      </button>
    </header>

    <div class="area-trabalho">
      <!-- Metade esquerda: campos de preenchimento -->
      <section class="painel painel-campos">
        <p v-if="carregando" class="mensagem-info">Carregando dados da prova...</p>
        <template v-else>
          <p v-if="erroCarregamento" class="mensagem-erro">
            {{ erroCarregamento }}
            <button type="button" class="btn-secundario" @click="carregar">Tentar novamente</button>
          </p>

          <div class="bloco">
            <h3>Dados da prova</h3>
            <div class="campo">
              <label for="turmas">Turma(s)</label>
              <textarea
                id="turmas"
                v-model="metadados.turmasTexto"
                rows="2"
                placeholder="Uma turma por linha, por exemplo:&#10;Turma 2026 A"
              ></textarea>
            </div>

            <div class="campo">
              <label for="disciplina">Disciplina</label>
              <select v-if="!modoDisciplinaManual" id="disciplina" :value="metadados.codigo_disciplina" @change="selecionarDisciplina($event.target.value)">
                <option value="">Selecione</option>
                <option v-for="disciplina in disciplinas" :key="disciplina.codigo_disciplina" :value="disciplina.codigo_disciplina">
                  {{ disciplina.nome_disciplina }} ({{ disciplina.codigo_disciplina }})
                </option>
              </select>
              <div v-else class="disciplina-manual">
                <input v-model.trim="metadados.codigo_disciplina" placeholder="Código, ex.: MAT" />
                <input v-model.trim="metadados.nome_disciplina" placeholder="Nome, ex.: Matemática" />
              </div>
              <button v-if="disciplinas.length" type="button" class="btn-link" @click="alternarModoDisciplina">
                {{ modoDisciplinaManual ? "Selecionar disciplina cadastrada" : "Informar disciplina manualmente" }}
              </button>
            </div>

            <div class="grade-campos">
              <div class="campo">
                <label for="tipo">Tipo</label>
                <select id="tipo" v-model="metadados.tipo">
                  <option>Objetiva</option>
                  <option>Dissertativa</option>
                </select>
              </div>
              <div class="campo">
                <label for="serie">Série</label>
                <input id="serie" v-model.number="metadados.serie" type="number" min="1" />
              </div>
              <div class="campo">
                <label for="bimestre">Bimestre</label>
                <input id="bimestre" v-model.trim="metadados.bimestre" placeholder="1° bimestre" />
              </div>
              <div class="campo">
                <label for="dataAplicacao">Data de aplicação</label>
                <input id="dataAplicacao" v-model="metadados.data_de_aplicacao" type="date" />
              </div>
              <div v-if="draft.provaId" class="campo">
                <label for="status">Status</label>
                <select id="status" v-model="metadados.status">
                  <option v-for="status in opcoesStatus" :key="status">{{ status }}</option>
                </select>
              </div>
            </div>
          </div>

          <div class="bloco">
            <h3>Questões ({{ questoes.length }})</h3>
            <QuestaoEditor
              v-for="(questao, index) in questoes"
              :key="questao._idLocal"
              :questao="questao"
              :numero="index + 1"
              :tipo="metadados.tipo"
              :primeira="index === 0"
              :ultima="index === questoes.length - 1"
              @atualizar="Object.assign(questao, $event)"
              @mover="moverQuestao(index, $event)"
              @remover="removerQuestao(index)"
            />

            <div class="acoes-questoes">
              <button type="button" class="btn-primario" @click="adicionarQuestao">+ Nova questão</button>
              <div class="importar-banco">
                <select v-model="questaoBancoSelecionada" :disabled="!questoesBancoCompativeis.length">
                  <option value="">
                    {{ questoesBancoCompativeis.length ? "Importar questão do banco..." : "Nenhuma questão compatível no banco" }}
                  </option>
                  <option v-for="questao in questoesBancoCompativeis" :key="questao._id" :value="questao._id">
                    {{ resumo(questao.enunciado) }}
                  </option>
                </select>
                <button type="button" class="btn-secundario" :disabled="!questaoBancoSelecionada" @click="importarQuestao">Importar</button>
              </div>
            </div>
          </div>

          <p v-if="erro" class="mensagem-erro">{{ erro }}</p>
        </template>
      </section>

      <!-- Metade direita: prova montada a partir do template -->
      <section class="painel painel-preview">
        <PreviewProva
          :template="template"
          :metadados="metadados"
          :questoes="questoes"
          :professor="authStore.user?.nome || ''"
        />
      </section>
    </div>

    <ModalSairEdicao
      :visivel="mostrarModalSair"
      :salvando="salvando"
      :provaSalva="Boolean(draft.provaId)"
      @cancelar="cancelarSaida"
      @sair-sem-salvar="sairSemSalvar"
      @salvar-e-sair="salvarESair"
    />
  </div>
</template>

<script>
import QuestaoEditor from "@/components/QuestaoEditor.vue";
import PreviewProva from "@/components/PreviewProva.vue";
import ModalSairEdicao from "@/components/ModalSairEdicao.vue";
import { useAuthStore } from "@/stores/auth";
import { novaQuestaoEditor, questaoDoBanco, useProvaDraftStore } from "@/stores/provaDraft";
import { listarDisciplinas } from "@/services/disciplinas";
import { atualizarQuestao, criarQuestao, listarQuestoes } from "@/services/questoes";
import { adicionarQuestoes, atualizarProva, buscarProva, criarProva } from "@/services/provas";
import { obterTemplateProva } from "@/services/templates";
import { htmlVazio, sanitizar, textoPuro } from "@/utils/html";

export default {
  name: "CriarProvaView",
  components: { QuestaoEditor, PreviewProva, ModalSairEdicao },
  props: {
    id: { type: String, default: null },
  },
  setup() {
    return { authStore: useAuthStore(), draft: useProvaDraftStore() };
  },
  data: () => ({
    temaAtual: "tema-claro",
    template: "",
    disciplinas: [],
    bancoQuestoes: [],
    modoDisciplinaManual: false,
    questaoBancoSelecionada: "",
    carregando: true,
    salvando: false,
    erro: "",
    erroCarregamento: "",
    mostrarModalSair: false,
    destinoPendente: null,
    liberarSaida: false,
    monitorandoAlteracoes: false,
  }),
  computed: {
    metadados() {
      return this.draft.metadados;
    },
    questoes() {
      return this.draft.questoesEditor;
    },
    tituloTela() {
      const nome = this.metadados.nome_disciplina;
      if (!this.draft.provaId) return nome ? `Nova prova · ${nome}` : "Nova prova";
      return nome ? `Editar prova · ${nome}` : "Editar prova";
    },
    opcoesStatus() {
      return [...new Set(["Aguardando questões", "Não Corrigida", "Corrigida", this.metadados.status].filter(Boolean))];
    },
    disciplinaAtual() {
      const codigo = String(this.metadados.codigo_disciplina || "").trim();
      const nome = String(this.metadados.nome_disciplina || "").trim();
      return codigo && nome ? { codigo_disciplina: codigo, nome_disciplina: nome } : null;
    },
    questoesBancoCompativeis() {
      const disciplina = this.disciplinaAtual;
      if (!disciplina) return [];
      const referencias = [disciplina.codigo_disciplina, disciplina.nome_disciplina].map((item) => item.toLowerCase());
      const idsNaProva = new Set(this.questoes.map((questao) => questao._idBanco).filter(Boolean));
      return this.bancoQuestoes.filter((questao) =>
        !idsNaProva.has(questao._id)
        && questao.tipo_questao === this.metadados.tipo
        && Array.isArray(questao.disciplina)
        && questao.disciplina.some((item) => referencias.includes(String(item).trim().toLowerCase())),
      );
    },
  },
  watch: {
    "draft.metadados": {
      deep: true,
      handler() {
        if (this.monitorandoAlteracoes) this.draft.marcarSujo();
      },
    },
    "draft.questoesEditor": {
      deep: true,
      handler() {
        if (this.monitorandoAlteracoes) this.draft.marcarSujo();
      },
    },
  },
  async mounted() {
    window.addEventListener("beforeunload", this.aoFecharJanela);
    await this.carregar();
  },
  beforeUnmount() {
    window.removeEventListener("beforeunload", this.aoFecharJanela);
  },
  beforeRouteLeave(to) {
    if (this.liberarSaida || !this.draft.sujo) {
      this.draft.descartarRascunho();
      return true;
    }
    this.destinoPendente = to.fullPath;
    this.mostrarModalSair = true;
    return false;
  },
  methods: {
    mensagemErro(error) {
      return error?.details || error?.message || "Não foi possível concluir a operação.";
    },
    resumo(html) {
      const texto = textoPuro(html) || "[questão com imagem]";
      return texto.length > 90 ? `${texto.slice(0, 90)}…` : texto;
    },
    async carregar() {
      this.monitorandoAlteracoes = false;
      this.carregando = true;
      this.erro = "";
      this.erroCarregamento = "";

      const [resTemplate, resDisciplinas, resQuestoes] = await Promise.allSettled([
        obterTemplateProva(),
        listarDisciplinas(),
        listarQuestoes(),
      ]);
      const falhas = [];
      this.template = resTemplate.status === "fulfilled" ? resTemplate.value : "";
      if (resTemplate.status === "rejected") falhas.push(this.mensagemErro(resTemplate.reason));
      this.disciplinas = resDisciplinas.status === "fulfilled" && Array.isArray(resDisciplinas.value?.disciplinas) ? resDisciplinas.value.disciplinas : [];
      if (resDisciplinas.status === "rejected") falhas.push(this.mensagemErro(resDisciplinas.reason));
      this.bancoQuestoes = resQuestoes.status === "fulfilled" && Array.isArray(resQuestoes.value?.questoes) ? resQuestoes.value.questoes : [];
      if (resQuestoes.status === "rejected") falhas.push(this.mensagemErro(resQuestoes.reason));
      this.erroCarregamento = [...new Set(falhas)].join(" ");
      this.modoDisciplinaManual = !this.disciplinas.length;

      if (this.id) await this.carregarProvaExistente();
      else this.iniciarNovaProva();

      this.carregando = false;
      await this.$nextTick();
      this.monitorandoAlteracoes = true;
    },
    iniciarNovaProva() {
      const filaDoBanco = [...this.draft.questoes];
      this.draft.iniciarNova();
      this.draft.limpar();
      if (!filaDoBanco.length) return;

      const primeira = filaDoBanco[0];
      this.metadados.tipo = primeira.tipo_questao || (primeira.tipo === "objetiva" ? "Objetiva" : "Dissertativa");
      const referencias = primeira.disciplinasOriginais || (Array.isArray(primeira.disciplina) ? primeira.disciplina : []);
      const disciplina = this.disciplinas.find((item) =>
        referencias.some((ref) => [item.codigo_disciplina, item.nome_disciplina].some((valor) => valor.toLowerCase() === String(ref).toLowerCase())),
      );
      if (disciplina) {
        this.selecionarDisciplina(disciplina.codigo_disciplina);
      } else if (referencias.length) {
        this.modoDisciplinaManual = true;
        this.metadados.nome_disciplina = [...referencias].sort((a, b) => String(b).length - String(a).length)[0];
      }

      const completas = filaDoBanco
        .map((item) => this.bancoQuestoes.find((questao) => questao._id === item._id))
        .filter(Boolean);
      this.draft.questoesEditor = completas.map((questao) => this.comAssinatura(questaoDoBanco(questao)));
      if (!this.draft.questoesEditor.length) this.draft.questoesEditor = [novaQuestaoEditor()];
    },
    async carregarProvaExistente() {
      this.draft.iniciarNova();
      try {
        const prova = await buscarProva(this.id);
        if (!prova) {
          this.erro = "A prova não foi encontrada ou está inativa.";
          return;
        }
        this.draft.provaId = prova._id;
        this.modoDisciplinaManual = !this.disciplinas.some((item) => item.codigo_disciplina === prova.disciplina.codigo_disciplina);
        Object.assign(this.draft.metadados, {
          turmasTexto: (Array.isArray(prova.id_turma) ? prova.id_turma : [prova.id_turma]).join("\n"),
          codigo_disciplina: prova.disciplina.codigo_disciplina,
          nome_disciplina: prova.disciplina.nome_disciplina,
          tipo: prova.tipo,
          serie: prova.serie,
          bimestre: prova.bimestre,
          data_de_aplicacao: prova.data_de_aplicacao,
          status: prova.status,
        });
        const porId = new Map(this.bancoQuestoes.map((questao) => [questao._id, questao]));
        const ids = Array.isArray(prova.questoes) ? prova.questoes : [];
        const encontradas = ids.filter((idQuestao) => porId.has(idQuestao));
        this.draft.questoesEditor = encontradas.map((idQuestao) => this.comAssinatura(questaoDoBanco(porId.get(idQuestao))));
        if (encontradas.length < ids.length) {
          this.erro = `${ids.length - encontradas.length} questão(ões) desta prova não está(ão) mais disponível(is) e foi(ram) removida(s) da edição.`;
        }
        if (!this.draft.questoesEditor.length) this.draft.questoesEditor = [novaQuestaoEditor()];
      } catch (error) {
        this.erro = this.mensagemErro(error);
      }
    },
    selecionarDisciplina(codigo) {
      const disciplina = this.disciplinas.find((item) => item.codigo_disciplina === codigo);
      this.metadados.codigo_disciplina = disciplina?.codigo_disciplina || "";
      this.metadados.nome_disciplina = disciplina?.nome_disciplina || "";
    },
    alternarModoDisciplina() {
      this.modoDisciplinaManual = !this.modoDisciplinaManual;
      this.metadados.codigo_disciplina = "";
      this.metadados.nome_disciplina = "";
    },
    adicionarQuestao() {
      this.draft.questoesEditor.push(novaQuestaoEditor());
    },
    importarQuestao() {
      const questao = this.bancoQuestoes.find((item) => item._id === this.questaoBancoSelecionada);
      if (questao) this.draft.questoesEditor.push(this.comAssinatura(questaoDoBanco(questao)));
      this.questaoBancoSelecionada = "";
    },
    moverQuestao(index, direcao) {
      const destino = index + direcao;
      if (destino < 0 || destino >= this.questoes.length) return;
      const lista = [...this.questoes];
      [lista[index], lista[destino]] = [lista[destino], lista[index]];
      this.draft.questoesEditor = lista;
    },
    removerQuestao(index) {
      window.$modal.abrir({
        titulo: "Remover questão",
        mensagem: "Deseja remover esta questão da prova? Questões já cadastradas continuam no banco.",
        tipo: "confirmacao",
        onConfirm: () => this.draft.questoesEditor.splice(index, 1),
      });
    },
    turmas() {
      return this.metadados.turmasTexto.split(/\r?\n/).map((turma) => turma.trim()).filter(Boolean);
    },
    payloadQuestao(questao) {
      const disciplina = this.disciplinaAtual;
      const nomeProfessor = questao.professor?.nome || this.authStore.user.nome;
      const payload = {
        professor: { nome: nomeProfessor },
        autor: questao.autor || nomeProfessor,
        assunto: questao.assunto.trim(),
        disciplina: [...new Set([disciplina.codigo_disciplina, disciplina.nome_disciplina])],
        tipo_questao: this.metadados.tipo,
        dificuldade: questao.dificuldade,
        enunciado: sanitizar(questao.enunciado),
      };
      if (this.metadados.tipo === "Objetiva") {
        payload.alternativas = questao.alternativas.map((alternativa) => sanitizar(alternativa));
        payload.alternativa_correta = payload.alternativas[questao.indiceCorreta];
      } else {
        payload.numero_linhas = Number(questao.numeroLinhas);
      }
      return payload;
    },
    // Guarda a "foto" do que está no banco para só enviar PUT de questões realmente alteradas.
    comAssinatura(questao) {
      if (this.disciplinaAtual) questao.assinaturaSalva = JSON.stringify(this.payloadQuestao(questao));
      return questao;
    },
    validar() {
      const turmas = this.turmas();
      if (!turmas.length) return "Informe ao menos uma turma.";
      if (!this.disciplinaAtual) return "Selecione uma disciplina ou informe seu código e nome.";
      if (this.disciplinaAtual.nome_disciplina.length < 3) return "O nome da disciplina deve ter ao menos 3 caracteres.";
      if (!Number.isInteger(this.metadados.serie) || this.metadados.serie <= 0) return "Informe uma série válida.";
      if (!this.metadados.bimestre) return "Informe o bimestre.";
      if (!this.metadados.data_de_aplicacao) return "Informe a data de aplicação.";
      if (!this.questoes.length) return "Adicione ao menos uma questão.";
      if (this.authStore.user?.registro === undefined || this.authStore.user?.registro === null) {
        return "Não foi possível identificar o registro do professor. Faça login novamente.";
      }

      const enunciados = new Set();
      for (const [index, questao] of this.questoes.entries()) {
        const numero = index + 1;
        if (questao.assunto.trim().length < 2) return `Questão ${numero}: informe o assunto.`;
        if (htmlVazio(questao.enunciado)) return `Questão ${numero}: o enunciado está vazio.`;
        const chave = sanitizar(questao.enunciado).toLowerCase();
        if (enunciados.has(chave)) return `Questão ${numero}: existe outra questão com o mesmo enunciado.`;
        enunciados.add(chave);

        if (this.metadados.tipo === "Objetiva") {
          if (questao.alternativas.some(htmlVazio)) return `Questão ${numero}: preencha as cinco alternativas.`;
          const distintas = new Set(questao.alternativas.map((alternativa) => sanitizar(alternativa).trim()));
          if (distintas.size !== questao.alternativas.length) return `Questão ${numero}: as alternativas devem ser diferentes entre si.`;
        } else if (!Number.isInteger(questao.numeroLinhas) || questao.numeroLinhas <= 0) {
          return `Questão ${numero}: informe o número de linhas.`;
        }
      }
      return "";
    },
    async salvar() {
      if (this.salvando) return false;
      this.erro = this.validar();
      if (this.erro) return false;

      this.salvando = true;
      try {
        // 1. Questões: cria as novas e atualiza as alteradas (o id é guardado a cada passo para não duplicar em nova tentativa).
        for (const [index, questao] of this.questoes.entries()) {
          const payload = this.payloadQuestao(questao);
          const assinatura = JSON.stringify(payload);
          try {
            if (!questao._idBanco) {
              const data = await criarQuestao(payload);
              questao._idBanco = data.questao._id;
            } else if (assinatura !== questao.assinaturaSalva) {
              await atualizarQuestao(questao._idBanco, payload);
            }
            questao.assinaturaSalva = assinatura;
          } catch (error) {
            throw new Error(`Questão ${index + 1}: ${this.mensagemErro(error)}`);
          }
        }

        // 2. Prova-base: criada apenas no primeiro salvamento.
        const turmas = this.turmas();
        const base = {
          id_turma: turmas.length === 1 ? turmas[0] : turmas,
          professor: { registro: this.authStore.user.registro, nome: this.authStore.user.nome },
          disciplina: { ...this.disciplinaAtual },
          tipo: this.metadados.tipo,
          serie: Number(this.metadados.serie),
          bimestre: this.metadados.bimestre,
          data_de_aplicacao: this.metadados.data_de_aplicacao,
        };
        const ids = this.questoes.map((questao) => questao._idBanco);
        const primeiraVez = !this.draft.provaId;

        if (primeiraVez) {
          const data = await criarProva(base);
          this.draft.provaId = data.prova._id;
          this.metadados.status = data.prova.status;
        } else {
          await atualizarProva(this.draft.provaId, { ...base, status: this.metadados.status, questoes: ids });
        }

        // 3. Vincula as questões e (re)gera as versões individuais dos alunos.
        await adicionarQuestoes(this.draft.provaId, ids);

        await this.$nextTick();
        this.draft.sujo = false;
        if (primeiraVez) this.$router.replace(`/provas/${this.draft.provaId}/editar`);
        return true;
      } catch (error) {
        this.erro = this.mensagemErro(error);
        return false;
      } finally {
        this.salvando = false;
      }
    },
    voltar() {
      this.$router.push("/provas");
    },
    cancelarSaida() {
      if (this.salvando) return;
      this.mostrarModalSair = false;
      this.destinoPendente = null;
    },
    sairSemSalvar() {
      this.mostrarModalSair = false;
      this.liberarSaida = true;
      this.$router.push(this.destinoPendente || "/provas");
    },
    async salvarESair() {
      const salvou = await this.salvar();
      this.mostrarModalSair = false;
      if (!salvou) return;
      this.liberarSaida = true;
      this.$router.push(this.destinoPendente || "/provas");
    },
    aoFecharJanela(evento) {
      if (!this.draft.sujo) return;
      evento.preventDefault();
      evento.returnValue = "";
    },
  },
};
</script>

<style scoped>
.criar-prova {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
}

.criar-prova.tema-claro {
  background-color: #f5f5f5;
  color: #333;
}

.criar-prova.tema-escuro {
  background-color: #1a1a1a;
  color: #e5e5e5;
}

/* Barra superior no mesmo azul da barra lateral */
.barra-superior {
  display: flex;
  align-items: center;
  gap: 16px;
  height: 64px;
  padding: 0 20px;
  background: linear-gradient(135deg, #00488b 0%, #003366 100%);
  color: white;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  flex-shrink: 0;
}

.barra-superior h1 {
  flex: 1;
  font-size: 18px;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.btn-voltar {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border: none;
  border-radius: 8px;
  background: transparent;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-voltar:hover {
  background: rgba(255, 255, 255, 0.15);
}

.indicador-alteracoes {
  font-size: 12px;
  padding: 4px 10px;
  border-radius: 12px;
  background: #ffc10730;
  color: #ffe08a;
}

.btn-salvar {
  padding: 8px 18px;
  background: white;
  color: #00488b;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.btn-salvar:hover:not(:disabled) {
  transform: scale(1.02);
  background: #e8f0f8;
}

.btn-salvar:disabled {
  opacity: 0.65;
  cursor: wait;
}

/* Duas metades */
.area-trabalho {
  flex: 1;
  display: grid;
  grid-template-columns: 1fr 1fr;
  min-height: 0;
}

.painel {
  overflow-y: auto;
  padding: 24px;
}

.painel-campos {
  border-right: 1px solid #e0e0e0;
}

.tema-escuro .painel-campos {
  border-right-color: #404040;
}

.painel-preview {
  background: #e9ecef;
}

.tema-escuro .painel-preview {
  background: #111;
}

.bloco {
  margin-bottom: 24px;
}

.bloco h3 {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 2px solid #00488b;
}

.campo {
  margin-bottom: 12px;
}

.campo label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  margin-bottom: 6px;
  color: #666;
}

.tema-escuro .campo label {
  color: #aaa;
}

.campo input,
.campo select,
.campo textarea,
.importar-banco select {
  width: 100%;
  padding: 9px 10px;
  border: 1px solid #d8d8d8;
  border-radius: 6px;
  font: inherit;
  background: white;
  color: inherit;
}

.tema-escuro .campo input,
.tema-escuro .campo select,
.tema-escuro .campo textarea,
.tema-escuro .importar-banco select {
  background: #2a2a2a;
  border-color: #404040;
}

.grade-campos {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0 12px;
}

.disciplina-manual {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 8px;
}

.btn-link {
  margin-top: 6px;
  padding: 0;
  border: none;
  background: none;
  color: #00488b;
  cursor: pointer;
  font-size: 13px;
}

.tema-escuro .btn-link {
  color: #0066cc;
}

.acoes-questoes {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.importar-banco {
  display: flex;
  gap: 8px;
}

.btn-primario {
  padding: 10px 20px;
  background: #00488b;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.btn-primario:hover {
  background: #0066cc;
  transform: scale(1.02);
}

.btn-secundario {
  padding: 8px 14px;
  border: 1px solid #00488b;
  border-radius: 6px;
  background: transparent;
  color: #00488b;
  cursor: pointer;
  white-space: nowrap;
}

.btn-secundario:disabled {
  opacity: 0.5;
  cursor: default;
}

.tema-escuro .btn-secundario {
  border-color: #0066cc;
  color: #0066cc;
}

.mensagem-info {
  color: #888;
}

.mensagem-erro {
  color: #b42318;
  font-weight: 500;
  margin: 12px 0;
}

@media (max-width: 768px) {
  .area-trabalho {
    grid-template-columns: 1fr;
    overflow-y: auto;
  }

  .painel {
    overflow: visible;
    padding: 16px;
  }

  .painel-campos {
    border-right: none;
    border-bottom: 1px solid #e0e0e0;
  }

  .grade-campos,
  .disciplina-manual {
    grid-template-columns: 1fr;
  }

  .indicador-alteracoes {
    display: none;
  }
}
</style>
