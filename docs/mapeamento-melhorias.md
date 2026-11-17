# Mapeamento de melhorias — TCC 2026

Levantamento feito em 16/11/2026 sobre o código atual (`main`). Nenhum código foi alterado.
Cada item traz: **causa / situação atual**, **arquivos envolvidos**, **o que mudar** e **como testar**.

Ordem sugerida de implementação: 2 → 1 → 5 → 3 → 7 → 6 → 4 → 8 → 9
(primeiro os bugs, depois o layout de impressão, que é compartilhado por vários itens).

---

## 1. Enunciado extrapolando a largura da tela

### Causa (confirmada no banco)
O enunciado salvo da questão da imagem tem **todos os espaços gravados como `&nbsp;`**:

```
<p>A&nbsp;Segunda&nbsp;Guerra&nbsp;Mundial&nbsp;(1939–1945)&nbsp;foi&nbsp;um&nbsp;dos ...
```

`&nbsp;` é um espaço que **não quebra linha**, então o parágrafo inteiro vira uma "palavra" gigante.
A única quebra que aparece na imagem é logo após o travessão "–", o único ponto de quebra que sobrou.

A origem é o próprio editor: o Quill 2 (`quill@^2.0.3`) gera `&nbsp;` no lugar dos espaços
em `getSemanticHTML()`, e o `EditorQuill.vue` usa exatamente esse método para emitir o HTML.
Ou seja, **toda questão salva tem o problema**, e ele só fica visível quando o texto é longo.

Dois agravantes de CSS:
- `CriarProvaView.vue`: `.area-trabalho { grid-template-columns: 1fr 1fr }`. Uma coluna `1fr`
  não encolhe abaixo do conteúdo mínimo, então o painel esquerdo cresce junto com a linha sem quebra.
  Além disso, `.questao-texto` tem `overflow-x: auto`, o que cria a rolagem lateral.
- `QuestoesView.vue`: `.questao-texto` não tem nenhuma regra de quebra de linha.

### Arquivos
| Arquivo | Ponto |
|---|---|
| `frontend/src/components/EditorQuill.vue` | `atualizarConteudo()` (linha ~158): `sanitizar(this.quill.getSemanticHTML())` |
| `frontend/src/views/QuestoesView.vue` | CSS `.questao-texto` (~586) e `.texto-alternativa` |
| `frontend/src/views/CriarProvaView.vue` | CSS `.area-trabalho` (~413), `.questao-texto` (~468), `.questao-card` (~456) |
| `frontend/src/components/PreviewProva.vue` | `.folha` já usa `word-wrap: break-word`, mas quebra no meio da palavra |
| `backend/api/services/questao_service.py` | `_setar_modelo_questao()`: ponto para normalizar no servidor também |
| **novo** `backend/scripts/normalizar_nbsp_questoes.py` | migração das questões já salvas |

### O que mudar
1. **Corrigir na origem (frontend):** em `atualizarConteudo()`, trocar `&nbsp;` por espaço normal
   antes de emitir. Para preservar espaços duplos intencionais, trocar só o `&nbsp;` que fica entre
   dois caracteres que não são espaço, ou alternar entre `" "` e `"&nbsp;"` quando houver uma sequência.
   Criar uma função `normalizarEspacos(html)` em `utils/html.js` e testá-la em `tests/html.test.js`.
2. **Defesa no backend:** aplicar a mesma normalização em `_setar_modelo_questao()` (enunciado e
   alternativas). Assim uma questão enviada por outro cliente também chega correta.
3. **Corrigir os dados existentes:** script único que percorre `questoes` e regrava
   `enunciado` e `alternativas[].texto` normalizados.
   Atenção: existe um **índice único em `enunciado`**, e o script precisa tratar a colisão
   caso duas questões fiquem iguais depois da normalização.
