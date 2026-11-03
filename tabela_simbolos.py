# tabela_simbolos.py

class TabelaSimbolos:
    def __init__(self):
        # Tabela de dispersão principal dividida por categorias (hash tables)
        self.tabela = {
            'packages': {},
            'classes': {},
            'relations': {},
            'types': {},
            'instances': {},
            'gensets': {}
        }
        self.pacote_atual = "global"

    def inserir(self, categoria, nome, dados):
        """Insere um símbolo na categoria correspondente."""
        if categoria not in self.tabela:
            self.tabela[categoria] = {}
        
        # Adiciona contexto do pacote atual
        dados['pacote'] = self.pacote_atual
        self.tabela[categoria][nome] = dados

    def buscar(self, categoria, nome):
        """Busca um símbolo na tabela de dispersão."""
        return self.tabela.get(categoria, {}).get(nome, None)

    def definir_pacote(self, nome_pacote):
        self.pacote_atual = nome_pacote
        if nome_pacote not in self.tabela['packages']:
            self.tabela['packages'][nome_pacote] = {'classes': [], 'relacoes': []}

    def obter_resumo(self):
        """Retorna as contagens para a tabela de síntese."""
        return {
            'Pacotes': list(self.tabela['packages'].keys()),
            'Total Pacotes': len(self.tabela['packages']),
            'Classes': list(self.tabela['classes'].keys()),
            'Total Classes': len(self.tabela['classes']),
            'Relações': list(self.tabela['relations'].keys()),
            'Total Relações': len(self.tabela['relations']),
            'Tipos': list(self.tabela['types'].keys()),
            'Total Tipos': len(self.tabela['types']),
            'Indivíduos': list(self.tabela['instances'].keys()),
            'Total Indivíduos': len(self.tabela['instances']),
            'Gensets': list(self.tabela['gensets'].keys()),
            'Total Gensets': len(self.tabela['gensets'])
        }