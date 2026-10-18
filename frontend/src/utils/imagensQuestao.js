export const LIMITE_IMAGENS = 3;
// O CSS usa 45 mm; os atributos e as alças do Quill trabalham com pixels.
export const ALTURA_MAXIMA_IMAGEM_PX = Math.floor(45 * 96 / 25.4);

// Aceita um arquivo ou o src de uma imagem colada. Não amplia imagens pequenas.
export const prepararImagem = (origem) => new Promise((resolve, reject) => {
  const carregar = (src) => {
    const imagem = new Image();
    imagem.crossOrigin = "anonymous";
    imagem.onerror = () => reject(new Error("Não foi possível ler a imagem. Use um arquivo PNG, JPEG, GIF ou WebP."));
    imagem.onload = () => {
      try {
        const escala = Math.min(1, 800 / imagem.width, 600 / imagem.height);
        const canvas = document.createElement("canvas");
        canvas.width = Math.max(1, Math.round(imagem.width * escala));
        canvas.height = Math.max(1, Math.round(imagem.height * escala));
        const contexto = canvas.getContext("2d");
        contexto.fillStyle = "#ffffff";
        contexto.fillRect(0, 0, canvas.width, canvas.height);
        contexto.drawImage(imagem, 0, 0, canvas.width, canvas.height);
        const exibicao = Math.min(1, ALTURA_MAXIMA_IMAGEM_PX / canvas.height);
        resolve({
          dataUrl: canvas.toDataURL("image/jpeg", 0.75),
          largura: Math.max(1, Math.floor(canvas.width * exibicao)),
          altura: Math.max(1, Math.floor(canvas.height * exibicao)),
        });
      } catch (_) {
        reject(new Error("Não foi possível reduzir a imagem. Baixe o arquivo e use o botão de imagem do editor."));
      }
    };
    imagem.src = src;
  };
  if (typeof origem === "string") carregar(origem);
  else {
    const leitor = new FileReader();
    leitor.onerror = () => reject(new Error("Não foi possível ler o arquivo de imagem."));
    leitor.onload = () => carregar(leitor.result);
    leitor.readAsDataURL(origem);
  }
});
