const { test } = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs"), path = require("node:path"), vm = require("node:vm");
const { transformSync } = require("@babel/core");

test("clipboard trata HTML com imagens antes da inserção e mantém o fluxo nativo para texto", () => {
  const chamadas = [];
  class Clipboard {
    constructor(options) { this.options = options; }
    onPaste(...args) { chamadas.push({ nativo: args }); }
  }
  const fonte = fs.readFileSync(path.join(__dirname, "../src/utils/clipboardQuestao.js"), "utf8");
  const contexto = { exports: {}, require: nome => {
    assert.equal(nome, "quill"); return { import: modulo => { assert.equal(modulo, "modules/clipboard"); return Clipboard; } };
  } };
  vm.runInNewContext(transformSync(fonte, { babelrc: false, configFile: false, plugins: ["@babel/plugin-transform-modules-commonjs"] }).code, contexto);
  const clipboard = new contexto.exports.default({ inserirImagens: (...args) => chamadas.push({ imagens: args }) });
  const selecao = { index: 1, length: 0 }, texto = { html: "<p>Texto</p>", text: "Texto" };
  clipboard.onPaste(selecao, texto);
  clipboard.onPaste(selecao, { html: '<p>Texto<img src="imagem.png"></p>' });
  assert.deepEqual(chamadas[0].nativo, [selecao, texto]);
  assert.equal(chamadas[1].imagens[0], selecao);
  assert.match(chamadas[1].imagens[1].html, /<img/);
  assert.equal(chamadas.length, 2);
});
