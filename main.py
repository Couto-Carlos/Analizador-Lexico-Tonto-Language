# main.py
import sys
from analisador_lexico import lexer, find_column
from analisador_sintatico import parser, tabela_simbolos, erros_sintaticos

def analisar_arquivo(caminho_arquivo):
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            codigo = f.read()
    except FileNotFoundError:
        print(f"ERRO: Arquivo '{caminho_arquivo}' não encontrado.")
        return

    print(f"\n=== INICIANDO ANÁLISE DO ARQUIVO: {caminho_arquivo} ===")
    
    # 1. Executa a Análise Sintática (que por sua vez consome o Léxico)
    resultado_parser = parser.parse(codigo, lexer=lexer)

    # 2. Relatório de Síntese (Requisito do Professor)
    resumo = tabela_simbolos.obter_resumo()
    
    print("\n" + "="*50)
    print(f"{'TABELA DE SÍNTESE (CONSTRUTOS TONTO)':<50}")
    print("="*50)
    print(f"{'Construto / Categoria':<30} {'Quantidade':<10} {'Elementos encontrados':<20}")
    print("-"*50)
    print(f"{'Pacotes':<30} {resumo['Total Pacotes']:<10} {str(resumo['Pacotes'])[:20]}")
    print(f"{'Classes':<30} {resumo['Total Classes']:<10} {str(resumo['Classes'])[:20]}")
    print(f"{'Relações':<30} {resumo['Total Relações']:<10} {str(resumo['Relações'])[:20]}")
    print(f"{'Tipos de Dados':<30} {resumo['Total Tipos']:<10} {str(resumo['Tipos'])[:20]}")
    print(f"{'Indivíduos':<30} {resumo['Total Indivíduos']:<10} {str(resumo['Indivíduos'])[:20]}")
    print(f"{'Gensets':<30} {resumo['Total Gensets']:<10} {str(resumo['Gensets'])[:20]}")
    print("="*50)

    # 3. Relatório de Erros Sintáticos e Sugestões
    if erros_sintaticos:
        print("\n" + "="*50)
        print(f"{'RELATÓRIO DE ERROS E SUGESTÕES DE TRATAMENTO':<50}")
        print("="*50)
        for i, erro in enumerate(erros_sintaticos, 1):
            print(f"[{i}] {erro['mensagem']}")
            print(f"    💡 Sugestão: {erro['sugestao']}\n")
    else:
        print("\n✨ Análise concluída com sucesso! Nenhum erro sintático encontrado.")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python main.py <caminho_para_arquivo.tonto>")
        sys.exit(1)
        
    arquivo = sys.argv[1]
    analisar_arquivo(arquivo)