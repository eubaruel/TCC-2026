// Template local usado enquanto a rota de templates não existir no backend.
// Marcadores substituídos pelo PreviewProva.vue:
//   {{DISCIPLINA}} {{CODIGO_DISCIPLINA}} {{TURMAS}} {{SERIE}} {{BIMESTRE}}
//   {{DATA_APLICACAO}} {{PROFESSOR}} {{TIPO}} {{QUESTOES}}
// O template vindo do banco deve seguir os mesmos marcadores.
export default `
<header class="prova-cabecalho">
  <h1>{{DISCIPLINA}}</h1>
  <table class="prova-dados">
    <tbody>
      <tr>
        <td><strong>Professor(a):</strong> {{PROFESSOR}}</td>
        <td><strong>Data:</strong> {{DATA_APLICACAO}}</td>
      </tr>
      <tr>
        <td><strong>Turma(s):</strong> {{TURMAS}}</td>
        <td><strong>Série:</strong> {{SERIE}} · <strong>Bimestre:</strong> {{BIMESTRE}}</td>
      </tr>
      <tr>
        <td colspan="2"><strong>Aluno(a):</strong> ____________________________________________ <strong>Nº:</strong> ______</td>
      </tr>
    </tbody>
  </table>
  <p class="prova-tipo">Avaliação {{TIPO}}</p>
</header>
<hr />
<section class="prova-questoes">
  {{QUESTOES}}
</section>
`;
