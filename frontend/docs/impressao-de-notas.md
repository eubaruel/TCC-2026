# Impressão de notas sobre as folhas com gabarito

## Uso

1. Corrigir as imagens na tela do processo pedagógico. A ordem das imagens
   selecionadas será a ordem das folhas; o tempo de processamento não a altera.
2. Abrir **Organizar folhas e imprimir notas do lote salvo**. Conferir a lista
   com posição, nome, matrícula, turma e nota. Separar somente as folhas com
   cartão-resposta, não as provas inteiras nem as listas da sala.
3. Fazer **Imprimir teste (1 folha)** em uma cópia descartável do gabarito.
   Essa ação usa a nota da primeira posição do lote. Não imprime outros dados.
4. Se necessário, ajustar horizontal/vertical em milímetros. Valores positivos
   movem direita/baixo, negativos esquerda/cima. Começar em zero; intervalo
   permitido −10 a 10 mm. Os ajustes da tela não alteram dados do lote.
5. Organizar a pilha na sequência mostrada, marcar a conferência e imprimir.
   Configurar A4, escala 100%, uma página por folha, somente frente, sem ordem
   inversa e sem cabeçalhos/rodapés do navegador. Conferir lado e borda de entrada
   de papel na impressora real antes de um lote grande.

O sistema não conhece a ordem de alimentação da impressora e não pode garantir
alinhamento físico antes do teste. Abrir/cancelar o diálogo não confirma que a
impressora imprimiu. Não há novo status de impressão de notas.

## Regras

- Notas e gabaritos agora são salvos em `provas_x_alunos.correcao`. Resultados
  anteriores a essa implementação não foram armazenados: é necessário reenviar
  suas imagens, sem recriar as provas ou regenerar gabaritos.
- Um resultado só retorna como sucesso após salvar a correção; cada tentativa
  tem seu próprio `id_correcao`. O status existente `Corrigida` continua sendo
  aplicado às bases que estavam impressas.
- `lotes_correcao` preserva uma cópia das notas e da identificação naquela
  sequência. Reabrir/reimprimir o endereço não usa notas de uma tentativa posterior.
- O frontend não escolhe a nota ao criar o lote: envia somente referências
  confirmadas, nomes dos arquivos e posições de falha. O backend verifica as
  tentativas e copia os valores salvos. Não são guardadas imagens no lote.
- Qualquer pendência bloqueia toda a impressão do lote. Falhas não viram zero
  nem são removidas da sequência. Resolver e enviar o conjunto completo novamente,
  na mesma ordem. Cartões duplicados e identificação incompleta são recusados.
- Se salvar o lote falhar, os resultados confirmados continuam visíveis e
  podem ser registrados novamente pelo botão de tentar salvar. Não há impressão
  liberada sem um lote confirmado. O ID do último lote fica no armazenamento local
  como atalho; o endereço também permite reabrir mesmo sem esse armazenamento.

## Arquivos e responsabilidades

| Arquivo | Responsabilidade e motivo |
|---|---|
| `backend/api/DAOs/prova_x_aluno_dao.py` | Salvar o resultado somente se a configuração individual ainda for a mesma; buscar referências em lote sem uma consulta por folha |
| `backend/api/DAOs/lote_correcao_dao.py` | Criar e consultar a coleção dos lotes, sem rotas de edição que mudem uma sequência já conferida |
| `backend/api/services/correcao_service.py` | Persistir correções antes do sucesso e montar a cópia ordenada com notas do banco; validar tentativas, duplicatas e dados incompletos |
| `backend/api/controles/prova_controle.py` | Validar o corpo do POST e manter o envelope padrão de resposta |
| `backend/api/roteador/prova_rotas.py` | Registrar POST `/lotes-correcao` e GET `/lotes-correcao/{id}` no fluxo existente |
| `backend/servidor.py` | Injetar o DAO de lotes no service, reutilizando a conexão existente |
| `frontend/src/services/correcao.js` | Chamar as novas rotas pelo cliente HTTP existente |
| `frontend/src/views/CorrigirProvasView.vue` | Salvar a sequência ao terminar as correções, mostrar falhas sem perder resultados e oferecer acesso ao lote |
| `frontend/src/router/index.js` | Restringir `/provas/notas/{id}` ao processo pedagógico autenticado |
| `frontend/src/views/ImprimirNotasView.vue` | Conferência da pilha, bloqueios, teste, ajustes e folhas A4 apenas com notas |
| `frontend/src/components/NotaSobreposta.vue` | Desenhar exclusivamente o número centralizado, sem imagens, QR, rótulos ou fundos |
| `frontend/src/utils/cartaoResposta.js` | Compartilhar o campo da nota e as dimensões da página original |
| `frontend/src/utils/impressaoNotas.js` | Formatar notas, calcular posição e conservar entradas na ordem original |

## Verificação

- Testes backend: persistência, configuração alterada, erro de gravação,
  lotes ordenados, tentativa substituída, campos inválidos, duplicatas,
  notas inválidas, pendências e rotas de criação/consulta.
- Testes frontend: ordenação original, posições de falha, zero válido,
  formato decimal, conteúdo somente numérico, confirmação da pilha, um teste
  versus lote completo, limites dos ajustes, salvamento/retentativa e acesso restrito.
- No frontend real, cartões sintéticos foram enviados na ordem Carla, Ana e
  Bruno: notas 3,33; 10,00; 6,67. O lote persistiu nessa ordem e reabriu por GET.
  Outro lote com Ana e um cartão sem QR preservou a segunda posição como pendente
  e manteve impressão/teste desabilitados. Nenhuma impressão física foi realizada.
- O padrão atual é A4 com 16 mm nas laterais, 13 mm no topo e 12 mm na base.
  O cartão ocupa 178 mm de largura, sem deformação, e as questões usam as mesmas
  margens laterais. `PreviewProva.vue` compartilha a folha entre a seleção do
  professor, a visualização individual e a impressão; em telas menores, a folha
  e suas margens reduzem proporcionalmente. As listas de turma mantêm seu modelo.
- A nota acompanha essas medidas pelo centro do campo: aproximadamente
  X=24,27 mm e Y=29,98 mm. Folhas do modelo anterior exigem novo teste e calibração.
  Capturas de tela redimensionadas não servem como medida da impressão física.
