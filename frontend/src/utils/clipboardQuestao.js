import Quill from "quill";

const Clipboard = Quill.import("modules/clipboard");

// Texto sem imagens continua no fluxo nativo de colagem do Quill.
export default class ClipboardQuestao extends Clipboard {
  onPaste(selecao, conteudo) {
    if (/<img\b/i.test(conteudo.html || "") && this.options.inserirImagens) {
      return this.options.inserirImagens(selecao, conteudo);
    }
    return super.onPaste(selecao, conteudo);
  }
}
