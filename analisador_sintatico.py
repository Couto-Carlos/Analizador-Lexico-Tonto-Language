# analisador_sintatico.py
import ply.yacc as yacc
from analisador_lexico import tokens, lexer
from tabela_simbolos import TabelaSimbolos

# Instancia a tabela de símbolos global do compilador
tabela_simbolos = TabelaSimbolos()
erros_sintaticos = []

# --- Regras da Gramática (CFG) ---

def p_program(p):
    '''program : statement_list
               | empty'''
    p[0] = p[1]

def p_statement_list(p):
    '''statement_list : statement_list statement
                      | statement'''
    if len(p) == 3:
        p[0] = (p[1] if isinstance(p[1], list) else [p[1]]) + [p[2]]
    else:
        p[0] = [p[1]]

def p_statement(p):
    '''statement : keyword_statement
                 | class_decl
                 | relation_decl
                 | type_decl'''
    p[0] = p[1]

# Regra unificada para palavras reservadas
def p_keyword_statement(p):
    '''keyword_statement : RESERVED_WORD CLASS_NAME LBRACE statement_list RBRACE
                         | RESERVED_WORD CLASS_NAME LBRACE RBRACE
                         | RESERVED_WORD CLASS_NAME COLON class_list_genset
                         | RESERVED_WORD CLASS_NAME
                         | RESERVED_WORD RELATION_NAME'''
    
    keyword = p[1]
    name = p[2]

    if keyword == 'package':
        tabela_simbolos.definir_pacote(name)
        corpo = p[4] if len(p) == 6 else []
        p[0] = ('package', name, corpo)
    elif keyword == 'import':
        p[0] = ('import', name)
    elif keyword == 'genset':
        elementos = p[4] if len(p) == 5 else []
        tabela_simbolos.inserir('gensets', name, {'elementos': elementos})
        p[0] = ('genset', name, elementos)
    else:
        p[0] = ('reserved_stmt', keyword, name)

# Declaração de Classes
def p_class_decl(p):
    '''class_decl : STEREOTYPE_CLASS CLASS_NAME class_body
                  | CLASS_NAME class_body
                  | STEREOTYPE_CLASS CLASS_NAME
                  | CLASS_NAME'''
    if len(p) == 4:
        st, nome, corpo = p[1], p[2], p[3]
        tabela_simbolos.inserir('classes', nome, {'stereotype': st, 'corpo': corpo})
        p[0] = ('class', st, nome)
    elif len(p) == 3:
        if p.slice[1].type == 'STEREOTYPE_CLASS':
            st, nome = p[1], p[2]
            tabela_simbolos.inserir('classes', nome, {'stereotype': st, 'corpo': []})
            p[0] = ('class', st, nome)
        else:
            nome, corpo = p[1], p[2]
            tabela_simbolos.inserir('classes', nome, {'stereotype': None, 'corpo': corpo})
            p[0] = ('class', None, nome)
    else:
        nome = p[1]
        tabela_simbolos.inserir('classes', nome, {'stereotype': None, 'corpo': []})
        p[0] = ('class', None, nome)

def p_class_body(p):
    '''class_body : LBRACE class_member_list RBRACE
                  | LBRACE RBRACE'''
    p[0] = p[2] if len(p) == 4 else []

def p_class_member_list(p):
    '''class_member_list : class_member_list class_member
                         | class_member'''
    if len(p) == 3:
        p[0] = (p[1] if isinstance(p[1], list) else [p[1]]) + [p[2]]
    else:
        p[0] = [p[1]]

def p_class_member(p):
    '''class_member : attribute_decl
                    | relation_decl'''
    p[0] = p[1]

# Atributos e Fins de Associação internos às classes
def p_attribute_decl(p):
    '''attribute_decl : RELATION_NAME COLON NATIVE_TYPE LBRACKET NUMBER RANGE cardinality_bound RBRACKET
                      | RELATION_NAME COLON CLASS_NAME LBRACKET NUMBER RANGE cardinality_bound RBRACKET
                      | RELATION_NAME COLON NATIVE_TYPE
                      | RELATION_NAME COLON NEW_TYPE'''
    tipo_alvo = p[3]
    tabela_simbolos.inserir('relations', p[1], {'tipo': 'atributo', 'tipo_dado': tipo_alvo})
    p[0] = ('attribute', p[1], tipo_alvo)

# Declaração de Relações Globais ou com Estereótipos
def p_relation_decl(p):
    '''relation_decl : STEREOTYPE_RELATION RELATION_NAME class_body
                     | STEREOTYPE_RELATION CLASS_NAME class_body
                     | STEREOTYPE_RELATION RELATION_NAME LBRACKET NUMBER RANGE cardinality_bound RBRACKET COLON CLASS_NAME
                     | STEREOTYPE_RELATION RELATION_NAME COLON CLASS_NAME
                     | RELATION_NAME COLON CLASS_NAME'''
    if len(p) == 4 and isinstance(p[3], list):
        st, rel, corpo = p[1], p[2], p[3]
        tabela_simbolos.inserir('relations', rel, {'stereotype': st, 'corpo': corpo})
        p[0] = ('relation_body', st, rel, corpo)
    elif len(p) == 10:
        st, rel, alvo = p[1], p[2], p[9]
        tabela_simbolos.inserir('relations', rel, {'stereotype': st, 'alvo': alvo})
        p[0] = ('relation', st, rel, alvo)
    elif len(p) == 5:
        st, rel, alvo = p[1], p[2], p[4]
        tabela_simbolos.inserir('relations', rel, {'stereotype': st, 'alvo': alvo})
        p[0] = ('relation', st, rel, alvo)
    elif len(p) == 4:
        rel, alvo = p[1], p[3]
        tabela_simbolos.inserir('relations', rel, {'stereotype': None, 'alvo': alvo})
        p[0] = ('relation', None, rel, alvo)

def p_cardinality_bound(p):
    '''cardinality_bound : NUMBER
                         | STAR'''
    p[0] = p[1]

def p_class_list_genset(p):
    '''class_list_genset : class_list_genset CLASS_NAME
                         | CLASS_NAME'''
    if len(p) == 3:
        p[0] = (p[1] if isinstance(p[1], list) else [p[1]]) + [p[2]]
    else:
        p[0] = [p[1]]

# Novos Tipos de Dados
def p_type_decl(p):
    '''type_decl : NEW_TYPE'''
    tabela_simbolos.inserir('types', p[1], {'base': 'custom'})
    p[0] = ('new_type', p[1])

def p_empty(p):
    '''empty :'''
    pass

# Tratamento de Erros Sintáticos
def p_error(p):
    if p:
        msg = f"Erro sintático na linha {p.lineno}, posição {p.lexpos}: token inesperado '{p.value}' (tipo: {p.type})"
        sugestao = "Verifique se a estrutura da classe, pacote ou relação está correta de acordo com a especificação da linguagem TONTO."
    else:
        msg = "Erro sintático: Fim inesperado do arquivo (EOF)."
        sugestao = "Verifique se faltaram chaves '}' de fechamento ou ponto e vírgula."
    
    erros_sintaticos.append({'mensagem': msg, 'sugestao': sugestao})
    print(f"ERRO SINTÁTICO: {msg} -> Sugestão: {sugestao}")

# Constrói o parser
parser = yacc.yacc()