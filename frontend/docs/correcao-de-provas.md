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

`services/correcao.js` prepara uma imagem por vez e envia `FormData` no campo `imagens` para `POST /provas/corrigir-provas`. Envia também `ids_provas_alunos`, uma lista JSON na mesma ordem das imagens, com os IDs lidos no QR pelo frontend ou `null` quando não identificados. O ID é preservado mesmo quando não é possível recortar com segurança. Não define `Content-Type` manualmente; reutiliza `services/api.js`.

Um conjunto de 400 imagens pequenas vira oito requisições de até 50 arquivos. O limite adicional de 40 MiB por lote deixa margem dentro dos 50 MiB do servidor. Cada imagem deve ter até 5 MiB após o recorte; arquivos vazios, não-imagens e arquivos maiores são recusados individualmente, sem impedir os demais.

As requisições são sequenciais e assíncronas; dentro de cada requisição o backend já consulta o microserviço concorrentemente. Isso evita manter centenas de imagens decodificadas ou centenas de chamadas simultâneas em memória. A tela informa preparação, processamento e quantidade de recortes; bloqueia novo clique e navegação interna enquanto trabalha.

Resultados e erros mantêm o índice e o nome do arquivo original, inclusive entre lotes e nomes repetidos. Falhas de conexão de um lote aparecem para seus arquivos; os próximos lotes continuam. Respostas incompletas ou com índices inválidos são tratadas como erro, não como notas confirmadas.

## Resultado e limites do MVP

Exibe matrícula, nome, nota calculada, respostas do aluno e gabarito correto. Questões em branco aparecem como **Em branco**.

Ao finalizar, as falhas ficam na seção **Provas não corrigidas**, destacada antes dos resultados. Ela mostra o total de provas, o **nome, matrícula e turma do aluno**, a posição no conjunto enviado (a partir de 1) e o indicador **Não corrigida**, sem expor os motivos técnicos. A lista mantém a ordem do envio e tem rolagem para conjuntos extensos. O destaque também se adapta ao tema escuro e às telas pequenas.

Quando não há matrícula identificada, mostra também o **nome do arquivo e a miniatura da página original**, antes do recorte. Para PNG/JPEG, a miniatura abre a imagem original em outra aba para o funcionário ler o cabeçalho. Arquivos inválidos/não visualizáveis ou de outros formatos mantêm nome e posição com o aviso **Prévia indisponível para este arquivo**; SVG não é aberto como documento ativo. A associação usa o índice original, inclusive com nomes repetidos. As imagens ficam locais, com URLs temporárias e carregamento sob demanda; as referências são liberadas ao selecionar outro conjunto, corrigir novamente ou sair da tela. Não há novos uploads, mudanças no leitor ou alterações no banco para exibir essas prévias.

Essa lista representa provas **sem correção confirmada**, inclusive em falhas de comunicação, e não um histórico no banco. A API usa o QR lido pelo microserviço ou, se não disponível, o ID lido pelo frontend para consultar `provas_x_alunos` e o cadastro do aluno. O QR do microserviço prevalece em caso de diferença. O ID auxiliar serve somente para identificação da pendência: não substitui a leitura das respostas, não libera uma correção e não produz nota.

Sem QR válido/cadastro correspondente, aparece **Aluno não identificado**, com matrícula/turma não identificadas. Se só a matrícula estiver disponível na versão individual, ela é exibida sem inventar nome ou turma. Não se deduz identidade pelo nome do arquivo. Se o lote não alcançar a API ou a imagem for recusada localmente, pode não ser possível recuperar esses dados. Os motivos continuam internamente no retorno, sem exibição. Se não houver falhas, a tela informa que não há pendências. Selecionar outro conjunto limpa os resultados anteriores; não há reenvio automático nem nova rota.

A identificação foi conferida com o mesmo lote real: a falha do PNG de Bruno passou a exibir matrícula `20260002`, nome `Bruno Demonstracao` e turma `Turma MVP 2026 A`, usando o QR já lido no frontend. O cartão sem QR e o arquivo corrompido permaneceram explicitamente sem aluno identificado. A API principal foi reiniciada para carregar o novo contrato; o microserviço não foi modificado.

A API **persiste as notas e ambos os gabaritos na versão individual** e, após uma correção bem-sucedida, altera
a prova-base de `Impressa` para o status existente `Corrigida`, utilizando o
`id_prova` da versão individual. Outros status não mudam. A interface comunica
que os resultados confirmados foram salvos e que a transição pode ocorrer mesmo com cartões
pendentes: não é uma confirmação de correção de todos os alunos. Se todas as
imagens falharem, a base permanece impressa. Ao retornar à listagem, a prova
aparece em **Provas Corrigidas**. O microserviço não foi alterado.

## Organização e impressão das notas

Ao concluir a correção, a tela salva a ordem do conjunto completo em
`POST /provas/lotes-correcao`. Envia somente referências aos resultados
confirmados (`id_prova_aluno` e `id_correcao`), nomes dos arquivos e posições de
falha. O backend copia as notas e a identificação salvas, sem confiar em notas
enviadas pelo navegador. `id_correcao` identifica a tentativa: se foi substituída,
o lote é recusado em vez de imprimir uma nota de outra tentativa.

