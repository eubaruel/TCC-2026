<template>
  <div class="editor-quill" :class="{ compacto }" :style="expandido ? { minHeight: `${alturaOriginal}px` } : undefined">
    <dialog ref="modal" class="editor-modal" :aria-label="rotulo || 'Editor de texto'" @cancel.prevent="alternarExpansao" @click.self="alternarExpansao"></dialog>
    <dialog ref="avisoImagem" class="editor-modal editor-aviso" role="alertdialog" aria-label="Aviso sobre imagens" @close="restaurarSelecaoImagem">
      <h3>Aviso sobre imagens</h3>
      <p>{{ mensagemImagem }}</p>
      <button type="button" class="editor-expandir" @click="$refs.avisoImagem.close()">OK</button>
    </dialog>
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
        <div v-if="limiteCaracteres" :id="id ? `${id}-contador` : undefined" class="editor-contador"
          :class="{ 'proximo-limite': quantidadeCaracteres >= limiteCaracteres * 0.9, 'limite-excedido': limiteExcedido }">
          <span v-if="quantidadeCaracteres >= limiteCaracteres * 0.9" role="status">{{ limiteExcedido ? 'Limite excedido. Reduza o texto para salvar.' : 'Atenção: próximo do limite.' }}</span>
          <span class="contador-total">Caracteres de texto: {{ quantidadeCaracteres.toLocaleString('pt-BR') }} / {{ limiteCaracteres.toLocaleString('pt-BR') }}</span>
        </div>
        <div class="editor-imagens" :class="{ 'imagens-excedidas': quantidadeImagens > limiteImagens }">
          <span v-if="processandoImagens" role="status">Processando imagens...</span>
          <span>Imagens: {{ quantidadeImagens }} / {{ limiteImagens }}</span>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script>
import Quill from "quill";
import "quill/dist/quill.snow.css";
import { contarCaracteres, contarImagens, sanitizar } from "@/utils/html";
import RedimensionarImagem from "@/utils/redimensionarImagem";
import ClipboardQuestao from "@/utils/clipboardQuestao";
import { LIMITE_IMAGENS, prepararImagem } from "@/utils/imagensQuestao";

Quill.register("modules/redimensionarImagem", RedimensionarImagem);
Quill.register("modules/clipboard", ClipboardQuestao, true);
const Delta = Quill.import("delta");

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

