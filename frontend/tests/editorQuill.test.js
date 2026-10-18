const { test } = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs"), path = require("node:path"), vm = require("node:vm");
const { parse } = require("@vue/compiler-sfc");
const { transformSync } = require("@babel/core");
const { contarCaracteres, contarImagens, criarElementoHTML } = require("./helpers/html");
const Delta = require("quill-delta");
const { parseFragment } = require("parse5");

function converterHtml(html) {
  let delta = new Delta();
  const visitar = no => {
    if (no.nodeName === "#text") delta.insert(no.value);
    else if (no.tagName === "img") {
      const attrs = Object.fromEntries(no.attrs.map(a => [a.name, a.value]));
      delta.insert({ image: attrs.src }, { width: attrs.width, height: attrs.height });
    } else (no.childNodes || []).forEach(visitar);
  };
  visitar(parseFragment(html || ""));
  delta.html = html;
  return delta;
}

function ambiente(larguraImagem = 1000, alturaImagem = 400, falharImagem = false) {
  const instancias = [], eventos = [], inputs = [], canvases = [];
  const corpo = { style: { overflow: "auto" } };
  class QuillSimulado {
    static register() {}
    static import(nome) { assert.equal(nome, "delta"); return Delta; }
    constructor(elemento, opcoes) {
      this.elemento = elemento; this.opcoes = opcoes; this.atributos = {}; this.conteudos = [];
      this.root = { innerHTML: "", setAttribute: (nome, valor) => { this.atributos[nome] = valor; } };
      this.clipboard = { convert: (conteudo) => converterHtml(conteudo.html) };
      this.history = { cutoff() {}, clear: () => { this.historicosLimpos = (this.historicosLimpos || 0) + 1; } };
      this.redimensionador = { hide: () => { this.selecoesImagemFechadas = (this.selecoesImagemFechadas || 0) + 1; }, destroy: () => { this.redimensionador.destruido = true; } };
      instancias.push(this);
    }
    setContents(conteudo, origem) { this.conteudos.push({ conteudo, origem }); this.root.innerHTML = conteudo.html; }
    getSemanticHTML() { this.exportacoes = (this.exportacoes || 0) + 1; return this.root.innerHTML; }
    getModule() { return this.redimensionador; }
    disable() { this.desabilitado = true; }
    enable() { this.desabilitado = false; }
    focus() { this.focado = true; }
    getSelection() { return this.intervalo || { index: 3, length: 0 }; }
    getContents(indice, tamanho) {
      const conteudo = converterHtml(this.root.innerHTML);
      return indice === undefined ? conteudo : conteudo.slice(indice, indice + tamanho);
    }
    setSelection(...args) { this.selecao = args; }
    updateContents(operacoes, origem) {
      const ops = operacoes.ops || operacoes;
      this.insercao = JSON.parse(JSON.stringify({ operacoes: ops, origem }));
      const resultado = this.getContents().compose(new Delta(ops));
      this.root.innerHTML = `<p>${resultado.ops.map(op => op.insert?.image
        ? `<img src="${op.insert.image}" width="${op.attributes?.width}" height="${op.attributes?.height}">`
        : typeof op.insert === "string" ? op.insert.replace(/&/g, "&amp;").replace(/</g, "&lt;") : "").join("")}</p>`;
      this.listener();
    }
    on(nome, listener) { this.evento = nome; this.listener = listener; }
    off(nome, listener) { assert.equal(nome, this.evento); assert.equal(listener, this.listener); this.listener = null; }
  }
  const fonte = fs.readFileSync(path.join(__dirname, "../src/components/EditorQuill.vue"), "utf8");
  const script = parse(fonte).descriptor.script.content;
  const codigo = transformSync(script, { babelrc: false, configFile: false, plugins: ["@babel/plugin-transform-modules-commonjs"] }).code;
  const modulos = { quill: QuillSimulado, "quill/dist/quill.snow.css": {},
    "@/utils/redimensionarImagem": {}, "@/utils/clipboardQuestao": {},
    "@/utils/html": { contarCaracteres, contarImagens, sanitizar: (html) => (html || "").replace(/<script[\s\S]*?<\/script>/gi, "") } };
  const contexto = {
    exports: {},
    FileReader: class { readAsDataURL() { this.result = "data:image/png;base64,original"; this.onload(); } },
    Image: class {
      constructor() { this.width = larguraImagem; this.height = alturaImagem; }
      set src(valor) { if (falharImagem) this.onerror(); else this.onload(); }
    },
    document: { body: corpo, createElement: tag => {
      if (tag === "div") return criarElementoHTML();
      if (tag === "input") {
        const input = { click() {}, files: [{}] };
        inputs.push(input); return input;
      }
      assert.equal(tag, "canvas");
      const canvas = { getContext: () => ({ fillRect() {}, drawImage() {} }), toDataURL(tipo, qualidade) { this.formato = tipo; this.qualidade = qualidade; return "data:image/jpeg;base64,teste"; } };
      canvases.push(canvas); return canvas;
    } },
    require: nome => { assert.ok(nome in modulos); return modulos[nome]; },
  };
  const fonteImagens = fs.readFileSync(path.join(__dirname, "../src/utils/imagensQuestao.js"), "utf8");
  const contextoImagens = { ...contexto, exports: {} };
  vm.runInNewContext(transformSync(fonteImagens, { babelrc: false, configFile: false, plugins: ["@babel/plugin-transform-modules-commonjs"] }).code, contextoImagens);
  modulos["@/utils/imagensQuestao"] = contextoImagens.exports;
  vm.runInNewContext(codigo, contexto);
  const opcoes = contexto.exports.default;
  const criar = (props = {}) => {
    const tela = { modelValue: "", placeholder: "Digite...", compacto: false, id: "enunciado", rotulo: "Enunciado", obrigatorio: true, limiteCaracteres: 0,
      ...opcoes.data(), ...props, $nextTick: async () => {},
      $refs: {
        editor: {}, painel: { getBoundingClientRect: () => ({ height: 162 }) },
        modal: { showModal() { this.open = true; }, close() { this.open = false; } },
        avisoImagem: { showModal() { this.open = true; }, close() { this.open = false; } },
        botaoExpandir: { focus() { this.focado = true; } },
      }, $emit: (...args) => eventos.push(args) };
    Object.entries(opcoes.methods).forEach(([nome, metodo]) => { tela[nome] = metodo.bind(tela); });
    Object.entries(opcoes.computed).forEach(([nome, metodo]) => Object.defineProperty(tela, nome, { get: metodo.bind(tela) }));
    opcoes.mounted.call(tela);
    return tela;
  };
  return { criar, opcoes, instancias, eventos, inputs, canvases, corpo, imagensUtils: modulos["@/utils/imagensQuestao"] };
}

