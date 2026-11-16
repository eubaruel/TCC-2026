# Editor de texto das questões

O formulário de `QuestoesView.vue` reutiliza `EditorQuill.vue` para o enunciado
e para cada uma das cinco alternativas. A dependência Quill 2.0.3 já estava
instalada; a integração inicial não precisou de outro componente de edição.

## Fluxo

- Cada campo tem sua própria instância e sincroniza o HTML pelo `v-model`, usando
  `getSemanticHTML()` para exportar o conteúdo sem os elementos internos do editor.
- A alternativa A continua sendo a correta; B a E são as demais alternativas.
  Na edição, a resposta correta existente é carregada primeiro, sem alterar o
  registro no banco antes de salvar.
- Conteúdo recebido e emitido pelo editor passa pela sanitização existente.
  O envio também sanitiza enunciado e alternativas, preservando o contrato da API:
  strings HTML em `enunciado` e `alternativas`, e o primeiro texto como
  `alternativa_correta`.
- O formulário verifica conteúdo vazio com `htmlVazio`, inclusive quando o
  Quill produz `<p><br></p>`. Uma imagem válida também é conteúdo preenchido.
- Trocar ou limpar o conteúdo limpa o histórico daquele editor. O retorno do
  mesmo valor pelo `v-model` não reinicializa o campo nem reposiciona o cursor.
  A desmontagem remove o listener de alterações.
- Os campos têm identificação acessível, papel de caixa de texto multilinha
  e indicação de obrigatoriedade. As letras A a E continuam visíveis.

## Configuração

O enunciado permite até **7.000 caracteres** e cada alternativa até **2.000**,
sem limite total adicional por questão. O contador aparece no campo e no modal,
fica amarelo a partir de 90% e vermelho acima do limite, com orientação para
reduzir o texto. Não impede digitar, colar ou desfazer, e nunca corta o conteúdo.
O salvamento de cadastro/edição é bloqueado com aviso enquanto houver excesso;
a API também valida POST/PUT e retorna HTTP 400 antes de gravar.

A contagem considera o texto dos nós HTML, sem remover nem agrupar espaços, e
inclui pontuação. Tags, atributos, comentários e dados base64 das imagens não
contam; entidades como `&amp;` representam um caractere. Usa caracteres Unicode
(um emoji simples conta como um), não bytes nem unidades UTF-16. Quebras escritas
no texto contam, com CRLF/CR normalizados para LF; tags de parágrafo e `<br>` não
acrescentam caracteres. Imagens continuam com o limite de altura independente.
Registros antigos não são truncados nem migrados: ao editar, devem respeitar os
limites para salvar. Isso não garante que a questão caiba em uma única página.

Cada um dos seis campos tem o botão **Expandir**, à direita da barra de edição.
Ele abre um modal centralizado, com 92% da largura e 88% da altura da tela
(máximo 1200 × 900 px), fundo levemente escurecido e área de texto com rolagem.
**Fechar**, Esc ou clique no fundo retorna ao formulário. O diálogo nativo mantém
o foco dentro do modal; ao fechar, ele volta ao botão de expansão. A rolagem do
fundo fica bloqueada enquanto aberto e é restaurada inclusive ao sair da tela.
Os campos são independentes e o `Teleport` move a mesma instância do Quill, sem
perder texto, imagens, formatação ou histórico. A expansão só altera a interface,
não o HTML salvo nem a aparência da prova impressa.

O conteúdo dos seis editores, das listagens, da seleção e das prévias/impressões
das questões usa Arial 10 pt. A regra compartilhada está em
`src/assets/css/texto_questao.css` e prevalece sobre fonte/tamanho trazidos no HTML
colado, inclusive em títulos. Negrito, itálico e outras marcações são preservados.
Não altera os registros existentes no banco, os controles da interface nem o
cartão-resposta, que mantém suas medidas e tipografia próprias.

As barras já existentes em `EditorQuill.vue` foram mantidas: completa para o
enunciado e compacta nas alternativas, com tema Snow e integração visual ao CSS
do projeto. A seleção definitiva de ferramentas e formatos fica para a próxima
etapa, concentrada nesse mesmo componente. Não foi criado serviço de upload:
as imagens continuam embutidas no HTML, e a API valida os limites antes de salvar.

