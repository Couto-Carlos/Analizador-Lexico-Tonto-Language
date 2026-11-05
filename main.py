# main.py
import os
import sys
import glob

import analisador_lexico as lexico
from analisador_lexico import lexer
from analisador_sintatico import (parser, erros_sintaticos, ErroSintatico,
                                  tabela_simbolos, resetar_escopo)
from tabela_simbolos import percorrer


def coletar_arquivos(argumentos):
    """Aceita arquivos e/ou pastas (todos os .tonto da pasta)."""
    arquivos = []
    for a in argumentos:
        if os.path.isdir(a):
            arquivos += sorted(glob.glob(os.path.join(a, '*.tonto')))
        else:
            arquivos.append(a)
    return arquivos


def analisar_arquivo(caminho):
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            codigo = f.read()
    except FileNotFoundError:
        print(f"ERRO: Arquivo '{caminho}' não encontrado.")
        return

    print(f"Analisando: {caminho}")
    lexico.estado['arquivo'] = caminho
    lexer.lineno = 1                     # zera a contagem de linhas a cada arquivo
    resetar_escopo()                     # cada arquivo começa no escopo global
    try:
        parser.parse(codigo, lexer=lexer)   # o parser preenche a tabela de símbolos
    except ErroSintatico:
        pass                             # já registrado em erros_sintaticos


# Tabela de síntese
def itens(escopo, categoria):
    return [s for s in escopo.tabela.values() if s['categoria'] == categoria]


def descrever_atributo(a):
    txt = f"{a['nome']}: {a['tipo_dado']}"
    if a.get('cardinalidade'):
        txt += f" [{a['cardinalidade']}]"
    if a.get('meta'):
        txt += " {" + ", ".join(a['meta']) + "}"
    return txt


def descrever_relacao(r):
    est = f"@{r['estereotipo']} " if r.get('estereotipo') else ""
    co = f" [{r['card_origem']}]" if r.get('card_origem') else ""
    meio = f" {r['simbolo']} "
    if r.get('nome'):
        meio = f" {r['simbolo']} {r['nome']} {r['simbolo']} "
    return f"{est}{r['origem']}{co}{meio}[{r['card_alvo']}] {r['alvo']}"


def imprimir_escopo(escopo, recuo="  "):
    for c in itens(escopo, 'class'):
        esp = f" especializa {', '.join(c['especializa'])}" if c.get('especializa') else ""
        nat = f" of {c['natureza']}" if c.get('natureza') else ""
        print(f"{recuo}Classe {c['nome']} [{c['estereotipo']}]{nat}{esp}")
        attrs = itens(c['escopo'], 'attribute')
        rels = itens(c['escopo'], 'relation')
        if attrs:
            print(f"{recuo}    atributos: " + ", ".join(descrever_atributo(a) for a in attrs))
        if rels:
            print(f"{recuo}    relações internas: " + "; ".join(descrever_relacao(r) for r in rels))
    externas = itens(escopo, 'relation')
    if externas:
        print(f"{recuo}Relações externas: " + "; ".join(descrever_relacao(r) for r in externas))
    for t in itens(escopo, 'type'):
        attrs = itens(t['escopo'], 'attribute')
        corpo = ", ".join(descrever_atributo(a) for a in attrs)
        print(f"{recuo}Datatype {t['nome']}" + (f" {{ {corpo} }}" if corpo else ""))
    for e in itens(escopo, 'enum'):
        valores = ", ".join(v['nome'] for v in itens(e['escopo'], 'instance'))
        print(f"{recuo}Enum {e['nome']}: {valores}")
    for g in itens(escopo, 'genset'):
        restr = " ".join(g['restricoes']) + " " if g.get('restricoes') else ""
        print(f"{recuo}Genset {restr}{g['nome']}: {g['geral']} -> " + ", ".join(g['especificos']))


def imprimir_sintese(tabela):
    todos = list(percorrer(tabela))
    cont = lambda cat, **f: sum(1 for s in todos if s['categoria'] == cat
                                and all(s.get(k) == v for k, v in f.items()))
    print("\n" + "=" * 60)
    print("TABELA DE SÍNTESE (CONSTRUTOS TONTO)")
    print("=" * 60)
    print(f"Pacotes: {cont('package')} | Classes: {cont('class')} | "
          f"Atributos: {cont('attribute')}")
    print(f"Relações internas: {cont('relation', externa=False)} | "
          f"externas: {cont('relation', externa=True)} | "
          f"Datatypes: {cont('type')} | Enums: {cont('enum')} | "
          f"Gensets: {cont('genset')}")
    print("-" * 60)

    if any(s['categoria'] != 'package' for s in tabela.tabela.values()):
        print("Fora de pacotes (global):")
        imprimir_escopo(tabela)
    for p in itens(tabela, 'package'):
        imp = f" (importa: {', '.join(p['escopo'].imports)})" if p['escopo'].imports else ""
        print(f"\nPacote {p['nome']}{imp}  [{p['arquivo']}]")
        imprimir_escopo(p['escopo'])
    print("=" * 60)


# Relatório de erros
def imprimir_erros(secoes):
    total = sum(len(e) for _, e in secoes)
    print("\n" + "=" * 60)
    print("RELATÓRIO DE ERROS E SUGESTÕES DE TRATAMENTO")
    print("=" * 60)
    if total == 0:
        print("Nenhum erro encontrado.")
        return
    for titulo, erros in secoes:
        if not erros:
            continue
        print(f"\n{titulo} ({len(erros)})")
        for i, e in enumerate(erros, 1):
            pos = f"linha {e['linha']}" + (f", coluna {e['coluna']}" if e.get('coluna') else "")
            print(f"[{i}] {e['arquivo']}, {pos}: {e['mensagem']}")
            print(f"    Sugestão: {e['sugestao']}")


def main(argumentos):
    arquivos = coletar_arquivos(argumentos)
    if not arquivos:
        print("Nenhum arquivo .tonto encontrado.")
        return
    for caminho in arquivos:
        analisar_arquivo(caminho)
    imprimir_sintese(tabela_simbolos)
    imprimir_erros([("Erros léxicos", lexico.erros_lexicos),
                    ("Erros sintáticos", erros_sintaticos)])


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python main.py <arquivo.tonto | pasta> [mais arquivos...]")
        sys.exit(1)
    main(sys.argv[1:])