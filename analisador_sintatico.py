# analisador_sintatico.py
# Analisador sintático e integração com a tabela de símbolos.
import ply.yacc as yacc
from analisador_lexico import tokens, lexer, find_column, estado
from tabela_simbolos import TabelaSimbolos

erros_sintaticos = []

# Tabela de símbolos global e escopo em que o parser se encontra
tabela_simbolos = TabelaSimbolos(nome='global', tipo='global')
escopo_atual = tabela_simbolos

class ErroSintatico(Exception):
    """Interrompe a análise do arquivo atual no primeiro erro sintático."""

# Funções auxiliares
def resetar_escopo():
    """Volta ao escopo global (chamado antes de cada arquivo)."""
    global escopo_atual
    escopo_atual = tabela_simbolos

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

# Gramática

def p_program(p):
    '''program : statement_list
               | empty'''

def p_statement_list(p):
    '''statement_list : statement_list statement
                      | statement'''

def p_statement(p):
    '''statement : package_decl
                 | import_decl
                 | genset_decl
                 | reserved_stmt
                 | class_decl
                 | relation_decl
                 | type_decl
                 | enum_decl'''

# Pacotes: package Nome { ... }
def p_package_header(p):
    '''package_header : PACKAGE CLASS_NAME LBRACE'''
    abrir_escopo(p[2], {'categoria': 'package', 'nome': p[2], 'linha': p.lineno(2)}, 'package')

def p_package_decl(p):
    '''package_decl : package_header statement_list RBRACE
                    | package_header RBRACE'''
    fechar_escopo()

# Importação: import Nome
def p_import_decl(p):
    '''import_decl : IMPORT CLASS_NAME'''
    escopo_atual.imports.append(p[2])

# Generalização: genset Geral: Especifica1 Especifica2
def p_genset_decl(p):
    '''genset_decl : GENSET CLASS_NAME COLON class_list_genset
                   | GENSET CLASS_NAME'''
    especificos = p[4] if len(p) == 5 else []
    # chave com prefixo para não colidir com a classe de mesmo nome
    inserir(f"genset:{p[2]}", {'categoria': 'genset', 'nome': p[2], 'geral': p[2],
                               'especificos': especificos, 'linha': p.lineno(2)})

def p_class_list_genset(p):
    '''class_list_genset : class_list_genset CLASS_NAME
                         | CLASS_NAME'''
    p[0] = p[1] + [p[2]] if len(p) == 3 else [p[1]]

# Outras palavras reservadas soltas (aceitas, sem efeito na tabela)
def p_reserved_stmt(p):
    '''reserved_stmt : RESERVED_WORD CLASS_NAME
                     | RESERVED_WORD RELATION_NAME'''

# Classes (estereótipo obrigatório)
def p_class_header(p):
    '''class_header : STEREOTYPE_CLASS CLASS_NAME'''
    abrir_escopo(p[2], {'categoria': 'class', 'nome': p[2], 'estereotipo': p[1],
                        'linha': p.lineno(2)}, 'class')

def p_class_decl(p):
    '''class_decl : class_header class_body
                  | class_header'''
    fechar_escopo()

# Classes enumeradas: enum Cor { Vermelho1 Verde2 }
def p_enum_decl(p):
    '''enum_decl : ENUM CLASS_NAME LBRACE instance_list RBRACE'''
    filho = escopo_atual.novo_escopo(p[2], 'enum')
    inserir(p[2], {'categoria': 'enum', 'nome': p[2], 'linha': p.lineno(2), 'escopo': filho})
    for v in p[4]:
        filho.put(v, {'categoria': 'instance', 'nome': v, 'linha': p.lineno(2),
                      'arquivo': estado['arquivo']})

def p_instance_list(p):
    '''instance_list : instance_list INSTANCE_NAME
                     | INSTANCE_NAME'''
    p[0] = p[1] + [p[2]] if len(p) == 3 else [p[1]]

def p_class_body(p):
    '''class_body : LBRACE class_member_list RBRACE
                  | LBRACE RBRACE'''

