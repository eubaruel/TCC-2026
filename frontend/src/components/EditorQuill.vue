<template>
  <div class="editor-quill" :class="{ compacto }" :style="expandido ? { minHeight: `${alturaOriginal}px` } : undefined">
    <dialog ref="modal" class="editor-modal" :aria-label="rotulo || 'Editor de texto'" @cancel.prevent="alternarExpansao" @click.self="alternarExpansao"></dialog>
    <Teleport :to="expandido ? $refs.modal : 'body'" :disabled="!expandido">
      <div ref="painel" class="editor-painel" :class="{ expandido }">
        <div class="editor-acoes">
          <h3 v-if="expandido">{{ rotulo || 'Editor de texto' }}</h3>
          <button
            ref="botaoExpandir"
            type="button"
            class="editor-expandir"
            :aria-expanded="expandido"
            :aria-controls="id || undefined"
            :aria-label="`${expandido ? 'Fechar editor de' : 'Expandir'} ${rotulo || 'campo de texto'}`"
            @click="alternarExpansao"
          >
            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
              <path v-if="expandido" d="m6 6 12 12M6 18 18 6" />
              <path v-else d="M8 3H3v5m13 13h5v-5M3 3l6 6m12 12-6-6" />
            </svg>
            {{ expandido ? 'Fechar' : 'Expandir' }}
          </button>
        </div>
        <div ref="editor"></div>
      </div>
    </Teleport>
  </div>
</template>

<script>
import Quill from "quill";
import "quill/dist/quill.snow.css";
import { sanitizar } from "@/utils/html";
import RedimensionarImagem, { ALTURA_MAXIMA_IMAGEM_PX } from "@/utils/redimensionarImagem";

Quill.register("modules/redimensionarImagem", RedimensionarImagem);

const LARGURA_MAXIMA_IMAGEM = 1000;
const QUALIDADE_IMAGEM = 0.8;

const toolbarCompleta = [
  ["bold", "italic", "underline", "strike"],
  [{ script: "sub" }, { script: "super" }],
  [{ list: "ordered" }, { list: "bullet" }],
  [{ align: [] }],
  ["image"],
  ["clean"],
];

const toolbarCompacta = [
  ["bold", "italic", "underline"],
  [{ script: "sub" }, { script: "super" }],
  ["image"],
  ["clean"],
];

// Redimensiona a imagem antes de embuti-la em base64: o backend não possui upload
// e cada questão é salva como um único documento no MongoDB (limite de 16 MB).
const lerImagemRedimensionada = (arquivo) =>
  new Promise((resolve, reject) => {
    const leitor = new FileReader();
    leitor.onerror = () => reject(new Error("Não foi possível ler a imagem."));
    leitor.onload = () => {
      const imagem = new Image();
      imagem.onerror = () => reject(new Error("Arquivo de imagem inválido."));
      imagem.onload = () => {
        const escala = Math.min(1, LARGURA_MAXIMA_IMAGEM / imagem.width);
        const canvas = document.createElement("canvas");
        canvas.width = Math.round(imagem.width * escala);
        canvas.height = Math.round(imagem.height * escala);
        const contexto = canvas.getContext("2d");
        contexto.fillStyle = "#ffffff";
        contexto.fillRect(0, 0, canvas.width, canvas.height);
        contexto.drawImage(imagem, 0, 0, canvas.width, canvas.height);
        // Limita a exibição sem reduzir a resolução do arquivo para apenas 96 dpi.
        const escalaExibicao = Math.min(1, ALTURA_MAXIMA_IMAGEM_PX / canvas.height);
        resolve({
          dataUrl: canvas.toDataURL("image/jpeg", QUALIDADE_IMAGEM),
          largura: Math.max(1, Math.floor(canvas.width * escalaExibicao)),
          altura: Math.max(1, Math.floor(canvas.height * escalaExibicao)),
        });
      };
      imagem.src = leitor.result;
    };
    leitor.readAsDataURL(arquivo);
  });

