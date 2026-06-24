<template>
  <div class="editor-container">
    <div class="editor-header">
      <h2>{{ titulo }}</h2>
      <div class="editor-actions">
        <button @click="salvar" class="btn-salvar">💾 Salvar</button>
        <button @click="fechar" class="btn-fechar">✕ Fechar</button>
      </div>
    </div>
    <div ref="editor" class="quill-editor"></div>
  </div>
</template>

<script>
import Quill from "quill";
import "quill/dist/quill.snow.css";

export default {
  name: "EditorProva",
  props: {
    provaId: {
      type: Number,
      default: null,
    },
    titulo: {
      type: String,
      default: "Nova Prova",
    },
  },
  data() {
    return {
      quill: null,
      conteudo: "",
      autoSaveInterval: null,
    };
  },
  mounted() {
    this.inicializarEditor();
    this.carregarConteudo();

    this.autoSaveInterval = setInterval(() => {
      this.salvarAutomaticamente();
    }, 30000);
  },
  beforeUnmount() {
    if (this.autoSaveInterval) {
      clearInterval(this.autoSaveInterval);
    }
    if (this.quill) {
      this.quill = null;
    }
  },
  methods: {
    inicializarEditor() {
      const opcoes = {
        theme: "snow",
        modules: {
          toolbar: {
            container: [
              [{ header: [1, 2, 3, 4, 5, 6, false] }],
              ["bold", "italic", "underline", "strike"],
              ["blockquote", "code-block"],
              [{ list: "ordered" }, { list: "bullet" }],
              [{ script: "sub" }, { script: "super" }],
              [{ indent: "-1" }, { indent: "+1" }],
              [{ align: [] }],
              ["link", "image", "video"],
              ["clean"],
            ],
            handlers: {
              image: this.imageHandler,
            },
          },
        },
      };

      this.quill = new Quill(this.$refs.editor, opcoes);

      this.quill.on("text-change", () => {
        this.conteudo = this.quill.root.innerHTML;
      });
    },

    imageHandler() {
      const input = document.createElement("input");
      input.setAttribute("type", "file");
      input.setAttribute("accept", "image/*");
      input.click();

      input.onchange = () => {
        const file = input.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (e) => {
          try {
            // Usa um try-catch para capturar qualquer erro
            const range = this.quill.getSelection();
            const position = range ? range.index : this.quill.getLength();
            this.quill.insertEmbed(position, "image", e.target.result);
          } catch (error) {
            // Se der erro, insere no final
            try {
              const position = this.quill.getLength();
              this.quill.insertEmbed(position, "image", e.target.result);
            } catch (err) {
              console.error("Erro ao inserir imagem:", err);
            }
          }
        };
        reader.readAsDataURL(file);
      };
    },

    carregarConteudo() {
      if (this.provaId) {
        const provas = JSON.parse(localStorage.getItem("provas") || "[]");
        const prova = provas.find((p) => p.id === this.provaId);
        if (prova && prova.conteudo) {
          this.quill.root.innerHTML = prova.conteudo;
          this.conteudo = prova.conteudo;
        }
      }
    },

    salvar() {
      const conteudoAtual = this.quill.root.innerHTML;
      const provas = JSON.parse(localStorage.getItem("provas") || "[]");

      if (this.provaId) {
        const index = provas.findIndex((p) => p.id === this.provaId);
        if (index !== -1) {
          provas[index].conteudo = conteudoAtual;
          provas[index].atualizadoEm = new Date().toISOString();
        }
      } else {
        const novaProva = {
          id: Date.now(),
          titulo:
            this.titulo || `Prova ${new Date().toLocaleDateString("pt-BR")}`,
          conteudo: conteudoAtual,
          status: "rascunho",
          criadaEm: new Date().toISOString(),
          atualizadoEm: new Date().toISOString(),
        };
        provas.push(novaProva);
      }

      localStorage.setItem("provas", JSON.stringify(provas));

      window.$modal.abrir({
        titulo: "Sucesso",
        mensagem: "Prova salva com sucesso!",
        tipo: "pequeno",
      });

      setTimeout(() => {
        const modal = document.querySelector(".modal-overlay");
        if (modal) modal.click();
      }, 1500);
    },

    salvarAutomaticamente() {
      if (this.quill) {
        const conteudoAtual = this.quill.root.innerHTML;
        if (conteudoAtual !== this.conteudo) {
          this.salvar();
          console.log("Auto-salvamento realizado");
        }
      }
    },

    fechar() {
      if (this.quill) {
        const conteudoAtual = this.quill.root.innerHTML;
        if (conteudoAtual !== this.conteudo) {
          window.$modal.abrir({
            titulo: "Alterações não salvas",
            mensagem:
              "Você tem alterações não salvas. Deseja salvar antes de sair?",
            tipo: "confirmacao",
            onConfirm: () => {
              this.salvar();
              this.$emit("fechar");
            },
            onCancel: () => {
              this.$emit("fechar");
            },
          });
        } else {
          this.$emit("fechar");
        }
      } else {
        this.$emit("fechar");
      }
    },
  },
};
</script>

<style scoped>
.editor-container {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 1000px;
  margin: 0 auto;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
}

.tema-escuro .editor-container {
  background: #2a2a2a;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e0e0e0;
}

.tema-escuro .editor-header {
  border-bottom-color: #404040;
}

.editor-header h2 {
  font-size: 20px;
  font-weight: 600;
  margin: 0;
  color: inherit;
}

.editor-actions {
  display: flex;
  gap: 12px;
}

.btn-salvar {
  padding: 8px 16px;
  background: #28a745;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.btn-salvar:hover {
  background: #218838;
}

.btn-fechar {
  padding: 8px 16px;
  background: #dc3545;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.btn-fechar:hover {
  background: #c82333;
}

.quill-editor {
  flex: 1;
  overflow: hidden;
  border-radius: 8px;
}

:deep(.ql-toolbar) {
  border-radius: 8px 8px 0 0;
  border-color: #e0e0e0;
}

:deep(.ql-container) {
  border-radius: 0 0 8px 8px;
  border-color: #e0e0e0;
  min-height: 400px;
}

.tema-escuro :deep(.ql-toolbar) {
  border-color: #404040;
  background: #1a1a1a;
}

.tema-escuro :deep(.ql-container) {
  border-color: #404040;
  background: #1a1a1a;
  color: #e5e5e5;
}

.tema-escuro :deep(.ql-picker-label) {
  color: #e5e5e5;
}

.tema-escuro :deep(.ql-stroke) {
  stroke: #e5e5e5;
}

.tema-escuro :deep(.ql-fill) {
  fill: #e5e5e5;
}

@media (max-width: 768px) {
  .editor-container {
    padding: 12px;
    max-height: 95vh;
  }

  .editor-header {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }

  .editor-actions {
    justify-content: flex-end;
  }
}
</style>
