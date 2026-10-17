import jsQR from "jsqr";
import { CARTAO_RESPOSTA as modelo } from "./cartaoResposta";

function canvas(largura, altura) {
  const elemento = document.createElement("canvas");
  elemento.width = Math.ceil(largura); elemento.height = Math.ceil(altura);
  return elemento;
}

// Exige o QR do modelo E as duas bordas longas. O QR sozinho não autoriza um corte.
export function localizarFaixa(imagem, codigo) {
  if (!codigo || !/^[a-f\d]{24}$/i.test(codigo.data)) return null;
  const { topLeftCorner: inicio, topRightCorner: direita, bottomLeftCorner: baixo } = codigo.location;
  const distancia = (a, b) => Math.hypot(a.x - b.x, a.y - b.y);
  const lado = distancia(inicio, direita);
  if (Math.abs(distancia(inicio, baixo) / lado - 1) > .12 || Math.abs(direita.y - inicio.y) > lado * .05) return null;
  const modulos = 17 + 4 * codigo.version;
  const escala = lado / (modelo.qr.tamanho * modulos / (modulos + 2 * modelo.qr.margem));
  const margemQr = modelo.qr.tamanho * modelo.qr.margem / (modulos + 2 * modelo.qr.margem);
  const esquerda = inicio.x - (modelo.qr.x + margemQr) * escala;
  const topo = inicio.y - (modelo.qr.y + margemQr) * escala;
  const largura = modelo.largura * escala, altura = modelo.altura * escala;
  if (!Number.isFinite(escala) || escala <= 0 || esquerda < -largura * .03 || esquerda + largura > imagem.width + largura * .03 || topo < -2 || topo + altura > imagem.height + 2) return null;

  const x1 = Math.max(0, Math.ceil(esquerda + largura * .02));
  const x2 = Math.min(imagem.width, Math.floor(esquerda + largura * .98));
  const borda = (prevista) => {
    let melhor = null, coberturaMaior = .8;
    const tolerancia = Math.max(3, altura * .06);
    for (let y = Math.max(0, Math.floor(prevista - tolerancia)); y <= Math.min(imagem.height - 1, Math.ceil(prevista + tolerancia)); y++) {
      let escuros = 0;
      for (let x = x1; x < x2; x++) {
        const i = (y * imagem.width + x) * 4;
        if ((imagem.data[i] + imagem.data[i + 1] + imagem.data[i + 2]) / 3 < 190) escuros++;
      }
      const cobertura = escuros / (x2 - x1);
      if (cobertura > coberturaMaior || (cobertura === coberturaMaior && melhor !== null && Math.abs(y - prevista) < Math.abs(melhor - prevista))) {
        coberturaMaior = cobertura; melhor = y;
      }
    }
    return melhor;
  };
  const superior = borda(topo), inferior = borda(topo + altura);
  if (superior === null || inferior === null || Math.abs((inferior - superior) / altura - 1) > .1) return null;
  // Preserva a largura inteira e 15% da altura do cartão em cada extremidade.
  const y = Math.max(0, Math.floor(superior - altura * .15));
  const fim = Math.min(imagem.height, Math.ceil(inferior + altura * .15));
  if (fim - y > imagem.height * .8) return null; // Já recortada: não reprocessa.
  return { y, altura: fim - y };
}

export async function recortarCartao(arquivo) {
  let bitmap, analise, alinhada, saida, id_prova_aluno = null;
  try {
    bitmap = await createImageBitmap(arquivo);
    const escala = Math.min(1, 1600 / Math.max(bitmap.width, bitmap.height));
    analise = canvas(bitmap.width * escala, bitmap.height * escala);
    analise.getContext("2d").drawImage(bitmap, 0, 0, analise.width, analise.height);
    let pixels = analise.getContext("2d").getImageData(0, 0, analise.width, analise.height);
    const codigo = jsQR(pixels.data, pixels.width, pixels.height, { inversionAttempts: "dontInvert" });
    if (!codigo || !/^[a-f\d]{24}$/i.test(codigo.data)) return { arquivo, recortada: false };
    id_prova_aluno = codigo.data;

    const { topLeftCorner: origem, topRightCorner: direita } = codigo.location;
    const angulo = Math.atan2(direita.y - origem.y, direita.x - origem.x);
    const cos = Math.cos(angulo), sin = Math.sin(angulo);
    alinhada = canvas(Math.abs(analise.width * cos) + Math.abs(analise.height * sin), Math.abs(analise.width * sin) + Math.abs(analise.height * cos));
    const contexto = alinhada.getContext("2d");
    contexto.fillStyle = "white"; contexto.fillRect(0, 0, alinhada.width, alinhada.height);
    contexto.translate(alinhada.width / 2, alinhada.height / 2); contexto.rotate(-angulo);
    contexto.drawImage(analise, -analise.width / 2, -analise.height / 2);
    const transformar = (ponto) => {
      const x = ponto.x - analise.width / 2, y = ponto.y - analise.height / 2;
      return { x: x * cos + y * sin + alinhada.width / 2, y: -x * sin + y * cos + alinhada.height / 2 };
    };
    const localizacao = Object.fromEntries(Object.entries(codigo.location).map(([nome, ponto]) => [nome, transformar(ponto)]));
    pixels = contexto.getImageData(0, 0, alinhada.width, alinhada.height);
    const faixa = localizarFaixa(pixels, { ...codigo, location: localizacao });
    if (!faixa) return { arquivo, recortada: false, id_prova_aluno };

    // Desenha a partir do original, sem reduzir a resolução das marcações ou do QR.
    saida = canvas(alinhada.width / escala, faixa.altura / escala);
    const destino = saida.getContext("2d");
    destino.fillStyle = "white"; destino.fillRect(0, 0, saida.width, saida.height);
    destino.translate(alinhada.width / (2 * escala), (alinhada.height / 2 - faixa.y) / escala);
    destino.rotate(-angulo); destino.drawImage(bitmap, -bitmap.width / 2, -bitmap.height / 2);
    const blob = await new Promise((resolve) => saida.toBlob(resolve, "image/png"));
    if (!blob || blob.size > 5 * 1024 * 1024) return { arquivo, recortada: false, id_prova_aluno };
    const nome = `${arquivo.name.replace(/\.[^.]+$/, "")}.png`;
    return { arquivo: new File([blob], nome, { type: "image/png", lastModified: arquivo.lastModified }), recortada: true, id_prova_aluno };
  } catch (_) {
    // Falha de leitura/detecção nunca resulta em um recorte presumido.
    return { arquivo, recortada: false, id_prova_aluno };
  } finally {
    bitmap?.close();
    // Libera os buffers imediatamente, inclusive nos caminhos de preservação do original.
    for (const elemento of [analise, alinhada, saida]) {
      if (elemento) { elemento.width = 0; elemento.height = 0; }
    }
  }
}
