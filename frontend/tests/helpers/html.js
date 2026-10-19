const fs = require("node:fs"), path = require("node:path"), vm = require("node:vm");
const { transformSync } = require("@babel/core");
const { parseFragment, serialize } = require("parse5");

// DOM mínimo para testar o utilitário real sem adicionar dependências.
// A sanitização é simulada; o navegador verifica a integração com DOMPurify.
const texto = no => no.nodeName === "#text" ? no.value : (no.childNodes || []).map(texto).join("");
function criarElementoHTML() {
  let raiz = parseFragment("");
  return {
    set innerHTML(html) { raiz = parseFragment(html); },
    get innerHTML() { return serialize(raiz); },
    get textContent() { return texto(raiz); },
    querySelectorAll(seletor) {
      if (seletor !== "img") throw new Error(`Seletor não simulado: ${seletor}`);
      const encontrados = [];
      const visitar = no => {
        if (no.tagName === "img") encontrados.push({
          getAttribute: nome => no.attrs.find(a => a.name === nome)?.value ?? null,
          setAttribute: (nome, valor) => {
            const atributo = no.attrs.find(a => a.name === nome);
            if (atributo) atributo.value = valor;
            else no.attrs.push({ name: nome, value: valor });
          },
          removeAttribute: nome => { no.attrs = no.attrs.filter(a => a.name !== nome); },
          remove: () => { no.parentNode.childNodes = no.parentNode.childNodes.filter(filho => filho !== no); },
        });
        (no.childNodes || []).forEach(visitar);
      };
      visitar(raiz);
      return encontrados;
    },
  };
}
const fonte = fs.readFileSync(path.join(__dirname, "../../src/utils/html.js"), "utf8");
const codigo = transformSync(fonte, { babelrc: false, configFile: false, plugins: ["@babel/plugin-transform-modules-commonjs"] }).code;
const contexto = {
  exports: {}, document: { createElement: criarElementoHTML },
  require: nome => {
    if (nome !== "dompurify") throw new Error(`Importação inesperada: ${nome}`);
    return { sanitize: html => html.replace(/<(script|style)\b[^>]*>[\s\S]*?<\/\1>/gi, "") };
  },
};
vm.runInNewContext(codigo, contexto);
module.exports = { ...contexto.exports, criarElementoHTML };
