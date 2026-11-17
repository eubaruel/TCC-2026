const { test } = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const { transformSync } = require("@babel/core");

const fonte = fs.readFileSync(path.join(__dirname, "../src/utils/senha.js"), "utf8");
const codigo = transformSync(fonte, { babelrc: false, configFile: false, plugins: ["@babel/plugin-transform-modules-commonjs"] }).code;
const contexto = { exports: {} };
vm.runInNewContext(codigo, contexto);
const { regrasSenha } = contexto.exports;

test("nova senha segue as mesmas regras do backend", () => {
  assert.ok(regrasSenha("Nova123!", "Nova123!", "Antiga1!").every((regra) => regra.ok));
  const falhas = (senha, confirmacao = senha, atual = "Antiga1!") =>
    [...regrasSenha(senha, confirmacao, atual)].filter((regra) => !regra.ok).map((regra) => regra.texto);
  assert.deepEqual(falhas("Ab1!"), ["Ao menos 6 caracteres"]);
  assert.deepEqual(falhas("nova123!"), ["Uma letra maiúscula"]);
  assert.deepEqual(falhas("NovaSenha!"), ["Um número"]);
  assert.match(falhas("Nova1234")[0], /caractere especial/);
  assert.deepEqual(falhas("Antiga1!"), ["Diferente da senha atual"]);
  assert.deepEqual(falhas("Nova123!", "Nova123?"), ["Confirmação igual à nova senha"]);
});
