const { test } = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const { transformSync } = require("@babel/core");
const { parse, compileStyle } = require("@vue/compiler-sfc");
const { createSSRApp } = require("vue");
const { renderToString } = require("@vue/server-renderer");

function carregar(arquivo, modulos = {}) {
  const fonte = fs.readFileSync(path.join(__dirname, "../src", arquivo), "utf8");
  const partes = arquivo.endsWith(".vue") ? parse(fonte).descriptor : null;
  const codigo = transformSync(partes ? partes.script.content : fonte, { babelrc: false, configFile: false,
    plugins: ["@babel/plugin-transform-modules-commonjs"] }).code;
  const contexto = { exports: {}, require: nome => { assert.ok(nome in modulos); return modulos[nome]; } };
  vm.runInNewContext(codigo, contexto);
  return { ...contexto.exports, partes };
}

const { agruparVersoesPorTurma } = carregar("utils/listasTurma.js");
const lista = carregar("components/ListaTurma.vue", { "@/assets/templates/cartao-resposta.png": "logos.png" });
const prova = { disciplina: { nome_disciplina: "Desenvolvimento de Jogos" }, professor: { nome: "Helio" },
  periodo_letivo: "4º período letivo", data_de_aplicacao: "2026-10-08" };
const alunos = quantidade => Array.from({ length: quantidade }, (_, indice) => ({
  matricula_aluno: 50260000 + indice, nome_aluno: `Aluno Teste ${String(indice).padStart(2, "0")}`,
  turma_aluno: "1ºI - INFORMÁTICA", numero_chamada: indice + 1,
}));
const renderizar = (tipo, quantidade = 28) => renderToString(createSSRApp({ ...lista.default,
  template: lista.partes.template.content }, { tipo, alunos: alunos(quantidade), turma: "1ºI - INFORMÁTICA", prova }));

test("ordenação alfabética em português numera cada turma sem alterar versões ou questões", () => {
  const versoes = [
    { matricula_aluno: 3, nome_aluno: "Érica Silva", turma_aluno: "1ºI", questoes: ["q2", "q1"] },
    { matricula_aluno: 1, nome_aluno: "Ana Silva", turma_aluno: "1ºI", questoes: ["q1", "q2"] },
    { matricula_aluno: 2, nome_aluno: "Bruno Souza", turma_aluno: "1ºH", questoes: ["q2", "q1"] },
  ];
  const antes = JSON.stringify(versoes);
  const grupos = agruparVersoesPorTurma(versoes, ["1ºI", "1ºH"]);
  assert.deepEqual([...grupos.map(grupo => grupo.turma)], ["1ºH", "1ºI"]);
  assert.deepEqual([...grupos[1].alunos.map(aluno => aluno.numero_chamada)], [1, 2]);
  assert.equal(grupos[1].alunos[0].nome_aluno, "Ana Silva");
  assert.equal(grupos[1].alunos[1].questoes, versoes[0].questoes);
  assert.equal(JSON.stringify(versoes), antes);
});

test("cadastros incompletos, turma estranha e matrícula duplicada não geram listas", () => {
  const aluno = alunos(1)[0];
  for (const campo of ["nome_aluno", "turma_aluno"]) {
    assert.throws(() => agruparVersoesPorTurma([{ ...aluno, [campo]: " " }], aluno.turma_aluno), /Confira o nome e a turma/);
  }
  assert.throws(() => agruparVersoesPorTurma([aluno], "Outra turma"), /não pertence/);
  assert.throws(() => agruparVersoesPorTurma([aluno, aluno], aluno.turma_aluno), /versões repetidas/);
  assert.equal(agruparVersoesPorTurma([], "1ºI").length, 0);
});

test("planilha de notas mantém cinco colunas e notas/assinaturas/datas de controle vazias", async () => {
  const html = await renderizar("notas");
  assert.match(html, /PLANILHA DE NOTAS - AVALIAÇÃO OBJETIVA - 2026/);
  assert.match(html, /Colégio Técnico Antônio Teixeira Fernandes/);
  assert.match(html, /Unidade Centro/);
  assert.match(html, /1ºI - INFORMÁTICA/);
  assert.match(html, /08\/10\/2026/);
  assert.match(html, /4º período letivo/);
  assert.equal((html.match(/scope="col"/g) || []).length, 5);
  assert.equal((html.match(/class="nota-aluno"><\/td>/g) || []).length, 28);
  assert.equal((html.match(/class="assinatura-aluno"><\/td>/g) || []).length, 28);
  assert.match(html, /Data Entrega para Proc\. Pedagógico:/);
  assert.match(html, /Data Lançamento no Sistema:/);
  assert.match(html, /Assinatura do Professor \(a\):/);
  assert.doesNotMatch(html, /DISSERTATIVA|BIMESTRE|\bA1\b/);
});

test("relatório de entrega mantém faixa da turma, quatro colunas e assinatura do professor", async () => {
  const html = await renderizar("entrega");
  assert.match(html, /RELATÓRIO DE ENTREGA - AVALIAÇÃO OBJETIVA/);
  assert.match(html, /class="turma-faixa">1ºI - INFORMÁTICA/);
  assert.equal((html.match(/scope="col"/g) || []).length, 4);
  assert.equal((html.match(/class="assinatura-aluno"><\/td>/g) || []).length, 28);
  assert.match(html, /Assinatura do Professor \(a\)/);
  assert.doesNotMatch(html, /NOTA<|nota-aluno|Data Entrega|Data Lançamento|Data da Aplicação|DISSERTATIVA|BIMESTRE|\bA1\b/);
});

test("listas com mais de 28 alunos repetem cabeçalho e continuam a chamada", async () => {
  const html = await renderizar("notas", 57);
  assert.equal((html.match(/<section\b[^>]*\blista-turma-folha\b/g) || []).length, 3);
  assert.equal((html.match(/PLANILHA DE NOTAS/g) || []).length, 3);
  assert.equal((html.match(/class="nota-aluno"><\/td>/g) || []).length, 57);
  assert.match(html, /<td>29<\/td>/);
  assert.match(html, /<td>57<\/td>/);
});

test("estilos preservam impressão monocromática, linhas alternadas e folhas A4", () => {
  const css = lista.partes.styles[0].content;
  assert.deepEqual(compileStyle({ source: css, id: "lista-turma", scoped: true }).errors, []);
  assert.match(css, /nth-child\(odd\)/);
  assert.match(css, /background:\s*#222;\s*color:\s*white/);
  assert.match(css, /print-color-adjust:\s*exact/);
  assert.match(css, /min-height:\s*296mm/);
  assert.match(css, /break-inside:\s*avoid/);
});