test("com três imagens o botão não abre seletor e a colagem preserva o texto e as imagens existentes", async () => {
  const { criar, inputs, canvases } = ambiente();
  const img = '<img src="data:image/jpeg;base64,antiga">';
  const tela = criar({ modelValue: img.repeat(3) });
  await tela.selecionarImagem();
  assert.equal(inputs.length, 0);
  assert.equal(tela.$refs.avisoImagem.open, true);
  assert.match(tela.mensagemImagem, /até 3 imagens/);
  tela.$refs.avisoImagem.close();
  tela.restaurarSelecaoImagem();
  assert.deepEqual(tela.quill.selecao, [3, 0, "silent"]);
  assert.equal(tela.selecaoAntesAviso, null);
  await tela.inserirImagens({ index: 0, length: 0 }, { html: `<p>Texto colado${img}</p>` });
  assert.equal(contarImagens(tela.quill.root.innerHTML), 3);
  assert.match(tela.quill.root.innerHTML, /Texto colado/);
  assert.equal(canvases.length, 0);
  assert.match(tela.mensagemImagem, /Uma imagem excedente foi descartada/);
  assert.equal(tela.$refs.avisoImagem.open, true);
});

test("colagem múltipla comprime apenas as imagens que cabem e preserva o restante do texto", async () => {
  const { criar, canvases } = ambiente(2000, 1000);
  const img = '<img src="data:image/jpeg;base64,antiga">';
  const tela = criar({ modelValue: img });
  await tela.inserirImagens({ index: 0, length: 0 }, { html: `<p><strong>Antes</strong>${img.repeat(5)}Depois</p>` });
  assert.equal(contarImagens(tela.quill.root.innerHTML), 3);
  assert.equal(canvases.length, 2);
  assert.ok(canvases.every(c => c.width === 800 && c.height === 400));
  assert.match(tela.quill.root.innerHTML, /Antes.*Depois/);
  assert.match(tela.mensagemImagem, /3 imagens excedentes foram descartadas/);
  assert.equal(tela.quill.desabilitado, false);
});

