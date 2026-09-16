import sys
from analisador_lexico import lexer, find_column  # Importa o lexer que construímos

CATEGORIAS = {
    'CLASS_NAME':          'Classes',
    'RELATION_NAME':       'Relações',
    'STEREOTYPE_CLASS':    'Palavras-chave',
    'STEREOTYPE_RELATION': 'Palavras-chave',
    'NATIVE_TYPE':         'Palavras-chave',
    'INSTANCE_NAME':       'Indivíduos (instâncias)',
    'RESERVED_WORD':       'Palavras reservadas',
    'META_ATTRIBUTE':      'Meta-atributos',
}


def analisar_arquivo(caminho_arquivo):
    """
    Lê um arquivo, passa seu conteúdo para o analisador léxico e
    imprime a tabela de tokens e a tabela de síntese.
    """
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            codigo = f.read()
    except FileNotFoundError:
        print(f"ERRO: Arquivo '{caminho_arquivo}' não encontrado.")
        return

    # Alimenta o analisador léxico com o código
    lexer.input(codigo)
    
    # Prepara a tabela de saída
    tabela_de_simbolos = []
    
    # Itera sobre cada token encontrado pelo lexer
    while True:
        token = lexer.token()
        if not token:
            break  # Fim dos tokens
        
        tabela_de_simbolos.append({
            'lexema': token.value,
            'token': token.type,
            'linha': token.lineno,
            'coluna': find_column(token),
        })

    # Imprime a tabela formatada
    print("-" * 80)
    print(f"{'Lexema':<30} {'Token':<25} {'Linha':<8} {'Coluna':<8}")
    print("-" * 80)
    for entrada in tabela_de_simbolos:
        print(f"{str(entrada['lexema']):<30} {entrada['token']:<25} "
              f"{entrada['linha']:<8} {entrada['coluna']:<8}")

    contagem = {categoria: 0 for categoria in set(CATEGORIAS.values())}
    for entrada in tabela_de_simbolos:
        categoria = CATEGORIAS.get(entrada['token'])
        if categoria:
            contagem[categoria] += 1

    print("-" * 50)
    print(f"{'Categoria':<30} {'Quantidade':<10}")
    print("-" * 50)
    ordem_exibicao = [
        'Classes', 'Relações', 'Palavras-chave',
        'Indivíduos (instâncias)', 'Palavras reservadas', 'Meta-atributos',
    ]
    for categoria in ordem_exibicao:
        print(f"{categoria:<30} {contagem.get(categoria, 0):<10}")



if __name__ == '__main__':
    # Verifica se o nome do arquivo foi passado como argumento na linha de comando
    if len(sys.argv) < 2:
        print("Uso: python main.py <caminho_para_arquivo.tonto>")
        sys.exit(1)
        
    arquivo = sys.argv[1]
    analisar_arquivo(arquivo)