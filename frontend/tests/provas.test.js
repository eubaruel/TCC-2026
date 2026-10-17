const { test } = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const { parse, compileStyle } = require("@vue/compiler-sfc");
const { transformSync } = require("@babel/core");

// Executa as opções dos componentes com serviços simulados, sem servidor ou novas dependências.
function carregarOpcoes(arquivo, modulos, globais = {}) {
  const fonte = fs.readFileSync(path.join(__dirname, "..", "src", arquivo), "utf8");
  const script = arquivo.endsWith(".vue") ? parse(fonte).descriptor.script.content : fonte;
  const codigo = transformSync(script, { babelrc: false, configFile: false, plugins: ["@babel/plugin-transform-modules-commonjs"] }).code;
  const contexto = { ...globais, exports: {}, require: (nome) => {
    assert.ok(nome in modulos, `Importação não simulada: ${nome}`);
    return modulos[nome];
  } };
  vm.runInNewContext(codigo, contexto);
  return contexto.exports;
}

function instancia(opcoes, dados) {
  const estado = { ...opcoes.data(), ...dados, $nextTick: async () => {} };
  Object.entries(opcoes.methods).forEach(([nome, metodo]) => { estado[nome] = metodo.bind(estado); });
  Object.entries(opcoes.computed || {}).forEach(([nome, metodo]) => Object.defineProperty(estado, nome, { get: metodo.bind(estado) }));
  return estado;
}

const filtrosModulo = carregarOpcoes("utils/filtrosQuestoes.js", {
  "./html": { textoPuro: (html) => String(html ?? "").replace(/<[^>]*>/g, "") },
});
const filtrosComponente = {
  ...carregarOpcoes("components/FiltrosQuestoes.vue", { "@/utils/filtrosQuestoes": filtrosModulo }).default,
  template: parse(fs.readFileSync(path.join(__dirname, "../src/components/FiltrosQuestoes.vue"), "utf8")).descriptor.template.content,
};

function ambiente(quantidade = 3, tamanhoBanco = 3) {
  const draftModulo = carregarOpcoes("stores/provaDraft.js", { pinia: { defineStore: (_, opcoes) => opcoes } });
  const draftOpcoes = draftModulo.useProvaDraftStore;
  const draft = draftOpcoes.state();
  Object.entries(draftOpcoes.actions).forEach(([nome, acao]) => { draft[nome] = acao.bind(draft); });
  const banco = Array.from({ length: tamanhoBanco }, (_, index) => `q${index + 1}`).map((_id) => ({ _id, enunciado: _id, disciplina: ["mat"], tipo_questao: "Objetiva",
    alternativas: ["A", "B", "C", "D", "E"].map((texto) => ({ id: texto, texto })), alternativa_correta: "C" }));
  let prova = { _id: "base-existente", professor: { registro: 1, nome: "Professor Teste" },
    disciplina: { codigo_disciplina: "MAT", nome_disciplina: "Matemática" }, id_turma: "Turma A", tipo: "Objetiva",
    serie: 3, periodo_letivo: "3º período letivo", data_de_aplicacao: "2026-10-14", status: "Aguardando questões", questoes: ["q2", "q1"] };
  const chamadas = [];
  const servicos = {
    buscarProva: async (id) => { assert.equal(id, prova._id); return prova; },
    provaEditavel: (item) => ["Aguardando questões", "Em elaboração"].includes(item.status),
    adicionarQuestoes: async (id, ids) => { chamadas.push({ rota: "selecionar", id, ids: [...ids] }); prova = { ...prova, questoes: [...ids], status: "Em elaboração" }; return { prova, provas_alunos_geradas: quantidade }; },
    enviarProva: async (id) => { chamadas.push({ rota: "enviar", id }); prova = { ...prova, status: "Enviada ao pedagógico" }; return { prova }; },
  };
  const opcoes = carregarOpcoes("views/CriarProvaView.vue", {
    "@/components/QuestaoEditor.vue": {}, "@/components/PreviewProva.vue": {}, "@/components/ModalSairEdicao.vue": {},
    "@/components/FiltrosQuestoes.vue": filtrosComponente, "@/utils/filtrosQuestoes": filtrosModulo,
    "@/stores/auth": {}, "@/stores/provaDraft": draftModulo, "@/services/questoes": { listarQuestoes: async () => ({ questoes: banco }) },
    "@/services/provas": servicos, "@/services/templates": { obterTemplateProva: async () => "template" },
    "@/utils/html": { sanitizar: (valor) => valor, textoPuro: (valor) => valor, htmlVazio: (valor) => !valor || valor === "<p><br></p>" },
  }).default;
  return { tela: instancia(opcoes, { id: prova._id, draft, authStore: { user: { registro: 1 } } }), chamadas, draft, banco, prova, servicos, opcoes };
}

function ambienteProvaBase() {
  const chamadas = [], eventos = [];
  const professores = [{ registro: 1, nome: "Ana Silva" }, { registro: 2, nome: "Ana Silva" }];
  const disciplinas = [
    { codigo_disciplina: "MAT", nome_disciplina: "Matemática", turma: "Turma 2026 A", professor: { registro: 2 } },
    { codigo_disciplina: "POR", nome_disciplina: "Português", turma: "Turma 2026 B" },
    { codigo_disciplina: "FIS", nome_disciplina: "Física", turma: "Turma 2026 A" },
  ];
  const opcoes = carregarOpcoes("components/CriarProvaBase.vue", {
    "@/services/usuarios": { listarUsuarios: async () => ({ usuarios: professores }) },
    "@/services/disciplinas": { listarDisciplinas: async () => ({ disciplinas }) },
    "@/services/provas": { criarProva: async (payload) => { chamadas.push(payload); return { prova: { ...payload, _id: "nova-base" } }; } },
  }).default;
  return { tela: instancia(opcoes, { $emit: (...args) => eventos.push(args) }), chamadas, eventos, opcoes };
}

test("prova-base seleciona professor pelo registro mesmo com nomes iguais e impede texto livre", async () => {
  const { tela, chamadas } = ambienteProvaBase();
  await tela.carregar();
  tela.formulario.codigoDisciplina = "MAT"; tela.selecionarDisciplina();
  assert.equal(tela.buscaProfessor, "Ana Silva (2)");
  tela.formulario.periodo_letivo = "2º período letivo"; tela.formulario.data = "2026-10-20";
  tela.formulario.quantidade_questoes = 3;
  tela.buscaProfessor = "Ana Silva (1)";
  await tela.salvar();
  assert.equal(chamadas[0].professor.registro, 1);
  assert.equal(chamadas[0].serie, 3);
  assert.equal(chamadas[0].quantidade_questoes, 3);
  assert.equal(chamadas[0].periodo_letivo, "2º período letivo");
  assert.equal(chamadas[0].id_turma, "Turma 2026 A");
  assert.equal("questoes" in chamadas[0], false);
  tela.buscaProfessor = "Ana Silva";
  await tela.salvar();
  assert.equal(tela.formulario.registroProfessor, "");
  assert.equal(chamadas.length, 1);
});

test("prova-base exige quantidade inteira de duas a dez questões", async () => {
  for (const quantidade of ["", 1, 11, 2.5, true]) {
    const { tela, chamadas } = ambienteProvaBase();
    await tela.carregar();
    tela.formulario.codigoDisciplina = "MAT"; tela.selecionarDisciplina();
    Object.assign(tela.formulario, { periodo_letivo: "1º período letivo", data: "2026-10-20", quantidade_questoes: quantidade });
    await tela.salvar();
    assert.equal(chamadas.length, 0);
    assert.ok(tela.erro);
  }
});