test("substituir uma imagem selecionada libera sua vaga sem ultrapassar três", async () => {
  const { criar } = ambiente();
  const tela = criar({ modelValue: '<img src="data:image/jpeg;base64,antiga">'.repeat(3) });
  await tela.inserirImagens({ index: 0, length: 1 }, { arquivos: [{}] });
  assert.equal(contarImagens(tela.quill.root.innerHTML), 3);
  assert.match(tela.quill.root.innerHTML, /base64,teste/);
  assert.equal(tela.mensagemImagem, "");
  assert.equal(tela.$refs.avisoImagem.open, undefined);
});

test("falha de leitura não elimina imagens existentes nem deixa o editor bloqueado", async () => {
  const { criar } = ambiente(1000, 400, true);
  const original = '<p>Texto<img src="data:image/jpeg;base64,antiga"></p>';
  const tela = criar({ modelValue: original });
  await tela.inserirImagens({ index: 0, length: 0 }, { arquivos: [{}] });
  assert.equal(tela.quill.root.innerHTML, original);
  assert.equal(tela.processandoImagens, false);
  assert.equal(tela.quill.desabilitado, false);
  assert.match(tela.mensagemImagem, /Não foi possível ler ou reduzir/);
});

test("inserções simultâneas não ultrapassam a cota enquanto a imagem é processada", async () => {
  const { criar, imagensUtils } = ambiente();
  const tela = criar({ modelValue: '<img src="data:image/jpeg;base64,antiga">'.repeat(2) });
  let resolver;
  imagensUtils.prepararImagem = () => new Promise(resolve => { resolver = resolve; });
  const primeira = tela.inserirImagens({ index: 0, length: 0 }, { arquivos: [{}] });
  assert.equal(tela.processandoImagens, true);
  await tela.inserirImagens({ index: 0, length: 0 }, { arquivos: [{}] });
  resolver({ dataUrl: "data:image/jpeg;base64,teste", largura: 425, altura: 170 });
  await primeira;
  assert.equal(contarImagens(tela.quill.root.innerHTML), 3);
  assert.equal(tela.processandoImagens, false);
});

test("inserção comprime para até 800x600 em JPEG 75% e limita exibição a 45 mm, sem ampliar", async () => {
  for (const [largura, altura, larguraEsperada, alturaEsperada] of [
    [1000, 400, 425, 170], [400, 1000, 68, 170], [120, 80, 120, 80], [2000, 200, 800, 80],
  ]) {
    const { criar, inputs, canvases, eventos } = ambiente(largura, altura);
    const tela = criar();
    tela.selecionarImagem();
    await inputs[0].onchange();
    assert.deepEqual(tela.quill.insercao, {
      operacoes: [
        { retain: 3 },
        { insert: { image: "data:image/jpeg;base64,teste" }, attributes: { width: String(larguraEsperada), height: String(alturaEsperada) } },
      ], origem: "user",
    });
    assert.deepEqual(tela.quill.selecao, [4, 0, "silent"]);
    assert.equal(eventos.length, 1);
    assert.match(eventos[0][1], new RegExp(`width="${larguraEsperada}" height="${alturaEsperada}"`));
    const escala = Math.min(1, 800 / largura, 600 / altura);
    assert.equal(canvases[0].width, Math.round(largura * escala));
    assert.equal(canvases[0].height, Math.round(altura * escala));
    assert.equal(canvases[0].formato, "image/jpeg");
    assert.equal(canvases[0].qualidade, .75);
    assert.equal(tela.quill.desabilitado, false);
  }
});

test("limite identifica excesso sem truncar HTML ou limpar o histórico", () => {
  const { criar, opcoes } = ambiente();
  const tela = criar({ limiteCaracteres: 2000, modelValue: `<p>${"á".repeat(2001)}</p>` });
  assert.equal(tela.quantidadeCaracteres, 2001);
  assert.equal(tela.limiteExcedido, true);
  assert.equal(tela.quill.atributos["aria-invalid"], "true");
  assert.equal(tela.quill.atributos["aria-describedby"], "enunciado-contador");
  assert.equal(tela.quill.root.innerHTML, tela.modelValue);
  tela.modelValue = `<p>${"á".repeat(2000)}</p>`;
  opcoes.watch.limiteExcedido.call(tela, tela.limiteExcedido);
  assert.equal(tela.limiteExcedido, false);
  assert.equal(tela.quill.atributos["aria-invalid"], "false");
  assert.equal(tela.quill.historicosLimpos, 1);
});

