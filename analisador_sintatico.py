# analisador_sintatico.py
import ply.yacc as yacc
from analisador_lexico import tokens, lexer
from tabela_simbolos import TabelaSimbolos

tabela_simbolos = TabelaSimbolos()
erros_sintaticos = []

class ErroSintatico(Exception):
    pass

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
    '''statement : package_decl
                 | import_decl
                 | datatype_decl
                 | enum_decl
                 | genset_decl
                 | class_decl
                 | relation_decl
                 | annotated_relation_decl
                 | type_decl'''
    p[0] = p[1]

def p_package_decl(p):
    '''package_decl : PACKAGE_KW CLASS_NAME LBRACE statement_list RBRACE
                    | PACKAGE_KW CLASS_NAME LBRACE RBRACE
                    | PACKAGE_KW CLASS_NAME'''
    nome = p[2]
    linha = p.lineno(1)
    tabela_simbolos.definir_pacote(nome, linha=linha)
    corpo = p[4] if len(p) == 6 else []
    p[0] = ('package', nome, corpo)

def p_import_decl(p):
    '''import_decl : IMPORT_KW CLASS_NAME'''
    p[0] = ('import', p[2])

def p_datatype_decl(p):
    '''datatype_decl : DATATYPE_KW CLASS_NAME LBRACE attr_or_member_list RBRACE
                     | DATATYPE_KW CLASS_NAME LBRACE RBRACE'''
    nome = p[2]
    linha = p.lineno(1)
    campos = p[4] if len(p) == 6 else []
    tabela_simbolos.inserir('types', nome, {'kind': 'datatype', 'campos': campos}, linha=linha)
    p[0] = ('datatype', nome, campos)

def p_enum_decl(p):
    '''enum_decl : ENUM_KW CLASS_NAME LBRACE enum_item_list RBRACE
                 | ENUM_KW CLASS_NAME LBRACE RBRACE'''
    nome = p[2]
    linha = p.lineno(1)
    itens = p[4] if len(p) == 6 else []
    tabela_simbolos.inserir('types', nome, {'kind': 'enum', 'itens': itens}, linha=linha)
    p[0] = ('enum', nome, itens)

def p_enum_item_list(p):
    '''enum_item_list : enum_item_list enum_item
                      | enum_item'''
    if len(p) == 3:
        p[0] = (p[1] if isinstance(p[1], list) else [p[1]]) + [p[2]]
    else:
        p[0] = [p[1]]

def p_enum_item(p):
    '''enum_item : CLASS_NAME
                 | INSTANCE_NAME
                 | RELATION_NAME'''
    p[0] = p[1]

def p_genset_decl(p):
    '''genset_decl : genset_mods GENSET_KW CLASS_NAME LBRACE genset_body_items RBRACE
                   | GENSET_KW CLASS_NAME LBRACE genset_body_items RBRACE
                   | genset_mods GENSET_KW CLASS_NAME WHERE_KW class_name_list SPECIALIZES class_name_list
                   | GENSET_KW CLASS_NAME WHERE_KW class_name_list SPECIALIZES class_name_list'''
    if p.slice[1].type == 'genset_mods':
        mods = p[1]
        nome = p[3]
        linha = p.lineno(2)
        elementos = p[5] if p[4] == '{' else (p[5] + p[7])
    else:
        mods = []
        nome = p[2]
        linha = p.lineno(1)
        elementos = p[4] if p[3] == '{' else (p[4] + p[6])

    tabela_simbolos.inserir(
        'gensets',
        nome,
        {'elementos': elementos, 'modificadores': mods},
        linha=linha
    )
    p[0] = ('genset', nome, elementos, mods)

def p_genset_mods(p):
    '''genset_mods : GENSET_MOD GENSET_MOD
                   | GENSET_MOD'''
    p[0] = [p[1], p[2]] if len(p) == 3 else [p[1]]

def p_genset_body_items(p):
    '''genset_body_items : genset_body_items genset_body_item
                         | genset_body_item'''
    if len(p) == 3:
        prev = p[1] if isinstance(p[1], list) else [p[1]]
        p[0] = prev + (p[2] if isinstance(p[2], list) else [p[2]])
    else:
        p[0] = p[1] if isinstance(p[1], list) else [p[1]]

def p_genset_body_item(p):
    '''genset_body_item : GENERAL_KW CLASS_NAME
                        | SPECIFICS_KW class_name_list'''
    p[0] = p[2] if isinstance(p[2], list) else [p[2]]