test("quantidade da base limita a seleção e só permite concluir quando estiver completa", async () => {
  const { tela, prova, chamadas } = ambiente(3, 5);
  prova.quantidade_questoes = 3;
  await tela.carregar();
  assert.equal(tela.limiteQuestoes, 3);
  assert.equal(await tela.salvar(), true);
  assert.equal(chamadas.length, 1);
  await tela.enviar();
  assert.match(tela.erro, /exatamente 3 questões/);
  assert.equal(chamadas.length, 1);
  tela.confirmarEnvio();
  assert.match(tela.erro, /exatamente 3 questões/);
  tela.importarQuestao("q3");
  tela.importarQuestao("q4");
  assert.equal(tela.questoes.length, 3);
  assert.match(tela.erro, /máximo 3/);
  await tela.enviar();
  assert.equal(tela.prova.status, "Enviada ao pedagógico");
  assert.equal(chamadas.at(-1).rota, "enviar");
  assert.deepEqual(chamadas.at(-2).ids, ["q2", "q1", "q3"]);
});

test("importação em lote não ultrapassa a quantidade da base", async () => {
  const { tela, prova, draft, banco } = ambiente(3, 5);
  prova.quantidade_questoes = 3;
  draft.questoes = [banco[2], banco[3]];
  await tela.carregar();
  assert.equal(tela.questoes.length, 2);
  assert.match(tela.aviso, /limite de 3 questões/);
});

test("turmas digitáveis selecionam várias sem duplicatas, removem e rejeitam turma desconhecida", async () => {
  const { tela, chamadas } = ambienteProvaBase();
  await tela.carregar();
  tela.formulario.codigoDisciplina = "MAT"; tela.selecionarDisciplina();
  assert.deepEqual([...tela.turmasDisponiveis], ["Turma 2026 B"]);
  tela.buscaTurma = "Turma 2026 B"; tela.adicionarTurma();
  tela.buscaTurma = "Turma 2026 B"; tela.adicionarTurma();
  assert.equal(tela.turmasSelecionadas.length, 2);
  tela.formulario.periodo_letivo = "1º período letivo"; tela.formulario.data = "2026-10-20";
  tela.formulario.quantidade_questoes = 3;
  await tela.salvar();
  assert.deepEqual([...chamadas[0].id_turma], ["Turma 2026 A", "Turma 2026 B"]);
  tela.removerTurma("Turma 2026 A");
  assert.deepEqual([...tela.turmasSelecionadas], ["Turma 2026 B"]);
  tela.buscaTurma = "Turma inexistente";
  await tela.salvar();
  assert.equal(chamadas.length, 1);
  assert.match(tela.erro, /turma cadastrada/);
  tela.salvando = true; tela.removerTurma("Turma 2026 B");
  assert.equal(tela.turmasSelecionadas.length, 1);
});

test("formulário usa sugestões digitáveis, professor em largura total e selects de série e período letivo", async () => {
  const { createSSRApp } = require("vue");
  const { renderToString } = require("@vue/server-renderer");
  const { tela, opcoes } = ambienteProvaBase();
  await tela.carregar();
  const fonte = fs.readFileSync(path.join(__dirname, "../src/components/CriarProvaBase.vue"), "utf8");
  const template = parse(fonte).descriptor.template.content;
  const html = await renderToString(createSSRApp({ ...opcoes, template, mounted: undefined, data: () => ({ ...opcoes.data(), carregando: false, professores: tela.professores, disciplinas: tela.disciplinas }) }));
  assert.match(html, /class="form-group-modal campo-largo"/);
  assert.match(html, /<input id="base-professor"[^>]*list="base-professores"/);
  assert.match(html, /<input id="base-turmas"[^>]*list="base-turmas-opcoes"/);
  assert.match(html, /<select id="base-serie"/);
  assert.match(html, /<select id="base-periodo-letivo"/);
  assert.match(html, /<input id="base-quantidade"[^>]*type="number" min="2" max="10" step="1" inputmode="numeric"/);
  assert.match(html, /aria-describedby="base-quantidade-ajuda"/);
  assert.match(html, /De 2 a 10 questões\./);
  assert.match(html, /3ª série/);
  assert.match(html, /4º período letivo/);
  assert.doesNotMatch(html, /<textarea/);
});

test("editor mostra apenas a seleção e sua quantidade, preservando metadados na prévia", async () => {
  const { createSSRApp, h } = require("vue");
  const { renderToString } = require("@vue/server-renderer");
  const template = parse(fs.readFileSync(path.join(__dirname, "../src/views/CriarProvaView.vue"), "utf8")).descriptor.template.content;
  for (const quantidade of [0, 1, 3, 10]) {
    const { tela, prova, banco, draft, opcoes } = ambiente(3, 10);
    prova.questoes = banco.slice(0, quantidade).map((questao) => questao._id);
    await tela.carregar();
    const html = await renderToString(createSSRApp({ ...opcoes, template,
      components: {
        ...opcoes.components,
        QuestaoEditor: () => null, ModalSairEdicao: () => null,
        PreviewProva: { props: ["metadados"], setup: (props) => () => h("div", { class: "preview-teste" }, props.metadados.nome_disciplina) },
      },
      setup: () => ({ authStore: tela.authStore, draft }),
      data: () => ({ ...opcoes.data(), prova: tela.prova, bancoQuestoes: banco, carregando: false }),
    }, { id: prova._id }));
    const painel = html.match(/<section class="painel painel-campos">([\s\S]*?)<\/section>/)[1];
    assert.match(painel, new RegExp(`<h3>Questões \\(${quantidade}\\)</h3>`));
    assert.doesNotMatch(painel, /Dados da prova|Professor responsável|Data de aplicação|O leitor de correção|\d+\/10/);
    assert.equal((painel.match(/<h3>/g) || []).length, 1);
    assert.match(html, /class="preview-teste"[^>]*>Matemática<\/div>/);
    assert.equal(tela.metadados.codigo_disciplina, "MAT");
    assert.equal(tela.limiteQuestoes, 10);
  }
});

test("aceita duas ou dez questões e envia apenas IDs", async () => {
  for (const quantidade of [2, 10]) {
    const { tela, prova, banco, chamadas } = ambiente(3, 11);
    prova.questoes = banco.slice(0, quantidade).map((questao) => questao._id);
    await tela.carregar(); await tela.enviar();
    assert.equal(tela.erro, "");
    assert.equal(chamadas.length, 2);
    assert.deepEqual(chamadas[0].ids, prova.questoes);
  }
});

test("bloqueia salvar e enviar com menos de duas questões", async () => {
  for (const quantidade of [0, 1]) {
    const { tela, prova, banco, chamadas } = ambiente();
    prova.questoes = banco.slice(0, quantidade).map((questao) => questao._id);
    await tela.carregar();
    assert.equal(await tela.salvar(), false);
    await tela.enviar();
    assert.match(tela.erro, /ao menos duas questões/);
    assert.equal(chamadas.length, 0);
  }
});

