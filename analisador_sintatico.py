# analisador_sintatico.py
# Analisador sintático e integração com a tabela de símbolos.
import ply.yacc as yacc
import analisador_lexico as lexico
from analisador_lexico import tokens, lexer, find_column, estado
from tabela_simbolos import TabelaSimbolos

erros_sintaticos = []

# Tabela de símbolos global e escopo em que o parser se encontra
tabela_simbolos = TabelaSimbolos(nome='global', tipo='global')
escopo_atual = tabela_simbolos
_contador_relacoes = 0
_imports_pendentes = []# imports lidos antes do 'package' do arquivo


class ErroSintatico(Exception):
    """Interrompe a análise do arquivo atual no primeiro erro sintático."""


# Funções auxiliares
def resetar_escopo():
    """Volta ao escopo global (chamado antes de cada arquivo)."""
    global escopo_atual
    escopo_atual = tabela_simbolos
    _imports_pendentes.clear()

def inserir(chave, simbolo):
    simbolo['arquivo'] = estado['arquivo']
    escopo_atual.put(chave, simbolo)

def abrir_escopo(chave, simbolo, tipo_escopo):
    """Insere o símbolo no escopo atual e entra em um novo escopo filho."""
    global escopo_atual
    filho = escopo_atual.novo_escopo(chave, tipo_escopo)
    simbolo['escopo'] = filho
    inserir(chave, simbolo)
    escopo_atual = filho

def fechar_escopo():
    global escopo_atual
    if escopo_atual.prev is not None:
        escopo_atual = escopo_atual.prev

def inserir_relacao(nome, estereotipo, origem, tail, externa, linha):
    """Insere uma relação (interna ou externa). Relações sem nome recebem chave única."""
    global _contador_relacoes
    _contador_relacoes += 1
    chave = nome if nome else f"relation#{_contador_relacoes}"
    inserir(chave, {
        'categoria': 'relation', 'nome': nome, 'estereotipo': estereotipo,
        'origem': origem, 'alvo': tail['alvo'],
        'card_origem': tail['card_origem'], 'card_alvo': tail['card_alvo'],
        'simbolo': tail['simbolo'], 'externa': externa, 'linha': linha,
    })


# Gramática

def p_program(p):
    '''program : preamble package_section_list
               | package_section_list
               | empty'''


def p_preamble(p):
    '''preamble : preamble import_decl
                | import_decl'''


def p_import_decl(p):
    '''import_decl : IMPORT CLASS_NAME'''
    _imports_pendentes.append(p[2])


def p_package_section_list(p):
    '''package_section_list : package_section_list package_section
                            | package_section'''


def p_package_section(p):
    '''package_section : package_header statement_list
                       | package_header'''


def p_package_header(p):
    '''package_header : PACKAGE CLASS_NAME'''
    if escopo_atual.tipo == 'package':
        fechar_escopo()
    abrir_escopo(p[2], {'categoria': 'package', 'nome': p[2], 'linha': p.lineno(2)}, 'package')
    escopo_atual.imports.extend(_imports_pendentes)
    _imports_pendentes.clear()


def p_statement_list(p):
    '''statement_list : statement_list statement
                      | statement'''


def p_statement(p):
    '''statement : class_decl
                 | type_decl
                 | enum_decl
                 | genset_decl
                 | external_relation'''


# Listas de nomes de classes separados por vírgula
def p_class_list(p):
    '''class_list : class_list COMMA CLASS_NAME
                  | CLASS_NAME'''
    p[0] = p[1] + [p[3]] if len(p) == 4 else [p[1]]


# Classes:
def p_class_header(p):
    '''class_header : STEREOTYPE_CLASS CLASS_NAME opt_nature opt_specializes'''
    abrir_escopo(p[2], {'categoria': 'class', 'nome': p[2], 'estereotipo': p[1],
                        'natureza': p[3], 'especializa': p[4],
                        'linha': p.lineno(2)}, 'class')


def p_opt_nature(p):
    '''opt_nature : OF RESERVED_WORD
                  | empty'''
    p[0] = p[2] if len(p) == 3 else None


def p_opt_specializes(p):
    '''opt_specializes : SPECIALIZES class_list
                       | empty'''
    p[0] = p[2] if len(p) == 3 else []


def p_class_decl(p):
    '''class_decl : class_header class_body
                  | class_header'''
    fechar_escopo()


def p_class_body(p):
    '''class_body : LBRACE class_member_list RBRACE
                  | LBRACE RBRACE'''


def p_class_member_list(p):
    '''class_member_list : class_member_list class_member
                         | class_member'''


def p_class_member(p):
    '''class_member : attribute_decl
                    | internal_relation'''


# Atributos
def p_attribute_decl(p):
    '''attribute_decl : attr_name COLON type_ref opt_cardinality opt_meta'''
    inserir(p[1], {'categoria': 'attribute', 'nome': p[1], 'tipo_dado': p[3],
                   'cardinalidade': p[4], 'meta': p[5], 'linha': p.lineno(2)})