4. **CSS defensivo**, para textos colados que ainda tragam linhas muito longas (URLs, fórmulas):
   - `CriarProvaView.vue`: `grid-template-columns: minmax(0, 1fr) minmax(0, 1fr)`;
     em `.questao-texto`, remover `overflow-x: auto` e usar `overflow-wrap: break-word`.
   - `QuestoesView.vue`: em `.questao-texto` e `.texto-alternativa`, usar `overflow-wrap: break-word; min-width: 0`.
   - Tabelas e `pre` dentro do enunciado: `max-width: 100%` e `white-space: pre-wrap`.

### Como testar
- Colar um texto longo de Word, PDF ou site no editor, salvar e conferir no banco que não há `&nbsp;` entre as palavras.
- Abrir "Buscar Questão", "Minhas Questões", a lista do banco no editor de prova e a prévia:
  nenhuma rolagem horizontal, apenas a vertical.
- Teste unitário de `normalizarEspacos` com espaços simples, duplos e com `&nbsp;` dentro de `<pre>`.

---

## 2. Imagem no enunciado não é aceita (erro ao salvar)

### Causa (reproduzida)
Enviei para a API local uma questão com uma imagem de tamanho real (~120 KB em base64).
A resposta foi **HTTP 500 "Ocorreu um erro interno no servidor"**. O log do PM2
(`api-principal-out.log`) mostra:

```
pymongo.errors.OperationFailure: Regular expression is invalid:
pattern string is longer than the limit set by the application (code 51091)
```

Antes de criar a questão, `questao_service.criar()` chama
`questao_dao.campo_existe("enunciado", enunciado)`, que monta um **regex com o enunciado inteiro**:

```python
filtro = {campo: {"$regex": f"^{re.escape(valor)}$", "$options": "i"}}
```

O MongoDB limita o tamanho do padrão de regex. Com texto puro o padrão é pequeno e funciona;
com uma imagem em base64 o padrão passa do limite e a consulta explode.
Uma imagem minúscula (1×1 px) passa, por isso o erro parece aleatório.

O editor (`EditorQuill.vue`, `imagensQuestao.js`) e o sanitizador (`utils/html.js`)
estão corretos: a imagem é reduzida para JPEG ≤ 800×600 e o `data:image/jpeg;base64` é permitido.

> Os documentos de teste que criei para reproduzir o erro foram apagados do banco.

### Arquivos
| Arquivo | Ponto |
|---|---|
| `backend/api/DAOs/questao_dao.py` | `campo_existe()` (linha ~114) |
| `backend/api/services/questao_service.py` | `criar()`: checagem de duplicidade e mensagem de erro que inclui o enunciado inteiro |
| `backend/api/DAOs/questao_dao.py` | `criar()`: tratar `DuplicateKeyError` do índice único |

### O que mudar
1. Em `campo_existe`, **parar de usar regex** para o enunciado. Opções, da mais simples à mais robusta:
   - **(a)** comparação exata `{campo: valor}`, que usa o índice único `enunciado_1` já existente; ou
   - **(b, recomendada)** gravar um campo `enunciado_hash` (SHA-256 do texto normalizado:
     minúsculas, espaços colapsados, mais os `src` das imagens) com índice único,
     e comparar por ele. Isso mantém a regra "sem diferenciar maiúsculas" que o regex tentava garantir
     e evita indexar strings de centenas de KB.
2. Em `questao_dao.criar()`, capturar `pymongo.errors.DuplicateKeyError` e devolver **400 "Enunciado repetido"**
   em vez de 500.
3. Em `questao_service.criar()`, a mensagem de duplicidade não deve repetir o enunciado (com base64 ela fica enorme).
   Usar `textoPuro` truncado em ~80 caracteres.
4. O mesmo padrão de regex com `re.escape` só deve continuar onde o valor é curto (nome, código).

### Como testar
- Criar uma questão com 1, 2 e 3 imagens grandes: deve salvar (201).
- Criar a mesma questão duas vezes: a segunda deve retornar 400 com mensagem curta.
- Editar uma questão existente e incluir uma imagem: deve salvar.
- Adicionar um teste em `backend/tests/test_daos.py` com um enunciado de mais de 50 KB.

---

## 3. QR code ocupando todo o quadrado reservado

### Situação atual
Geometria em `frontend/src/utils/cartaoResposta.js` (viewBox 1200×286):