test("bloqueia a décima primeira seleção e remover uma questão libera espaço", async () => {
  const { tela, prova, banco } = ambiente(3, 11);
  prova.questoes = banco.slice(0, 10).map((questao) => questao._id);
  await tela.carregar();
  tela.importarQuestao("q11");
  assert.equal(tela.questoes.length, 10);
  assert.match(tela.erro, /máximo 10/);
  tela.removerQuestao(0); tela.importarQuestao("q11");
  assert.equal(tela.questoes.length, 10);
  assert.equal(tela.questoes[9]._idBanco, "q11");
  assert.equal(tela.erro, "");
});

test("cards filtram por enunciado, excluem incompatíveis e não duplicam seleção", async () => {
  const { tela, banco } = ambiente(3, 6);
  banco[2].assunto = "Geometria"; banco[2].enunciado = "Área de um quadrado";
  banco[3].assunto = "Equações"; banco[3].enunciado = "Resolva a igualdade";
  banco[4].disciplina = ["História"]; banco[5].tipo_questao = "Outro tipo";
  await tela.carregar();
  assert.deepEqual([...tela.questoesBancoFiltradas.map((questao) => questao._id)], ["q3", "q4"]);
  tela.filtrosQuestoes.enunciado = "  QUADRADO ";
  assert.deepEqual([...tela.questoesBancoFiltradas.map((questao) => questao._id)], ["q3"]);
  tela.filtrosQuestoes.enunciado = "igualdade";
  assert.deepEqual([...tela.questoesBancoFiltradas.map((questao) => questao._id)], ["q4"]);
  tela.importarQuestao("q4"); tela.importarQuestao("q4"); tela.importarQuestao("q5");
  assert.equal(tela.questoes.length, 3); assert.equal(tela.questoesBancoFiltradas.length, 0);
  tela.removerQuestao(2);
  assert.deepEqual([...tela.questoesBancoFiltradas.map((questao) => questao._id)], ["q4"]);
  tela.salvando = true; tela.importarQuestao("q4"); assert.equal(tela.questoes.length, 2);
});

test("editor renderiza cards com selects apenas para filtros e oculta o banco após concluir", async () => {
  const { createSSRApp } = require("vue");
  const { renderToString } = require("@vue/server-renderer");
  const template = parse(fs.readFileSync(path.join(__dirname, "../src/views/CriarProvaView.vue"), "utf8")).descriptor.template.content;
  const { tela, banco, prova, draft, opcoes } = ambiente(3, 4);
  await tela.carregar();
  const renderizar = () => renderToString(createSSRApp({ ...opcoes, template,
    components: { ...opcoes.components, QuestaoEditor: () => null, PreviewProva: () => null, ModalSairEdicao: () => null },
    setup: () => ({ authStore: tela.authStore, draft }),
    data: () => ({ ...opcoes.data(), prova, bancoQuestoes: banco, carregando: false }),
  }, { id: prova._id }));
  const html = await renderizar();
  assert.equal((html.match(/<select/g) || []).length, 2);
  assert.equal((html.match(/<article class="questao-card"/g) || []).length, 2);
  assert.match(html, /<details>/); assert.match(html, /Ver questão completa/); assert.match(html, /Adicionar à prova/);
  assert.match(html, /class="correta"/);
  prova.status = "Enviada ao pedagógico";
  const concluida = await renderizar();
  assert.doesNotMatch(concluida, /Banco de questões|Adicionar à prova/);
  assert.match(concluida, /somente visualização/);
});

test("quatro filtros combinam disciplina por código/nome, dificuldade exata, autor e texto sem HTML", () => {
  const disciplinas = [{ codigo_disciplina: "MAT", nome_disciplina: "Matemática" }];
  const questoes = [
    { _id: "q1", disciplina: ["MAT"], dificuldade: "Fácil", professor: { nome: "José Silva" }, enunciado: "<p>Calcule a área do quadrado</p>" },
    { _id: "q2", disciplina: ["Matemática"], dificuldade: "Muito Fácil", autor: "Ana", enunciado: "Área do quadrado" },
    { _id: "q3", disciplina: ["HIST"], dificuldade: "Fácil", professor: { nome: "José Silva" }, enunciado: "Área do quadrado" },
  ];
  const filtros = { disciplina: "Matemática", dificuldade: "facil", autor: " JOSE ", enunciado: "AREA  DO\nquadrado" };
  assert.deepEqual([...filtrosModulo.filtrarQuestoes(questoes, filtros, disciplinas).map((questao) => questao._id)], ["q1"]);
  assert.equal(filtrosModulo.filtrarQuestoes(questoes, { ...filtros, enunciado: "<p>" }, disciplinas).length, 0);
  const legado = [{ ...questoes[1], disciplinasOriginais: ["Matemática"], disciplina: "MAT, Matemática" }];
  assert.equal(filtrosModulo.filtrarQuestoes(legado, { disciplina: "MAT", autor: "ana" }, disciplinas).length, 1);
  assert.equal(filtrosModulo.filtrarQuestoes(questoes, filtrosModulo.novosFiltrosQuestoes(), disciplinas).length, 3);
});

test("select de disciplinas evita repetir código e nome e inclui registros sem disciplina cadastrada", () => {
  const questoes = [{ disciplina: ["mat", "Matemática", "Física"] }];
  const opcoes = filtrosModulo.opcoesDisciplinas(questoes, [{ codigo_disciplina: "MAT", nome_disciplina: "Matemática" }]);
  assert.equal(opcoes.length, 2);
  assert.deepEqual([...opcoes.map((item) => item.nome_disciplina)], ["Física", "Matemática"]);
  assert.equal(filtrosModulo.opcoesDisciplinas([{ disciplina: ["Geografia"] }]).length, 1);
});

