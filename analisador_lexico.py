import ply.lex as lex

# --- Dicionário de Palavras Reservadas e Estereótipos ---
# (O dicionário 'reserved' continua o mesmo)
reserved = {
    # Estereótipos de Classe
    'event': 'STEREOTYPE_CLASS', 
    'situation': 'STEREOTYPE_CLASS', 
    'process': 'STEREOTYPE_CLASS', 
    'category': 'STEREOTYPE_CLASS', 
    'mixin': 'STEREOTYPE_CLASS', 
    'phaseMixin': 'STEREOTYPE_CLASS', 
    'roleMixin': 'STEREOTYPE_CLASS', 
    'historicalRoleMixin': 'STEREOTYPE_CLASS', 
    'kind': 'STEREOTYPE_CLASS', 
    'collective': 'STEREOTYPE_CLASS', 
    'quantity': 'STEREOTYPE_CLASS', 
    'quality': 'STEREOTYPE_CLASS', 
    'mode': 'STEREOTYPE_CLASS', 
    'intrisicMode': 'STEREOTYPE_CLASS', 
    'extrinsicMode': 'STEREOTYPE_CLASS', 
    'subkind': 'STEREOTYPE_CLASS', 'phase': 
    'STEREOTYPE_CLASS', 
    'role': 'STEREOTYPE_CLASS', 
    'historicalRole': 'STEREOTYPE_CLASS',
    
    # Estereótipos de Relação
    'material': 'STEREOTYPE_RELATION', 
    'derivation': 'STEREOTYPE_RELATION', 
    'comparative': 'STEREOTYPE_RELATION', 
    'mediation': 'STEREOTYPE_RELATION', 
    'characterization': 'STEREOTYPE_RELATION', 
    'externalDependence': 'STEREOTYPE_RELATION', 
    'componentOf': 'STEREOTYPE_RELATION', 
    'memberOf': 'STEREOTYPE_RELATION', 
    'subCollectionOf': 'STEREOTYPE_RELATION', 
    'subQualityOf': 'STEREOTYPE_RELATION', 
    'instantiation': 'STEREOTYPE_RELATION', 
    'termination': 'STEREOTYPE_RELATION', 
    'participational': 'STEREOTYPE_RELATION', 
    'participation': 'STEREOTYPE_RELATION', 
    'historicalDependence': 'STEREOTYPE_RELATION', 
    'creation': 'STEREOTYPE_RELATION', 
    'manifestation': 'STEREOTYPE_RELATION', 
    'bringsAbout': 'STEREOTYPE_RELATION', 
    'triggers': 'STEREOTYPE_RELATION', 
    'composition': 'STEREOTYPE_RELATION', 
    'aggregation': 'STEREOTYPE_RELATION', 
    'inherence': 'STEREOTYPE_RELATION', 
    'value': 'STEREOTYPE_RELATION', 
    'formal': 'STEREOTYPE_RELATION', 
    'constitution': 'STEREOTYPE_RELATION',

    # Palavras Reservadas
    'genset': 'RESERVED_WORD', 
    'disjoint': 'RESERVED_WORD', 
    'complete': 'RESERVED_WORD', 
    'general': 'RESERVED_WORD', 
    'specifics': 'RESERVED_WORD', 
    'where': 'RESERVED_WORD', 
    'package': 'RESERVED_WORD',
    'import': 'RESERVED_WORD',
    'functional-complexes': 'RESERVED_WORD',

    # Tipos de Dados Nativos
    'number': 'NATIVE_TYPE', 
    'string': 'NATIVE_TYPE', 
    'boolean': 'NATIVE_TYPE', 
    'date': 'NATIVE_TYPE', 
    'time': 'NATIVE_TYPE', 
    'datetime': 'NATIVE_TYPE',

    # Meta-atributos
    'ordered': 'META_ATTRIBUTE', 
    'const': 'META_ATTRIBUTE', 
    'derived': 'META_ATTRIBUTE', 
    'subsets': 'META_ATTRIBUTE', 
    'redefines': 'META_ATTRIBUTE'
}


# --- Lista de Nomes de Tokens ---
tokens = [
    'CLASS_NAME', 'RELATION_NAME', 'INSTANCE_NAME', 'NEW_TYPE',
    'LBRACE', 'RBRACE', 'LPAREN', 'RPAREN', 'LBRACKET', 'RBRACKET',
    'RANGE', 'REL_BI_DIR', 'REL_UNI_DIR', 'STAR', 'AT', 'COLON',
    'NUMBER',  # <-- NOVO TOKEN ADICIONADO
    'PACKAGE_SEPARATOR' # <-- NOVO TOKEN ADICIONADO
] + list(set(reserved.values()))

# --- Regras de Expressão Regular para Tokens Simples ---
t_PACKAGE_SEPARATOR = r'::-' # <-- NOVA REGRA ADICIONADA
t_LBRACE      = r'\{'
t_RBRACE      = r'\}'
t_LPAREN      = r'\('
t_RPAREN      = r'\)'
t_LBRACKET    = r'\['
t_RBRACKET    = r'\]'
t_RANGE       = r'\.\.'
t_REL_BI_DIR  = r'<>--'
t_REL_UNI_DIR = r'--<>'
t_STAR        = r'\*'
t_AT          = r'@'
t_COLON       = r':'

# --- Regras com Funções ---

# 💡 NOVA REGRA PARA NÚMEROS
def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value) # Converte a string de dígitos para um inteiro
    return t

def t_INSTANCE_NAME(t):
    r'[a-zA-Z][a-zA-Z_]*[0-9]+'
    return t

def t_NEW_TYPE(t):
    r'[a-zA-Z]+DataType'
    return t

def t_CLASS_NAME(t):
    r'[A-Z][a-zA-Z_]*'
    return t

def t_RELATION_NAME(t):
    r'functional\-complexes|[a-z][a-zA-Z_]*'
    t.type = reserved.get(t.value, 'RELATION_NAME')
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    t.lexer.ultimo_inicio_linha = t.lexpos + len(t.value)

t_ignore = ' \t'

def t_ignore_COMMENT(t):
    r'//.*'
    pass

def find_column(token):
    inicio_da_linha = getattr(lexer, 'ultimo_inicio_linha', 0)
    return (token.lexpos - inicio_da_linha) + 1

SUGESTOES_ERRO = {
    ';': "Talvez você esteja querendo usar ':'.",
    '=': "O sinal de '=' não é suportado.",
    '"': "Textos entre aspas duplas não são aceitos.",
    "'": "Textos entre aspas simples não são aceitos.",
    '-': "Hífen isolado não é aceito. Para setas, use '--<>' ou '<>--'. (A única exceção é 'functional-complexes').",
    '.': "Ponto isolado não é válido. Use dois pontos seguidos para intervalos ('..').",
    '_': "Nomes de variáveis ou blocos não podem começar com sublinhado ('_').",
}

def t_error(t):
    sugestao = SUGESTOES_ERRO.get(
        t.value[0],
        "verifique se o símbolo pertence à linguagem e, se não, exclua-o."
    )
    print(f"ERRO: Linha {t.lexer.lineno}: caractere inválido '{t.value[0]}'. {sugestao}")
    t.lexer.skip(1)

# --- Construção do Analisador Léxico ---
lexer = lex.lex()
