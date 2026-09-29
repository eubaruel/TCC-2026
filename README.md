# Sistema de banco de questões com integração de correção automatizadas de provas objetivas

> Trabalho de Conclusão de Curso - Curso técnico de informática da UNIVAP

---

## Sobre o Projeto

Este projeto tem como objetivo desenvolver um sistema capaz de armazenar questões para provas e corrigir avaliações objetivas.

O sistema foi criado para solucionar o problema de descentralização das ferramentas de criação, armazenamento e correção das provas do Colégio Técnico UNIVAP Centro, oferecendo uma solução integrada, centralizada e intuitiva.

---

## Objetivos

### Objetivo Geral
Desenvolver um sistema para armazenar questões de prova e corrigir provas objetivas automaticamente.

### Objetivos Específicos
- Desenvolver um banco de questões onde professores possam criar e consultar questões para as provas

- Implementar o sistema de correção automática das provas objetivas

- Garantir que tudo seja integrado e intuitivo

---

## Tecnologias Utilizadas

<table width="100%" border="1" cellspacing="0" cellpadding="10">
  <thead>
    <tr>
      <th align="left">Camada</th>
      <th align="left">Tecnologias</th>
      <th align="left">Descrição</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>Frontend</strong></td>
      <td>JavaScript · Vue.js</td>
      <td>Interface do usuário e interação</td>
    </tr>
    <tr>
      <td><strong>Backend</strong></td>
      <td>Python · Flask</td>
      <td>Regras de negócio e API REST</td>
    </tr>
    <tr>
      <td><strong>Banco de Dados</strong></td>
      <td>MongoDB</td>
      <td>Persistência e armazenamento de dados</td>
    </tr>
    <tr>
      <td><strong>Ferramentas</strong></td>
      <td>Git</td>
      <td>Versionamento</td>
    </tr>
  </tbody>
</table>

---

## Arquitetura do Projeto

O projeto segue o padrão MVC e a API REST

---

## Funcionalidades

- Criar e consultar questões de prova
- Montar provas direto pelo sistema
- O professor pode enviar a prova para revisão e aprovação
- Correção das provas objetivas

---

## Informações Acadêmicas

**Autores:**  
- Vitor Doring Leitão
- Lucas Baruel Cestaro
- Jean Machado Brasil

**Orientador:**  
- Prof. Me. Hélio Lourenço Esperidião Ferreira

**Instituição:**  
Colégio Técnico UNIVAP Unidade Centro

**Ano:**  
2026  


---

**Jsons Questão**

		"questao": [
			{
				"_id": "6a0d94f7a30c197b44675521",
				"assunto": "Guerra Dos Vários Anos",
				"autor": "ENEM",
				"dificuldade": "Médio",
				"disciplina": [
					"História"
				],
				"enunciado": "Acerta essa e as outras questões pra você tirar um 10 bem chave e legal",
				"numero_linhas": 5,
				"professor": {
					"nome": "Ricardão Dos Santos"
				},
				"tipo_questao": "Dissertativa"
			},
			{
				"_id": "6a0d97fea30c197b44675522",
				"alternativa_correta": "certa",
				"alternativas": [
					"errada1",
					"errada2",
					"errada3",
					"errada4",
					"certa"
				],
				"assunto": "Guerra Dos Vários Anos",
				"autor": "ENEM",
				"dificuldade": "Médio",
				"disciplina": [
					"História"
				],
				"enunciado": "Acerta essa e as outras questões pra você tirar um 10 bem chave e legal e foda",
				"professor": {
					"nome": "Ricardão Dos Santos"
				},
				"tipo_questao": "Objetiva"
			}