def p_class_name_list(p):
    '''class_name_list : class_name_list CLASS_NAME
                       | CLASS_NAME'''
    if len(p) == 3:
        p[0] = (p[1] if isinstance(p[1], list) else [p[1]]) + [p[2]]
    else:
        p[0] = [p[1]]

def p_of_opt(p):
    '''of_opt : OF_KW RESERVED_WORD
              | OF_KW RELATION_NAME
              | empty'''
    pass

def p_specializes_opt(p):
    '''specializes_opt : SPECIALIZES class_name_list
                       | empty'''
    p[0] = p[2] if len(p) == 3 else []

def p_class_decl(p):
    '''class_decl : STEREOTYPE_CLASS CLASS_NAME of_opt specializes_opt class_body
                  | STEREOTYPE_CLASS CLASS_NAME of_opt specializes_opt
                  | CLASS_NAME of_opt specializes_opt class_body
                  | CLASS_NAME of_opt specializes_opt'''
    if p.slice[1].type == 'STEREOTYPE_CLASS':
        st = p[1]
        nome = p[2]
        linha = p.lineno(1)
        bases = p[4]
        corpo = p[5] if len(p) == 6 else []
    else:
        st = None
        nome = p[1]
        linha = p.lineno(1)
        bases = p[3]
        corpo = p[4] if len(p) == 5 else []

    tabela_simbolos.inserir('classes', nome, {
        'stereotype': st,
        'bases': bases,
        'base': bases[0] if bases else None,
        'corpo': corpo
    }, linha=linha)
    p[0] = ('class', st, nome, bases, corpo)

def p_class_body(p):
    '''class_body : LBRACE attr_or_member_list RBRACE
                  | LBRACE RBRACE'''
    p[0] = p[2] if len(p) == 4 else []

def p_attr_or_member_list(p):
    '''attr_or_member_list : attr_or_member_list class_member
                           | class_member'''
    if len(p) == 3:
        p[0] = (p[1] if isinstance(p[1], list) else [p[1]]) + [p[2]]
    else:
        p[0] = [p[1]]

def p_class_member(p):
    '''class_member : attribute_decl
                    | relation_decl
                    | annotation_member
                    | association_continuation'''
    p[0] = p[1]

def p_association_continuation(p):
    '''association_continuation : ASSOCIATION_LINE RELATION_NAME ASSOCIATION_LINE card_opt CLASS_NAME
                                | ASSOCIATION_LINE card_opt CLASS_NAME'''
    p[0] = ('assoc_cont', p[2] if len(p) == 6 else p[3])

def p_meta_attrs_opt(p):
    '''meta_attrs_opt : LBRACE meta_attr_list RBRACE
                      | empty'''
    pass

def p_meta_attr_list(p):
    '''meta_attr_list : meta_attr_list META_ATTRIBUTE
                      | META_ATTRIBUTE'''
    pass

def p_attribute_decl(p):
    '''attribute_decl : RELATION_NAME COLON NATIVE_TYPE card_opt meta_attrs_opt
                      | RELATION_NAME COLON CLASS_NAME card_opt meta_attrs_opt
                      | RELATION_NAME COLON NEW_TYPE card_opt meta_attrs_opt
                      | NATIVE_TYPE COLON NATIVE_TYPE card_opt meta_attrs_opt
                      | NATIVE_TYPE COLON CLASS_NAME card_opt meta_attrs_opt
                      | NATIVE_TYPE COLON NEW_TYPE card_opt meta_attrs_opt'''
    nome_attr = p[1]
    tipo_alvo = p[3]
    linha = p.lineno(1)
    tabela_simbolos.inserir('relations', nome_attr, {
        'tipo': 'atributo',
        'tipo_dado': tipo_alvo
    }, linha=linha)
    p[0] = ('attribute', nome_attr, tipo_alvo)

def p_annotation_member(p):
    '''annotation_member : AT STEREOTYPE_RELATION ASSOCIATION_LINE RELATION_NAME ASSOCIATION_LINE card_opt CLASS_NAME
                         | AT STEREOTYPE_RELATION card_opt REL_BI_DIR card_opt CLASS_NAME
                         | AT STEREOTYPE_RELATION card_opt REL_UNI_DIR card_opt CLASS_NAME
                         | AT STEREOTYPE_RELATION card_opt ASSOCIATION_LINE card_opt CLASS_NAME
                         | AT STEREOTYPE_RELATION card_opt CLASS_NAME
                         | AT STEREOTYPE_RELATION
                         | AT RELATION_NAME ASSOCIATION_LINE RELATION_NAME ASSOCIATION_LINE card_opt CLASS_NAME
                         | AT RELATION_NAME card_opt REL_BI_DIR card_opt CLASS_NAME
                         | AT RELATION_NAME card_opt REL_UNI_DIR card_opt CLASS_NAME
                         | AT RELATION_NAME card_opt ASSOCIATION_LINE card_opt CLASS_NAME
                         | AT RELATION_NAME card_opt CLASS_NAME
                         | AT RELATION_NAME'''
    p[0] = ('annotation', p[2])

