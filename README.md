# Analisador Léxico e Sintático para a Linguagem TONTO (Textual Ontology Language)

Projeto da disciplina de Compiladores, Sexto Período, UFERSA.

## 1. Visão Geral

Analisador léxico e sintático para a TONTO, uma linguagem textual para especificação de ontologias. O programa lê arquivos `.tonto`, reconhece os construtos da linguagem, preenche uma tabela de símbolos e produz duas saídas:

* **Tabela de síntese:** resumo dos construtos encontrados (pacotes, classes, atributos, relações internas e externas, tipos de dados, enums e gensets), organizados por pacote.
* **Relatório de erros:** erros léxicos e sintáticos, com arquivo, linha, coluna e sugestão de tratamento.

## 2. Equipe

* Carlos Eduardo Couto de Castro
* Adriam Keven Ferreira de Sousa

## 3. Tecnologias

* **Python 3.x**
* **PLY (Python Lex-Yacc)**: `ply.lex` para o léxico e `ply.yacc` para o sintático.

## 4. Estrutura do Projeto

| Arquivo | Função |
|---|---|
| `analisador_lexico.py` | Reconhecimento dos tokens e identificação de erros léxicos |
| `analisador_sintatico.py` | Regras da gramática e preenchimento da tabela de símbolos |
| `tabela_simbolos.py` | Implementação da tabela de símbolos e dos escopos |
| `main.py` | Execução das análises e apresentação dos resultados |

## 5. Configuração do Ambiente

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

## 6. Construtos Reconhecidos

* Pacotes (`package Nome { ... }`) e importações (`import Nome`)
* Classes com estereótipo (`kind Person { ... }`), com atributos e relações internas
* Classes enumeradas (`enum Cor { Vermelho1 Verde2 }`)
* Relações internas e externas às classes
* Novos tipos de dados (nomes terminados em `DataType`), baseados em `number`, `string`, `boolean`, `date`, `time` e `datetime`
* Conjuntos de generalização (`genset Geral: Especifica1 Especifica2`)

## 7. Implementação da Tabela de Símbolos

A tabela está em `tabela_simbolos.py`, na classe `TabelaSimbolos`. Cada **escopo** possui sua própria tabela de dispersão, implementada com o `dict` do Python e são encadeados.

```
global
 └── package UniversitySystem
      ├── class Person
      │    └── atributos e relações internas
      └── relation isEnrolledIn
```

**Campos de `TabelaSimbolos`**

* `tabela`: o `dict` do escopo (nome -> símbolo)
* `prev`: escopo pai (`None` no global)
* `nome` e `tipo`: identificação do escopo (`global`, `package`, `class`, `relation` ou `enum`)
* `imports`: pacotes importados naquele escopo

**Operações**

* `put(chave, simbolo)`: insere no escopo atual; se o nome já existir ali, não insere e retorna `False`
* `novo_escopo(nome, tipo)`: cria um escopo filho
* `percorrer(escopo)`: percorre os símbolos, inclusive os dos escopos internos

**Colisões de nomes:** nomes repetidos no mesmo escopo não são sobrescritos (`put` recusa). Nomes iguais em escopos diferentes não colidem, pois cada escopo tem seu próprio `dict` (por exemplo, o atributo `name` de `Person` e o de `University`).

**Uso pelo parser:** o parser mantém o `escopo_atual`. `abrir_escopo` cria e entra em um escopo filho ao reconhecer pacote, classe, relação com corpo ou enum; `fechar_escopo` volta ao escopo pai; `inserir` grava cada símbolo no escopo corrente; `resetar_escopo` retorna ao global antes de cada arquivo. O léxico não altera a tabela.

**Uso na saída:** a tabela de síntese é gerada percorrendo a tabela (`percorrer`), contando e listando os símbolos por pacote e por classe. A análise é baseada na tabela de símbolos.

## 8. Tratamento de Erros

* **Erros léxicos:** ocorrem quando o analisador encontra caracteres que não pertencem à linguagem.
* **Erros sintáticos:** ocorrem quando os elementos do arquivo não seguem as regras da gramática.

## 9. Exemplo de Saída

```
Analisando: testes/teste_avancado.tonto

============================================================
TABELA DE SÍNTESE (CONSTRUTOS TONTO)
============================================================
Pacotes: 1 | Classes: 4 | Atributos: 7
Relações internas: 0 | externas: 1 | Tipos de dados: 2 | Enums: 0 | Gensets: 1
------------------------------------------------------------

Pacote HealthSystem (importa: UniversitySystem)  [testes/teste_avancado.tonto]
  Classe LivingBeing [mixin]
      atributos: name: string, birthDate: date
  Classe Patient [kind]
      atributos: medicalRecordNumber: string, email: string
  Classe Doctor [kind]
      atributos: crm: string, specialty: string
  Classe Dose [quantity]
      atributos: amount: number
  Relações externas: @material MedicalConsultation { patient: Patient [1..1], doctor: Doctor [1..*] }
  Tipos de dados: PhoneDataType, AddressDataType
  Genset: Doctor -> GeneralPractician, Surgeon
============================================================

============================================================
RELATÓRIO DE ERROS E SUGESTÕES DE TRATAMENTO
============================================================
Nenhum erro encontrado.
```