export default {
  name: "EditorQuill",
  props: {
    modelValue: { type: String, default: "" },
    placeholder: { type: String, default: "" },
    compacto: { type: Boolean, default: false },
    id: { type: String, default: "" },
    rotulo: { type: String, default: "" },
    obrigatorio: { type: Boolean, default: false },
  },
  emits: ["update:modelValue"],
  data: () => ({ expandido: false, alturaOriginal: 0 }),
  mounted() {
    // Mantido fora de data() para que a instância do Quill não se torne reativa.
    this.quill = new Quill(this.$refs.editor, {
      theme: "snow",
      placeholder: this.placeholder,
      modules: {
        redimensionarImagem: true,
        toolbar: {
          container: this.compacto ? toolbarCompacta : toolbarCompleta,
          handlers: { image: this.selecionarImagem },
        },
      },
    });
    this.quill.root.id = this.id;
    this.quill.root.setAttribute("role", "textbox");
    this.quill.root.setAttribute("aria-label", this.rotulo);
    this.quill.root.setAttribute("aria-multiline", "true");
    this.quill.root.setAttribute("aria-required", String(this.obrigatorio));
    this.definirConteudo(this.modelValue);
    this.quill.on("text-change", this.atualizarConteudo);
  },
  beforeUnmount() {
    this.fecharExpansao();
    this.quill?.getModule("redimensionarImagem")?.destroy();
    this.quill?.off("text-change", this.atualizarConteudo);
    this.quill = null;
  },
  watch: {
    modelValue(valor) {
      if (this.quill && valor !== this.ultimoHtml) this.definirConteudo(valor);
    },
  },
  methods: {
    async alternarExpansao() {
      if (this.expandido) {
        this.fecharExpansao();
        await this.$nextTick();
        this.$refs.botaoExpandir?.focus();
        return;
      }
      this.quill.getModule("redimensionarImagem")?.hide();
      this.alturaOriginal = this.$refs.painel.getBoundingClientRect().height;
      this.rolagemAnterior = document.body.style.overflow;
      this.expandido = true;
      await this.$nextTick();
      if (!this.expandido || !this.quill) return;
      document.body.style.overflow = "hidden";
      this.$refs.modal.showModal();
      this.quill.focus();
    },
    fecharExpansao() {
      if (!this.expandido) return;
      this.quill?.getModule("redimensionarImagem")?.hide();
      this.$refs.modal.close();
      this.expandido = false;
      document.body.style.overflow = this.rolagemAnterior;
    },
    atualizarConteudo() {
      this.ultimoHtml = sanitizar(this.quill.getSemanticHTML());
      this.$emit("update:modelValue", this.ultimoHtml);
    },
    definirConteudo(html) {
      this.quill.getModule("redimensionarImagem")?.hide();
      this.ultimoHtml = html || "";
      this.quill.setContents(this.quill.clipboard.convert({ html: sanitizar(html) }), "silent");
      this.quill.history.clear();
    },
    selecionarImagem() {
      const input = document.createElement("input");
      input.type = "file";
      input.accept = "image/png, image/jpeg, image/gif, image/webp";
      input.onchange = async () => {
        const arquivo = input.files?.[0];
        if (!arquivo) return;
        try {
          const { dataUrl, largura, altura } = await lerImagemRedimensionada(arquivo);
          if (!this.quill) return;
          const selecao = this.quill.getSelection(true);
          // Uma única alteração insere a imagem já dimensionada e permite desfazer.
          this.quill.updateContents([
            { retain: selecao.index },
            { insert: { image: dataUrl }, attributes: { width: String(largura), height: String(altura) } },
          ], "user");
          this.quill.setSelection(selecao.index + 1, 0, "silent");
        } catch (error) {
          window.$modal?.abrir({ titulo: "Erro", mensagem: error.message, tipo: "alerta" });
        }
      };
      input.click();
    },
  },
};
</script>

<style scoped>
.editor-quill {
  min-width: 0;
  background: white;
  border-radius: 8px;
}

.editor-painel { position: relative; min-width: 0; }
.editor-modal {
  width: 92vw;
  max-width: 1200px;
  height: 88vh;
  max-height: 900px;
  padding: 0;
  margin: auto;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  background: white;
  color: #333;
  box-shadow: 0 20px 40px #0003;
  overflow: hidden;
}
.editor-modal::backdrop { background: #0006; }
.editor-modal[open] { display: flex; }
.editor-painel.expandido { display: flex; flex-direction: column; flex: 1; min-height: 0; }
.expandido .editor-acoes { display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 14px 20px; border-bottom: 1px solid #e0e0e0; }
.editor-acoes h3 { margin: 0; font-size: 18px; font-weight: 600; }
.expandido .editor-expandir { position: static; flex-shrink: 0; }
.expandido :deep(.ql-toolbar) { padding-right: 8px; flex-shrink: 0; border-radius: 0; }
.expandido :deep(.ql-container) { flex: 1; min-height: 0; overflow: hidden; }
.expandido :deep(.ql-editor) { height: 100%; overflow-y: auto; }
.tema-escuro .editor-modal { background: #1a1a1a; color: #e5e5e5; border-color: #404040; }
.tema-escuro .expandido .editor-acoes { border-color: #404040; }

.editor-expandir {
  position: absolute;
  top: 6px;
  right: 8px;
  z-index: 1;
  display: inline-flex;
  align-items: center;
  gap: 5px;
  height: 30px;
  padding: 0 8px;
  border: 0;
  border-radius: 4px;
  background: #00488b;
  color: white;
  font-size: 13px;
  cursor: pointer;
}

.editor-expandir:hover { background: #003366; }
.editor-expandir:focus-visible { outline: 2px solid #00488b; outline-offset: 2px; }
.editor-painel:not(.expandido) :deep(.ql-toolbar) { padding-right: 110px; }

.tema-escuro .editor-quill {
  background: #1a1a1a;
}

:deep(.ql-toolbar) {
  border-radius: 8px 8px 0 0;
  border-color: #e0e0e0;
}

:deep(.ql-container) {
  border-radius: 0 0 8px 8px;
  border-color: #e0e0e0;
  min-height: 120px;
}

.compacto :deep(.ql-container) {
  min-height: 48px;
}

:deep(.ql-editor img) {
  max-width: 100%;
  height: auto;
}

:deep(.ql-resize-overlay) { border-color: #00488b; }
:deep(.ql-resize-handle) { width: 14px; height: 14px; border-color: #00488b; background: #00488b; opacity: 1; }
:deep(.ql-resize-display) { font: 12px Arial, sans-serif; border-color: #00488b; }

:deep(.ql-imagem-excluir) {
  position: absolute;
  top: 6px;
  left: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  padding: 0;
  border: 0;
  border-radius: 4px;
  background: #c62828;
  color: white;
  cursor: pointer;
  pointer-events: auto;
  box-shadow: 0 1px 4px #0004;
}

:deep(.ql-imagem-excluir:hover) { background: #a51f1f; }
:deep(.ql-imagem-excluir:focus-visible) { outline: 2px solid #00488b; outline-offset: 2px; }

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

.tema-escuro :deep(.ql-editor.ql-blank::before) {
  color: #888;
}
</style>
