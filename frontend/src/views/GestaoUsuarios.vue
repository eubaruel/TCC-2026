<template>
  <div class="gestao-usuarios-container">
    <div class="page-header">
      <h2>Gestão de Usuários</h2>
      <div class="header-line"></div>
    </div>

    <!-- Botão para criar novo usuário -->
    <div class="actions-bar">
      <button @click="abrirModalCriar" class="btn-criar">+ Novo Usuário</button>
    </div>

    <!-- Tabs para separar professores e processo pedagógico -->
    <div class="tabs-container">
      <button
        @click="abaAtiva = 'professores'"
        class="tab-btn"
        :class="{ ativo: abaAtiva === 'professores' }"
      >
        Professores ({{ professores ? professores.length : 0 }})
      </button>
      <button
        @click="abaAtiva = 'processo'"
        class="tab-btn"
        :class="{ ativo: abaAtiva === 'processo' }"
      >
        Processo Pedagógico ({{ processo ? processo.length : 0 }})
      </button>
    </div>

    <!-- Filtros para Professores -->
    <div v-if="abaAtiva === 'professores'" class="filtros-container">
      <div class="filtro-row">
        <div class="filtro-group">
          <label>Registro</label>
          <input
            type="text"
            v-model="filtrosProfessores.registro"
            placeholder="Buscar por registro..."
            @input="buscarPorRegistroProfessor"
          />
          <div v-if="sugestoesRegistroProfessor && sugestoesRegistroProfessor.length" class="sugestoes">
            <div
              v-for="(sug, idx) in sugestoesRegistroProfessor"
              :key="idx"
              @click="selecionarSugestaoRegistroProfessor(sug)"
              class="sugestao-item"
            >
              {{ sug.registro }} - {{ sug.nome }}
            </div>
          </div>
        </div>

        <div class="filtro-group">
          <label>Nome</label>
          <input
            type="text"
            v-model="filtrosProfessores.nome"
            placeholder="Buscar por nome..."
            @input="buscarPorNomeProfessor"
          />
          <div v-if="sugestoesNomeProfessor && sugestoesNomeProfessor.length" class="sugestoes">
            <div
              v-for="(sug, idx) in sugestoesNomeProfessor"
              :key="idx"
              @click="selecionarSugestaoNomeProfessor(sug)"
              class="sugestao-item"
            >
              {{ sug.nome }} ({{ sug.registro }})
            </div>
          </div>
        </div>

        <div class="filtro-group">
          <label>Email</label>
          <input
            type="text"
            v-model="filtrosProfessores.email"
            placeholder="Buscar por email..."
            @input="filtrarProfessores"
          />
        </div>

        <div class="filtro-group">
          <label>Disciplina</label>
          <select v-model="filtrosProfessores.disciplina" @change="filtrarProfessores">
            <option value="">Todas as disciplinas</option>
            <option v-for="disc in disciplinas" :key="disc" :value="disc">
              {{ disc }}
            </option>
          </select>
        </div>

        <button @click="limparFiltrosProfessores" class="btn-limpar">
          Limpar Filtros
        </button>
      </div>
    </div>

    <!-- Filtros para Processo Pedagógico -->
    <div v-if="abaAtiva === 'processo'" class="filtros-container">
      <div class="filtro-row">
        <div class="filtro-group">
          <label>Registro</label>
          <input
            type="text"
            v-model="filtrosProcesso.registro"
            placeholder="Buscar por registro..."
            @input="buscarPorRegistroProcesso"
          />
          <div v-if="sugestoesRegistroProcesso && sugestoesRegistroProcesso.length" class="sugestoes">
            <div
              v-for="(sug, idx) in sugestoesRegistroProcesso"
              :key="idx"
              @click="selecionarSugestaoRegistroProcesso(sug)"
              class="sugestao-item"
            >
              {{ sug.registro }} - {{ sug.nome }}
            </div>
          </div>
        </div>

        <div class="filtro-group">
          <label>Nome</label>
          <input
            type="text"
            v-model="filtrosProcesso.nome"
            placeholder="Buscar por nome..."
            @input="buscarPorNomeProcesso"
          />
          <div v-if="sugestoesNomeProcesso && sugestoesNomeProcesso.length" class="sugestoes">
            <div
              v-for="(sug, idx) in sugestoesNomeProcesso"
              :key="idx"
              @click="selecionarSugestaoNomeProcesso(sug)"
              class="sugestao-item"
            >
              {{ sug.nome }} ({{ sug.registro }})
            </div>
          </div>
        </div>

        <div class="filtro-group">
          <label>Email</label>
          <input
            type="text"
            v-model="filtrosProcesso.email"
            placeholder="Buscar por email..."
            @input="filtrarProcesso"
          />
        </div>

        <button @click="limparFiltrosProcesso" class="btn-limpar">
          Limpar Filtros
        </button>
      </div>
    </div>

    <!-- Lista de Professores -->
    <div v-if="abaAtiva === 'professores'" class="lista-usuarios">
      <div v-if="!professoresFiltrados || professoresFiltrados.length === 0" class="sem-resultados">
        Nenhum professor encontrado.
      </div>
      <div v-else>
        <div
          v-for="user in professoresFiltrados"
          :key="user.id"
          class="usuario-card"
        >
          <div class="usuario-info">
            <div class="usuario-header">
              <h3>{{ user.nome }}</h3>
              <span class="badge professor">Professor</span>
            </div>
            <div class="usuario-detalhes">
              <p><strong>Registro:</strong> {{ user.registro }}</p>
              <p><strong>Email:</strong> {{ user.email }}</p>
              <p>
                <strong>Disciplina:</strong> {{ user.disciplina || "Nenhuma" }}
              </p>
              <p>
                <strong>Status:</strong>
                <span :class="user.ativo ? 'status-ativo' : 'status-inativo'">
                  {{ user.ativo ? "Ativo" : "Inativo" }}
                </span>
              </p>
            </div>
          </div>
          <div class="usuario-actions">
            <button @click="abrirModalEditar(user)" class="btn-editar">
              Editar
            </button>
            <button @click="confirmarExcluir(user)" class="btn-excluir">
              Excluir
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Lista de Processo Pedagógico -->
    <div v-if="abaAtiva === 'processo'" class="lista-usuarios">
      <div v-if="!processoFiltrados || processoFiltrados.length === 0" class="sem-resultados">
        Nenhum usuário do processo pedagógico encontrado.
      </div>
      <div v-else>
        <div
          v-for="user in processoFiltrados"
          :key="user.id"
          class="usuario-card"
        >
          <div class="usuario-info">
            <div class="usuario-header">
              <h3>{{ user.nome }}</h3>
              <span class="badge processo">Processo Pedagógico</span>
            </div>
            <div class="usuario-detalhes">
              <p><strong>Registro:</strong> {{ user.registro }}</p>
              <p><strong>Email:</strong> {{ user.email }}</p>
              <p>
                <strong>Status:</strong>
                <span :class="user.ativo ? 'status-ativo' : 'status-inativo'">
                  {{ user.ativo ? "Ativo" : "Inativo" }}
                </span>
              </p>
            </div>
          </div>
          <div class="usuario-actions">
            <button @click="abrirModalEditar(user)" class="btn-editar">
              Editar
            </button>
            <button @click="confirmarExcluir(user)" class="btn-excluir">
              Excluir
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal Criar/Editar Usuário -->
    <div v-if="modalUsuarioAberto" class="modal-overlay" @click="fecharModalUsuario">
      <div class="modal-container modal-horizontal">
        <div class="modal-header">
          <h3>{{ modoEdicao ? "Editar Usuário" : "Novo Usuário" }}</h3>
          <button @click="fecharModalUsuario" class="modal-close">&times;</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="salvarUsuario">
            <div class="form-grid">
              <div class="form-group-modal">
                <label>Registro *</label>
                <input
                  type="number"
                  v-model="formUsuario.registro"
                  :disabled="modoEdicao"
                  required
                  placeholder="Número de registro"
                />
              </div>

              <div class="form-group-modal">
                <label>Nome Completo *</label>
                <input
                  type="text"
                  v-model="formUsuario.nome"
                  required
                  placeholder="Nome e sobrenome"
                />
              </div>

              <div class="form-group-modal">
                <label>Email *</label>
                <input
                  type="email"
                  v-model="formUsuario.email"
                  required
                  placeholder="email@escola.com"
                />
              </div>

              <div class="form-group-modal">
                <label>Data de Nascimento</label>
                <input type="date" v-model="formUsuario.dataNascimento" />
                <small class="helper-text">Usada como senha temporária</small>
              </div>

              <div class="form-group-modal">
                <label>Tipo de Usuário *</label>
                <select v-model="formUsuario.role" required @change="onRoleChange">
                  <option value="Professor">Professor</option>
                  <option value="Processo pedagógico">
                    Processo Pedagógico
                  </option>
                </select>
              </div>

              <div class="form-group-modal" v-if="formUsuario.role === 'Professor'">
                <label>Disciplina *</label>
                <select v-model="disciplinaSelecionada" required>
                  <option value="">Selecione a disciplina</option>
                  <option v-for="disc in disciplinas" :key="disc" :value="disc">
                    {{ disc }}
                  </option>
                </select>
                <small class="helper-text"
                  >Cada professor pode lecionar apenas uma disciplina</small
                >
              </div>

              <div class="form-group-modal" v-if="!modoEdicao">
                <label>Senha Temporária</label>
                <input
                  type="text"
                  v-model="formUsuario.senha"
                  placeholder="Deixe em branco para usar data de nascimento"
                />
              </div>
            </div>

            <div class="modal-footer">
              <button type="submit" class="btn-modal-salvar">Salvar</button>
              <button
                type="button"
                @click="fecharModalUsuario"
                class="btn-modal-cancelar"
              >
                Cancelar
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Modal Confirmar Exclusão -->
    <div v-if="modalExcluirAberto" class="modal-overlay" @click="fecharModalExcluir">
      <div class="modal-container">
        <div class="modal-header">
          <h3>Confirmar Exclusão</h3>
        </div>
        <div class="modal-body">
          <p>
            Tem certeza que deseja excluir o usuário
            <strong>{{ usuarioParaExcluir ? usuarioParaExcluir.nome : '' }}</strong>
            ?
          </p>
          <p class="info-text">
            O usuário será desativado, mas seus dados permanecerão no sistema.
          </p>
        </div>
        <div class="modal-footer">
          <button @click="excluirUsuario" class="btn-modal-excluir">
            Excluir
          </button>
          <button @click="fecharModalExcluir" class="btn-modal-cancelar">
            Cancelar
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useUsersStore } from "@/stores/users";