O botão **Organizar folhas e imprimir notas do lote salvo** abre
`/provas/notas/{id}`, restrito ao processo pedagógico. Mostra a sequência exata
das imagens originais, com nome, matrícula, turma e nota, sem ordenação alfabética.
Lotes com pendências não podem ser impressos; as posições com falha não são
eliminadas nem recebem nota zero. Resolva os problemas e envie o conjunto completo
novamente, na mesma ordem. Cartões duplicados também são recusados.

A página consulta o lote salvo por GET e pode ser recarregada ou reaberta pelo
seu endereço. O último ID é guardado no navegador para disponibilizar o atalho na
correção; só o identificador fica no armazenamento local. Se o navegador bloquear
esse armazenamento, o link atual e a consulta pelo endereço continuam funcionando.
Se a criação do lote falhar, as notas confirmadas continuam visíveis, mas a
impressão fica bloqueada e há um botão de tentar salvar a sequência novamente.

Somente as folhas que contêm o gabarito devem voltar à impressora. Confirme a
ordem física no checkbox antes de imprimir o lote. O teste usa a nota da primeira
posição e imprime apenas uma folha; use uma cópia descartável para alinhar.
Os ajustes horizontal/vertical aceitam −10 a 10 mm (positivos direita/baixo).
Deixe zero no primeiro teste. Os ajustes são da tela atual, não alteram notas.

O componente `NotaSobreposta.vue` imprime exclusivamente o número, em preto,
Arial 12 pt, peso normal (400), com duas casas decimais. A posição deriva do centro do campo NOTA no
cartão vetorial, em `utils/cartaoResposta.js`, e das margens de 16 mm nas laterais
e 13 mm no topo. O cartão mantém a proporção e ocupa 178 mm de largura na folha A4.
O centro inicial da nota é aproximadamente X=24,27 mm e Y=29,98 mm.
Para folhas já impressas com o modelo anterior, refaça o teste de alinhamento:
a mudança não reposiciona o gabarito que já está no papel.
`ImprimirNotasView.vue` oculta os controles e a tabela na impressão, gera uma
página por nota e não acrescenta página final. Não desenha fundos, bordas, QR,
cartão ou identificação sobre a prova. Não cria PDFs nem instala dependências.

Configuração física: A4, escala 100%, uma página por folha, somente frente,
cabeçalhos/rodapés e ordem inversa desativados. Conferir o lado/borda de alimentação
e testar a impressora real antes de um lote grande. O sistema não conhece a
ordem física do alimentador nem garante alinhamento sem esse teste.
Reimprimir usa o retrato do lote, não a última nota recalculada. Abrir/cancelar
o diálogo não confirma que houve impressão física.

## Verificação

Em 17/10/2026, o fluxo integrado foi executado no frontend com API, MongoDB e leitor reais: criação de uma base para o Professor Teste, seleção/envio de três questões e obtenção das versões de três alunos. As páginas exibidas para impressão e seus SVGs reais foram usados para gerar imagens sintéticas de 2480 × 3508, com preenchimentos conhecidos. Não houve impressão física.

O lote final (dois PNGs válidos, um JPEG válido, um cartão sem QR e um arquivo de imagem corrompido) resultou nas notas esperadas **10**, **6,67** e **3,33**. As duas falhas propositais ficaram na seção de não corrigidas, sem motivos expostos. Os três cartões válidos foram recortados pelo frontend. O conjunto de testes automatizados do frontend passou a ter **71 testes aprovados**, além de lint e build concluídos.

Limitação observada: a versão PNG do cartão de Bruno falhou duas vezes no fluxo automático, embora o leitor conseguisse extrair suas respostas em um recorte de diagnóstico. A mesma página em JPEG funcionou pelo frontend. Isso evidencia sensibilidade do pipeline à rasterização/recorte; a causa exata não foi isolada e não foi alterado o leitor nem o algoritmo de recorte nesta entrega. As notas continuam sem persistência, e a base/versões de teste permanecem no banco.

`npm test` cobre geometria/margens, preservação em caso de dúvida, lotes de 400 arquivos, limites de tamanho, falhas individuais/de lote, associação dos índices e bloqueio de clique duplicado. A validação visual e com o leitor usa digitalizações sintéticas do modelo; uma rodada com imagens do scanner real ainda é necessária antes de uso em produção.

Na verificação em navegador, páginas sintéticas de 2480 × 3508 pixels tiveram aproximadamente 80% da área removida. Sete imagens (PNG/JPEG, três/dez questões e rotações de 5°, 90° e 180°) mantiveram o QR e as respostas esperadas das questões existentes após passar pelo leitor. Uma imagem de baixa resolução (774 × 1095) foi recortada sem perder o cartão, mas o leitor não reconheceu seu QR; não trate esse resultado como uma correção válida. No teste JPEG de três questões, o leitor indicou marcas adicionais nas colunas não utilizadas: a API existente considera somente as três questões registradas. O microserviço não foi alterado para corrigir essas limitações.

O teste de interface interceptou o multipart com API simulada e confirmou que o arquivo recortado foi enviado, enquanto imagens sem cartão reconhecido ou inválidas permaneceram intactas. Não inseriu notas ou registros no banco. Os 400 arquivos foram testados com recorte/API simulados para verificar a divisão do lote, não como benchmark de 400 correções reais.
