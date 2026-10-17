const { test } = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs"), path = require("node:path"), vm = require("node:vm");
const { transformSync } = require("@babel/core");
const { parse, compileStyle } = require("@vue/compiler-sfc");
const { createSSRApp } = require("vue");
const { renderToString } = require("@vue/server-renderer");

function carregar(arquivo, modulos = {}, globais = {}) {
  const fonte = fs.readFileSync(path.join(__dirname, "../src", arquivo), "utf8");
  const script = arquivo.endsWith(".vue") ? parse(fonte).descriptor.script.content : fonte;
  const codigo = transformSync(script, { babelrc: false, configFile: false, plugins: ["@babel/plugin-transform-modules-commonjs"] }).code;
  const contexto = { exports: {}, ...globais, require: nome => { assert.ok(nome in modulos, `Importação não simulada: ${nome}`); return modulos[nome]; } };
  vm.runInNewContext(codigo, contexto); return contexto.exports;
}
const modelo = carregar("utils/cartaoResposta.js");
const util = carregar("utils/impressaoNotas.js", { "./cartaoResposta": modelo });
const notaFonte = parse(fs.readFileSync(path.join(__dirname, "../src/components/NotaSobreposta.vue"), "utf8")).descriptor;
const NotaSobreposta = { ...carregar("components/NotaSobreposta.vue", { "@/utils/impressaoNotas": util }).default, template: notaFonte.template.content };
const fonte = fs.readFileSync(path.join(__dirname, "../src/views/ImprimirNotasView.vue"), "utf8");
const descritor = parse(fonte).descriptor;
const lote = () => ({ _id: "lote", criado_em: "2026-10-17T21:00:00Z", imprimivel: true, itens: [
  { posicao: 1, nome: "Zélia", matricula: 22, turma: "1ºI - INFORMÁTICA", nota_prova: 0, corrigida: true },
  { posicao: 2, nome: "Ana", matricula: 11, turma: "2ºH - INFORMÁTICA", nota_prova: 6.67, corrigida: true },
] });

function ambiente(dados = lote(), globais = {}) {
  const impressoes = [];
  const opcoes = carregar("views/ImprimirNotasView.vue", {
    "@/services/correcao": { buscarLoteCorrecao: async () => ({ lote: dados }) },
    "@/utils/impressaoNotas": util, "@/components/NotaSobreposta.vue": NotaSobreposta,
  }, { window: { print: () => impressoes.push(true) }, document: { fonts: { ready: Promise.resolve() } }, ...globais }).default;
  const tela = { ...opcoes.data(), id: "lote", $nextTick: async () => {} };
  Object.entries(opcoes.methods).forEach(([nome, metodo]) => { tela[nome] = metodo.bind(tela); });
  Object.entries(opcoes.computed).forEach(([nome, metodo]) => Object.defineProperty(tela, nome, { get: metodo.bind(tela) }));
  return { tela, opcoes, impressoes };
}

test("posição da nota usa o centro do campo original, margens de 12 mm e deslocamentos calibráveis", () => {
  const posicao = util.posicaoNota();
  assert.ok(Math.abs(parseFloat(posicao.left) - 20.64125) < .0001);
  assert.ok(Math.abs(parseFloat(posicao.top) - 29.7475) < .0001);
  assert.equal(parseFloat(util.posicaoNota(2, -1).left) - parseFloat(posicao.left), 2);
  assert.equal(parseFloat(util.posicaoNota(2, -1).top) - parseFloat(posicao.top), -1);
  assert.equal(util.formatarNota(0), "0,00"); assert.equal(util.formatarNota(10), "10,00"); assert.equal(util.formatarNota(6.67), "6,67");
  for (const nota of [null, "10", true, NaN, Infinity, -1, 11]) assert.throws(() => util.formatarNota(nota));
  for (const ajuste of ["", "1", NaN, Infinity, -11, 11]) assert.equal(util.ajusteValido(ajuste), false);
});

