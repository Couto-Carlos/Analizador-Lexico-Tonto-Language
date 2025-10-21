# Analisador Léxico para a Linguagem TONTO (Textual Ontology Language)

Projeto da disciplina de Compiladores Sexto Período da UFERSA

## 1. Visão Geral do Projeto

Este projeto consiste na implementação de um **Analisador Léxico** para a linguagem TONTO (Textual Ontology Language). TONTO é uma linguagem textual para especificação de ontologias computacionais, que são fundamentais para a Web Semântica (Web 3.0).

O objetivo deste analisador é ler um arquivo-fonte com a extensão `.tonto`, processar seu conteúdo e identificar todos os componentes léxicos (tokens) da linguagem, como palavras-chave, identificadores, símbolos e tipos.

O programa é capaz de:
* Reconhecer os tokens válidos da linguagem TONTO.
* Ignorar espaços em branco, tabulações e comentários (`//...`).
* Gerar uma **tabela de símbolos** formatada, listando o lexema, o tipo de token e a linha onde foi encontrado.
* Identificar e reportar **erros léxicos** (caracteres inesperados), indicando a linha do erro.

## 2. Equipe

* Carlos Eduardo Couto de Castro

## 3. Tecnologias Utilizadas

* **Python 3.x**
* **PLY (Python Lex-Yacc)**: Biblioteca utilizada para a geração do analisador léxico.

## 4. Configuração do Ambiente

Para executar este projeto, é necessário ter o Python 3 instalado e a biblioteca PLY.

**1. Clone o repositório:**
```bash
git clone [https://github.com/](https://github.com/)[SEU-USUARIO]/[NOME-DO-REPOSITORIO].git
cd [NOME-DO-REPOSITORIO]
```

O projeto depende apenas da biblioteca ply. Você pode instalá-la diretamente:
```bash
pip install ply
```

