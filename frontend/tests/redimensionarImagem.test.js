const { test } = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs"), path = require("node:path"), vm = require("node:vm");
const { transformSync } = require("@babel/core");

function ambiente(larguraEditor = 800) {
  const listeners = [], removidos = [], atualizacoes = [];
  const eventos = {
    addEventListener: (...args) => listeners.push(args), removeEventListener: (...args) => removidos.push(args),
    createElement: tag => ({ tag, atributos: {}, setAttribute(nome, valor) { this.atributos[nome] = valor; }, remove() { this.removido = true; } }),
  };
  class ResizeSimulado {
    static Modules = {
      Resize: class { onDestroy() { this.finalizado = true; } },
      Base: class { constructor(resizer) { Object.assign(this, resizer); this.resizer = resizer; } },
    };
    constructor(quill, options) { this.quill = quill; this.options = options; }
    hide() { this.oculto = true; }
  }
  const fonte = fs.readFileSync(path.join(__dirname, "../src/utils/redimensionarImagem.js"), "utf8");
  const codigo = transformSync(fonte, { babelrc: false, configFile: false, plugins: ["@babel/plugin-transform-modules-commonjs"] }).code;
  const modulos = {
    "quill-resize-module": ResizeSimulado, "quill-resize-module/dist/resize.css": {},
  };
  const contexto = { exports: {}, document: eventos, window: eventos,
    getComputedStyle: () => ({ paddingLeft: "15px", paddingRight: "15px" }),
    require: nome => { assert.ok(nome in modulos); return modulos[nome]; } };
  vm.runInNewContext(codigo, contexto);
  const interno = {};
  const quill = { root: { clientWidth: larguraEditor }, container: { contains: alvo => alvo === interno }, update: origem => atualizacoes.push(origem) };
  return { modulo: new contexto.exports.default(quill), listeners, removidos, atualizacoes, interno };
}

test("alças preservam proporção, limitam altura a 45 mm e largura somente ao editor", () => {
  for (const larguraEditor of [800, 350]) {
    const { modulo } = ambiente(larguraEditor);
    assert.equal(modulo.options.modules[1], "DisplaySize");
    assert.equal(modulo.options.modules.length, 3);
    assert.deepEqual([...modulo.options.parchment.image.attribute], ["width"]);
    assert.equal(modulo.options.parchment.video, undefined);
    modulo.options.onActive.call(modulo, {}, { naturalWidth: 800, naturalHeight: 400 });
    const limite = modulo.options.parchment.image.limit;
    assert.equal(limite.ratio, .5);
    assert.equal(limite.maxWidth, larguraEditor - 30);
    assert.equal(limite.maxHeight, Math.floor(45 * 96 / 25.4));
    modulo.options.onActive.call(modulo, {}, { naturalWidth: 200, naturalHeight: 600 });
    assert.equal(limite.ratio, 3);
  }
});

function lixeira() {
  const { modulo } = ambiente();
  const chamadas = [], imagem = {}, blot = {};
  let anexado;
  const resizer = {
    activeEle: imagem, blot,
    overlay: { appendChild: botao => { anexado = botao; } },
    hide: () => chamadas.push(["hide"]),
    quill: {
      root: { contains: alvo => alvo === imagem },
      getIndex: alvo => { assert.equal(alvo, blot); return 7; },
      history: { cutoff: () => chamadas.push(["cutoff"]) },
      deleteText: (...args) => chamadas.push(["deleteText", ...args]),
      setSelection: (...args) => chamadas.push(["setSelection", ...args]),
    },
  };
  const Lixeira = modulo.options.modules[2];
  const controle = new Lixeira(resizer);
  controle.onCreate();
  return { controle, botao: anexado, resizer, chamadas };
}

test("lixeira acessível fica no overlay, não envia formulário e exclui apenas o embed selecionado pelo Quill", () => {
  const { botao, chamadas } = lixeira();
  assert.equal(botao.tag, "button");
  assert.equal(botao.type, "button");
  assert.equal(botao.atributos["aria-label"], "Excluir imagem");
  let prevenidos = 0, propagacoes = 0;
  const evento = { preventDefault: () => prevenidos++, stopPropagation: () => propagacoes++ };
  botao.onmousedown(evento);
  botao.onclick(evento);
  assert.equal(prevenidos, 2);
  assert.equal(propagacoes, 1);
  assert.deepEqual(chamadas, [
    ["hide"], ["cutoff"], ["deleteText", 7, 1, "user"], ["cutoff"], ["setSelection", 7, 0, "silent"],
  ]);
});

test("lixeira não exclui uma imagem já removida e limpa botão e handlers ao fechar", () => {
  const { controle, botao, resizer, chamadas } = lixeira();
  resizer.quill.root.contains = () => false;
  botao.onclick({ preventDefault() {}, stopPropagation() {} });
  assert.deepEqual(chamadas, []);
  controle.onDestroy();
  assert.equal(botao.removido, true);
  assert.equal(botao.onclick, null);
  assert.equal(botao.onmousedown, null);
});

test("fim do arraste atualiza o HTML pelo Quill e clique externo fecha a seleção", () => {
  const { modulo, atualizacoes, interno } = ambiente();
  modulo.options.onChangeSize.call(modulo);
  assert.deepEqual(atualizacoes, ["user"]);
  modulo.fecharAoSair({ target: interno });
  assert.equal(modulo.oculto, undefined);
  modulo.fecharAoSair({ target: {} });
  assert.equal(modulo.oculto, true);
});

test("desmontagem encerra arrastes e remove os listeners de mouse, toque e janela", () => {
  const { modulo, listeners, removidos } = ambiente();
  const Alcas = modulo.options.modules[0];
  const alcas = new Alcas();
  alcas.handleDragProxy = () => {}; alcas.handleMouseupProxy = () => {};
  alcas.onDestroy();
  assert.equal(alcas.finalizado, true);
  for (const tipo of ["mousemove", "touchmove", "mouseup", "touchend", "touchcancel"]) assert.ok(removidos.some(([evento]) => evento === tipo));
  modulo.destroy();
  assert.equal(modulo.oculto, true);
  for (const [tipo, listener, captura] of listeners) assert.ok(removidos.some(item => item[0] === tipo && item[1] === listener && item[2] === captura));
});