```js
qr: { x: 9, y: 168, tamanho: 94, margem: 4 }
```

O quadro reservado (abaixo de "NOTA") vai de **x 0 → 111,5** e **y 143 → 286**,
ou seja 111,5 × 143. O QR usa só 94 × 94, e 4 desses módulos são margem branca (quiet zone)
gerada pela biblioteca `qrcode`.

### Arquivos
| Arquivo | Ponto |
|---|---|
| `frontend/src/utils/cartaoResposta.js` | `CARTAO_RESPOSTA.qr` |
| `frontend/src/components/CartaoResposta.vue` | `<image>` do QR (linha 43), que só lê a geometria |
| `frontend/src/views/ImprimirProvasView.vue` | `QRCode.toDataURL(..., { margin: CARTAO_RESPOSTA.qr.margem, width: 256 })` |
| `frontend/src/utils/recortarCartao.js` | **usa `qr.x`, `qr.y`, `qr.tamanho` e `qr.margem` para recortar o cartão na correção** |
| `backend/sistema-correcao/data_extractor.py` | `ler_qrcode()` (OpenCV) |

### O que mudar
- A largura limita: com ~4 de folga para não encostar na borda (traço 1,2), o QR fica com
  `tamanho ≈ 104`, `x ≈ 3,75`, centralizado na vertical: `y ≈ 143 + (143 − 104) / 2 ≈ 162,5`.
- Para o desenho preto ocupar mais área, reduzir `margem` de 4 para 2. As bordas do quadro
  ficam ~4 unidades afastadas, e o leitor OpenCV costuma aceitar quiet zone de 2 módulos.
  Isso **precisa ser validado** com folha impressa e escaneada.
- Aumentar `width` do `toDataURL` para 512, para não pixelar na impressão.
- Como `recortarCartao.js` lê a mesma constante, o recorte se ajusta sozinho.
  **Mas as provas já impressas com a geometria antiga deixarão de ser recortadas corretamente.**
  Só aplicar a mudança com nenhuma prova impressa pendente de correção, ou versionar a geometria
  (gravar `versao_cartao` na prova e manter as duas).

### Como testar
- Imprimir, escanear e corrigir um lote de teste pelo fluxo "Corrigir provas".
- Rodar `frontend/tests/correcao.test.js` e ajustar os valores esperados de recorte.

---

## 4. Campos "Conteúdo" e "Observação" para o professor

### Interpretação
O professor preenche, opcionalmente, **Conteúdo** (assuntos cobrados) e **Observação**
(instruções como "pode usar calculadora") ao montar a prova. Esses dados são impressos junto ao
cartão-resposta ("gabarito", como o cartão é chamado no sistema).
*Se a intenção era colocá-los no gabarito do professor do item 6, a mudança de dados é a mesma: muda só onde imprimir.*

### Situação atual
O professor só envia a lista de questões: `PATCH /provas/<id>/adicionar-questoes` com `{ prova: { questoes } }`.
O `PUT /provas/<id>` bloqueia alteração de metadados depois que há questões vinculadas.

### Arquivos
| Camada | Arquivo | O que fazer |
|---|---|---|
| Modelo | `backend/api/modelos/prova.py` | atributos `conteudo` e `observacao` (str opcional, `strip`, limite ~300 caracteres cada, texto puro) |
| Middleware | `backend/api/middlewares/prova_middleware.py` | validação do corpo de `adicionar-questoes` para aceitar os dois campos opcionais |
| Service | `backend/api/services/prova_service.py` | `adicionar_questoes()` recebe e grava os campos; `_formatar_prova()` devolve os dois |
| DAO | `backend/api/DAOs/prova_dao.py` | `atualizar_questoes()` faz `$set` de `conteudo` e `observacao`; `set_doc()` inclui os dois |
| Rota/controle | `prova_rotas.py`, `prova_controle.py` | repassar o corpo completo |
| Front service | `frontend/src/services/provas.js` | `adicionarQuestoes(id, questoes, { conteudo, observacao })` |
| Store | `frontend/src/stores/provaDraft.js` | guardar os dois campos no rascunho e marcar `sujo` ao alterar |
| Tela | `frontend/src/views/CriarProvaView.vue` | bloco acima de "Banco de questões" com dois `<textarea>` e contador; desabilitado quando `!editavel`; enviado em `salvar()` |
| Impressão | `frontend/src/components/CartaoResposta.vue` *ou* `ImprimirProvasView.vue` | ver abaixo |
| Docs | `backend/api/docs/Documentações de rotas/Provas.md` | documentar os campos |

