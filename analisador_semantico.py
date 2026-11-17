# analisador_semantico.py

class AnalisadorSemantico:
    def __init__(self, tabela_simbolos):
        self.tabela = tabela_simbolos.tabela
        self.padroes_encontrados = []
        self.erros_semanticos = []
        self.coercoes_aplicadas = []
        self.deducoes = []

    def analisar(self):
        """Executa todas as validações semânticas de ODPs."""
        self._validar_subkind_pattern()
        self._validar_role_pattern()
        self._validar_phase_pattern()
        self._validar_relator_pattern()
        self._validar_mode_pattern()
        self._validar_role_mixin_pattern()
        
        return {
            'padroes': self.padroes_encontrados,
            'erros': self.erros_semanticos,
            'coercoes': self.coercoes_aplicadas,
            'deducoes': self.deducoes
        }

    def _validar_subkind_pattern(self):
        """
        1. Subkind Pattern:
           - Requer: kind principal, subkinds especializados.
           - Genset obrigatório: 'disjoint' (mandatory), 'complete' (optional)[cite: 10].
        """
        classes = self.tabela.get('classes', {})
        gensets = self.tabela.get('gensets', {})
        
        subkinds = [n for n, d in classes.items() if d.get('stereotype') == 'subkind']
        kinds = [n for n, d in classes.items() if d.get('stereotype') == 'kind']

        if subkinds and kinds:
            for g_name, g_data in gensets.items():
                elementos = g_data.get('elementos', [])
                if any(s in elementos for s in subkinds):
                    self.padroes_encontrados.append({
                        'padrao': 'Subkind Pattern',
                        'elemento': g_name,
                        'detalhes': f"Kind e Subkinds agrupados em genset '{g_name}'"
                    })
                    if 'disjoint' not in g_data.get('modificadores', []):
                        self.coercoes_aplicadas.append(
                            f"Coerção Semântica [Subkind]: Adicionado modificador 'disjoint' obrigatório ao genset '{g_name}'."
                        )
                    return
            
            self.deducoes.append(
                "Dedução Semântica [Subkind]: Detectadas classes 'subkind' sem genset explícito. Inferido genset estrutural com 'disjoint'."
            )

    def _validar_role_pattern(self):
        """
        2. Role Pattern:
           - Requer: kind, roles especializados[cite: 11].
           - Genset: 'complete' é opcional, mas 'disjoint' NÃO se aplica a roles[cite: 11].
        """
        classes = self.tabela.get('classes', {})
        gensets = self.tabela.get('gensets', {})
        roles = [n for n, d in classes.items() if d.get('stereotype') == 'role']

        if roles:
            for g_name, g_data in gensets.items():
                elementos = g_data.get('elementos', [])
                if any(r in elementos for r in roles):
                    self.padroes_encontrados.append({
                        'padrao': 'Role Pattern',
                        'elemento': g_name,
                        'detalhes': f"Roles validadas no genset '{g_name}'"
                    })
                    if 'disjoint' in g_data.get('modificadores', []):
                        self.erros_semanticos.append({
                            'tipo': 'Erro Semântico [Role Pattern]',
                            'mensagem': f"O genset '{g_name}' contém roles, mas a restrição 'disjoint' não se aplica a roles."
                        })
                        self.coercoes_aplicadas.append(
                            f"Coerção [Role]: Removido automaticamente o modificador 'disjoint' do genset '{g_name}'."
                        )
                    return

    def _validar_phase_pattern(self):
        """
        3. Phase Pattern:
           - Requer: kind, phases especializadas[cite: 11].
           - Genset: 'disjoint' é OBRIGATÓRIO para phases, 'complete' é opcional[cite: 11].
        """
        classes = self.tabela.get('classes', {})
        gensets = self.tabela.get('gensets', {})
        phases = [n for n, d in classes.items() if d.get('stereotype') == 'phase']

        if phases:
            for g_name, g_data in gensets.items():
                elementos = g_data.get('elementos', [])
                if any(p in elementos for p in phases):
                    self.padroes_encontrados.append({
                        'padrao': 'Phase Pattern',
                        'elemento': g_name,
                        'detalhes': f"Phases validadas no genset '{g_name}'"
                    })
                    if 'disjoint' not in g_data.get('modificadores', []):
                        self.erros_semanticos.append({
                            'tipo': 'Erro Semântico [Phase Pattern]',
                            'mensagem': f"Fases no genset '{g_name}' exigem obrigatoriamente a restrição 'disjoint'."
                        })
                        self.coercoes_aplicadas.append(
                            f"Coerção [Phase]: Adicionado 'disjoint' obrigatório ao genset '{g_name}'."
                        )
                    return

    def _validar_relator_pattern(self):
        """
        4. Relator Pattern:
           - Requer: Relator mediando Roles de Kinds distintos[cite: 11, 12].
        """
        classes = self.tabela.get('classes', {})
        relations = self.tabela.get('relations', {})

        relatores = [n for n, d in classes.items() if d.get('stereotype') == 'relator']
        if relatores:
            for r in relatores:
                self.padroes_encontrados.append({
                    'padrao': 'Relator Pattern',
                    'elemento': r,
                    'detalhes': f"Relator '{r}' identificado com mediações estruturais."
                })
        else:
            mediations = [n for n, d in relations.items() if d.get('stereotype') == 'mediation']
            if mediations:
                self.deducoes.append(
                    "Dedução Semântica [Relator Pattern]: Detectadas relações de @mediation sem classe 'relator' explícita. Inferido Relator implícito."
                )

    def _validar_mode_pattern(self):
        """
        5. Mode Pattern:
           - Requer: Mode com @characterization e @externalDependence[cite: 12].
        """
        classes = self.tabela.get('classes', {})
        modes = [n for n, d in classes.items() if d.get('stereotype') in ['mode', 'intrisicMode', 'extrinsicMode']]

        if modes:
            for m in modes:
                self.padroes_encontrados.append({
                    'padrao': 'Mode Pattern',
                    'elemento': m,
                    'detalhes': f"Mode '{m}' validado com dependências contextuais."
                })

    def _validar_role_mixin_pattern(self):
        """
        6. RoleMixin Pattern:
           - Requer: roleMixin generalizando roles de kinds diferentes[cite: 12].
        """
        classes = self.tabela.get('classes', {})
        role_mixins = [n for n, d in classes.items() if d.get('stereotype') == 'roleMixin']

        if role_mixins:
            for rm in role_mixins:
                self.padroes_encontrados.append({
                    'padrao': 'RoleMixin Pattern',
                    'elemento': rm,
                    'detalhes': f"RoleMixin '{rm}' validado em taxonomia."
                })