test("lote conserva ordem original e posições das falhas, mesmo com resultados fora de sequência", () => {
  const arquivos = [{ name: "z.png" }, { name: "erro.png" }, { name: "a.png" }];
  const resultados = [{ indice: 2, id_prova_aluno: "a", id_correcao: "ca" }, { indice: 0, id_prova_aluno: "z", id_correcao: "cz" }];
  const entradas = util.entradasDoLote(arquivos, resultados, [{ indice: 1 }]);
  assert.deepEqual(JSON.parse(JSON.stringify(entradas)), [
    { arquivo: "z.png", id_prova_aluno: "z", id_correcao: "cz" }, { arquivo: "erro.png", erro: true }, { arquivo: "a.png", id_prova_aluno: "a", id_correcao: "ca" },
  ]);
  assert.ok(entradas.every(item => !("nota_prova" in item)));
  assert.throws(() => util.entradasDoLote(arquivos, [{ indice: 0, id_prova_aluno: "z" }], []), /não confirmou/);
});

test("tela mostra sequência com nome, matrícula, turma e nota sem reordenar alfabeticamente", async () => {
  const { opcoes } = ambiente();
  const html = await renderToString(createSSRApp({ ...opcoes, props: [], template: descritor.template.content, data: () => ({ ...opcoes.data(), carregando: false, lote: lote() }) }));
  assert.ok(html.indexOf("Zélia") < html.indexOf("Ana"));
  assert.match(html, /Ordem da folha/); assert.match(html, /1ºI - INFORMÁTICA/); assert.match(html, /Matrícula/);
  assert.match(html, /0,00/); assert.match(html, /6,67/);
  assert.match(html, /somente as folhas que contêm o gabarito/);
  assert.match(html, /disabled[^>]*>Imprimir notas \(2 folhas\)/);
});

test("impressão exige conferência, teste tem uma folha e lote completo preserva a sequência", async () => {
  const { tela, opcoes, impressoes } = ambiente();
  await opcoes.mounted.call(tela);
  await tela.imprimir(); assert.equal(impressoes.length, 0); assert.equal(tela.paginasImpressao.length, 0);
  await tela.imprimir(true); assert.equal(impressoes.length, 1); assert.equal(tela.paginasImpressao.length, 1);
  tela.conferido = true;
  await tela.imprimir(false); assert.equal(impressoes.length, 2);
  assert.deepEqual(tela.paginasImpressao.map(item => item.matricula), [22, 11]);
  tela.ajusteX = ""; await tela.imprimir(true); assert.equal(impressoes.length, 2);
  assert.equal(tela.paginasImpressao.length, 0);
});

test("pendências, resposta incompleta e falha de fonte não imprimem notas", async () => {
  const pendente = lote(); pendente.imprimivel = false; pendente.itens[0] = { posicao: 1, corrigida: false };
  const contexto = ambiente(pendente);
  await contexto.opcoes.mounted.call(contexto.tela);
  contexto.tela.conferido = true; await contexto.tela.imprimir(true); await contexto.tela.imprimir(false);
  assert.equal(contexto.impressoes.length, 0);
  const invalido = lote(); invalido.itens[1].posicao = 3;
  const outro = ambiente(invalido); await outro.opcoes.mounted.call(outro.tela);
  assert.equal(outro.tela.lote, null); assert.match(outro.tela.erro, /inválido/);
  const falha = ambiente(lote(), { document: { fonts: { get ready() { throw new Error("Falha"); } } } });
  await falha.opcoes.mounted.call(falha.tela); await falha.tela.imprimir(true);
  assert.equal(falha.impressoes.length, 0); assert.match(falha.tela.erro, /Não foi possível/);
});