def p_class_member_list(p):
    '''class_member_list : class_member_list class_member
                         | class_member'''

def p_class_member(p):
    '''class_member : attribute_decl
                    | relation_decl'''

# Atributos
def p_attribute_decl(p):
    '''attribute_decl : RELATION_NAME COLON NATIVE_TYPE LBRACKET NUMBER RANGE cardinality_bound RBRACKET
                      | RELATION_NAME COLON NATIVE_TYPE
                      | RELATION_NAME COLON NEW_TYPE'''
    inserir(p[1], {'categoria': 'attribute', 'nome': p[1], 'tipo_dado': p[3],
                   'linha': p.lineno(1)})

# Relações de cardinalidade
def p_relation_decl_card(p):
    '''relation_decl : RELATION_NAME COLON CLASS_NAME LBRACKET NUMBER RANGE cardinality_bound RBRACKET'''
    inserir(p[1], {'categoria': 'relation', 'nome': p[1], 'estereotipo': None,
                   'alvo': p[3], 'cardinalidade': f"{p[5]}..{p[7]}",
                   'externa': _externa(), 'linha': p.lineno(1)})
# Relações com corpo: material Nome { ... }
def _externa():
    """True fora de classes, False dentro de classe, None nas extremidades de uma relação."""
    if escopo_atual.tipo in ('global', 'package'):
        return True
    if escopo_atual.tipo == 'class':
        return False
    return None

def p_relation_header(p):
    '''relation_header : STEREOTYPE_RELATION RELATION_NAME
                       | STEREOTYPE_RELATION CLASS_NAME'''
    abrir_escopo(p[2], {'categoria': 'relation', 'nome': p[2], 'estereotipo': p[1],
                        'externa': _externa(), 'linha': p.lineno(2)}, 'relation')

def p_relation_decl_corpo(p):
    '''relation_decl : relation_header class_body'''
    fechar_escopo()

# Relações simples (dentro ou fora de classes)
def p_relation_decl(p):
    '''relation_decl : STEREOTYPE_RELATION RELATION_NAME LBRACKET NUMBER RANGE cardinality_bound RBRACKET COLON CLASS_NAME
                     | STEREOTYPE_RELATION RELATION_NAME COLON CLASS_NAME
                     | RELATION_NAME COLON CLASS_NAME'''
    if len(p) == 10:
        est, nome, alvo = p[1], p[2], p[9]
    elif len(p) == 5:
        est, nome, alvo = p[1], p[2], p[4]
    else:
        est, nome, alvo = None, p[1], p[3]
    inserir(nome, {'categoria': 'relation', 'nome': nome, 'estereotipo': est,
                   'alvo': alvo, 'externa': _externa(), 'linha': p.lineno(1)})

def p_cardinality_bound(p):
    '''cardinality_bound : NUMBER
                         | STAR'''
    p[0] = p[1]

# Novos Tipos de Dados
def p_type_decl(p):
    '''type_decl : NEW_TYPE'''
    inserir(p[1], {'categoria': 'type', 'nome': p[1], 'linha': p.lineno(1)})

def p_empty(p):
    '''empty :'''
    pass

# Tratamento de erros
def p_error(p):
    if p:
        linha, coluna = p.lineno, find_column(p)
        msg = f"token inesperado '{p.value}' (tipo: {p.type})"
        sugestao = ("Verifique se a estrutura da classe, pacote, relação ou genset "
                    "está de acordo com a gramática da linguagem TONTO.")
    else:
        linha, coluna = lexer.lineno, None
        msg = "fim inesperado do arquivo (EOF)"
        sugestao = "Verifique se faltou alguma chave '}' de fechamento."

    erros_sintaticos.append({
        'arquivo': estado['arquivo'], 'linha': linha, 'coluna': coluna,
        'mensagem': msg, 'sugestao': sugestao,
    })
    raise ErroSintatico(msg)

# Inicialização do parser
parser = yacc.yacc()