export default {
  name: "GestaoUsuarios",
  setup() {
    const usersStore = useUsersStore();
    return { usersStore };
  },
  data() {
    return {
      abaAtiva: "professores",

      // Filtros para professores
      filtrosProfessores: {
        registro: "",
        nome: "",
        email: "",
        disciplina: "",
      },
      sugestoesRegistroProfessor: [],
      sugestoesNomeProfessor: [],

      // Filtros para processo pedagógico
      filtrosProcesso: {
        registro: "",
        nome: "",
        email: "",
      },
      sugestoesRegistroProcesso: [],
      sugestoesNomeProcesso: [],

      // Modal
      modalUsuarioAberto: false,
      modalExcluirAberto: false,
      modoEdicao: false,
      usuarioParaExcluir: null,

      // Formulário
      disciplinaSelecionada: "",
      formUsuario: {
        registro: null,
        nome: "",
        email: "",
        role: "Professor",
        disciplina: "",
        dataNascimento: "",
        senha: "",
      },

      // Lista de disciplinas
      disciplinas: [
        "Matemática FGB",
        "Matemática AP",
        "Português",
        "Literatura",
        "Inglês",
        "Projeto de Vida",
        "Eletiva",
        "Física FGB",
        "Física AP",
        "Química FGB",
        "Química AP",
        "Biologia FGB",
        "Biologia AP",
        "História",
        "Geografia",
        "Filosofia/Sociologia",
        "Arte",
        "Educação Física",
        "Redação",
      ],
    };
  },
  computed: {
    professores() {
      return this.usersStore.professores || [];
    },
    processo() {
      return this.usersStore.processoPedagogico || [];
    },
    professoresFiltrados() {
      let resultado = this.professores ? [...this.professores] : [];

      if (this.filtrosProfessores.registro) {
        resultado = resultado.filter((u) =>
          u.registro && u.registro.toString().includes(this.filtrosProfessores.registro)
        );
      }

      if (this.filtrosProfessores.nome) {
        const termo = this.filtrosProfessores.nome.toLowerCase();
        resultado = resultado.filter((u) =>
          u.nome && u.nome.toLowerCase().includes(termo)
        );
      }

      if (this.filtrosProfessores.email) {
        const termo = this.filtrosProfessores.email.toLowerCase();
        resultado = resultado.filter((u) =>
          u.email && u.email.toLowerCase().includes(termo)
        );
      }

      if (this.filtrosProfessores.disciplina) {
        resultado = resultado.filter(
          (u) => u.disciplina === this.filtrosProfessores.disciplina
        );
      }

      return resultado;
    },
    processoFiltrados() {
      let resultado = this.processo ? [...this.processo] : [];

      if (this.filtrosProcesso.registro) {
        resultado = resultado.filter((u) =>
          u.registro && u.registro.toString().includes(this.filtrosProcesso.registro)
        );
      }

      if (this.filtrosProcesso.nome) {
        const termo = this.filtrosProcesso.nome.toLowerCase();
        resultado = resultado.filter((u) =>
          u.nome && u.nome.toLowerCase().includes(termo)
        );
      }

      if (this.filtrosProcesso.email) {
        const termo = this.filtrosProcesso.email.toLowerCase();
        resultado = resultado.filter((u) =>
          u.email && u.email.toLowerCase().includes(termo)
        );
      }

      return resultado;
    },
  },
  mounted() {
    this.usersStore.fetchUsers();
  },
  methods: {
    // Filtros Professores
    buscarPorRegistroProfessor() {
      const termo = this.filtrosProfessores.registro;
      if (termo && termo.length > 0) {
        this.sugestoesRegistroProfessor = this.usersStore
          .getByRegistro(parseInt(termo))
          .filter((u) => u.role === "Professor")
          .slice(0, 3);
      } else {
        this.sugestoesRegistroProfessor = [];
      }
    },

    buscarPorNomeProfessor() {
      const termo = this.filtrosProfessores.nome;
      if (termo && termo.length > 0) {
        this.sugestoesNomeProfessor = this.usersStore
          .getByNome(termo)
          .filter((u) => u.role === "Professor")
          .slice(0, 3);
      } else {
        this.sugestoesNomeProfessor = [];
      }
    },

    selecionarSugestaoRegistroProfessor(sugestao) {
      this.filtrosProfessores.registro = sugestao.registro.toString();
      this.sugestoesRegistroProfessor = [];
    },

    selecionarSugestaoNomeProfessor(sugestao) {
      this.filtrosProfessores.nome = sugestao.nome;
      this.sugestoesNomeProfessor = [];
    },

    filtrarProfessores() {},

    limparFiltrosProfessores() {
      this.filtrosProfessores = {
        registro: "",
        nome: "",
        email: "",
        disciplina: "",
      };
      this.sugestoesRegistroProfessor = [];
      this.sugestoesNomeProfessor = [];
    },

    // Filtros Processo
    buscarPorRegistroProcesso() {
      const termo = this.filtrosProcesso.registro;
      if (termo && termo.length > 0) {
        this.sugestoesRegistroProcesso = this.usersStore
          .getByRegistro(parseInt(termo))
          .filter((u) => u.role === "Processo pedagógico")
          .slice(0, 3);
      } else {
        this.sugestoesRegistroProcesso = [];
      }
    },

    buscarPorNomeProcesso() {
      const termo = this.filtrosProcesso.nome;
      if (termo && termo.length > 0) {
        this.sugestoesNomeProcesso = this.usersStore
          .getByNome(termo)
          .filter((u) => u.role === "Processo pedagógico")
          .slice(0, 3);
      } else {
        this.sugestoesNomeProcesso = [];
      }
    },

    selecionarSugestaoRegistroProcesso(sugestao) {
      this.filtrosProcesso.registro = sugestao.registro.toString();
      this.sugestoesRegistroProcesso = [];
    },

    selecionarSugestaoNomeProcesso(sugestao) {
      this.filtrosProcesso.nome = sugestao.nome;
      this.sugestoesNomeProcesso = [];
    },

    filtrarProcesso() {},

    limparFiltrosProcesso() {
      this.filtrosProcesso = {
        registro: "",
        nome: "",
        email: "",
      };
      this.sugestoesRegistroProcesso = [];
      this.sugestoesNomeProcesso = [];
    },

    onRoleChange() {
      if (this.formUsuario.role !== "Professor") {
        this.disciplinaSelecionada = "";
      }
    },

    abrirModalCriar() {
      this.modoEdicao = false;
      this.formUsuario = {
        registro: null,
        nome: "",
        email: "",
        role: "Professor",
        disciplina: "",
        dataNascimento: "",
        senha: "",
      };
      this.disciplinaSelecionada = "";
      this.modalUsuarioAberto = true;
    },

    abrirModalEditar(user) {
      this.modoEdicao = true;
      this.formUsuario = {
        id: user.id,
        registro: user.registro,
        nome: user.nome,
        email: user.email,
        role: user.role,
        disciplina: user.disciplina || "",
        dataNascimento: user.dataNascimento || "",
        senha: "",
      };
      this.disciplinaSelecionada = user.disciplina || "";
      this.modalUsuarioAberto = true;
    },

    salvarUsuario() {
      try {
        if (this.modoEdicao) {
          const updates = {
            nome: this.formUsuario.nome,
            email: this.formUsuario.email,
            role: this.formUsuario.role,
            disciplina:
              this.formUsuario.role === "Professor"
                ? this.disciplinaSelecionada
                : null,
          };
          this.usersStore.updateUser(this.formUsuario.id, updates);
          alert("Usuário atualizado com sucesso!");
        } else {
          const userData = {
            registro: this.formUsuario.registro,
            nome: this.formUsuario.nome,
            email: this.formUsuario.email,
            role: this.formUsuario.role,
            disciplina:
              this.formUsuario.role === "Professor"
                ? this.disciplinaSelecionada
                : null,
            dataNascimento: this.formUsuario.dataNascimento,
            senha: this.formUsuario.senha || null,
          };
          this.usersStore.createUser(userData);
          alert("Usuário criado com sucesso!");
        }
        this.fecharModalUsuario();
        this.usersStore.fetchUsers();
      } catch (error) {
        alert(error.message);
      }
    },

    confirmarExcluir(user) {
      this.usuarioParaExcluir = user;
      this.modalExcluirAberto = true;
    },

    excluirUsuario() {
      if (this.usuarioParaExcluir) {
        this.usersStore.softDeleteUser(this.usuarioParaExcluir.id);
        alert(`Usuário ${this.usuarioParaExcluir.nome} foi desativado.`);
        this.fecharModalExcluir();
        this.usersStore.fetchUsers();
      }
    },

    fecharModalUsuario() {
      this.modalUsuarioAberto = false;
    },

    fecharModalExcluir() {
      this.modalExcluirAberto = false;
      this.usuarioParaExcluir = null;
    },
  },
};
</script>