**Onde imprimir:** a área "INFORMAÇÕES GERAIS" do cartão não tem espaço livre suficiente, e
**o interior do cartão é lido pelo corretor**. Recomendo um quadro logo abaixo do cartão, dentro do
slot `#cabecalho` (no lugar ou acima de `.orientacao-cartao`), exibido só quando houver conteúdo.
Esse quadro também aparece na prévia do `CriarProvaView`, que usa o mesmo slot.

### Como testar
- Salvar com e sem os campos, reabrir a prova e conferir que os valores voltam.
- Prova concluída: os campos ficam somente leitura.
- Impressão: o quadro aparece só quando preenchido e não altera a posição do cartão.

---

## 5. Diminuir o espaçamento entre linhas de questões e alternativas

### Situação atual (`frontend/src/components/PreviewProva.vue`, usado na prévia e na impressão)
| Regra | Valor atual | Sugestão |
|---|---|---|
| `.folha { line-height }` | 1.5 | 1.25 |
| `.folha :deep(p) { margin }` | 0 0 4px | 0 0 2px |
| `.preview-questao { margin-bottom }` | 20px | 10–12px |
| `.preview-alternativas { margin-top }` | 8px | 4px |
| `.preview-alternativas li { margin-bottom }` | 4px | 1px |

Fonte padrão em `assets/css/texto_questao.css`: Arial 10pt (manter).

Ajuste extra: o Quill gera parágrafos vazios `<p><br></p>` quando o professor dá Enter a mais.
Em `htmlQuestoes`, remover parágrafos vazios no início e no fim do enunciado e das alternativas.

Opcional: aplicar a mesma redução nas listas de tela (`QuestoesView.vue` `.alternativas li`,
`CriarProvaView.vue` `.alternativas li { margin: 8px 0 }`).

### Como testar
Comparar a prévia e o PDF ("Salvar como PDF" na impressão) antes e depois, com uma prova de 10 questões.
Rodar `tests/tipografiaQuestoes.test.js`.

---

## 6. Checkbox "Imprimir gabarito" na impressão

### Situação atual
`ImprimirProvasView.vue` (só para o Processo pedagógico) imprime, por turma:
`ListaTurma tipo="notas"`, `ListaTurma tipo="entrega"` e as provas individuais.
**Cada aluno tem uma versão embaralhada**, então o gabarito é por aluno.
O dado já está disponível: `versao.questoes[i].indiceCorreta`, montado por `questaoDoBanco()`.
Não precisa mexer no backend.

### Arquivos
| Arquivo | O que fazer |
|---|---|
| `frontend/src/views/ImprimirProvasView.vue` | checkbox "Incluir gabarito" no `.impressao-acoes`, desmarcado por padrão (`data: incluirGabarito`); renderizar `<GabaritoTurma v-if="incluirGabarito">` em cada grupo, depois das duas `ListaTurma` |
| **novo** `frontend/src/components/GabaritoTurma.vue` | folha `documento-impressao` com o mesmo cabeçalho da `ListaTurma` (logos, disciplina, professor, turma, data) e a tabela **Nº · Matrícula · Nome · 1 · 2 · … · N** com a letra correta (`LETRAS[indiceCorreta]`); paginação igual à de `ListaTurma` |
| `frontend/src/utils/listasTurma.js` | reaproveitar a paginação/agrupamento |
| `frontend/tests/listasTurma.test.js` (ou novo teste) | testar a montagem da tabela |

Cuidados:
- Título claro, como **"GABARITO DO PROFESSOR — USO INTERNO"**, para não confundir com o
  cartão-resposta, que o `ImprimirNotasView` chama de "folhas que contêm o gabarito".
