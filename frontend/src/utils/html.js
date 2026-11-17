import DOMPurify from "dompurify";

const configuracao = {
  ALLOWED_TAGS: [
    "p", "br", "span", "strong", "b", "em", "i", "u", "s", "sub", "sup",
    "ol", "ul", "li", "img", "h1", "h2", "h3", "blockquote", "pre", "code",
    "table", "thead", "tbody", "tr", "th", "td", "div", "header", "section", "hr",
  ],
  ALLOWED_ATTR: ["src", "alt", "width", "height", "class", "style", "data-list", "colspan", "rowspan"],
  // Dimensões não são URLs; não devem passar pela restrição de protocolos abaixo.
  ADD_URI_SAFE_ATTR: ["width", "height"],
  ALLOWED_URI_REGEXP: /^(?:data:image\/(?:png|jpe?g|gif|webp);base64,|https?:)/i,
};

export const sanitizar = (html) => DOMPurify.sanitize(html || "", configuracao);

export const contarImagens = (html) => {
  const div = document.createElement("div");
  div.innerHTML = sanitizar(html);
  return div.querySelectorAll("img").length;
};

// Diferente do resumo, não remove nem agrupa espaços. Entidades HTML contam como texto.
export const contarCaracteres = (html) => {
  const div = document.createElement("div");
  div.innerHTML = sanitizar(html);
  return Array.from(div.textContent || "").length;
};

export const textoPuro = (html) => {
  const div = document.createElement("div");
  div.innerHTML = sanitizar(html);
  return (div.textContent || "").replace(/\s+/g, " ").trim();
};

// Um editor Quill vazio produz "<p><br></p>"; considera preenchido quem tem texto ou imagem.
export const htmlVazio = (html) => !textoPuro(html) && !/<img\s/i.test(html || "");

// O Quill 2 grava cada espaço como &nbsp;, o que impede a quebra de linha e faz o texto
// extrapolar a tela. Mantém &nbsp; só onde preserva espaços consecutivos; <pre> fica intacto.
const NBSP = /&nbsp;|&#160;|&#xa0;| /gi;
export const normalizarEspacos = (html) =>
  String(html ?? "")
    .split(/(<pre\b[\s\S]*?<\/pre>)/i)
    .map((parte, i) => (i % 2 ? parte : parte.replace(NBSP, " ")
      .replace(/[  ]+/g, (espacos) => " " + "&nbsp;".repeat(espacos.length - 1))))
    .join("");

export const escaparHtml = (texto) =>
  String(texto ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