<style scoped>
/* Estilos permanecem os mesmos do código anterior */
.gestao-usuarios-container {
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

.actions-bar {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 20px;
}

.btn-criar {
  padding: 10px 20px;
  background: #28a745;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
}

.btn-criar:hover {
  background: #218838;
  transform: scale(1.02);
}

.tabs-container {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.tab-btn {
  padding: 10px 20px;
  background: transparent;
  border: none;
  font-size: 16px;
  cursor: pointer;
  color: #666;
  transition: all 0.3s ease;
}

.tab-btn.ativo {
  color: #00488b;
  border-bottom: 2px solid #00488b;
}

.filtros-container {
  background: #f5f5f5;
  padding: 20px;
  border-radius: 12px;
  margin-bottom: 20px;
}

.tema-escuro .filtros-container {
  background: #2a2a2a;
}

.filtro-row {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  align-items: flex-end;
}

.filtro-group {
  flex: 1;
  min-width: 150px;
  position: relative;
}

.filtro-group label {
  display: block;
  margin-bottom: 5px;
  font-size: 12px;
  font-weight: 500;
}

.filtro-group input,
.filtro-group select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  background: white;
}

.tema-escuro .filtro-group input,
.tema-escuro .filtro-group select {
  background: #1a1a1a;
  border-color: #404040;
  color: #e5e5e5;
}

.sugestoes {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #ddd;
  border-radius: 6px;
  max-height: 200px;
  overflow-y: auto;
  z-index: 100;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.tema-escuro .sugestoes {
  background: #2a2a2a;
  border-color: #404040;
}

.sugestao-item {
  padding: 8px 12px;
  cursor: pointer;
  border-bottom: 1px solid #eee;
}

.sugestao-item:hover {
  background: #f0f0f0;
}

.tema-escuro .sugestao-item:hover {
  background: #3a3a3a;
}

.btn-limpar {
  padding: 8px 16px;
  background: #6c757d;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.btn-limpar:hover {
  background: #5a6268;
}

.lista-usuarios {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.usuario-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  border: 1px solid #e0e0e0;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  transition: all 0.3s ease;
}

.tema-escuro .usuario-card {
  background: #2a2a2a;
  border-color: #404040;
}

.usuario-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.usuario-info {
  flex: 1;
}

.usuario-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.usuario-header h3 {
  font-size: 18px;
  margin: 0;
}

.badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.badge.professor {
  background: #00488b20;
  color: #00488b;
}

.badge.processo {
  background: #6c757d20;
  color: #6c757d;
}

.usuario-detalhes p {
  margin: 0;
  color: #666;
  display: flex;
  align-items: center;
  gap: 8px;  /* ADICIONA ESPAÇO ENTRE O LABEL E O VALOR */
}

.usuario-detalhes p strong {
  min-width: 70px;  /* LARGURA FIXA PARA OS LABELS */
}

.tema-escuro .usuario-detalhes p {
  color: #aaa;
}

.status-ativo {
  color: #28a745;
  font-weight: 500;
}

.status-inativo {
  color: #dc3545;
  font-weight: 500;
}

.usuario-actions {
  display: flex;
  gap: 10px;
}

.btn-editar,
.btn-excluir {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.3s ease;
}

.btn-editar {
  background: #ffc107;
  color: #333;
}

.btn-editar:hover {
  background: #e0a800;
}

.btn-excluir {
  background: #dc3545;
  color: white;
}

.btn-excluir:hover {
  background: #c82333;
}

.sem-resultados {
  text-align: center;
  padding: 40px;
  color: #888;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.modal-container {
  background: white;
  border-radius: 12px;
  max-width: 500px;
  width: 90%;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
  max-height: 90vh;
  overflow-y: auto;
}

.modal-horizontal {
  max-width: 700px;
}

.tema-escuro .modal-container {
  background: #2a2a2a;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e0e0e0;
}

.tema-escuro .modal-header {
  border-bottom-color: #404040;
}

.modal-header h3 {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
}

.modal-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #999;
}

.modal-body {
  padding: 24px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.form-group-modal {
  margin-bottom: 0;
}

.form-group-modal label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  font-size: 14px;
}

.form-group-modal input,
.form-group-modal select {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
}

.tema-escuro .form-group-modal input,
.tema-escuro .form-group-modal select {
  background: #1a1a1a;
  border-color: #404040;
  color: #e5e5e5;
}

.helper-text {
  display: block;
  margin-top: 5px;
  font-size: 11px;
  color: #888;
}

.info-text {
  font-size: 12px;
  color: #888;
  margin-top: 8px;
}

.modal-footer {
  display: flex;
  gap: 12px;
  padding: 20px 24px;
  border-top: 1px solid #e0e0e0;
  justify-content: flex-end;
  margin-top: 20px;
}

.tema-escuro .modal-footer {
  border-top-color: #404040;
}

.btn-modal-salvar {
  padding: 10px 20px;
  background: #28a745;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-modal-salvar:hover {
  background: #218838;
}

.btn-modal-cancelar {
  padding: 10px 20px;
  background: transparent;
  border: 1px solid #ddd;
  border-radius: 6px;
  cursor: pointer;
}

.btn-modal-excluir {
  padding: 10px 20px;
  background: #dc3545;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.btn-modal-excluir:hover {
  background: #c82333;
}

@media (max-width: 768px) {
  .filtro-row {
    flex-direction: column;
  }

  .usuario-card {
    flex-direction: column;
  }

  .usuario-actions {
    margin-top: 15px;
    width: 100%;
    justify-content: flex-end;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .modal-horizontal {
    max-width: 90%;
  }
}
</style>