- Opcional: lembrar a escolha por sessão com `sessionStorage`, sempre dentro de `try/catch`, como já é feito em `auth.js`.

### Como testar
Marcar e desmarcar a opção e conferir a prévia de impressão: a folha aparece uma vez por turma,
com a letra de cada aluno batendo com a sua prova individual.

---

## 7. Checkbox "Duas colunas (modelo ENEM)" na criação da prova

### Arquivos
| Camada | Arquivo | O que fazer |
|---|---|---|
| Modelo | `backend/api/modelos/prova.py` | atributo `colunas` (int, 1 ou 2; padrão 1) |
| Service | `backend/api/services/prova_service.py` | incluir em `_CAMPOS_PROVA_BASE`, `criar_prova()` e `_formatar_prova()`; tratar o valor ausente em provas antigas como 1 |
| DAO | `backend/api/DAOs/prova_dao.py` | `set_doc()` |
| Middleware | `prova_middleware.py` | aceitar e validar `colunas` |
| Front | `frontend/src/components/CriarProvaBase.vue` | checkbox "Dividir questões em duas colunas (modelo ENEM)" em `formulario.duas_colunas`, enviado como `colunas: 2` ou `1` no `criarProva()` |
| Front | `frontend/src/views/ProvasView.vue` | se houver edição da prova-base ou exibição dos detalhes, mostrar e editar o campo |
| Prévia/impressão | `frontend/src/components/PreviewProva.vue` | classe `duas-colunas` na `.conteudo-prova` quando `metadados.colunas === 2` |

CSS (em `PreviewProva.vue`):
```css
.conteudo-prova.duas-colunas { column-count: 2; column-gap: 6mm; column-rule: 1px solid #999; }
.duas-colunas .preview-questao { break-inside: avoid; }
.duas-colunas img { max-width: 100%; }
```
O cartão-resposta fica no slot `#cabecalho`, fora da `.conteudo-prova`, e continua ocupando a largura toda.
`CriarProvaView` e `ImprimirProvasView` já passam `metadados` com os dados da prova, então a prévia
do professor mostra o layout automaticamente.

Combinações com outros itens: fica melhor junto com o item 5 (menos espaço) e com o item 1
(sem `&nbsp;`, senão as colunas estreitas estouram).

### Como testar
Prova com 10 questões, uma delas com imagem: nenhuma questão é cortada entre colunas ou páginas.

---

## 8. Forçar o professor a trocar a senha no primeiro login

### Situação atual
- **O backend já tem tudo:** todo usuário criado recebe `deve_alterar_senha: True`
  (`usuario_dao.py`), o login devolve o campo (`usuario_service.login`), e existe
  `PATCH /usuarios/<registro>/alterar-senha` com `{ usuario: { senha_atual, nova_senha } }`,
  que grava `deve_alterar_senha: false`. Quando o Processo pedagógico redefine a senha
  (com `solicitante`), o campo volta a `true`.
- **O frontend guarda o campo mas não usa:** `stores/auth.js` salva `deve_alterar_senha`;
  a action `trocarSenha()` está vazia e não há rota nem tela.

### Arquivos
| Arquivo | O que fazer |
|---|---|
| `frontend/src/services/usuarios.js` | `alterarSenha(registro, senha_atual, nova_senha)` chamando o PATCH acima |
| `frontend/src/stores/auth.js` | implementar `trocarSenha()`: chamar o serviço; em caso de sucesso, `user.deve_alterar_senha = false` e `salvarUsuario(user)` |
| **novo** `frontend/src/views/TrocarSenhaView.vue` | tela cheia (como o login): senha atual, nova senha e confirmação; checklist das regras ao vivo; botão "Sair" |
| `frontend/src/router/index.js` | rota `/trocar-senha` (`requiresAuth`, fora da `TelaPrincipal`); no `beforeEach`, se `isProfessor && user.deve_alterar_senha && to.name !== 'TrocarSenha'`, redirecionar para lá |
| `frontend/src/components/LoginFormulario.vue` | depois do login (linha ~103), ir para `/trocar-senha` quando o flag vier `true` |
| `frontend/tests/auth.test.js`, `loginFormulario.test.js` | casos do redirecionamento e da troca |

