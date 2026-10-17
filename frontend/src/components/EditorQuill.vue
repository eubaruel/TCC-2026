<template>
  <div class="editor-quill" :class="{ compacto }">
    <div ref="editor"></div>
  </div>
</template>

<script>
import Quill from "quill";
import "quill/dist/quill.snow.css";

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
        resolve(canvas.toDataURL("image/jpeg", QUALIDADE_IMAGEM));
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
  },
  emits: ["update:modelValue"],
  mounted() {
    // Mantido fora de data() para que a instância do Quill não se torne reativa.
    this.quill = new Quill(this.$refs.editor, {
      theme: "snow",
      placeholder: this.placeholder,
      modules: {
        toolbar: {
          container: this.compacto ? toolbarCompacta : toolbarCompleta,
          handlers: { image: this.selecionarImagem },
        },
      },
    });
    this.definirConteudo(this.modelValue);
    this.quill.on("text-change", () => {
      this.ultimoHtml = this.quill.root.innerHTML;
      this.$emit("update:modelValue", this.ultimoHtml);
    });
  },
  beforeUnmount() {
    this.quill = null;
  },
  watch: {
    modelValue(valor) {
      if (this.quill && valor !== this.ultimoHtml) this.definirConteudo(valor);
    },
  },
  methods: {
    definirConteudo(html) {
      this.ultimoHtml = html || "";
      this.quill.setContents(this.quill.clipboard.convert({ html: html || "" }), "silent");
    },
    selecionarImagem() {
      const input = document.createElement("input");
      input.type = "file";
      input.accept = "image/png, image/jpeg, image/gif, image/webp";
      input.onchange = async () => {
        const arquivo = input.files?.[0];
        if (!arquivo) return;
        try {
          const dataUrl = await lerImagemRedimensionada(arquivo);
          const selecao = this.quill.getSelection(true);
          this.quill.insertEmbed(selecao.index, "image", dataUrl, "user");
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
  background: white;
  border-radius: 8px;
}

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
  font-family: inherit;
  font-size: 14px;
}

.compacto :deep(.ql-container) {
  min-height: 48px;
}

:deep(.ql-editor img) {
  max-width: 100%;
  height: auto;
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

.tema-escuro :deep(.ql-editor.ql-blank::before) {
  color: #888;
}
</style>
