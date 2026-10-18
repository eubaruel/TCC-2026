const { test } = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs"), path = require("node:path");
const postcss = require("postcss");

const ler = arquivo => fs.readFileSync(path.join(__dirname, "../src", arquivo), "utf8");

test("tipografia compartilhada fixa Arial 10 pt inclusive em HTML com fonte própria, sem afetar o gabarito", () => {
  const css = postcss.parse(ler("assets/css/texto_questao.css"));
  const regras = css.nodes.filter(no => no.type === "rule");
  const regra = regras[0];
  assert.deepEqual(regra.selectors, [".texto-questao", ".texto-questao *", ".editor-quill .ql-editor", ".editor-quill .ql-editor *"]);
  const fonte = regra.nodes.find(no => no.prop === "font-family");
  const tamanho = regra.nodes.find(no => no.prop === "font-size");
  assert.equal(fonte.value, "Arial, sans-serif"); assert.equal(fonte.important, true);
  assert.equal(tamanho.value, "10pt"); assert.equal(tamanho.important, true);
  assert.ok(regra.nodes.every(no => !["font-weight", "font-style"].includes(no.prop)));
  assert.match(ler("main.js"), /import "\.\/assets\/css\/texto_questao\.css"/);
  assert.doesNotMatch(ler("components/CartaoResposta.vue"), /texto-questao/);
  assert.doesNotMatch(ler("components/NotaSobreposta.vue"), /texto-questao/);
});

test("imagens do conteúdo respeitam 45 mm inclusive com HTML antigo, sem limitar largura nem afetar cartão", () => {
  const css = postcss.parse(ler("assets/css/texto_questao.css"));
  const regra = css.nodes.find(no => no.type === "rule" && no.selectors.includes(".texto-questao img"));
  assert.deepEqual(regra.selectors, [".texto-questao img", ".editor-quill .ql-editor img"]);
  const altura = regra.nodes.find(no => no.prop === "max-height");
  assert.equal(altura.value, "45mm");
  assert.equal(altura.important, true);
  assert.ok(regra.nodes.some(no => no.prop === "height" && no.value === "auto" && no.important));
  assert.ok(regra.nodes.some(no => no.prop === "object-fit" && no.value === "contain"));
  assert.ok(regra.nodes.every(no => !["width", "max-width"].includes(no.prop)));
});

test("prévia, impressão e leitura das questões aplicam o mesmo estilo ao enunciado e às alternativas", () => {
  assert.match(ler("components/PreviewProva.vue"), /class="conteudo-prova texto-questao"/);
  assert.match(ler("components/QuestaoEditor.vue"), /class="alternativa-editor texto-questao"/);
  assert.match(ler("views/CriarProvaView.vue"), /class="alternativas texto-questao"/);
  const questoes = ler("views/QuestoesView.vue");
  assert.equal((questoes.match(/class="questao-texto texto-questao"/g) || []).length, 2);
  assert.equal((questoes.match(/class="alternativas texto-questao"/g) || []).length, 2);
});
