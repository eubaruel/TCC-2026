const { test } = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const { transformSync } = require("@babel/core");
const { parse } = require("@vue/compiler-sfc");
const { createSSRApp } = require("vue");
const { renderToString } = require("@vue/server-renderer");

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
const notas = carregar("utils/impressaoNotas.js", { "./cartaoResposta": modelo });
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

test("recorte reconhece o cartão A4 com margens laterais de 16 mm e superior de 13 mm", () => {
  const { PAGINA_PROVA: pagina, CARTAO_RESPOSTA: cartao } = modelo;
  const pixelsPorMm = 2;
  const width = pagina.largura * pixelsPorMm, height = pagina.altura * pixelsPorMm;
  const imagem = { width, height, data: new Uint8ClampedArray(width * height * 4).fill(255) };
  const escala = (pagina.largura - 2 * pagina.margemLateral) * pixelsPorMm / cartao.largura;
  const x = pagina.margemLateral * pixelsPorMm, y = pagina.margemSuperior * pixelsPorMm;
  const fim = Math.round(y + cartao.altura * escala);
  for (const linha of [y, fim]) {
    for (let coluna = x; coluna <= width - x; coluna++) imagem.data.fill(0, (linha * width + coluna) * 4, (linha * width + coluna) * 4 + 3);
  }
  const quiet = cartao.qr.tamanho * cartao.qr.margem / 33;
  const lado = cartao.qr.tamanho * 25 / 33 * escala;
  const origem = { x: x + (cartao.qr.x + quiet) * escala, y: y + (cartao.qr.y + quiet) * escala };
  const codigo = { data: "6acecbcd32149b41b3a09574", version: 2, location: {
    topLeftCorner: origem, topRightCorner: { x: origem.x + lado, y: origem.y }, bottomLeftCorner: { x: origem.x, y: origem.y + lado },
  } };
  const faixa = recorte.localizarFaixa(imagem, codigo);
  assert.ok(faixa);
  assert.ok(faixa.y < y);
  assert.ok(faixa.y + faixa.altura > fim);
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
  const chamadas = [], identificadores = [];
  class Formulario {
    constructor() { this.itens = []; }
    append(campo, valor) {
      if (campo === "imagens") this.itens.push(valor);
      else { assert.equal(campo, "ids_provas_alunos"); this.ids = JSON.parse(valor); }
    }
  }
  const servico = carregar("services/correcao.js", {
    "./api": { api: async (rota, opcoes) => {
      assert.equal(rota, "/provas/corrigir-provas"); assert.equal(opcoes.method, "POST");
      assert.equal(opcoes.headers, undefined); chamadas.push(opcoes.body.itens);
      identificadores.push(opcoes.body.ids);
      if (api) return api(opcoes.body.itens, chamadas.length);
      return { resultados: opcoes.body.itens.map((_, indice) => ({ indice, nota_prova: 10 })), erros: [] };
    } },
    "@/utils/recortarCartao": { recortarCartao: recortar || (async (arquivo) => ({ arquivo, recortada: false })) },
  }, { FormData: Formulario, setTimeout: (acao) => acao() });
  const arquivos = (quantidade, size = 100) => Array.from({ length: quantidade }, (_, i) => ({ name: `pagina-${i}.jpg`, type: "image/jpeg", size }));
  return { servico, chamadas, arquivos, identificadores };
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
  const opcoes = carregar("views/CorrigirProvasView.vue", { "@/utils/impressaoNotas": notas, "@/services/correcao": { corrigirImagens: () => {
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

async function renderizarCorrecao(dados) {
  const opcoes = carregar("views/CorrigirProvasView.vue", { "@/utils/impressaoNotas": notas, "@/services/correcao": {} }).default;
  const fonte = fs.readFileSync(path.join(__dirname, "../src/views/CorrigirProvasView.vue"), "utf8");
  return renderToString(createSSRApp({ ...opcoes,
    template: parse(fonte).descriptor.template.content,
    data: () => ({ ...opcoes.data(), finalizado: true, ...dados }),
  }));
}

test("área de não corrigidas mostra nome, matrícula e turma sem nome do arquivo ou motivo", async () => {
  const html = await renderizarCorrecao({
    resultados: [{ indice: 0, arquivo: "corrigida.png", matricula: 1, nome: "Aluno Teste", nota_prova: 10 }],
    erros: [{ indice: 1, arquivo: "sem-leitura.png", mensagem: "Detalhe técnico privado",
      matricula: 20260002, nome: "Bruno Teste", turma: "Turma A" }],
  });
  assert.match(html, /Provas não corrigidas/);
  assert.match(html, /1 prova\(s\)/);
  assert.match(html, /#2/);
  assert.match(html, /Bruno Teste/);
  assert.match(html, /Matrícula: 20260002/);
  assert.match(html, /Turma: Turma A/);
  assert.match(html, /Não corrigida/);
  assert.ok(html.indexOf("Provas não corrigidas") < html.indexOf("<table"));
  assert.doesNotMatch(html, /sem-leitura\.png|Detalhe técnico privado|Não há provas pendentes/);
});

test("todos os arquivos com falha são identificados mesmo com nomes repetidos", async () => {
  const erros = Array.from({ length: 400 }, (_, indice) => ({ indice, arquivo: "pagina.png", mensagem: "Erro oculto" }));
  const html = await renderizarCorrecao({ erros });
  assert.equal((html.match(/class="pendente-aluno"/g) || []).length, 400);
  assert.match(html, /400 prova\(s\)/);
  assert.ok(html.indexOf("#1<") < html.indexOf("#400<"));
  assert.doesNotMatch(html, /Erro oculto|<table/);
});

test("envio sem falhas mostra confirmação e não exibe área de pendências", async () => {
  const html = await renderizarCorrecao({ resultados: [{ indice: 0, arquivo: "corrigida.png", nota_prova: 10 }] });
  assert.match(html, /Não há provas pendentes neste envio/);
  assert.doesNotMatch(html, /Provas não corrigidas|pendentes-lista/);
  assert.match(html, /resultados confirmados foram salvos no banco/);
  assert.match(html, /impressas passam para o status Corrigida/);
  assert.match(html, /mesmo que ainda existam cartões pendentes/);
  assert.doesNotMatch(html, /status das provas não foi alterado|Prova Corrigida/);
});

test("nova seleção limpa os resultados e as pendências anteriores", () => {
  const opcoes = carregar("views/CorrigirProvasView.vue", { "@/utils/impressaoNotas": notas, "@/services/correcao": {} }).default;
  const tela = { ...opcoes.data(), finalizado: true, erros: [{ indice: 0, arquivo: "anterior.png" }], resultados: [{}] };
  tela.limparPrevias = opcoes.methods.limparPrevias.bind(tela);
  opcoes.methods.selecionar.call(tela, { target: { files: [{ name: "nova.png" }] } });
  assert.equal(tela.finalizado, false);
  assert.equal(tela.erros.length, 0);
  assert.equal(tela.resultados.length, 0);
});

test("sem identificação confiável, a tela não inventa matrícula, nome ou turma", async () => {
  const html = await renderizarCorrecao({ erros: [{ indice: 0, arquivo: "20260002-bruno.png" }] });
  assert.match(html, /Aluno não identificado/);
  assert.match(html, /Matrícula: Não identificada/);
  assert.match(html, /Turma: Não identificada/);
  assert.match(html, /Arquivo: 20260002-bruno\.png/);
  assert.doesNotMatch(html, /Matrícula: 20260002/);
});

test("matrícula conhecida continua visível quando o cadastro do aluno está indisponível", async () => {
  const html = await renderizarCorrecao({ erros: [{ indice: 0, matricula: 20260002, nome: null, turma: null }] });
  assert.match(html, /Matrícula: 20260002/);
  assert.match(html, /Nome não disponível/);
  assert.match(html, /Turma: Não identificada/);
  assert.doesNotMatch(html, /Aluno não identificado/);
});

test("IDs lidos no frontend acompanham cada imagem e preservam identificação retornada", async () => {
  const id = "000000000000000000000001";
  const { servico, identificadores, arquivos } = ambiente({
    recortar: async (arquivo) => ({ arquivo, recortada: false, id_prova_aluno: id }),
    api: async (lote) => ({ resultados: [], erros: lote.map((_, indice) => ({ indice, matricula: 1, nome: "Aluno", turma: "A" })) }),
  });
  const dados = await servico.corrigirImagens(arquivos(51));
  assert.deepEqual(identificadores.map(ids => ids.length), [50, 1]);
  assert.ok(identificadores.every(ids => ids.every(item => item === id)));
  assert.equal(dados.erros[50].indice, 50);
  assert.equal(dados.erros[50].nome, "Aluno");
  assert.equal(dados.erros[50].matricula, 1);
  assert.equal(dados.erros[50].turma, "A");
});

test("QR identificado é preservado mesmo sem bordas que autorizem um recorte", async () => {
  const { imagem, codigo } = imagemComCartao();
  imagem.data.fill(255);
  const util = carregar("utils/recortarCartao.js", { jsqr: () => codigo, "./cartaoResposta": modelo }, {
    createImageBitmap: async () => ({ width: imagem.width, height: imagem.height, close() {} }),
    document: { createElement: () => ({ getContext: () => ({
      drawImage() {}, fillRect() {}, translate() {}, rotate() {}, getImageData: () => imagem,
    }) }) },
  });
  const original = { name: "pagina.png" };
  const resultado = await util.recortarCartao(original);
  assert.equal(resultado.arquivo, original);
  assert.equal(resultado.recortada, false);
  assert.equal(resultado.id_prova_aluno, codigo.data);
});

test("sem aluno identificado, mostra arquivo, posição e miniatura da página original", async () => {
  const html = await renderizarCorrecao({ erros: [{ indice: 26, arquivo: "pagina-27.png", imagemOriginal: "blob:original" }] });
  assert.match(html, /#27/);
  assert.match(html, /Arquivo: pagina-27\.png/);
  assert.match(html, /href="blob:original"/);
  assert.match(html, /src="blob:original"/);
  assert.match(html, /Visualizar página original da imagem 27/);
  assert.match(html, /loading="lazy"/);
  assert.match(html, /rel="noopener noreferrer"/);
});

test("prévia inválida ou arquivo sem imagem usa aviso e conserva arquivo e posição", async () => {
  for (const dados of [{ imagemOriginal: null }, { imagemOriginal: "blob:invalida", previaIndisponivel: true }]) {
    const html = await renderizarCorrecao({ erros: [{ indice: 2, arquivo: "corrompida.png", ...dados }] });
    assert.match(html, /Prévia indisponível para este arquivo/);
    assert.match(html, /Arquivo: corrompida\.png/);
    assert.match(html, /#3/);
    assert.doesNotMatch(html, /<img|href="blob:/);
  }
});

test("miniaturas usam o arquivo original pelo índice e são liberadas entre envios e ao sair", async () => {
  const criadas = [], revogadas = [];
  const opcoes = carregar("views/CorrigirProvasView.vue", { "@/utils/impressaoNotas": notas, "@/services/correcao": {
    corrigirImagens: async () => ({ resultados: [], erros: [
      { indice: 1, arquivo: "repetido.png" }, { indice: 0, arquivo: "repetido.png", matricula: 123 },
    ] }),
  } }, { URL: { createObjectURL: arquivo => { criadas.push(arquivo); return `blob:${criadas.length}`; },
    revokeObjectURL: url => revogadas.push(url) }, window: { removeEventListener() {} } }).default;
  const arquivos = [{ name: "repetido.png", type: "image/png" }, { name: "repetido.png", type: "image/png" }];
  const tela = { ...opcoes.data(), arquivos };
  Object.entries(opcoes.methods).forEach(([nome, metodo]) => { tela[nome] = metodo.bind(tela); });
  await tela.corrigir();
  assert.equal(criadas[0], arquivos[1]);
  assert.equal(tela.erros[0].imagemOriginal, "blob:1");
  assert.equal(tela.erros[1].imagemOriginal, null);
  await tela.corrigir();
  assert.deepEqual(revogadas, ["blob:1"]);
  tela.selecionar({ target: { files: arquivos } });
  assert.deepEqual(revogadas, ["blob:1", "blob:2"]);
  await tela.corrigir();
  opcoes.beforeUnmount.call(tela);
  assert.deepEqual(revogadas, ["blob:1", "blob:2", "blob:3"]);
});

test("prévia não abre SVG como documento ativo nem cria URLs para outros formatos", async () => {
  const opcoes = carregar("views/CorrigirProvasView.vue", { "@/utils/impressaoNotas": notas, "@/services/correcao": {
    corrigirImagens: async () => ({ resultados: [], erros: [{ indice: 0, arquivo: "pagina.svg" }] }),
  } }, { URL: { createObjectURL: () => { assert.fail("Não deve criar prévia para SVG"); } } }).default;
  const tela = { ...opcoes.data(), arquivos: [{ type: "image/svg+xml" }] };
  Object.entries(opcoes.methods).forEach(([nome, metodo]) => { tela[nome] = metodo.bind(tela); });
  await tela.corrigir();
  assert.equal(tela.finalizado, true);
  assert.equal(tela.erros[0].imagemOriginal, null);
});