test("contador aparece no editor e modal, alerta em 90% e destaca o excesso", async () => {
  const { createSSRApp } = require("vue");
  const { renderToString } = require("@vue/server-renderer");
  const { opcoes } = ambiente();
  const template = parse(fs.readFileSync(path.join(__dirname, "../src/components/EditorQuill.vue"), "utf8")).descriptor.template.content;
  for (const [tamanho, aviso, excedido] of [[1799, false, false], [1800, true, false], [2000, true, false], [2001, true, true]]) {
    const html = await renderToString(createSSRApp({ ...opcoes, template }, { id: "alternativa-A", limiteCaracteres: 2000, modelValue: `<p>${"a".repeat(tamanho)}</p>` }));
    assert.match(html, new RegExp(`${tamanho.toLocaleString("pt-BR")} / 2.000`));
    assert.equal(html.includes('proximo-limite'), aviso);
    assert.equal(html.includes('limite-excedido'), excedido);
    assert.equal(html.includes('Limite excedido.'), excedido);
  }
});

test("modal mantém instância, HTML e histórico, sem afetar outro campo, e restaura foco e rolagem", async () => {
  const { criar, instancias, eventos, corpo } = ambiente();
  const html = '<p><strong>Enunciado</strong><img src="data:image/jpeg;base64,teste" width="425" height="170"></p>';
  const tela = criar({ modelValue: html });
  const alternativa = criar({ compacto: true });
  const quill = tela.quill;
  assert.equal(tela.expandido, false);
  await tela.alternarExpansao();
  assert.equal(tela.expandido, true);
  assert.equal(tela.$refs.modal.open, true);
  assert.equal(tela.alturaOriginal, 162);
  assert.equal(corpo.style.overflow, "hidden");
  assert.equal(quill.focado, true);
  assert.equal(alternativa.expandido, false);
  await tela.alternarExpansao();
  assert.equal(tela.expandido, false);
  assert.equal(tela.$refs.modal.open, false);
  assert.equal(tela.$refs.botaoExpandir.focado, true);
  assert.equal(corpo.style.overflow, "auto");
  assert.equal(tela.quill, quill);
  assert.equal(quill.root.innerHTML, html);
  assert.equal(quill.conteudos.length, 1);
  assert.equal(quill.historicosLimpos, 1);
  assert.equal(quill.selecoesImagemFechadas, 3);
  assert.equal(instancias.length, 2);
  assert.equal(eventos.length, 0);
});