test("filtros apresentam disciplina, dificuldade, autor e enunciado por último, sem mutar o modelo", async () => {
  const { createSSRApp } = require("vue");
  const { renderToString } = require("@vue/server-renderer");
  const modelo = filtrosModulo.novosFiltrosQuestoes();
  const html = await renderToString(createSSRApp(filtrosComponente, { modelValue: modelo }));
  const labels = [...html.matchAll(/<label[^>]*>([\s\S]*?)<\/label>/g)].map((match) => match[1].split(/<(?:select|input|textarea)/)[0].trim());
  assert.deepEqual(labels, ["Disciplina", "Dificuldade", "Autor", "Enunciado"]);
  assert.match(html, /<textarea[^>]*rows="2"/);
  const estilo = parse(fs.readFileSync(path.join(__dirname, "../src/components/FiltrosQuestoes.vue"), "utf8")).descriptor.styles[0].content;
  const css = compileStyle({ source: estilo, id: "data-v-teste-filtros", scoped: true }).code;
  assert.match(css, /\.tema-escuro \.filtros-questoes input/);
  assert.doesNotMatch(css, /\.tema-escuro\s*\{/);
  let emitido;
  filtrosComponente.methods.atualizar.call({ modelValue: modelo, $emit: (evento, valor) => { assert.equal(evento, "update:modelValue"); emitido = valor; } }, "autor", "Ana");
  assert.equal(modelo.autor, ""); assert.equal(emitido.autor, "Ana");
});

test("filtros do editor não permitem questões de outra disciplina ou já selecionadas", async () => {
  const { tela, banco } = ambiente(3, 4);
  banco[2].dificuldade = "Difícil"; banco[2].professor = { nome: "Ana" };
  banco[3].disciplina = ["HIST"]; banco[3].professor = { nome: "Ana" };
  await tela.carregar();
  tela.filtrosQuestoes = { disciplina: "MAT", dificuldade: "Difícil", autor: "ana", enunciado: "q3" };
  assert.deepEqual([...tela.questoesBancoFiltradas.map((questao) => questao._id)], ["q3"]);
  tela.importarQuestao("q3");
  assert.equal(tela.questoesBancoFiltradas.length, 0);
  tela.filtrosQuestoes.disciplina = "HIST";
  assert.equal(tela.questoesBancoFiltradas.length, 0);
  tela.importarQuestao("q4"); assert.equal(tela.questoes.length, 3);
});

test("visualização e Minhas Questões compartilham os filtros sem alterar o banco carregado", async () => {
  const banco = [
    { _id: "q1", disciplina: ["MAT"], dificuldade: "Médio", professor: { nome: "Ana" }, enunciado: "Área", alternativas: [] },
    { _id: "q2", disciplina: ["Matemática"], dificuldade: "Fácil", professor: { nome: "Beto" }, enunciado: "Área", alternativas: [] },
    { _id: "q3", disciplina: ["HIST"], dificuldade: "Médio", professor: { nome: "Ana" }, enunciado: "Brasil", alternativas: [] },
  ];
  const opcoes = carregarOpcoes("views/QuestoesView.vue", {
    "vue-router": {}, "@/stores/auth": {}, "@/stores/provaDraft": {}, "@/components/FiltrosQuestoes.vue": filtrosComponente,
    "@/utils/filtrosQuestoes": filtrosModulo, "@/utils/html": { sanitizar: (valor) => valor },
    "@/services/disciplinas": { listarDisciplinas: async () => ({ disciplinas: [{ codigo_disciplina: "MAT", nome_disciplina: "Matemática" }] }) },
    "@/services/questoes": { listarQuestoes: async () => ({ questoes: banco }) },
  }).default;
  const tela = instancia(opcoes, { authStore: { isProfessor: true, user: { nome: "Ana" } } });
  await tela.carregarDisciplinas(); await tela.carregarQuestoes();
  assert.equal(tela.resultados.length, 3); assert.equal(tela.minhasQuestoes.length, 2);
  tela.filtrosQuestoes.disciplina = "MAT";
  assert.equal(tela.resultados.length, 2); assert.equal(tela.minhasQuestoes.length, 1);
  tela.filtrosQuestoes.dificuldade = "Fácil";
  assert.equal(tela.resultados.length, 1); assert.equal(tela.minhasQuestoes.length, 0);
  tela.filtrosQuestoes = filtrosModulo.novosFiltrosQuestoes(); tela.filtrosQuestoes.autor = "ANA";
  assert.equal(tela.resultados.length, 2); tela.filtrosQuestoes.enunciado = "brasil";
  assert.deepEqual([...tela.resultados.map((questao) => questao.id)], ["q3"]);
  assert.equal(tela.todasQuestoes.length, 3); assert.equal(tela.carregandoQuestoes, false);
});

test("seleção em lote acima do limite é recusada com aviso, sem alterar a seleção salva", async () => {
  const { tela, draft, banco } = ambiente(3, 11);
  banco.slice(2).forEach((questao) => draft.adicionar(questao));
  await tela.carregar();
  assert.deepEqual([...tela.questoes.map((questao) => questao._idBanco)], ["q2", "q1"]);
  assert.match(tela.aviso, /Nenhuma questão dessa seleção foi adicionada/);
  assert.equal(draft.sujo, false);
});

test("seleção em lote que completa dez questões é aceita", async () => {
  const { tela, draft, banco } = ambiente(3, 11);
  banco.slice(2, 10).forEach((questao) => draft.adicionar(questao));
  await tela.carregar();
  assert.equal(tela.questoes.length, 10);
  assert.equal(tela.validar(), "");
  assert.equal(draft.sujo, true);
});

test("registro antigo com onze questões não é truncado nem salvo ou enviado", async () => {
  const { tela, prova, banco, chamadas } = ambiente(3, 11);
  prova.questoes = banco.map((questao) => questao._id);
  await tela.carregar();
  assert.equal(tela.questoes.length, 11);
  assert.equal(await tela.salvar(), false);
  await tela.enviar();
  assert.match(tela.erro, /máximo 10/);
  assert.equal(chamadas.length, 0);
});

test("lista vazia não pode ser salva ou enviada", async () => {
  const { tela, prova, chamadas } = ambiente();
  prova.questoes = [];
  await tela.carregar(); await tela.enviar();
  assert.match(tela.erro, /ao menos duas/);
  assert.equal(chamadas.length, 0);
});

test("carrega a base e conserva a ordem, sem recriação ou escrita de questões", async () => {
  const { tela, draft } = ambiente();
  await tela.carregar();
  assert.equal(tela.erroCarregamento, "");
  assert.equal(draft.provaId, "base-existente");
  assert.deepEqual([...tela.questoes.map((item) => item._idBanco)], ["q2", "q1"]);
  assert.equal(tela.metadados.codigo_disciplina, "MAT");
});

test("seleciona, ordena e envia exclusivamente IDs para PATCH", async () => {
  const { tela, chamadas } = ambiente();
  await tela.carregar();
  tela.importarQuestao("q3"); tela.moverQuestao(2, -1);
  assert.equal(await tela.salvar(), true);
  assert.deepEqual(chamadas, [{ rota: "selecionar", id: "base-existente", ids: ["q2", "q3", "q1"] }]);
});

test("correta ausente, enunciado vazio e alternativas incompletas impedem salvar", async () => {
  const { tela, chamadas } = ambiente();
  await tela.carregar();
  tela.questoes[0].indiceCorreta = -1;
  assert.equal(await tela.salvar(), false);
  tela.questoes[0].indiceCorreta = 2; tela.questoes[0].enunciado = "<p><br></p>";
  assert.equal(await tela.salvar(), false);
  tela.questoes[0].enunciado = "Questão"; tela.questoes[0].alternativas.pop();
  assert.equal(await tela.salvar(), false);
  assert.equal(chamadas.length, 0);
});

test("zero versões mostra aviso e não chama envio", async () => {
  const { tela, chamadas } = ambiente(0);
  await tela.carregar(); await tela.enviar();
  assert.match(tela.aviso, /nenhuma versão/);
  assert.equal(chamadas.length, 1);
});

test("envio conclui e bloqueia seleção, reordenação, remoção e salvamento", async () => {
  const { tela, chamadas } = ambiente();
  await tela.carregar(); await tela.enviar();
  assert.equal(tela.editavel, false);
  tela.importarQuestao("q3"); tela.moverQuestao(0, 1); tela.removerQuestao(0);
  assert.equal(await tela.salvar(), false);
  assert.deepEqual([...tela.questoes.map((item) => item._idBanco)], ["q2", "q1"]);
  assert.equal(chamadas.length, 2);
});

test("toast de prova-base fecha o modal, expira e limpa o temporizador anterior", () => {
  const temporizadores = new Map(); let proximoId = 0;
  const opcoes = carregarOpcoes("views/ProvasView.vue", {
    "@/stores/auth": {}, "@/services/provas": { provaEditavel: () => false }, "@/components/CriarProvaBase.vue": {},
  }, {
    setTimeout: (callback, duracao) => { assert.equal(duracao, 8000); temporizadores.set(++proximoId, callback); return proximoId; },
    clearTimeout: (id) => temporizadores.delete(id),
  }).default;
  const tela = instancia(opcoes, { mostrarCriacaoBase: true });
  tela.provaBaseCriada({ professor: { nome: "Ana Silva" } });
  assert.equal(tela.mostrarCriacaoBase, false);
  assert.match(tela.aviso, /Ana Silva/);
  assert.equal(temporizadores.size, 1);
  tela.provaBaseCriada({ professor: { nome: "Bruno Souza" } });
  assert.equal(temporizadores.size, 1);
  assert.match(tela.aviso, /Bruno Souza/);
  temporizadores.get(tela.temporizadorAviso)();
  assert.equal(tela.aviso, ""); assert.equal(temporizadores.size, 0);
  tela.provaBaseCriada({ professor: { nome: "Ana Silva" } });
  tela.fecharAviso();
  assert.equal(tela.aviso, ""); assert.equal(temporizadores.size, 0);
  tela.provaBaseCriada({ professor: { nome: "Ana Silva" } });
  opcoes.beforeUnmount.call(tela);
  assert.equal(temporizadores.size, 0);
});

test("confirmação de criação renderiza um toast azul acessível e com botão de fechar", async () => {
  const { createSSRApp } = require("vue"); const { renderToString } = require("@vue/server-renderer");
  const opcoes = carregarOpcoes("views/ProvasView.vue", {
    "@/stores/auth": {}, "@/services/provas": { provaEditavel: () => false }, "@/components/CriarProvaBase.vue": {},
  }).default;
  const fonte = fs.readFileSync(path.join(__dirname, "../src/views/ProvasView.vue"), "utf8");
  const html = await renderToString(createSSRApp({ ...opcoes, template: parse(fonte).descriptor.template.content,
    setup: () => ({ authStore: { isProfessor: false, isProcessoPedagogico: true } }),
    data: () => ({ ...opcoes.data(), aviso: "Atribuída a Ana Silva." }),
  }));
  assert.match(html, /class="toast-aviso" role="status" aria-live="polite"/);
  assert.match(html, /Prova-base criada!/);
  assert.match(html, /aria-label="Fechar aviso"/);
  assert.doesNotMatch(html, /<p role="status">/);
  assert.match(fonte, /\.toast-aviso\s*\{[^}]*background: #00488b;\s*color: #fff;/);
  assert.match(fonte, /\.toast-conteudo p\s*\{[^}]*color: inherit/);
});

test("listagem filtra professor por registro e pedagógico por provas enviadas", async () => {
  const dados = ambiente();
  let filtro;
  const opcoes = carregarOpcoes("views/ProvasView.vue", {
    "@/stores/auth": {}, "@/services/questoes": {}, "@/components/CriarProvaBase.vue": {}, "@/utils/html": {},
    "@/services/provas": { ...dados.servicos, listarProvas: async (params) => { filtro = params; return { provas: [
      { ...dados.tela.prova, _id: "base", disciplina: { nome_disciplina: "Matemática" }, status: "Em elaboração" },
      { _id: "enviada", disciplina: { nome_disciplina: "Matemática" }, id_turma: "A", status: "Enviada ao pedagógico" },
    ] }; } },
  }).default;
  const tela = instancia(opcoes, { authStore: { isProfessor: true, user: { registro: 1 } } });
  await tela.carregarProvas(); assert.equal(filtro.registro, 1); assert.equal(tela.minhasProvas.length, 2);
  tela.authStore.isProfessor = false;
  await tela.carregarProvas(); assert.equal(Object.keys(filtro).length, 0);
  assert.deepEqual([...tela.minhasProvas.map((prova) => prova.id)], ["enviada"]);
});

test("professor separa provas ainda editáveis das enviadas e mantém as corrigidas na segunda aba", () => {
  const opcoes = carregarOpcoes("views/ProvasView.vue", {
    "@/stores/auth": {}, "@/components/CriarProvaBase.vue": {},
    "@/services/provas": { provaEditavel: (prova) => ["Aguardando questões", "Em elaboração"].includes(prova.status) },
  }).default;
  const status = ["Aguardando questões", "Em elaboração", "Enviada ao pedagógico", "Impressa", "Corrigida"];
  const tela = instancia(opcoes, { authStore: { isProfessor: true }, minhasProvas: status.map((status, id) => ({ id, status })) });
  assert.deepEqual([...tela.provasExibidas.map((prova) => prova.id)], [0, 1]);
  assert.equal(tela.provasAguardandoQuestoes.length, 2); assert.equal(tela.provasEnviadas.length, 3);
  tela.abaAtiva = "enviadas";
  assert.deepEqual([...tela.provasExibidas.map((prova) => prova.id)], [2, 3, 4]);
  assert.deepEqual([...tela.minhasProvas.map((prova) => prova.status)], status);
  tela.authStore.isProfessor = false; tela.abaAtiva = "minhas";
  assert.deepEqual([...tela.provasExibidas.map((prova) => prova.id)], [2]);
  tela.abaAtiva = "impressas";
  assert.deepEqual([...tela.provasExibidas.map((prova) => prova.id)], [3]);
  tela.abaAtiva = "corrigidas";
  assert.deepEqual([...tela.provasExibidas.map((prova) => prova.id)], [4]);
});

test("professor mantém suas abas; pedagógico vê recebidas, impressas e corrigidas", async () => {
  const { createSSRApp } = require("vue");
  const { renderToString } = require("@vue/server-renderer");
  const opcoes = carregarOpcoes("views/ProvasView.vue", {
    "@/stores/auth": {}, "@/services/provas": { provaEditavel: () => false }, "@/components/CriarProvaBase.vue": {},
  }).default;
  const template = parse(fs.readFileSync(path.join(__dirname, "../src/views/ProvasView.vue"), "utf8")).descriptor.template.content;
  for (const professor of [true, false]) {
    const html = await renderToString(createSSRApp({ ...opcoes, template,
      setup: () => ({ authStore: { isProfessor: professor, isProcessoPedagogico: !professor } }),
    }));
    const abas = [...html.matchAll(/<button[^>]*class="[^"]*tab-btn[^"]*"[^>]*>([^<]*)<\/button>/g)].map((match) => match[1].trim());
    assert.deepEqual(abas, professor
      ? ["Aguardando questões (0)", "Enviada ao processo pedagógico (0)"]
      : ["Provas Recebidas (0)", "Provas Impressas (0)", "Provas Corrigidas (0)"]);
  }
});

test("botão de correção aparece apenas para o processo pedagógico", async () => {
  const { createSSRApp } = require("vue");
  const { renderToString } = require("@vue/server-renderer");
  const opcoes = carregarOpcoes("views/ProvasView.vue", {
    "@/stores/auth": {}, "@/services/provas": { provaEditavel: () => false }, "@/components/CriarProvaBase.vue": {},
  }).default;
  const fonte = fs.readFileSync(path.join(__dirname, "../src/views/ProvasView.vue"), "utf8");
  const template = parse(fonte).descriptor.template.content;
  for (const processo of [false, true]) {
    const html = await renderToString(createSSRApp({ ...opcoes, template,
      setup: () => ({ authStore: { isProfessor: !processo, isProcessoPedagogico: processo } }),
    }));
    assert.equal(html.includes("btn-corrigir"), processo);
  }
});

test("professor não vê a lixeira nas provas aguardando questões ou em elaboração", async () => {
  const { createSSRApp } = require("vue");
  const { renderToString } = require("@vue/server-renderer");
  const opcoes = carregarOpcoes("views/ProvasView.vue", {
    "@/stores/auth": {}, "@/components/CriarProvaBase.vue": {},
    "@/services/provas": { provaEditavel: (prova) => ["Aguardando questões", "Em elaboração"].includes(prova.status) },
  }).default;
  const template = parse(fs.readFileSync(path.join(__dirname, "../src/views/ProvasView.vue"), "utf8")).descriptor.template.content;
  for (const professor of [true, false]) {
    const html = await renderToString(createSSRApp({ ...opcoes, template,
      setup: () => ({ authStore: { isProfessor: professor, isProcessoPedagogico: !professor } }),
      data: () => ({ ...opcoes.data(), carregando: false, minhasProvas: ["Aguardando questões", "Em elaboração"].map((status, id) => ({
        id, status, titulo: "Prova teste", criadaEm: "2026-10-14", professor: { nome: "Professor Teste" },
      })) }),
    }));
    assert.equal((html.match(/class="prova-card"/g) || []).length, professor ? 2 : 0);
    assert.equal((html.match(/class="btn-excluir-prova"/g) || []).length, 0);
  }
});

test("método de exclusão ignora professor e mantém confirmação para pedagógico", async () => {
  let modal = null;
  const exclusoes = [];
  const opcoes = carregarOpcoes("views/ProvasView.vue", {
    "@/stores/auth": {}, "@/components/CriarProvaBase.vue": {},
    "@/services/provas": { provaEditavel: () => true, excluirProva: async (id) => { exclusoes.push(id); }, listarProvas: async () => ({ provas: [] }) },
  }, { window: { $modal: { abrir: (dados) => { modal = dados; } } } }).default;
  const tela = instancia(opcoes, { authStore: { isProfessor: true, isProcessoPedagogico: false } });
  tela.excluirProva("base");
  assert.equal(modal, null); assert.equal(exclusoes.length, 0);
  tela.authStore = { isProfessor: false, isProcessoPedagogico: true };
  tela.excluirProva("base");
  assert.equal(modal.tipo, "confirmacao"); assert.equal(exclusoes.length, 0);
  await modal.onConfirm();
  assert.deepEqual(exclusoes, ["base"]); assert.equal(tela.excluindoId, null);
});

test("rota de correção bloqueia professor e visitante, mas permite processo pedagógico", () => {
  let configuracao, guarda, auth;
  carregarOpcoes("router/index.js", {
    "vue-router": {
      createWebHistory: () => ({}),
      createRouter: (opcoes) => { configuracao = opcoes; return { beforeEach: (callback) => { guarda = callback; } }; },
    },
    "@/views/LoginTelaPrincipal.vue": {}, "@/components/TelaPrincipal.vue": {}, "@/views/ProvasView.vue": {},
    "@/views/QuestoesView.vue": {}, "@/views/GestaoUsuarios.vue": {}, "@/views/ConfiGuracoes.vue": {},
    "@/views/CriarProvaView.vue": {}, "@/stores/auth": { useAuthStore: () => auth },
  });
  const principal = configuracao.routes.find((rota) => rota.children);
  const correcao = principal.children.find((rota) => rota.name === "CorrigirProvasView");
  assert.equal(correcao.meta.requiresProcesso, true);
  const destino = { meta: { ...principal.meta, ...correcao.meta } };
  for (const [perfil, esperado] of [
    [{ isLoggedIn: false }, "/"],
    [{ isLoggedIn: true, isProfessor: true, isProcessoPedagogico: false }, "/provas"],
    [{ isLoggedIn: true, isProfessor: false, isProcessoPedagogico: true }, undefined],
  ]) {
    auth = perfil;
    let redirecionamento = "não executado";
    guarda(destino, {}, (valor) => { redirecionamento = valor; });
    assert.equal(redirecionamento, esperado);
  }
});

test("cada status da prova tem um balão distinto e status desconhecido usa o estilo neutro", () => {
  const opcoes = carregarOpcoes("views/ProvasView.vue", {
    "@/stores/auth": {}, "@/services/provas": {}, "@/components/CriarProvaBase.vue": {},
  }).default;
  const esperados = {
    "Aguardando questões": "aguardando", "Em elaboração": "elaboracao",
    "Enviada ao pedagógico": "enviado", "Impressa": "impressa", "Corrigida": "corrigido",
  };
  const fonte = fs.readFileSync(path.join(__dirname, "../src/views/ProvasView.vue"), "utf8");
  for (const [status, classe] of Object.entries(esperados)) {
    assert.equal(opcoes.methods.classeStatus(status), classe);
    assert.match(fonte, new RegExp(`\\.status\\.${classe}\\s*\\{`));
  }
  assert.equal(new Set(Object.values(esperados)).size, 5);
  assert.equal(opcoes.methods.classeStatus("Outro status"), "");
  assert.equal(opcoes.methods.classeStatus(null), "");
});

test("prévia utiliza o novo campo e marcador de período letivo", () => {
  const opcoes = carregarOpcoes("components/PreviewProva.vue", {
    "@/stores/provaDraft": { LETRAS: ["A", "B", "C", "D", "E"] },
    "@/utils/html": { escaparHtml: String, sanitizar: (valor) => valor, htmlVazio: (valor) => !valor },
  }).default;
  const html = opcoes.computed.htmlFinal.call({
    template: "<p>{{PERIODO_LETIVO}}</p>", metadados: { turmasTexto: "Turma A", periodo_letivo: "2º período letivo" },
    professor: "", matricula: "", htmlQuestoes: "",
  });
  assert.equal(html, "<p>2º período letivo</p>");
});

test("template das exibições contém somente questões, sem cabeçalho duplicado", () => {
  const template = carregarOpcoes("assets/templates/templateProva.js", {}).default;
  assert.match(template, /\{\{QUESTOES\}\}/);
  assert.doesNotMatch(template, /<header|<h1|<table|<hr|Professor|Matrícula|Avaliação/);
});

test("cartão vetorial preserva dez colunas, cinco alternativas e geometria do QR", async () => {
  const { createSSRApp } = require("vue");
  const { renderToString } = require("@vue/server-renderer");
  const modelo = carregarOpcoes("utils/cartaoResposta.js", {}).CARTAO_RESPOSTA;
  const fonte = fs.readFileSync(path.join(__dirname, "../src/components/CartaoResposta.vue"), "utf8");
  const opcoes = carregarOpcoes("components/CartaoResposta.vue", {
    "@/assets/templates/cartao-resposta.png": "logos-originais.png",
    "@/utils/cartaoResposta": { CARTAO_RESPOSTA: modelo },
  }).default;
  const { prova } = ambiente();
  const html = await renderToString(createSSRApp({ ...opcoes, template: parse(fonte).descriptor.template.content }, {
    prova, matricula: 20260001, nomeAluno: "Ana Maria da Silva", qrCode: "qr-individual.png",
  }));
  assert.match(html, /viewBox="0 0 1200 286"/i);
  assert.equal((html.match(/M[\d.]+ 86V257/g) || []).length, 10);
  for (const letra of ["A", "B", "C", "D", "E"]) assert.match(html, new RegExp(`>${letra}</text>`));
  assert.match(html, /href="qr-individual.png" x="9" y="168" width="94" height="94"/);
  assert.equal((html.match(/href="logos-originais.png"/g) || []).length, 2);
  assert.match(html, /M0 143H1200/);
  assert.match(html, /Matemática/);
  assert.match(html, /3º período letivo/);
  assert.match(html, /20260001/);
  assert.equal((html.match(/Ana Maria da Silva/g) || []).length, 1);
  assert.match(html, /x="705" y="107"[^>]*>Ana Maria da Silva<\/text>/);
  assert.match(html, /M738 250H1107/);
  assert.match(html, />NOME DO ALUNO POR EXTENSO<\/text>/);
});

function ambienteImpressao(versoes, globais) {
  const { banco, prova, servicos } = ambiente();
  prova.status = "Enviada ao pedagógico";
  const qrs = [];
  const draftModulo = carregarOpcoes("stores/provaDraft.js", { pinia: { defineStore: (_, opcoes) => opcoes } });
  const dados = versoes || [{ id_prova_aluno: "versao-individual", matricula_aluno: 20260001, nome_aluno: "Ana Maria da Silva", turma_aluno: "Turma A", questoes: [banco[2], banco[0]] }];
  const opcoes = carregarOpcoes("views/ImprimirProvasView.vue", {
    qrcode: { toDataURL: async (id) => { qrs.push(id); return `qr:${id}`; } },
    "@/components/CartaoResposta.vue": {}, "@/components/PreviewProva.vue": {},
    "@/components/ListaTurma.vue": {},
    "@/utils/listasTurma": carregarOpcoes("utils/listasTurma.js", {}),
    "@/services/provas": { ...servicos, imprimirProvas: async (id) => {
      assert.equal(id, prova._id); return { provas_alunos: dados };
    } },
    "@/services/templates": { obterTemplateProva: async () => "template" }, "@/stores/provaDraft": draftModulo,
    "@/utils/cartaoResposta": { CARTAO_RESPOSTA: { qr: { margem: 4 } } },
  }, globais).default;
  return { tela: instancia(opcoes, { id: prova._id }), prova, dados, qrs };
}

function ambienteConfirmacaoImpressao(responder) {
  const { prova, servicos } = ambiente();
  prova.status = "Enviada ao pedagógico";
  const confirmacoes = [], modais = [];
  const opcoes = carregarOpcoes("views/ProvasView.vue", {
    "@/stores/auth": {}, "@/components/CriarProvaBase.vue": {},
    "@/services/provas": { ...servicos, confirmarImpressao: async (id) => {
      confirmacoes.push(id);
      return responder ? responder() : { prova: { ...prova, status: "Impressa" } };
    } },
  }, { window: { $modal: { abrir: (opcoes) => modais.push(opcoes) } } }).default;
  const tela = instancia(opcoes, { authStore: { isProcessoPedagogico: true, isProfessor: false } });
  const card = tela.adaptarProva(prova);
  tela.minhasProvas = [card];
  return { tela, card, confirmacoes, modais, opcoes };
}

test("impressão usa a ordem individual e gera QR com id_prova_aluno", async () => {
  const { tela, qrs } = ambienteImpressao();
  await tela.carregar();
  assert.equal(tela.erro, "");
  assert.equal(tela.versoes[0].matricula_aluno, 20260001);
  assert.equal(tela.versoes[0].nome_aluno, "Ana Maria da Silva");
  assert.deepEqual([...tela.versoes[0].questoes.map((q) => q._idBanco)], ["q3", "q1"]);
  assert.deepEqual([...tela.versoes[0].questoes[0].alternativas], ["A", "B", "C", "D", "E"]);
  assert.deepEqual(qrs, ["versao-individual"]);
});

test("não monta impressão de prova editável, sem identificador ou acima de dez questões", async () => {
  const ambienteBase = ambienteImpressao();
  ambienteBase.prova.status = "Em elaboração";
  await ambienteBase.tela.carregar();
  assert.match(ambienteBase.tela.erro, /Conclua e envie/);
  const semId = ambienteImpressao([{ questoes: [{}] }]);
  await semId.tela.carregar();
  assert.equal(semId.tela.versoes.length, 0);
  assert.equal(semId.qrs.length, 0);
  const acimaDoLimite = ambienteImpressao([{ id_prova_aluno: "individual", questoes: Array(11).fill({}) }]);
  await acimaDoLimite.tela.carregar();
  assert.match(acimaDoLimite.tela.erro, /1 a 10/);
});

test("impressão sem versões não gera QR nem mostra erro de carregamento", async () => {
  const { tela, qrs } = ambienteImpressao([]);
  await tela.carregar();
  assert.equal(tela.erro, "");
  assert.equal(tela.carregando, false);
  assert.equal(tela.versoes.length, 0);
  assert.equal(qrs.length, 0);
});

test("impressão não monta versão com quantidade diferente da base", async () => {
  const { tela, prova, qrs } = ambienteImpressao();
  prova.quantidade_questoes = 3;
  await tela.carregar();
  assert.equal(tela.versoes.length, 0);
  assert.equal(qrs.length, 0);
  assert.match(tela.erro, /quantidade de questões definida/);
});

test("serviço de impressão chama a rota individualizada", async () => {
  const chamadas = [];
  const servicos = carregarOpcoes("services/provas.js", { "./api": { api: async (rota) => { chamadas.push(rota); return {}; } } });
  await servicos.imprimirProvas("base-1");
  assert.deepEqual(chamadas, ["/provas/imprimir-provas/base-1"]);
});

test("card solicita confirmação em modal e só chama API após confirmar", async () => {
  const { tela, card, confirmacoes, modais } = ambienteConfirmacaoImpressao();
  tela.solicitarConfirmacaoImpressao(card);
  assert.equal(modais[0].tipo, "confirmacao");
  assert.match(modais[0].mensagem, /Confirmar impressão da prova\?/);
  assert.equal(confirmacoes.length, 0);
  assert.equal(card.status, "Enviada ao pedagógico");
  // Fechar/cancelar o modal não executa onConfirm e não altera o status.
  tela.solicitarConfirmacaoImpressao(card);
  assert.equal(confirmacoes.length, 0);
  await modais[1].onConfirm();
  assert.equal(card.status, "Impressa");
  assert.equal(tela.provasRecebidas.length, 0);
  assert.equal(tela.provasImpressas.length, 1);
  assert.equal(confirmacoes.length, 1);
  assert.equal(confirmacoes[0], card.id);
  await tela.confirmarImpressao(card);
  card.status = "Corrigida";
  tela.solicitarConfirmacaoImpressao(card);
  await tela.confirmarImpressao(card);
  assert.equal(confirmacoes.length, 1);
  assert.equal(modais.length, 2);
});

test("confirmação bloqueia professor e envios repetidos enquanto aguarda a API", async () => {
  let resolver;
  const contexto = ambienteConfirmacaoImpressao(() => new Promise((resolve) => { resolver = resolve; }));
  const { tela, card, modais, confirmacoes } = contexto;
  tela.authStore.isProcessoPedagogico = false;
  tela.solicitarConfirmacaoImpressao(card);
  await tela.confirmarImpressao(card);
  assert.equal(modais.length, 0); assert.equal(confirmacoes.length, 0);
  tela.authStore.isProcessoPedagogico = true;
  const pendente = tela.confirmarImpressao(card);
  assert.equal(tela.confirmandoImpressaoId, card.id);
  assert.equal(card.status, "Enviada ao pedagógico");
  tela.solicitarConfirmacaoImpressao(card);
  await tela.confirmarImpressao(card);
  assert.equal(confirmacoes.length, 1); assert.equal(modais.length, 0);
  resolver({ prova: { ...card, _id: card.id, status: "Impressa" } });
  await pendente;
  assert.equal(tela.confirmandoImpressaoId, null);
  assert.equal(card.status, "Impressa");
});

test("botão de confirmação fica ao lado da impressora só para pedagógico e provas recebidas", async () => {
  const { createSSRApp } = require("vue"), { renderToString } = require("@vue/server-renderer");
  const { opcoes, card } = ambienteConfirmacaoImpressao();
  const template = parse(fs.readFileSync(path.join(__dirname, "../src/views/ProvasView.vue"), "utf8")).descriptor.template.content;
  for (const [pedagogico, status, aba, esperado] of [[true, "Enviada ao pedagógico", "minhas", true], [true, "Impressa", "impressas", false], [true, "Corrigida", "corrigidas", false], [false, "Enviada ao pedagógico", "enviadas", false]]) {
    const html = await renderToString(createSSRApp({ ...opcoes, template,
      setup: () => ({ authStore: { isProcessoPedagogico: pedagogico, isProfessor: !pedagogico } }),
      data: () => ({ ...opcoes.data(), carregando: false, abaAtiva: aba, minhasProvas: [{ ...card, status }] }),
    }));
    assert.equal(html.includes('aria-label="Confirmar impressão realizada"'), esperado);
    if (esperado) assert.match(html, /🖨️\s*<\/button>\s*<button[^>]*btn-confirmar-impressao/);
  }
  const impressao = carregarOpcoes("views/ImprimirProvasView.vue", {
    qrcode: {}, "@/components/CartaoResposta.vue": {}, "@/components/PreviewProva.vue": {}, "@/components/ListaTurma.vue": {},
    "@/utils/listasTurma": {}, "@/services/provas": {}, "@/services/templates": {}, "@/stores/provaDraft": {}, "@/utils/cartaoResposta": {},
  }).default;
  assert.equal(impressao.methods.confirmarImpressao, undefined);
  const fonte = fs.readFileSync(path.join(__dirname, "../src/views/ImprimirProvasView.vue"), "utf8");
  assert.doesNotMatch(fonte, /Confirmar impressão realizada|confirmando|confirmarImpressao/);
});

test("serviço confirma impressão por PATCH dedicado", async () => {
  const chamadas = [];
  const servicos = carregarOpcoes("services/provas.js", { "./api": { api: async (...args) => { chamadas.push(args); return {}; } } });
  await servicos.confirmarImpressao("base-1");
  assert.equal(chamadas[0][0], "/provas/base-1/confirmar-impressao");
  assert.equal(chamadas[0][1].method, "PATCH");
});

test("falha ao confirmar impressão mantém status anterior e permite tentar novamente", async () => {
  for (const responder of [() => { throw new Error("API indisponível"); }, () => ({ prova: { status: "Enviada ao pedagógico" } })]) {
    const { tela, card, confirmacoes, modais } = ambienteConfirmacaoImpressao(responder);
    await tela.confirmarImpressao(card);
    assert.equal(card.status, "Enviada ao pedagógico");
    assert.equal(tela.confirmandoImpressaoId, null);
    assert.equal(modais[0].tipo, "alerta");
    assert.match(modais[0].mensagem, /API indisponível|servidor não confirmou/);
    await tela.confirmarImpressao(card);
    assert.equal(confirmacoes.length, 2);
  }
});

test("impressão remove contagem e reserva as margens dentro da prova, sem URL ou paginação", () => {
  const fonte = fs.readFileSync(path.join(__dirname, "../src/views/ImprimirProvasView.vue"), "utf8");
  const { descriptor } = parse(fonte);
  assert.doesNotMatch(descriptor.template.content, /\{\{\s*versoes.length\s*\}\}/);
  const css = descriptor.styles.find((estilo) => !estilo.scoped).content;
  assert.match(css, /@page\s*\{[^}]*margin:\s*0\s*;/);
  assert.match(css, /\.documento-impressao\s*\{[^}]*padding:\s*12mm\s*!important/);
  assert.match(css, /box-decoration-break:\s*clone/);
  assert.match(css, /\.sidebar[^}]*display:\s*none\s*!important/);
});

test("espera as imagens antes de imprimir e bloqueia impressão se uma delas falhar", async () => {
  let impressoes = 0;
  let decodificadas = 0;
  let falhar = false;
  const { tela } = ambienteImpressao(undefined, {
    window: { print: () => { assert.equal(decodificadas, 2); impressoes++; } },
    document: { fonts: { ready: Promise.resolve() }, querySelectorAll: () => [{ src: "figura.png" }, { href: { baseVal: "cartao.png" } }] },
    Image: class { async decode() { if (falhar) throw new Error("Imagem indisponível"); decodificadas++; } },
  });
  await tela.carregar(); await tela.imprimir();
  assert.equal(impressoes, 1);
  assert.equal(tela.prova.status, "Enviada ao pedagógico");
  assert.equal(tela.imprimindo, false);
  falhar = true;
  await tela.imprimir();
  assert.match(tela.erro, /imagem não carregou/);
  assert.equal(impressoes, 1);
});

test("impressão agrupa duas listas e as versões de cada turma sem misturar alunos", async () => {
  const contexto = ambienteImpressao();
  const base = contexto.dados[0];
  contexto.prova.id_turma = ["1ºI - INFORMÁTICA", "1ºH - INFORMÁTICA"];
  contexto.dados.splice(0, 1,
    { ...base, matricula_aluno: 20260002, nome_aluno: "Bruno Teste", turma_aluno: "1ºI - INFORMÁTICA" },
    { ...base, matricula_aluno: 20260001, nome_aluno: "Ana Teste", turma_aluno: "1ºI - INFORMÁTICA" },
    { ...base, matricula_aluno: 20260003, nome_aluno: "Carla Teste", turma_aluno: "1ºH - INFORMÁTICA" });
  await contexto.tela.carregar();
  assert.equal(contexto.tela.erro, "");
  assert.equal(contexto.tela.turmas.length, 2);
  assert.deepEqual([...contexto.tela.turmas[1].alunos.map(a => a.nome_aluno)], ["Ana Teste", "Bruno Teste"]);
  assert.deepEqual([...contexto.tela.turmas[1].alunos.map(a => a.numero_chamada)], [1, 2]);
  const fonte = parse(fs.readFileSync(path.join(__dirname, "../src/views/ImprimirProvasView.vue"), "utf8")).descriptor.template.content;
  assert.match(fonte, /ListaTurma[^>]*tipo="notas"/);
  assert.match(fonte, /ListaTurma[^>]*tipo="entrega"/);
  assert.match(fonte, /v-for="versao in grupo.alunos"/);
});

test("nome ou turma indisponíveis impedem imprimir listas incorretas", async () => {
  for (const campo of ["nome_aluno", "turma_aluno"]) {
    const contexto = ambienteImpressao();
    contexto.dados[0][campo] = "";
    await contexto.tela.carregar();
    assert.match(contexto.tela.erro, /Confira o nome e a turma/);
    assert.equal(contexto.tela.versoes.length, 0);
    assert.equal(contexto.tela.turmas.length, 0);
  }
});
