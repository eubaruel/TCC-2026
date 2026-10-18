import QuillResize from "quill-resize-module";
import "quill-resize-module/dist/resize.css";

// CSS usa 45 mm; os atributos da imagem e o arraste trabalham com pixels.
export const ALTURA_MAXIMA_IMAGEM_PX = Math.floor(45 * 96 / 25.4);

// O módulo fornece as quatro alças; esta extensão também encerra um arraste interrompido.
class AlcasImagem extends QuillResize.Modules.Resize {
  onDestroy() {
    document.removeEventListener("mousemove", this.handleDragProxy);
    document.removeEventListener("touchmove", this.handleDragProxy);
    document.removeEventListener("mouseup", this.handleMouseupProxy, true);
    document.removeEventListener("touchend", this.handleMouseupProxy, true);
    document.removeEventListener("touchcancel", this.handleMouseupProxy, true);
    super.onDestroy();
  }
}

class LixeiraImagem extends QuillResize.Modules.Base {
  onCreate() {
    this.botao = document.createElement("button");
    this.botao.type = "button";
    this.botao.className = "ql-imagem-excluir";
    this.botao.title = "Excluir imagem";
    this.botao.setAttribute("aria-label", "Excluir imagem");
    this.botao.innerHTML = '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M3 6h18M9 6V3h6v3M5 6l1 15h12l1-15M10 10v7M14 10v7"/></svg>';
    this.botao.onmousedown = evento => evento.preventDefault();
    this.botao.onclick = evento => {
      evento.preventDefault();
      evento.stopPropagation();
      if (!this.quill.root.contains(this.activeEle)) return;
      const indice = this.quill.getIndex(this.blot);
      this.resizer.hide();
      this.quill.history.cutoff();
      this.quill.deleteText(indice, 1, "user");
      this.quill.history.cutoff();
      this.quill.setSelection(indice, 0, "silent");
    };
    this.overlay.appendChild(this.botao);
  }

  onDestroy() {
    this.botao.remove();
    this.botao.onmousedown = null;
    this.botao.onclick = null;
  }
}

export default class RedimensionarImagem extends QuillResize {
  constructor(quill) {
    super(quill, {
      modules: [AlcasImagem, "DisplaySize", LixeiraImagem],
      keyboardSelect: false, selectedClass: "", activeClass: "", embedTags: [],
      parchment: { image: { attribute: ["width"], limit: { minWidth: 16 } } },
      onActive(blot, imagem) {
        const estilo = getComputedStyle(this.quill.root);
        const larguraEditor = this.quill.root.clientWidth - parseFloat(estilo.paddingLeft) - parseFloat(estilo.paddingRight);
        const limite = this.options.parchment.image.limit;
        limite.maxWidth = Math.max(16, Math.floor(larguraEditor));
        limite.maxHeight = ALTURA_MAXIMA_IMAGEM_PX;
        limite.ratio = (imagem.naturalHeight || imagem.offsetHeight) / (imagem.naturalWidth || imagem.offsetWidth);
      },
      onChangeSize() { this.quill.update("user"); },
    });
    this.fecharAoSair = (evento) => {
      if (!this.quill.container.contains(evento.target)) this.hide();
    };
    this.fecharAoRedimensionar = () => this.hide();
    document.addEventListener("mousedown", this.fecharAoSair, true);
    document.addEventListener("touchstart", this.fecharAoSair, true);
    window.addEventListener("resize", this.fecharAoRedimensionar);
  }

  destroy() {
    this.hide();
    document.removeEventListener("mousedown", this.fecharAoSair, true);
    document.removeEventListener("touchstart", this.fecharAoSair, true);
    window.removeEventListener("resize", this.fecharAoRedimensionar);
  }
}