def p_card_opt(p):
    '''card_opt : LBRACKET cardinality_content RBRACKET
                | empty'''
    pass

def p_cardinality_content(p):
    '''cardinality_content : NUMBER RANGE cardinality_bound
                           | NUMBER
                           | STAR'''
    pass

def p_cardinality_bound(p):
    '''cardinality_bound : NUMBER
                         | STAR'''
    p[0] = p[1]

def p_relation_decl(p):
    '''relation_decl : RELATION_KW CLASS_NAME card_opt ASSOCIATION_LINE card_opt CLASS_NAME
                     | RELATION_KW CLASS_NAME card_opt ASSOCIATION_LINE RELATION_NAME ASSOCIATION_LINE card_opt CLASS_NAME
                     | RELATION_KW CLASS_NAME card_opt REL_BI_DIR card_opt CLASS_NAME
                     | RELATION_KW CLASS_NAME card_opt REL_UNI_DIR card_opt CLASS_NAME
                     | STEREOTYPE_RELATION RELATION_NAME class_body
                     | STEREOTYPE_RELATION CLASS_NAME class_body
                     | STEREOTYPE_RELATION RELATION_NAME COLON CLASS_NAME
                     | RELATION_NAME COLON CLASS_NAME'''
    if p[1] == 'relation':
        rel_nome = p[5] if len(p) == 9 else f"rel_{p[2]}_{p[len(p)-1]}"
        tabela_simbolos.inserir('relations', rel_nome, {
            'stereotype': None,
            'alvo': p[len(p)-1]
        }, linha=p.lineno(1))
        p[0] = ('relation', None, rel_nome)
    elif len(p) == 4 and isinstance(p[3], list):
        st, rel, corpo = p[1], p[2], p[3]
        tabela_simbolos.inserir('relations', rel, {
            'stereotype': st,
            'corpo': corpo
        }, linha=p.lineno(1))
        p[0] = ('relation_body', st, rel, corpo)
    elif len(p) == 4:
        rel, alvo = p[1], p[3]
        tabela_simbolos.inserir('relations', rel, {
            'stereotype': None,
            'alvo': alvo
        }, linha=p.lineno(1))
        p[0] = ('relation', None, rel, alvo)
    else:
        p[0] = ('relation_complex', p[1], p[2])

def p_annotated_relation_decl(p):
    '''annotated_relation_decl : AT STEREOTYPE_RELATION RELATION_KW CLASS_NAME card_opt ASSOCIATION_LINE RELATION_NAME ASSOCIATION_LINE card_opt CLASS_NAME
                               | AT STEREOTYPE_RELATION RELATION_KW CLASS_NAME card_opt ASSOCIATION_LINE card_opt CLASS_NAME
                               | AT STEREOTYPE_RELATION RELATION_KW CLASS_NAME card_opt REL_BI_DIR card_opt CLASS_NAME
                               | AT STEREOTYPE_RELATION RELATION_KW CLASS_NAME card_opt REL_UNI_DIR card_opt CLASS_NAME'''
    st = p[2]
    rel_nome = p[7] if len(p) == 11 else f"{st}_{p[4]}_{p[len(p)-1]}"
    tabela_simbolos.inserir('relations', rel_nome, {
        'stereotype': st
    }, linha=p.lineno(1))
    p[0] = ('annotated_relation', st, rel_nome)

def p_type_decl(p):
    '''type_decl : NEW_TYPE'''
    tabela_simbolos.inserir('types', p[1], {'base': 'custom'}, linha=p.lineno(1))
    p[0] = ('new_type', p[1])

def p_empty(p):
    '''empty :'''
    pass

def p_error(p):
    if p:
        msg = f"Erro sintático na linha {p.lineno}, posição {p.lexpos}: token inesperado '{p.value}' (tipo: {p.type})"
        sugestao = "Verifique se a estrutura da classe, pacote, tipo ou relação está correta de acordo com a linguagem TONTO."
    else:
        msg = "Erro sintático: Fim inesperado do arquivo (EOF)."
        sugestao = "Verifique se faltaram chaves '}' de fechamento."

    erros_sintaticos.append({'mensagem': msg, 'sugestao': sugestao})
    raise ErroSintatico(msg)

parser = yacc.yacc()