def p_attr_name(p):
    '''attr_name : RELATION_NAME
                 | NATIVE_TYPE'''
    p[0] = p[1]


def p_type_ref(p):
    '''type_ref : NATIVE_TYPE
                | CLASS_NAME
                | NEW_TYPE'''
    p[0] = p[1]


def p_opt_cardinality(p):
    '''opt_cardinality : cardinality
                       | empty'''
    p[0] = p[1]


def p_opt_meta(p):
    '''opt_meta : LBRACE meta_list RBRACE
                | empty'''
    p[0] = p[2] if len(p) == 4 else []


def p_meta_list(p):
    '''meta_list : meta_list COMMA meta_item
                 | meta_item'''
    p[0] = p[1] + [p[3]] if len(p) == 4 else [p[1]]


def p_meta_item(p):
    '''meta_item : META_ATTRIBUTE
                 | META_ATTRIBUTE RELATION_NAME'''
    p[0] = p[1] if len(p) == 2 else f"{p[1]} {p[2]}"


# Cardinalidades
def p_cardinality(p):
    '''cardinality : LBRACKET bound RBRACKET
                   | LBRACKET bound RANGE bound RBRACKET'''
    p[0] = p[2] if len(p) == 4 else f"{p[2]}..{p[4]}"


def p_bound(p):
    '''bound : NUMBER
             | STAR'''
    p[0] = str(p[1])


# Relações
def p_rel_symbol(p):
    '''rel_symbol : REL_PLAIN
                  | REL_BI_DIR
                  | REL_UNI_DIR'''
    p[0] = p[1]


def p_rel_core(p):
    '''rel_core : rel_symbol cardinality CLASS_NAME
                | rel_symbol RELATION_NAME rel_symbol cardinality CLASS_NAME'''
    if len(p) == 4:
        p[0] = {'nome': None, 'card_origem': None, 'simbolo': p[1],
                'card_alvo': p[2], 'alvo': p[3]}
    else:
        p[0] = {'nome': p[2], 'card_origem': None, 'simbolo': p[1],
                'card_alvo': p[4], 'alvo': p[5]}


def p_rel_tail(p):
    '''rel_tail : cardinality rel_core
                | rel_core'''
    if len(p) == 3:
        p[2]['card_origem'] = p[1]
        p[0] = p[2]
    else:
        p[0] = p[1]


# Relação interna (dentro de classe):
def p_internal_relation(p):
    '''internal_relation : AT STEREOTYPE_RELATION rel_tail
                         | rel_core'''
    origem = getattr(escopo_atual, 'nome', None)
    if len(p) == 4:
        inserir_relacao(p[3]['nome'], p[2], origem, p[3], False, p.lineno(2))
    else:
        inserir_relacao(p[1]['nome'], None, origem, p[1], False, p.lexer.lineno)


# Relação externa:
def p_external_relation(p):
    '''external_relation : AT STEREOTYPE_RELATION RELATION CLASS_NAME rel_tail
                         | RELATION CLASS_NAME rel_tail'''
    if len(p) == 6:
        est, origem, tail, linha = p[2], p[4], p[5], p.lineno(4)
    else:
        est, origem, tail, linha = None, p[2], p[3], p.lineno(2)
    inserir_relacao(tail['nome'], est, origem, tail, True, linha)


# Tipos de dados: datatype
def p_datatype_header(p):
    '''datatype_header : DATATYPE CLASS_NAME
                       | DATATYPE NEW_TYPE'''
    abrir_escopo(p[2], {'categoria': 'type', 'nome': p[2], 'linha': p.lineno(2)}, 'type')


def p_type_decl(p):
    '''type_decl : datatype_header datatype_body
                 | datatype_header'''
    fechar_escopo()


def p_datatype_body(p):
    '''datatype_body : LBRACE attribute_list RBRACE
                     | LBRACE RBRACE'''


def p_attribute_list(p):
    '''attribute_list : attribute_list attribute_decl
                      | attribute_decl'''


def p_type_decl_simples(p):
    '''type_decl : NEW_TYPE'''
    filho = escopo_atual.novo_escopo(p[1], 'type')
    inserir(p[1], {'categoria': 'type', 'nome': p[1], 'linha': p.lineno(1), 'escopo': filho})


# Classes enumeradas
def p_instance_list(p):
    '''instance_list : instance_list COMMA instance_item
                     | instance_item'''
    p[0] = p[1] + [p[3]] if len(p) == 4 else [p[1]]


def p_instance_item(p):
    '''instance_item : INSTANCE_NAME
                     | CLASS_NAME'''
    p[0] = p[1]


def p_enum_decl(p):
    '''enum_decl : ENUM CLASS_NAME LBRACE instance_list RBRACE'''
    filho = escopo_atual.novo_escopo(p[2], 'enum')
    inserir(p[2], {'categoria': 'enum', 'nome': p[2], 'linha': p.lineno(2), 'escopo': filho})
    for v in p[4]:
        filho.put(v, {'categoria': 'instance', 'nome': v, 'linha': p.lineno(2),
                      'arquivo': estado['arquivo']})


