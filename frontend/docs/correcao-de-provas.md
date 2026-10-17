# Correção e recorte automático no frontend

Na tela de provas, **Corrigir cartões** aparece somente para o **Processo pedagógico** e abre `/provas/corrigir`. A navegação exige autenticação e esse perfil; professores são redirecionados para `/provas` caso tentem acessar a URL diretamente. Essa restrição é do frontend e não substitui autorização na API. Selecione as imagens digitalizadas e clique em **Corrigir imagens**. Não há ajuste nem confirmação individual do recorte.

## Recorte conservador

- Cada imagem deve conter uma única página/cartão, do modelo impresso pelo sistema. PNG/JPEG são recomendados; PDF não é aceito neste fluxo.
- O navegador lê o QR com `jsqr`. O conteúdo deve corresponder ao formato de `id_prova_aluno` (24 caracteres hexadecimais).
- A posição e o tamanho do QR permitem estimar a posição do cartão. A geometria está em `utils/cartaoResposta.js`, compartilhada com a impressão.
- A análise usa uma cópia de até 1600 pixels no maior lado. Corrige a orientação estimada pelo QR e exige bordas superior e inferior com pelo menos 80% de cobertura escura e dimensões compatíveis com o modelo.
- Só depois dessas verificações remove o excedente vertical, mantendo a largura inteira da imagem alinhada e uma margem de 15% da altura do cartão acima e abaixo. A grade de dez questões nunca é reduzida à quantidade de questões da prova.
- A saída é PNG, sem compressão com perda, desenhada a partir da resolução original. O arquivo original não é alterado.
- QR ausente/ilegível, bordas não reconhecidas, geometria incompatível, falha de leitura ou PNG maior que 5 MiB: envia o original, sem inventar um corte. Imagens já recortadas também são preservadas quando não há redução considerável.

Não há garantia de leitura de toda digitalização. Perspectiva intensa, cartão cortado pelo scanner, baixa resolução, múltiplos cartões na mesma imagem e modelos diferentes não são cobertos. A alternativa segura é preservar o original e exibir o erro devolvido pela API, caso ela também não consiga ler.

## Envio em lotes

`services/correcao.js` prepara uma imagem por vez e envia `FormData` no campo `imagens` para `POST /provas/corrigir-provas`. Não define `Content-Type` manualmente; reutiliza `services/api.js`.

Um conjunto de 400 imagens pequenas vira oito requisições de até 50 arquivos. O limite adicional de 40 MiB por lote deixa margem dentro dos 50 MiB do servidor. Cada imagem deve ter até 5 MiB após o recorte; arquivos vazios, não-imagens e arquivos maiores são recusados individualmente, sem impedir os demais.

As requisições são sequenciais e assíncronas; dentro de cada requisição o backend já consulta o microserviço concorrentemente. Isso evita manter centenas de imagens decodificadas ou centenas de chamadas simultâneas em memória. A tela informa preparação, processamento e quantidade de recortes; bloqueia novo clique e navegação interna enquanto trabalha.

Resultados e erros mantêm o índice e o nome do arquivo original, inclusive entre lotes e nomes repetidos. Falhas de conexão de um lote aparecem para seus arquivos; os próximos lotes continuam. Respostas incompletas ou com índices inválidos são tratadas como erro, não como notas confirmadas.

## Resultado e limites do MVP

Exibe matrícula, nome, nota calculada, respostas do aluno e gabarito correto. Questões em branco aparecem como **Em branco**. Erros de QR, imagem, fila/microserviço e envio são exibidos por arquivo conforme a resposta da API.

A API atual **não persiste essas notas nem altera o status da prova**. A interface comunica isso explicitamente. Não há alterações no backend ou no microserviço nesta implementação.

## Verificação

`npm test` cobre geometria/margens, preservação em caso de dúvida, lotes de 400 arquivos, limites de tamanho, falhas individuais/de lote, associação dos índices e bloqueio de clique duplicado. A validação visual e com o leitor usa digitalizações sintéticas do modelo; uma rodada com imagens do scanner real ainda é necessária antes de uso em produção.

Na verificação em navegador, páginas sintéticas de 2480 × 3508 pixels tiveram aproximadamente 80% da área removida. Sete imagens (PNG/JPEG, três/dez questões e rotações de 5°, 90° e 180°) mantiveram o QR e as respostas esperadas das questões existentes após passar pelo leitor. Uma imagem de baixa resolução (774 × 1095) foi recortada sem perder o cartão, mas o leitor não reconheceu seu QR; não trate esse resultado como uma correção válida. No teste JPEG de três questões, o leitor indicou marcas adicionais nas colunas não utilizadas: a API existente considera somente as três questões registradas. O microserviço não foi alterado para corrigir essas limitações.

O teste de interface interceptou o multipart com API simulada e confirmou que o arquivo recortado foi enviado, enquanto imagens sem cartão reconhecido ou inválidas permaneceram intactas. Não inseriu notas ou registros no banco. Os 400 arquivos foram testados com recorte/API simulados para verificar a divisão do lote, não como benchmark de 400 correções reais.