test("modal nativo é nomeado, move o mesmo editor e oferece Esc e clique no fundo para fechar", () => {
  const fonte = fs.readFileSync(path.join(__dirname, "../src/components/EditorQuill.vue"), "utf8");
  const { template, styles } = parse(fonte).descriptor;
  assert.match(template.content, /type="button"/);
  assert.match(template.content, /:aria-expanded="expandido"/);
  assert.match(template.content, /:aria-controls="id \|\| undefined"/);
  assert.match(template.content, /<dialog ref="modal"/);
  assert.match(template.content, /:aria-label="rotulo \|\| 'Editor de texto'"/);
  assert.match(template.content, /@cancel\.prevent="alternarExpansao"/);
  assert.match(template.content, /@click\.self="alternarExpansao"/);
  assert.match(template.content, /<Teleport :to="expandido \? \$refs.modal : 'body'" :disabled="!expandido">/);
  assert.equal((template.content.match(/ref="editor"/g) || []).length, 1);
  assert.match(styles[0].content, /\.editor-modal::backdrop \{ background: #0006; \}/);
  assert.match(styles[0].content, /\.ql-toolbar\) \{ padding-right: 110px; \}/);
});

test("desmontar o editor com modal aberto restaura a rolagem e fecha o diálogo", async () => {
  const { criar, opcoes, corpo } = ambiente();
  corpo.style.overflow = "scroll";
  const tela = criar();
  await tela.alternarExpansao();
  opcoes.beforeUnmount.call(tela);
  assert.equal(corpo.style.overflow, "scroll");
  assert.equal(tela.$refs.modal.open, false);
  assert.equal(tela.expandido, false);
  assert.equal(tela.quill, null);
});

test("cancelar a seleção de imagem não altera o conteúdo", async () => {
  const { criar, inputs, eventos } = ambiente();
  const tela = criar();
  tela.selecionarImagem();
  inputs[0].files = [];
  await inputs[0].onchange();
  assert.equal(tela.quill.insercao, undefined);
  assert.equal(eventos.length, 0);
});

test("Quill carrega HTML sanitizado sem disparar escrita e identifica o campo acessível", () => {
  const { criar, eventos } = ambiente();
  const tela = criar({ modelValue: "<p><strong>Texto</strong></p><script>ruim()</script>" });
  assert.equal(tela.quill.opcoes.theme, "snow");
  assert.equal(tela.quill.opcoes.modules.redimensionarImagem, true);
  assert.equal(tela.quill.root.innerHTML, "<p><strong>Texto</strong></p>");
  assert.equal(tela.quill.root.id, "enunciado");
  assert.equal(tela.quill.atributos.role, "textbox");
  assert.equal(tela.quill.atributos["aria-label"], "Enunciado");
  assert.equal(tela.quill.atributos["aria-required"], "true");
  assert.equal(tela.quill.conteudos[0].origem, "silent");
  assert.equal(eventos.length, 0);
});

test("digitação atualiza v-model sem reinicializar o editor ou deslocar o cursor no retorno do valor", () => {
  const { criar, eventos, opcoes } = ambiente();
  const tela = criar();
  tela.quill.root.innerHTML = "<p>Resposta <em>formatada</em></p>";
  tela.quill.listener();
  assert.deepEqual(eventos[0], ["update:modelValue", tela.quill.root.innerHTML]);
  assert.equal(tela.quill.exportacoes, 1);
  opcoes.watch.modelValue.call(tela, eventos[0][1]);
  assert.equal(tela.quill.conteudos.length, 1);
  opcoes.watch.modelValue.call(tela, "");
  assert.equal(tela.quill.root.innerHTML, "");
  assert.equal(tela.quill.historicosLimpos, 2);
});

test("cada campo mantém sua própria instância, e a desmontagem remove seu listener", () => {
  const { criar, opcoes, instancias, eventos } = ambiente();
  const enunciado = criar({ modelValue: "<p>Enunciado</p>" });
  const alternativa = criar({ id: "alternativa-A", rotulo: "Alternativa A - correta", compacto: true, modelValue: "<p>Correta</p>" });
  assert.equal(instancias.length, 2);
  alternativa.quill.root.innerHTML = "<p>Nova resposta</p>"; alternativa.quill.listener();
  assert.equal(enunciado.quill.root.innerHTML, "<p>Enunciado</p>");
  assert.equal(eventos.length, 1);
  const instancia = alternativa.quill;
  opcoes.beforeUnmount.call(alternativa);
  assert.equal(instancia.listener, null);
  assert.equal(instancia.redimensionador.destruido, true);
  assert.equal(alternativa.quill, null);
});

test("tamanho da imagem acompanha o HTML emitido e pode ser carregado novamente", () => {
  const { criar, eventos, opcoes } = ambiente();
  const tela = criar();
  const html = '<p><img src="data:image/png;base64,teste" width="240" height="120"></p>';
  tela.quill.root.innerHTML = html;
  tela.quill.listener();
  assert.equal(eventos[0][1], html);
  opcoes.watch.modelValue.call(tela, "");
  opcoes.watch.modelValue.call(tela, html);
  assert.equal(tela.quill.root.innerHTML, html);
});

test("sanitização trata dimensões como atributos sem URL, sem liberar protocolos de imagem perigosos", () => {
  let configuracao;
  const fonte = fs.readFileSync(path.join(__dirname, "../src/utils/html.js"), "utf8");
  const codigo = transformSync(fonte, { babelrc: false, configFile: false, plugins: ["@babel/plugin-transform-modules-commonjs"] }).code;
  const contexto = { exports: {}, require: nome => {
    assert.equal(nome, "dompurify");
    return { sanitize: (html, opcoes) => { configuracao = opcoes; return html; } };
  } };
  vm.runInNewContext(codigo, contexto);
  contexto.exports.sanitizar('<img src="data:image/png;base64,teste" width="240" height="120">');
  assert.deepEqual([...configuracao.ADD_URI_SAFE_ATTR], ["width", "height"]);
  assert.ok(configuracao.ALLOWED_ATTR.includes("width") && configuracao.ALLOWED_ATTR.includes("height"));
  assert.equal(configuracao.ALLOWED_URI_REGEXP.test("data:image/png;base64,teste"), true);
  for (const url of ["javascript:alert(1)", "data:text/html,teste", "data:image/svg+xml,teste"]) {
    assert.equal(configuracao.ALLOWED_URI_REGEXP.test(url), false);
  }
});
