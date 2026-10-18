const { test } = require("node:test");
const assert = require("node:assert/strict");
const { contarCaracteres, contarImagens } = require("./helpers/html");

test("contagem inclui espaços e pontuação sem agrupar ou aparar e decodifica entidades", () => {
  for (const [html, texto] of [
    ["  a  \n b! ", "  a  \n b! "],
    ["<p> A&nbsp; &amp; 😀! </p>", " A\u00a0 & 😀! "],
    ["<p>um</p><p>dois<br> três</p>", "umdois três"],
    ["<strong>ação</strong>&#33;&#x1F600;", "ação!😀"],
  ]) assert.equal(contarCaracteres(html), Array.from(texto).length);
});

test("contagem de imagens considera tags img, não src repetido nem texto base64", () => {
  const img = '<img src="data:image/jpeg;base64,teste">';
  assert.equal(contarImagens(`<p>${img.repeat(3)}</p>`), 3);
  assert.equal(contarImagens("texto img src=data:image/jpeg;base64,teste <!-- <img> -->"), 0);
});

test("contagem ignora marcação, comentários, atributos e base64 das imagens", () => {
  const imagem = `<img src="data:image/png;base64,${"a".repeat(100000)}" alt="Texto alternativo" width="425">`;
  assert.equal(contarCaracteres(`<p><strong>Olá!</strong>${imagem}</p><!-- comentário -->`), 4);
  assert.equal(contarCaracteres(imagem), 0);
  assert.equal(contarCaracteres("<p><br></p>"), 0);
  assert.equal(contarCaracteres("<script>ignorar</script><style>ignorar</style><p>A</p>"), 1);
});
