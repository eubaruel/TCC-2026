const { test } = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const { transformSync } = require("@babel/core");
const { defineStore, createPinia } = require("pinia");

function ambiente({ salvo = null, bloqueado = false, falharLogin = false, role = "Professor" } = {}) {
  const valores = new Map(salvo === null ? [] : [["tcc.usuario", salvo]]);
  const usuario = { registro: 1, nome: "Usuário Teste", email: "teste@escola.com", role, deve_alterar_senha: false };
  let chamadas = 0;
  const storage = {};
  for (const [metodo, acao] of Object.entries({
    getItem: (chave) => valores.get(chave) ?? null,
    setItem: (chave, valor) => valores.set(chave, valor),
    removeItem: (chave) => valores.delete(chave),
  })) storage[metodo] = (...args) => {
    if (bloqueado) throw new Error("Armazenamento bloqueado");
    return acao(...args);
  };
  const fonte = fs.readFileSync(path.join(__dirname, "../src/stores/auth.js"), "utf8");
  const codigo = transformSync(fonte, { babelrc: false, configFile: false, plugins: ["@babel/plugin-transform-modules-commonjs"] }).code;
  const contexto = { exports: {}, sessionStorage: storage, require: (nome) => {
    if (nome === "pinia") return { defineStore };
    assert.equal(nome, "@/services/usuarios");
    return { autenticarUsuario: async (registro, senha) => {
      chamadas++; assert.equal(registro, 1); assert.equal(senha, "senha-de-teste");
      if (falharLogin) throw new Error("Usuário ou senha inválidos");
      // Uma senha ou outro campo extra, mesmo vindo por engano da API, não deve ser persistido.
      return { usuario: { ...usuario, senha: "nunca-salvar", campo_extra: "ignorar" } };
    } };
  } };
  vm.runInNewContext(codigo, contexto);
  const criarStore = () => contexto.exports.useAuthStore(createPinia());
  return { store: criarStore(), criarStore, valores, usuario, chamadas: () => chamadas };
}

test("login persiste somente os dados necessários, sem senha, para ambos os perfis", async () => {
  for (const role of ["Professor", "Processo pedagógico"]) {
    const { store, valores, usuario } = ambiente({ role });
    assert.equal((await store.login(1, "senha-de-teste")).success, true);
    assert.deepEqual(JSON.parse(valores.get("tcc.usuario")), usuario);
    assert.equal(store.user.senha, undefined); assert.equal(store.user.campo_extra, undefined);
    assert.equal(store.loading, false);
  }
});

test("nova instância restaura login e perfil sem nova chamada à API", async () => {
  for (const role of ["Professor", "Processo pedagógico"]) {
    const { store, criarStore, chamadas } = ambiente({ role });
    await store.login(1, "senha-de-teste");
    const restaurada = criarStore();
    assert.equal(restaurada.isLoggedIn, true); assert.equal(restaurada.user.registro, 1);
    assert.equal(restaurada.isProfessor, role === "Professor");
    assert.equal(restaurada.isProcessoPedagogico, role === "Processo pedagógico");
    assert.equal(restaurada.user.deve_alterar_senha, false); assert.equal(chamadas(), 1);
  }
});

test("sair remove dados da memória e do armazenamento, impedindo restauração", async () => {
  const { store, criarStore, valores } = ambiente();
  await store.login(1, "senha-de-teste"); store.logout();
  assert.equal(store.user, null); assert.equal(valores.has("tcc.usuario"), false);
  assert.equal(criarStore().isLoggedIn, false);
});

test("sem sessão ou com dados corrompidos/incompletos, usuário permanece deslogado", () => {
  for (const salvo of [null, "não é JSON", "null", "[]", "{}", JSON.stringify({ registro: 1, nome: "Teste", email: "teste@escola.com", role: "Outro perfil" })]) {
    const { store } = ambiente({ salvo });
    assert.equal(store.isLoggedIn, false); assert.equal(store.user, null);
  }
});

test("dados restaurados também excluem campos extras e senhas", () => {
  const salvo = JSON.stringify({ registro: 1, nome: "Teste", email: "teste@escola.com", role: "Professor", senha: "não usar" });
  const { store } = ambiente({ salvo });
  assert.equal(store.isLoggedIn, true); assert.equal(store.user.senha, undefined);
});

test("armazenamento bloqueado não quebra login ou saída", async () => {
  const { store } = ambiente({ bloqueado: true });
  assert.equal(store.isLoggedIn, false);
  assert.equal((await store.login(1, "senha-de-teste")).success, true);
  assert.equal(store.isLoggedIn, true); store.logout(); assert.equal(store.isLoggedIn, false);
});

test("falha na autenticação não cria uma sessão persistida", async () => {
  const { store, valores } = ambiente({ falharLogin: true });
  const resultado = await store.login(1, "senha-de-teste");
  assert.equal(resultado.success, false); assert.equal(store.isLoggedIn, false);
  assert.equal(valores.size, 0); assert.equal(store.loading, false);
});