export default {
  name: "EditorQuill",
  props: {
    modelValue: { type: String, default: "" },
    placeholder: { type: String, default: "" },
    compacto: { type: Boolean, default: false },
    id: { type: String, default: "" },
    rotulo: { type: String, default: "" },
    obrigatorio: { type: Boolean, default: false },
    limiteCaracteres: { type: Number, default: 0 },
  },
  emits: ["update:modelValue"],
  data: () => ({ expandido: false, alturaOriginal: 0, limiteImagens: LIMITE_IMAGENS, processandoImagens: false, mensagemImagem: "" }),
  computed: {
    quantidadeImagens() { return contarImagens(this.modelValue); },
    quantidadeCaracteres() { return contarCaracteres(this.modelValue); },
    limiteExcedido() { return this.limiteCaracteres > 0 && this.quantidadeCaracteres > this.limiteCaracteres; },
  },
  mounted() {
    // Mantido fora de data() para que a instância do Quill não se torne reativa.
    this.quill = new Quill(this.$refs.editor, {
      theme: "snow",
      placeholder: this.placeholder,
      modules: {
        clipboard: { inserirImagens: this.inserirImagens },
        uploader: {
          mimetypes: ["image/png", "image/jpeg", "image/gif", "image/webp"],
          handler: (selecao, arquivos) => this.inserirImagens(selecao, { arquivos }),
        },
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
    this.quill.root.setAttribute("aria-invalid", String(this.limiteExcedido));
    if (this.id && this.limiteCaracteres) this.quill.root.setAttribute("aria-describedby", `${this.id}-contador`);
    this.definirConteudo(this.modelValue);
    this.quill.on("text-change", this.atualizarConteudo);
  },
  beforeUnmount() {
    this.$refs.avisoImagem.close();
    this.fecharExpansao();
    this.quill?.getModule("redimensionarImagem")?.destroy();
    this.quill?.off("text-change", this.atualizarConteudo);
    this.quill = null;
  },
  watch: {
    limiteExcedido(valor) {
      this.quill?.root.setAttribute("aria-invalid", String(valor));
    },
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
      if (this.processandoImagens) return;
      if (contarImagens(this.quill.getSemanticHTML()) >= LIMITE_IMAGENS) {
        return this.avisarImagem("Cada campo permite até 3 imagens. Nenhuma imagem nova foi adicionada. Exclua uma imagem deste campo para inserir outra.");
      }
      const input = document.createElement("input");
      input.type = "file";
      input.accept = "image/png, image/jpeg, image/gif, image/webp";
      input.onchange = async () => {
        const arquivo = input.files?.[0];
        if (!arquivo || !this.quill) return;
        await this.inserirImagens(this.quill.getSelection(true), { arquivos: [arquivo] });
      };
      input.click();
    },
    async avisarImagem(mensagem) {
      this.selecaoAntesAviso = this.quill?.getSelection(true);
      this.mensagemImagem = mensagem;
      await this.$nextTick();
      if (this.quill && !this.$refs.avisoImagem.open) this.$refs.avisoImagem.showModal();
    },
    restaurarSelecaoImagem() {
      const selecao = this.selecaoAntesAviso;
      this.selecaoAntesAviso = null;
      if (this.quill && selecao) this.quill.setSelection(selecao.index, selecao.length, "silent");
    },
    async inserirImagens(selecao, { arquivos = [], html = "", text = "" }) {
      if (!this.quill || this.processandoImagens) return;
      const quill = this.quill;
      const selecionadas = quill.getContents(selecao.index, selecao.length).ops.filter(op => op.insert?.image).length;
      let vagas = Math.max(0, LIMITE_IMAGENS - contarImagens(quill.getSemanticHTML()) + selecionadas);
      const trecho = document.createElement("div");
      trecho.innerHTML = sanitizar(html);
      const imagens = [...trecho.querySelectorAll("img")];
      let conteudo = new Delta(), descartadas = 0, falhas = 0;
      this.processandoImagens = true;
      quill.getModule("redimensionarImagem")?.hide();
      quill.disable();
      try {
        for (const origem of imagens.length ? imagens : arquivos) {
          const elemento = imagens.includes(origem) ? origem : null;
          if (!vagas) {
            descartadas++;
            elemento?.remove();
            continue;
          }
          try {
            const imagem = await prepararImagem(elemento ? elemento.getAttribute("src") || "" : origem);
            vagas--;
            const dimensoes = { width: String(imagem.largura), height: String(imagem.altura) };
            if (elemento) {
              elemento.removeAttribute("style");
              elemento.setAttribute("src", imagem.dataUrl);
              Object.entries(dimensoes).forEach(([nome, valor]) => elemento.setAttribute(nome, valor));
            } else conteudo = conteudo.insert({ image: imagem.dataUrl }, dimensoes);
          } catch (_) { falhas++; elemento?.remove(); }
        }
        if (html) conteudo = quill.clipboard.convert({ html: trecho.innerHTML, text });
        if (this.quill !== quill) return;
        quill.enable();
        if (conteudo.length()) {
          quill.history.cutoff();
          quill.updateContents(new Delta().retain(selecao.index).delete(selecao.length).concat(conteudo), "user");
          quill.history.cutoff();
          quill.setSelection(selecao.index + conteudo.length(), 0, "silent");
        }
        if (descartadas || falhas) {
          const aviso = [];
          if (descartadas) aviso.push(`${descartadas === 1 ? 'Uma imagem excedente foi descartada' : `${descartadas} imagens excedentes foram descartadas`}: cada campo permite até 3 imagens. Somente as imagens excedentes desta inserção foram descartadas.`);
          if (falhas) aviso.push("Não foi possível ler ou reduzir uma ou mais imagens. Baixe o arquivo e use o botão de imagem do editor.");
          if (html) aviso.push("O restante do conteúdo colado foi mantido.");
          await this.avisarImagem(aviso.join(" "));
        }
      } catch (_) {
        if (this.quill === quill) await this.avisarImagem("Não foi possível inserir o conteúdo. As imagens existentes foram preservadas. Tente novamente.");
      } finally {
        if (this.quill === quill) quill.enable();
        this.processandoImagens = false;
      }
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
.editor-imagens { display: flex; justify-content: flex-end; gap: 12px; padding: 4px 10px 6px; font-size: 12px; color: #00488b; }
.editor-imagens.imagens-excedidas { color: #a51f1f; }
.tema-escuro .editor-imagens { color: #8dc7ff; }
.tema-escuro .editor-imagens.imagens-excedidas { color: #ffb4b4; }
.editor-contador { display: flex; justify-content: space-between; flex-wrap: wrap; gap: 4px 12px; padding: 6px 10px; color: #666; font-size: 12px; }
.contador-total { margin-left: auto; white-space: nowrap; }
.editor-contador.proximo-limite { color: #805500; background: #fff3cd; }
.editor-contador.limite-excedido { color: #a51f1f; background: #fde8e8; }
.tema-escuro .editor-contador { color: #bbb; }
.tema-escuro .editor-contador.proximo-limite { color: #ffe08a; background: #493b16; }
.tema-escuro .editor-contador.limite-excedido { color: #ffb4b4; background: #4b2424; }
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
.editor-aviso { width: min(90vw, 440px); height: fit-content; max-height: 80vh; padding: 20px; flex-direction: column; gap: 16px; overflow-y: auto; }
.editor-aviso h3, .editor-aviso p { margin: 0; }
.editor-aviso p { line-height: 1.5; }
.editor-aviso .editor-expandir { position: static; align-self: flex-end; }
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
