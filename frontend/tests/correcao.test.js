const { test } = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const { transformSync } = require("@babel/core");
const { parse } = require("@vue/compiler-sfc");

function carregar(arquivo, modulos = {}, globais = {}) {
  const fonte = fs.readFileSync(path.join(__dirname, "../src", arquivo), "utf8");
  const script = arquivo.endsWith(".vue") ? parse(fonte).descriptor.script.content : fonte;
  const codigo = transformSync(script, { babelrc: false, configFile: false, plugins: ["@babel/plugin-transform-modules-commonjs"] }).code;
  const contexto = { exports: {}, ...globais, require: (nome) => {
    assert.ok(nome in modulos, `Importação não simulada: ${nome}`); return modulos[nome];
  } };
  vm.runInNewContext(codigo, contexto); return contexto.exports;
}

const modelo = carregar("utils/cartaoResposta.js");
const recorte = carregar("utils/recortarCartao.js", { jsqr: {}, "./cartaoResposta": modelo });

function imagemComCartao() {
  const imagem = { width: 1000, height: 1500, data: new Uint8ClampedArray(1000 * 1500 * 4).fill(255) };
  for (const y of [100, 315]) {
    for (let x = 30; x <= 930; x++) imagem.data.fill(0, (y * 1000 + x) * 4, (y * 1000 + x) * 4 + 3);
  }
  const quiet = 94 * 4 / 33, lado = 94 * 25 / 33 * .75;
  const origem = { x: 30 + (9 + quiet) * .75, y: 100 + (168 + quiet) * .75 };
  const codigo = { data: "6acecbcd32149b41b3a09574", version: 2, location: {
    topLeftCorner: origem, topRightCorner: { x: origem.x + lado, y: origem.y },
    bottomLeftCorner: { x: origem.x, y: origem.y + lado },
  } };
  return { imagem, codigo };
}

test("recorte mantém as dez colunas, QR, largura inteira e margem de segurança", () => {
  const { imagem, codigo } = imagemComCartao();
  const faixa = recorte.localizarFaixa(imagem, codigo);
  assert.ok(faixa); assert.ok(faixa.y < 100); assert.ok(faixa.y + faixa.altura > 315);
  assert.ok(faixa.altura < 1500 * .25);
  assert.ok(codigo.location.bottomLeftCorner.y < faixa.y + faixa.altura);
});

test("QR ausente, de outro tipo ou sem as duas bordas não permite corte", () => {
  const { imagem, codigo } = imagemComCartao();
  assert.equal(recorte.localizarFaixa(imagem, null), null);
  assert.equal(recorte.localizarFaixa(imagem, { ...codigo, data: "matricula-123" }), null);
  imagem.data.fill(255, 315 * 1000 * 4, 316 * 1000 * 4);
  assert.equal(recorte.localizarFaixa(imagem, codigo), null);
  imagem.data.fill(255);
  assert.equal(recorte.localizarFaixa(imagem, codigo), null);
});

test("QR fora da posição do modelo ou geometria cortada preserva original", () => {
  const { imagem, codigo } = imagemComCartao();
  for (const ponto of Object.values(codigo.location)) ponto.x += 200;
  assert.equal(recorte.localizarFaixa(imagem, codigo), null);
  for (const ponto of Object.values(codigo.location)) { ponto.x -= 200; ponto.y -= 120; }
  assert.equal(recorte.localizarFaixa(imagem, codigo), null);
});

test("falha ao decodificar imagem devolve o mesmo arquivo", async () => {
  const util = carregar("utils/recortarCartao.js", { jsqr: {}, "./cartaoResposta": modelo }, {
    createImageBitmap: async () => { throw new Error("Imagem inválida"); },
  });
  const original = { name: "original.png" };
  const resultado = await util.recortarCartao(original);
  assert.equal(resultado.arquivo, original); assert.equal(resultado.recortada, false);
});

function ambiente({ api, recortar } = {}) {
  const chamadas = [];
  class Formulario {
    constructor() { this.itens = []; }
    append(campo, arquivo) { assert.equal(campo, "imagens"); this.itens.push(arquivo); }
  }
  const servico = carregar("services/correcao.js", {
    "./api": { api: async (rota, opcoes) => {
      assert.equal(rota, "/provas/corrigir-provas"); assert.equal(opcoes.method, "POST");
      assert.equal(opcoes.headers, undefined); chamadas.push(opcoes.body.itens);
      if (api) return api(opcoes.body.itens, chamadas.length);
      return { resultados: opcoes.body.itens.map((_, indice) => ({ indice, nota_prova: 10 })), erros: [] };
    } },
    "@/utils/recortarCartao": { recortarCartao: recortar || (async (arquivo) => ({ arquivo, recortada: false })) },
  }, { FormData: Formulario, setTimeout: (acao) => acao() });
  const arquivos = (quantidade, size = 100) => Array.from({ length: quantidade }, (_, i) => ({ name: `pagina-${i}.jpg`, type: "image/jpeg", size }));
  return { servico, chamadas, arquivos };
}

