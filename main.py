# main.py
import sys
from analisador_lexico import lexer
from analisador_sintatico import parser, tabela_simbolos, erros_sintaticos, ErroSintatico
from analisador_semantico import AnalisadorSemantico
from gerador_arvore import GeradorArvoreGrafica

def analisar_arquivo(caminho_arquivo):
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            codigo = f.read()
    except FileNotFoundError:
        print(f"ERRO: Arquivo '{caminho_arquivo}' não encontrado.")
        return

    tabela_simbolos.resetar()
    erros_sintaticos.clear()
    lexer.lineno = 1
    lexer.ultimo_inicio_linha = 0

    print(f"\n=== INICIANDO COMPILAÇÃO DO ARQUIVO: {caminho_arquivo} ===")

    # 1. Análise Léxico-Sintática com tratamento de erros
    try:
        parser.parse(codigo, lexer=lexer)
    except ErroSintatico as e:
        print(f"\n❌ {e}")
        for err in erros_sintaticos:
            print(f"   Sugestão: {err['sugestao']}")
        return

    # 2. Tabela de Síntese
    resumo = tabela_simbolos.obter_resumo()

    print("\n" + "=" * 60)
    print(f"{'TABELA DE SÍNTESE (CONSTRUTOS TONTO)':<60}")
    print("=" * 60)
    print(f"{'Construto / Categoria':<30} {'Quantidade':<10} {'Elementos':<20}")
    print("-" * 60)
    print(f"{'Pacotes':<30} {resumo['Total Pacotes']:<10} {str(resumo['Pacotes'])[:20]}")
    print(f"{'Classes':<30} {resumo['Total Classes']:<10} {str(resumo['Classes'])[:20]}")
    print(f"{'Relações':<30} {resumo['Total Relações']:<10} {str(resumo['Relações'])[:20]}")
    print(f"{'Tipos de Dados':<30} {resumo['Total Tipos']:<10} {str(resumo['Tipos'])[:20]}")
    print(f"{'Indivíduos':<30} {resumo['Total Indivíduos']:<10} {str(resumo['Indivíduos'])[:20]}")
    print(f"{'Gensets':<30} {resumo['Total Gensets']:<10} {str(resumo['Gensets'])[:20]}")
    print("=" * 60)

    # 3. Análise Semântica (Validação de ODPs)
    semantica = AnalisadorSemantico(tabela_simbolos)
    resultado_semantico = semantica.analisar(tabela_simbolos)

    print("\n" + "=" * 60)
    print(f"{'RELATÓRIO DA ANÁLISE SEMÂNTICA (ODPs)':<60}")
    print("=" * 60)

    print("\n[1] Padrões de Projeto Encontrados (por linha):")
    if resultado_semantico['padroes']:
        for p in resultado_semantico['padroes']:
            print(f"  • {p['padrao']} -> Elemento: '{p['elemento']}' ({p['detalhes']})")
    else:
        print("  (Nenhum ODP completo identificado)")

    print("\n[2] Erros Semânticos e Correção por Coerção:")
    if resultado_semantico['erros'] or resultado_semantico['coercoes']:
        for e in resultado_semantico['erros']:
            print(f"  ❌ {e['tipo']}: {e['mensagem']}")
        for c in resultado_semantico['coercoes']:
            print(f"  🔧 {c}")
    else:
        print("  ✨ Nenhum erro semântico detectado.")

    print("\n[3] Dedução de Padrões Incompletos (Sobrecarregamento/Inferência):")
    if resultado_semantico['deducoes']:
        for d in resultado_semantico['deducoes']:
            print(f"  💡 {d}")
    else:
        print("  (Nenhuma dedução pendente)")
    print("=" * 60)
    # 4. Geração da Árvore Gráfica (Tokens, Classes, Gensets e ODPs)
    arvore = GeradorArvoreGrafica(caminho_arquivo, tabela_simbolos, resultado_semantico)
    arvore.gerar_imagem(caminho_saida="arvore_compilacao.png", abrir=True)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python main.py <caminho_para_arquivo.tonto>")
        sys.exit(1)

    arquivo = sys.argv[1]
    analisar_arquivo(arquivo)