# Generalizações
def p_genset_mods(p):
    '''genset_mods : genset_mods GENSET_MOD
                   | GENSET_MOD'''
    p[0] = p[1] + [p[2]] if len(p) == 3 else [p[1]]


def p_genset_head(p):
    '''genset_head : GENSET CLASS_NAME
                   | genset_mods GENSET CLASS_NAME'''
    if len(p) == 3:
        p[0] = ([], p[2], p.lineno(2))
    else:
        p[0] = (p[1], p[3], p.lineno(3))


def p_genset_decl(p):
    '''genset_decl : genset_head WHERE class_list SPECIALIZES CLASS_NAME
                   | genset_head LBRACE GENERAL CLASS_NAME SPECIFICS class_list RBRACE'''
    restricoes, nome, linha = p[1]
    if len(p) == 6:
        geral, especificos, forma = p[5], p[3], 'where'
    else:
        geral, especificos, forma = p[4], p[6], 'bloco'
    # chave com prefixo para não colidir com a classe de mesmo nome
    inserir(f"genset:{nome}", {'categoria': 'genset', 'nome': nome, 'geral': geral,
                               'especificos': especificos, 'restricoes': restricoes,
                               'forma': forma, 'linha': linha})


def p_empty(p):
    '''empty :'''
    p[0] = None


# Tratamento de erros
NOMES_TOKENS = {
    'LBRACE': "'{'", 'RBRACE': "'}'", 'LBRACKET': "'['", 'RBRACKET': "']'",
    'COMMA': "','", 'COLON': "':'", 'RANGE': "'..'", 'STAR': "'*'", 'AT': "'@'",
    'REL_BI_DIR': "'<>--'", 'REL_UNI_DIR': "'--<>'", 'REL_PLAIN': "'--'",
    'LPAREN': "'('", 'RPAREN': "')'",
    'CLASS_NAME': 'um nome de classe (maiúscula inicial)',
    'RELATION_NAME': 'um nome de atributo/relação (minúscula inicial)',
    'INSTANCE_NAME': 'um nome de instância (termina em número)',
    'NEW_TYPE': 'um tipo terminado em DataType', 'RESERVED_WORD': "'functional-complexes'",
    'NUMBER': 'um número', 'NATIVE_TYPE': 'um tipo nativo',
    'STEREOTYPE_CLASS': 'um estereótipo de classe',
    'STEREOTYPE_RELATION': 'um estereótipo de relação',
    'GENSET_MOD': 'disjoint/overlapping/complete/incomplete',
    'META_ATTRIBUTE': 'um meta-atributo', '$end': 'fim do arquivo',
    'PACKAGE': "'package'", 'IMPORT': "'import'", 'DATATYPE': "'datatype'",
    'ENUM': "'enum'", 'RELATION': "'relation'", 'GENSET': "'genset'",
    'SPECIALIZES': "'specializes'", 'WHERE': "'where'", 'GENERAL': "'general'",
    'SPECIFICS': "'specifics'", 'OF': "'of'",
}


def _esperados():
    """Tokens que o parser aceitaria no estado em que o erro ocorreu."""
    try:
        acoes = parser.action[parser.statestack[-1]]
        return sorted({NOMES_TOKENS.get(t, t) for t in acoes})
    except Exception:
        return []


def p_error(p):
    esperados = _esperados()
    dica = f" Esperado: {', '.join(esperados)}." if esperados else ""
    if p:
        linha, coluna = p.lineno, find_column(p)
        msg = f"token inesperado '{p.value}' (tipo: {p.type})"
        if escopo_atual is tabela_simbolos and p.type not in ('PACKAGE', 'IMPORT'):
            sugestao = ("Todo modelo Tonto deve ter uma declaração de pacote "
                        "(package Nome), opcionalmente precedida por imports.")
        else:
            sugestao = ("Verifique se a declaração está de acordo com a sintaxe Tonto "
                        "(vírgulas em listas, cardinalidades entre colchetes, "
                        "símbolos '--', '<>--' ou '--<>' nas relações)." + dica)
        if any(e['arquivo'] == estado['arquivo'] and e['linha'] == linha
               for e in lexico.erros_lexicos):
            sugestao = ("Provável consequência de um erro léxico nesta mesma linha; "
                        "corrija-o primeiro. ") + sugestao
    else:
        linha, coluna = lexer.lineno, None
        msg = "fim inesperado do arquivo (EOF)"
        sugestao = "Verifique se faltou alguma chave '}' de fechamento." + dica

    erros_sintaticos.append({
        'arquivo': estado['arquivo'], 'linha': linha, 'coluna': coluna,
        'mensagem': msg, 'sugestao': sugestao,
    })
    raise ErroSintatico(msg)


# Inicialização do parser (sem cache de tabelas, para nunca usar parsetab desatualizado)
parser = yacc.yacc(debug=False, write_tables=False)