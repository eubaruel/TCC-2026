import DOMPurify from "dompurify";

const configuracao = {
  ALLOWED_TAGS: [
    "p", "br", "span", "strong", "b", "em", "i", "u", "s", "sub", "sup",
    "ol", "ul", "li", "img", "h1", "h2", "h3", "blockquote", "pre", "code",
    "table", "thead", "tbody", "tr", "th", "td", "div", "header", "section", "hr",
  ],
  ALLOWED_ATTR: ["src", "alt", "width", "height", "class", "style", "data-list", "colspan", "rowspan"],
  ALLOWED_URI_REGEXP: /^(?:data:image\/(?:png|jpe?g|gif|webp);base64,|https?:)/i,
};

export const sanitizar = (html) => DOMPurify.sanitize(html || "", configuracao);

export const textoPuro = (html) => {
  const div = document.createElement("div");
  div.innerHTML = sanitizar(html);
  return (div.textContent || "").replace(/\s+/g, " ").trim();
};

// Um editor Quill vazio produz "<p><br></p>"; considera preenchido quem tem texto ou imagem.
export const htmlVazio = (html) => !textoPuro(html) && !/<img\s/i.test(html || "");

export const escaparHtml = (texto) =>
  String(texto ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
