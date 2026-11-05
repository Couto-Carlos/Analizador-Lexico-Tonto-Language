# tabela_simbolos.py
# Implementação da tabela de símbolos com escopos encadeados.

class TabelaSimbolos:
    def __init__(self, prev=None, nome="global", tipo="global"):
        self.tabela = {}      # tabela de dispersão deste escopo: nome -> símbolo
        self.prev = prev      # escopo envolvente (None no escopo global)
        self.nome = nome
        self.tipo = tipo      # global | package | class | relation | enum
        self.imports = []     # nomes de pacotes importados neste escopo

    def put(self, chave, simbolo):
        """Insere no escopo atual. Retorna False se o nome já existir neste escopo."""
        if chave in self.tabela:
            return False
        self.tabela[chave] = simbolo
        return True

    def get_local(self, chave):
        """Busca apenas no escopo atual."""
        return self.tabela.get(chave)

    def get(self, chave):
        """Busca no escopo atual e, se não achar, sobe pela cadeia 'prev'."""
        st = self
        while st is not None:
            achado = st.tabela.get(chave)
            if achado is not None:
                return achado
            st = st.prev
        return None

    def novo_escopo(self, nome, tipo):
        """Cria um escopo filho encadeado a este."""
        return TabelaSimbolos(prev=self, nome=nome, tipo=tipo)


def percorrer(escopo):
    """Gera todos os símbolos de um escopo e dos escopos aninhados."""
    for s in escopo.tabela.values():
        yield s
        if 'escopo' in s:
            yield from percorrer(s['escopo'])