test("400 imagens são enviadas automaticamente em oito lotes de 50", async () => {
  const { servico, chamadas, arquivos } = ambiente(); let progresso;
  const dados = await servico.corrigirImagens(arquivos(400), (valor) => { progresso = valor; });
  assert.equal(chamadas.length, 8); assert.ok(chamadas.every((lote) => lote.length === 50));
  assert.equal(dados.resultados.length, 400); assert.equal(dados.erros.length, 0);
  assert.equal(dados.resultados[399].indice, 399); assert.equal(dados.resultados[399].arquivo, "pagina-399.jpg");
  assert.equal(progresso.processadas, 400); assert.equal(progresso.preparadas, 400);
});

test("recorta antes do envio e mantém nome original nos resultados", async () => {
  const nova = { name: "recorte.png", type: "image/png", size: 50 };
  const { servico, chamadas, arquivos } = ambiente({ recortar: async () => ({ arquivo: nova, recortada: true }) });
  const originais = arquivos(1); const dados = await servico.corrigirImagens(originais);
  assert.equal(chamadas[0][0], nova); assert.equal(originais[0].name, "pagina-0.jpg");
  assert.equal(dados.resultados[0].arquivo, "pagina-0.jpg"); assert.equal(dados.recortadas, 1);
});

test("respeita limite de bytes por lote e de 5 MiB por imagem", async () => {
  const { servico, chamadas, arquivos } = ambiente();
  const originais = arquivos(17, 5 * 1024 * 1024); originais.push(...arquivos(1, 6 * 1024 * 1024));
  const dados = await servico.corrigirImagens(originais);
  assert.deepEqual(chamadas.map((lote) => lote.length), [8, 8, 1]);
  assert.equal(dados.resultados.length, 17); assert.equal(dados.erros.length, 1);
  assert.match(dados.erros[0].mensagem, /5 MiB/);
});

test("um lote indisponível não impede os seguintes e erros conservam índices", async () => {
  const { servico, arquivos } = ambiente({ api: async (lote, numero) => {
    if (numero === 1) throw new Error("Microserviço indisponível");
    return { resultados: lote.slice(1).map((_, i) => ({ indice: i + 1 })), erros: [{ indice: 0, mensagem: "QR Code não encontrado" }] };
  } });
  const dados = await servico.corrigirImagens(arquivos(55));
  assert.equal(dados.resultados.length, 4); assert.equal(dados.erros.length, 51);
  assert.equal(dados.erros[50].indice, 50); assert.equal(dados.erros[50].arquivo, "pagina-50.jpg");
  assert.match(dados.erros[50].mensagem, /QR Code/);
});

test("resposta incompleta/duplicada não anuncia notas como corrigidas", async () => {
  for (const resposta of [{ resultados: [{ indice: 0 }], erros: [] }, { resultados: [{ indice: 0 }, { indice: 0 }], erros: [] }]) {
    const { servico, arquivos } = ambiente({ api: async () => resposta });
    const dados = await servico.corrigirImagens(arquivos(2));
    assert.equal(dados.resultados.length, 0); assert.equal(dados.erros.length, 2);
  }
});

test("imagem vazia e arquivo que não é imagem não são enviados", async () => {
  const { servico, chamadas, arquivos } = ambiente();
  const itens = arquivos(3); itens[0].size = 0; itens[1].type = "application/pdf";
  const dados = await servico.corrigirImagens(itens);
  assert.equal(chamadas[0].length, 1); assert.equal(dados.resultados[0].indice, 2); assert.equal(dados.erros.length, 2);
});

test("tela impede clique duplicado e navegação enquanto processa", async () => {
  let finalizar, chamadas = 0;
  const opcoes = carregar("views/CorrigirProvasView.vue", { "@/services/correcao": { corrigirImagens: () => {
    chamadas++; return new Promise((resolve) => { finalizar = resolve; });
  } } });
  const tela = { ...opcoes.default.data(), arquivos: [{}] };
  Object.entries(opcoes.default.methods).forEach(([nome, metodo]) => { tela[nome] = metodo.bind(tela); });
  const primeira = tela.corrigir(); await tela.corrigir();
  assert.equal(chamadas, 1); assert.equal(opcoes.default.beforeRouteLeave.call(tela), false);
  finalizar({ resultados: [], erros: [] }); await primeira;
  assert.equal(tela.processando, false); assert.equal(tela.finalizado, true);
  assert.equal(opcoes.default.beforeRouteLeave.call(tela), true);
  assert.equal(tela.formatarGabarito({ 1: "A", 2: null }), "1: A · 2: Em branco");
});
