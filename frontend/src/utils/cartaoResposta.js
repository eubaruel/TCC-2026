// Geometria compartilhada pela impressão e pelo recorte; mantém as dez colunas do leitor.
export const CARTAO_RESPOSTA = {
  largura: 1200,
  altura: 286,
  nota: { x: 0, y: 86, largura: 111.5, altura: 57 },
  qr: { x: 9, y: 168, tamanho: 94, margem: 4 },
};

// Medidas em milímetros, compartilhadas pela prévia, impressão da prova e da nota.
export const PAGINA_PROVA = { largura: 210, altura: 297, margemLateral: 6.3, margemSuperior: 6.27, margemInferior: 5.7 };