Regras de senha a espelhar no front (vêm de `backend/api/modelos/usuario.py`):
mínimo de 6 caracteres, uma maiúscula, um número e um caractere especial de `!@#$%^&*(),.?":{}|<>`.
O backend também recusa nova senha igual à atual.

Observações:
- O pedido fala em "professor". O backend marca o flag para todos os perfis; para incluir o
  Processo pedagógico, basta tirar o `isProfessor` da condição do guard.
- As rotas da API não têm autenticação (o JWT está comentado), então a obrigação vale só no front.
  É aceitável para o TCC, mas vale citar na apresentação.
- O usuário de teste "Professor Teste" ainda está com o flag ativo e será obrigado a trocar a senha no próximo login.

---

## 9. Créditos no rodapé da tela "Informações"

### Arquivo
`frontend/src/views/ConfiGuracoes.vue` (rota `/informacoes`, componente `InformacoesView`).

### O que fazer
Adicionar um `<footer class="creditos">` depois do `<dl class="dados-usuario">`:

- Título: "Desenvolvido por — Turma 3°J · 2026"
- Lista:
  - Jean Machado Brasil — `@jeanmbr` → `https://github.com/jeanmbr`
  - Vitor Doring Leitão — `@VitorDoring` → `https://github.com/VitorDoring`
  - Lucas Baruel Cestaro — `@eubaruel` → `https://github.com/eubaruel`
- O texto visível é só o username. A URL não aparece na tela.
  Link com `target="_blank" rel="noopener noreferrer"`, sublinhado e com cor ao passar o mouse.
- Estilos do tema escuro no mesmo padrão `:global(.tema-escuro ...)` do arquivo.

Pontos para decidir:
- "Quando o mouse passar, direcionar": recomendo **clicar** para abrir, com destaque ao passar o mouse.
  Abrir só por passar o mouse é possível (`@mouseenter` + `window.open`), mas abre abas sem querer
  e costuma ser bloqueado como pop-up.
- "Escondendo o link": a URL não aparece no texto. Mesmo assim, todo navegador mostra o destino
  de um `<a>` na barra de status ao passar o mouse. Esconder isso exigiria um `<button>` com
  `window.open`, o que piora a acessibilidade. Recomendo manter o `<a>`.

---

## Resumo por arquivo

| Arquivo | Itens |
|---|---|
| `frontend/src/components/EditorQuill.vue` | 1 |
| `frontend/src/utils/html.js` | 1 |
| `frontend/src/views/QuestoesView.vue` | 1, 5 |
| `frontend/src/views/CriarProvaView.vue` | 1, 4, 5 |
| `frontend/src/components/PreviewProva.vue` | 1, 5, 7 |
| `frontend/src/utils/cartaoResposta.js` | 3 |
| `frontend/src/components/CartaoResposta.vue` | 3, 4 |
| `frontend/src/utils/recortarCartao.js` | 3 (só validar) |
| `frontend/src/views/ImprimirProvasView.vue` | 3, 4, 6 |
| `frontend/src/components/GabaritoTurma.vue` (novo) | 6 |
| `frontend/src/components/CriarProvaBase.vue` | 7 |
| `frontend/src/services/provas.js`, `stores/provaDraft.js` | 4, 7 |
| `frontend/src/services/usuarios.js`, `stores/auth.js`, `router/index.js`, `LoginFormulario.vue` | 8 |
| `frontend/src/views/TrocarSenhaView.vue` (novo) | 8 |
| `frontend/src/views/ConfiGuracoes.vue` | 9 |
| `backend/api/DAOs/questao_dao.py`, `services/questao_service.py` | 1, 2 |
| `backend/api/modelos/prova.py`, `services/prova_service.py`, `DAOs/prova_dao.py`, `middlewares/prova_middleware.py` | 4, 7 |
| `backend/scripts/normalizar_nbsp_questoes.py` (novo) | 1 |
