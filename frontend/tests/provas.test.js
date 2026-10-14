const { test } = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const { parse } = require("@vue/compiler-sfc");
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

function ambiente(quantidade = 3, tamanhoBanco = 3) {
  const draftModulo = carregarOpcoes("stores/provaDraft.js", { pinia: { defineStore: (_, opcoes) => opcoes } });
  const draftOpcoes = draftModulo.useProvaDraftStore;
  const draft = draftOpcoes.state();
  Object.entries(draftOpcoes.actions).forEach(([nome, acao]) => { draft[nome] = acao.bind(draft); });
  const banco = Array.from({ length: tamanhoBanco }, (_, index) => `q${index + 1}`).map((_id) => ({ _id, enunciado: _id, disciplina: ["mat"], tipo_questao: "Objetiva",
    alternativas: ["A", "B", "C", "D", "E"].map((texto) => ({ id: texto, texto })), alternativa_correta: "C" }));
  let prova = { _id: "base-existente", professor: { registro: 1, nome: "Professor Teste" },
    disciplina: { codigo_disciplina: "MAT", nome_disciplina: "Matemática" }, id_turma: "Turma A", tipo: "Objetiva",
    serie: 3, bimestre: "3º bimestre", data_de_aplicacao: "2026-10-14", status: "Aguardando questões", questoes: ["q2", "q1"] };
  const chamadas = [];
  const servicos = {
    buscarProva: async (id) => { assert.equal(id, prova._id); return prova; },
    provaEditavel: (item) => ["Aguardando questões", "Em elaboração"].includes(item.status),
    adicionarQuestoes: async (id, ids) => { chamadas.push({ rota: "selecionar", id, ids: [...ids] }); prova = { ...prova, questoes: [...ids], status: "Em elaboração" }; return { prova, provas_alunos_geradas: quantidade }; },
    enviarProva: async (id) => { chamadas.push({ rota: "enviar", id }); prova = { ...prova, status: "Enviada ao pedagógico" }; return { prova }; },
  };
  const opcoes = carregarOpcoes("views/CriarProvaView.vue", {
    "@/components/QuestaoEditor.vue": {}, "@/components/PreviewProva.vue": {}, "@/components/ModalSairEdicao.vue": {},
    "@/stores/auth": {}, "@/stores/provaDraft": draftModulo, "@/services/questoes": { listarQuestoes: async () => ({ questoes: banco }) },
    "@/services/provas": servicos, "@/services/templates": { obterTemplateProva: async () => "template" },
    "@/utils/html": { textoPuro: (valor) => valor, htmlVazio: (valor) => !valor || valor === "<p><br></p>" },
  }).default;
  return { tela: instancia(opcoes, { id: prova._id, draft, authStore: { user: { registro: 1 } } }), chamadas, draft, banco, prova, servicos };
}

test("aceita uma ou dez questões e envia apenas IDs", async () => {
  for (const quantidade of [1, 10]) {
    const { tela, prova, banco, chamadas } = ambiente(3, 11);
    prova.questoes = banco.slice(0, quantidade).map((questao) => questao._id);
    await tela.carregar(); await tela.enviar();
    assert.equal(tela.erro, "");
    assert.equal(chamadas.length, 2);
    assert.deepEqual(chamadas[0].ids, prova.questoes);
  }
});

test("bloqueia a décima primeira seleção e remover uma questão libera espaço", async () => {
  const { tela, prova, banco } = ambiente(3, 11);
  prova.questoes = banco.slice(0, 10).map((questao) => questao._id);
  await tela.carregar();
  tela.questaoBancoSelecionada = "q11"; tela.importarQuestao();
  assert.equal(tela.questoes.length, 10);
  assert.match(tela.erro, /máximo 10/);
  tela.removerQuestao(0); tela.importarQuestao();
  assert.equal(tela.questoes.length, 10);
  assert.equal(tela.questoes[9]._idBanco, "q11");
  assert.equal(tela.erro, "");
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
  assert.match(tela.erro, /ao menos uma/);
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
  tela.questaoBancoSelecionada = "q3"; tela.importarQuestao(); tela.moverQuestao(2, -1);
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
  tela.questaoBancoSelecionada = "q3"; tela.importarQuestao(); tela.moverQuestao(0, 1); tela.removerQuestao(0);
  assert.equal(await tela.salvar(), false);
  assert.deepEqual([...tela.questoes.map((item) => item._idBanco)], ["q2", "q1"]);
  assert.equal(chamadas.length, 2);
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

function ambienteImpressao(versoes, globais) {
  const { banco, prova, servicos } = ambiente();
  prova.status = "Enviada ao pedagógico";
  const qrs = [];
  const draftModulo = carregarOpcoes("stores/provaDraft.js", { pinia: { defineStore: (_, opcoes) => opcoes } });
  const dados = versoes || [{ id_prova_aluno: "versao-individual", matricula_aluno: 20260001, questoes: [banco[2], banco[0]] }];
  const opcoes = carregarOpcoes("views/ImprimirProvasView.vue", {
    qrcode: { toDataURL: async (id) => { qrs.push(id); return `qr:${id}`; } },
    "@/components/CartaoResposta.vue": {}, "@/components/PreviewProva.vue": {},
    "@/services/provas": { ...servicos, imprimirProvas: async (id) => {
      assert.equal(id, prova._id); return { provas_alunos: dados };
    } },
    "@/services/templates": { obterTemplateProva: async () => "template" }, "@/stores/provaDraft": draftModulo,
  }, globais).default;
  return { tela: instancia(opcoes, { id: prova._id }), prova, dados, qrs };
}

test("impressão usa a ordem individual e gera QR com id_prova_aluno", async () => {
  const { tela, qrs } = ambienteImpressao();
  await tela.carregar();
  assert.equal(tela.erro, "");
  assert.equal(tela.versoes[0].matricula_aluno, 20260001);
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

test("serviço de impressão chama a rota individualizada", async () => {
  const chamadas = [];
  const servicos = carregarOpcoes("services/provas.js", { "./api": { api: async (rota) => { chamadas.push(rota); return {}; } } });
  await servicos.imprimirProvas("base-1");
  assert.deepEqual(chamadas, ["/provas/imprimir-provas/base-1"]);
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
  assert.equal(tela.imprimindo, false);
  falhar = true;
  await tela.imprimir();
  assert.match(tela.erro, /imagem não carregou/);
  assert.equal(impressoes, 1);
});
