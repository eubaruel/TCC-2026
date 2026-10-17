import templateLocal from "@/assets/templates/templateProva";
// import { api } from "./api";

export async function obterTemplateProva() {
  // TODO: quando a rota de template existir no backend, substitua o retorno abaixo pela chamada à API.
  // O template deve ser um HTML com os mesmos marcadores de src/assets/templates/templateProva.js.
  // Exemplo (ajuste o caminho e o nome do campo conforme a rota criada):
  //
  //   try {
  //     const data = await api("/templates/prova");
  //     if (data?.template) return data.template;
  //   } catch (_) {
  //     // Em caso de falha, segue com o template local.
  //   }
  return templateLocal;
}