## Redimensionamento de imagens

Clique na imagem dentro de qualquer um dos seis editores e arraste uma das
quatro alças azuis. A proporção é mantida e o tamanho atual aparece sobre a
imagem. A altura máxima é de 45 mm, também aplicada pelo CSS compartilhado na
prévia e na impressão, inclusive para imagens já cadastradas. A proporção é
preservada, sem cortar a imagem. Não há um limite fixo de largura: permanece
somente a contenção ao espaço disponível para não ultrapassar as margens.
As alças usam o mesmo limite de altura, convertido para pixels.

Ao inserir uma imagem, o editor verifica as dimensões e já
insere `width`/`height` reduzidos proporcionalmente quando a altura ultrapassa
45 mm (170 px, arredondados para baixo). Imagens menores não são ampliadas.
A inserção e as dimensões entram juntas no histórico e no HTML emitido pelo
Quill. Antes da inserção, `utils/imagensQuestao.js` reduz o arquivo para caber em
**800 × 600 px**, proporcionalmente, sem ampliar imagens pequenas. O canvas usa
JPEG com qualidade **0,75** e fundo branco. Esse limite de resolução é diferente
dos 45 mm de exibição: não se reduz o arquivo a apenas 170 px de altura.

Cada campo aceita **até três imagens**, com contador no formulário e no modal.
Com três imagens, clicar no botão mostra um aviso sem abrir o seletor. Imagens
coladas ou arrastadas usam o mesmo processamento; na colagem múltipla, entram
somente as que couberem, mantendo o texto e sua formatação e avisando sobre as
excedentes descartadas. Substituir uma imagem selecionada libera sua vaga.
Falhas de leitura ou CORS descartam só a imagem nova inválida e exibem orientação;
imagens remotas precisam permitir leitura pelo canvas, ou devem ser baixadas e
inseridas como arquivo. GIF é convertido como imagem estática.

`utils/clipboardQuestao.js` estende apenas a colagem HTML com imagens; texto sem
imagens mantém o fluxo nativo do Quill. O uploader nativo também reutiliza a
inserção central para arquivos colados/arrastados. A edição do campo fica bloqueada
durante o processamento para evitar concorrência, e a inserção completa entra
como uma única ação desfazível. O aviso usa um diálogo próprio para aparecer
acima do editor expandido, sem ficar escondido atrás dele.

Cadastro e atualização validam três imagens por campo no frontend e na API.
Questões antigas acima da cota não são truncadas ao abrir: é necessário excluir
as excedentes para salvar. Imagens já cadastradas não são recomprimidas nem
migradas automaticamente. A API valida a quantidade; a compressão ocorre no
navegador. Não há novas dependências ou alteração do contrato de HTML/base64.

`quill-resize-module` 2.1.3 fornece as alças e o indicador de tamanho, sem ativar
ferramentas de alinhamento, vídeos ou atalhos adicionais. A integração fica em
`utils/redimensionarImagem.js`, que define os limites, fecha a seleção ao clicar
fora e remove os listeners ao desmontar, inclusive se um arraste for interrompido.

Ao selecionar uma imagem, aparece também uma lixeira vermelha no canto superior
esquerdo. Ela exclui apenas aquela imagem pelo Quill e atualiza o campo; Ctrl+Z
desfaz a exclusão sem desfazer a edição anterior. O botão fica fora do conteúdo
editável: não é salvo no HTML nem aparece na prova. Assim como as demais edições,
a exclusão só é persistida no banco ao salvar a questão.

As dimensões são atributos `width`/`height` da imagem no HTML. Ao soltar a alça,
o Quill atualiza o conteúdo do campo. A sanitização identifica `width` e `height`
como dimensões, sem submetê-los à validação de protocolos de URL, e mantém as
restrições existentes para `src`. O tamanho só é gravado no banco quando a questão é salva. Reabrir o
editor mantém as dimensões. Não é necessário alterar o contrato da API nem
recodificar o arquivo de imagem a cada arraste.

## Verificação

`npm test` cobre o carregamento e a emissão de HTML, as instâncias independentes,
a sincronização sem reinicialização, a limpeza do histórico e dos listeners,
os seis campos no formulário, o bloqueio de conteúdo vazio e a preservação da
resposta correta ao cadastrar ou editar.
