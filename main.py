
import sys
from analisador_lexico import lexer  # Importa o lexer que construímos

def analisar_arquivo(caminho_arquivo):
    """
    Lê um arquivo, passa seu conteúdo para o analisador léxico e
    imprime a tabela de tokens.
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
        })

    # Imprime a tabela formatada
    print(f"{'Lexema':<35} {'Token':<25} {'Linha':<10}")
    print("-" * 70)
    for entrada in tabela_de_simbolos:
        print(f"{entrada['lexema']:<35} {entrada['token']:<25} {entrada['linha']:<10}")


if __name__ == '__main__':
    # Verifica se o nome do arquivo foi passado como argumento na linha de comando
    if len(sys.argv) < 2:
        print("Uso: python main.py <caminho_para_arquivo.tonto>")
        sys.exit(1)
        
    arquivo = sys.argv[1]
    analisar_arquivo(arquivo)