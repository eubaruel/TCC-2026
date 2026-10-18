# Login e recarregamento de página

## Causa do redirecionamento

O login mantinha `authStore.user` apenas no estado em memória do Pinia. Recarregar recriava a aplicação com `user: null`; o guard do router verificava `isLoggedIn` e redirecionava para `/`.

## Correção do MVP

`src/stores/auth.js` salva os dados retornados após um login bem-sucedido em `sessionStorage`, na chave `tcc.usuario`. A função `state` restaura esses dados de forma síncrona, antes da primeira verificação do router. Não é necessário alterar o router ou adicionar dependências.

São preservados somente `registro`, `nome`, `email`, `role` e `deve_alterar_senha`. A senha não é armazenada nem reutilizada. O estado `loading` sempre começa como `false`.

O armazenamento é da sessão da aba, não um recurso de "lembrar de mim" entre sessões do navegador. `logout()` remove os dados tanto do Pinia quanto do armazenamento. Dados ausentes, inválidos ou incompletos são ignorados. Se o navegador bloquear o armazenamento, login e saída continuam funcionando em memória, mas a persistência no recarregamento fica indisponível.

As restrições de perfil permanecem: o Professor não ganha acesso às telas exclusivas do Processo pedagógico ao recarregar.

## Limite de segurança existente

Essa persistência mantém o estado da interface; **não cria uma sessão autenticada no servidor**. O backend atual retorna dados do usuário no login e ainda tem a emissão de token como pendência. O conteúdo de `sessionStorage` é controlado pelo navegador e não deve ser usado pelo backend como prova de identidade ou permissão. A autenticação e autorização reais da API continuam sendo uma tarefa separada.

## Testes

`tests/auth.test.js` verifica login dos dois perfis, restauração em uma nova instância do Pinia sem reenviar senha, logout, dados inválidos, exclusão de campos sensíveis e armazenamento indisponível.

No navegador isolado, com API simulada e sem escrever no banco, os dois perfis fizeram login pelo formulário e permaneceram na rota após recarregar, com apenas uma chamada de login por perfil. O Professor continuou bloqueado em `/provas/corrigir`. A saída pela barra lateral, com confirmação no modal, limpou o armazenamento e impediu novo acesso após recarregar. Uma aba independente permaneceu sem login. O conjunto de testes do frontend totalizou 38 testes aprovados, além de lint e build sem erros; permanece o aviso existente de tamanho do pacote principal.
