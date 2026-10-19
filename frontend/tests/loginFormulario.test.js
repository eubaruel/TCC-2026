const { test } = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const { parse } = require("@vue/compiler-sfc");
const { transformSync } = require("@babel/core");

const fonte = fs.readFileSync(path.join(__dirname, "../src/components/LoginFormulario.vue"), "utf8");
const { descriptor } = parse(fonte);
const codigo = transformSync(descriptor.script.content, {
  babelrc: false, configFile: false, plugins: ["@babel/plugin-transform-modules-commonjs"],
}).code;

function formulario() {
  let concluir;
  let chamadas = 0;
  const navegacoes = [];
  const authStore = {
    loading: false,
    async login() {
      chamadas++;
      this.loading = true;
      try { return await new Promise((resolve) => { concluir = resolve; }); }
      finally { this.loading = false; }
    },
  };
  const contexto = { exports: {}, require: (nome) => {
    if (nome === "@/stores/auth") return { useAuthStore: () => authStore };
    assert.equal(nome, "vue-router");
    return { useRouter: () => ({ push: (rota) => navegacoes.push(rota) }) };
  } };
  vm.runInNewContext(codigo, contexto);
  const componente = contexto.exports.default;
  const instancia = { ...componente.data(), ...componente.setup(), registro_usuario: "1", senha_usuario: "teste" };
  return { instancia, enviar: () => componente.methods.processarLogin.call(instancia),
    concluir: (resultado) => concluir(resultado), chamadas: () => chamadas, navegacoes };
}

test("envios repetidos durante o login geram uma única requisição", async () => {
  const login = formulario();
  const pendente = login.enviar();
  assert.equal(login.instancia.authStore.loading, true);
  await login.enviar();
  await login.enviar();
  assert.equal(login.chamadas(), 1);
  login.concluir({ success: true });
  await pendente;
  assert.deepEqual(login.navegacoes, ["/provas"]);
  assert.equal(login.instancia.authStore.loading, false);
});

test("falha libera nova tentativa e mantém a mensagem de erro", async () => {
  const login = formulario();
  const pendente = login.enviar();
  login.concluir({ success: false, message: "Senha inválida" });
  await pendente;
  assert.equal(login.instancia.erroRegistro, "Senha inválida");
  assert.equal(login.instancia.authStore.loading, false);
  assert.deepEqual(login.navegacoes, []);
  const tentativa = login.enviar();
  assert.equal(login.chamadas(), 2);
  login.concluir({ success: true });
  await tentativa;
});