test("preparação bloqueia clique repetido e navegação, e rota exige perfil pedagógico", async () => {
  let liberar;
  const contexto = ambiente(lote(), { document: { fonts: { ready: new Promise(resolve => { liberar = resolve; }) } } });
  await contexto.opcoes.mounted.call(contexto.tela); contexto.tela.conferido = true;
  const primeira = contexto.tela.imprimir(); await contexto.tela.imprimir();
  assert.equal(contexto.opcoes.beforeRouteLeave.call(contexto.tela), false);
  liberar(); await primeira;
  assert.equal(contexto.impressoes.length, 1);
  const router = fs.readFileSync(path.join(__dirname, "../src/router/index.js"), "utf8");
  assert.match(router, /path: "\/provas\/notas\/:id"[\s\S]*?meta: \{ requiresAuth: true, requiresProcesso: true \}/);
});

test("páginas contêm somente os números, sem imagens ou QR, e não geram folha extra final", async () => {
  const html = await renderToString(createSSRApp({ ...NotaSobreposta, props: [], data: () => ({ nota: 6.67, ajusteX: 0, ajusteY: 0 }) }));
  assert.match(html, />6,67<\/span>/); assert.doesNotMatch(html, /<img|<svg|NOTA|QR/);
  assert.match(notaFonte.styles[0].content, /font: 400 12pt\/1 Arial/);
  const css = descritor.styles.find(estilo => !estilo.scoped).content;
  assert.match(css, /@page\s*\{\s*size: A4; margin: 0;/);
  assert.match(css, /\.organizacao-notas\s*\{ display: none !important;/);
  assert.match(css, /height: 296mm/); assert.match(css, /break-after: page/); assert.match(css, /:last-child\s*\{ break-after: auto/);
  for (const estilo of descritor.styles) assert.deepEqual(compileStyle({ source: estilo.content, filename: "ImprimirNotasView.vue", id: "data-v-notas", scoped: estilo.scoped }).errors, []);
});

test("serviço cria e reabre lote sem enviar nota do navegador", async () => {
  const chamadas = [];
  const servicos = carregar("services/correcao.js", { "./api": { api: async (...args) => { chamadas.push(args); return {}; } }, "@/utils/recortarCartao": {} });
  await servicos.criarLoteCorrecao([{ id_prova_aluno: "id", id_correcao: "correcao", arquivo: "a.png" }]);
  await servicos.buscarLoteCorrecao("lote");
  assert.equal(chamadas[0][0], "/provas/lotes-correcao"); assert.equal(chamadas[0][1].method, "POST");
  assert.equal(chamadas[1][0], "/provas/lotes-correcao/lote");
});

test("fim da correção salva sequência confirmada e falha de salvamento impede acesso à impressão", async () => {
  const chamadas = [];
  let falhar = false;
  const opcoes = carregar("views/CorrigirProvasView.vue", {
    "@/utils/impressaoNotas": util,
    "@/services/correcao": {
      corrigirImagens: async () => ({ resultados: [{ indice: 0, id_prova_aluno: "id", id_correcao: "c", nota_prova: 6.67 }], erros: [] }),
      criarLoteCorrecao: async (entradas) => { chamadas.push(entradas); if (falhar) throw new Error("Banco indisponível"); return { lote: { _id: "lote" } }; },
    },
  }, { localStorage: { setItem: () => { throw new Error("Armazenamento bloqueado"); } } }).default;
  const tela = { ...opcoes.data(), arquivos: [{ name: "primeira.png" }] };
  Object.entries(opcoes.methods).forEach(([nome, metodo]) => { tela[nome] = metodo.bind(tela); });
  await tela.corrigir();
  assert.equal(tela.idLote, "lote"); assert.equal(tela.erroLote, "");
  assert.equal(chamadas[0][0].id_correcao, "c"); assert.equal("nota_prova" in chamadas[0][0], false);
  falhar = true; await tela.corrigir();
  assert.equal(tela.idLote, ""); assert.match(tela.erroLote, /Banco indisponível/);
  assert.equal(tela.resultados[0].nota_prova, 6.67);
  falhar = false; await tela.salvarLote(); assert.equal(tela.idLote, "lote");
});
