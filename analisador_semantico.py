# analisador_semantico.py

class AnalisadorSemantico:
    def __init__(self, tabela_simbolos=None):
        self.tabela = tabela_simbolos.tabela if tabela_simbolos else {}
        self.padroes_encontrados = []
        self.erros_semanticos = []
        self.coercoes_aplicadas = []
        self.deducoes = []

    def _resetar_relatorio(self):
        self.padroes_encontrados = []
        self.erros_semanticos = []
        self.coercoes_aplicadas = []
        self.deducoes = []

    # Sobrecarga: aceita (tabela_simbolos) ou (tabela_simbolos, modo_estrito)
    def analisar(self, tabela_simbolos=None, modo_estrito=False):
        """Executa todas as validações semânticas de ODPs."""
        if tabela_simbolos is not None:
            self.tabela = tabela_simbolos.tabela
        self._resetar_relatorio()

        self._validar_subkind_pattern(modo_estrito=modo_estrito)
        self._validar_role_pattern(modo_estrito=modo_estrito)
        self._validar_phase_pattern(modo_estrito=modo_estrito)
        self._validar_relator_pattern(modo_estrito=modo_estrito)
        self._validar_mode_pattern(modo_estrito=modo_estrito)
        self._validar_role_mixin_pattern(modo_estrito=modo_estrito)

        return {
            'padroes': self.padroes_encontrados,
            'erros': self.erros_semanticos,
            'coercoes': self.coercoes_aplicadas,
            'deducoes': self.deducoes
        }

    def _validar_subkind_pattern(self, modo_estrito=False):
        classes = self.tabela.get('classes', {})
        gensets = self.tabela.get('gensets', {})

        subkinds = {n: d for n, d in classes.items() if d.get('stereotype') == 'subkind'}
        kinds = {n: d for n, d in classes.items() if d.get('stereotype') == 'kind'}

        if subkinds and kinds:
            encontrou_genset = False
            for g_name, g_data in gensets.items():
                elementos = g_data.get('elementos', [])
                if any(s in elementos for s in subkinds):
                    encontrou_genset = True
                    linha = g_data.get('linha')
                    loc = f"linha {linha}" if linha else "linha N/D"
                    self.padroes_encontrados.append({
                        'padrao': 'Subkind Pattern',
                        'elemento': g_name,
                        'linha': linha,
                        'detalhes': f"{loc} — Kind e Subkinds agrupados em genset '{g_name}'"
                    })
                    mods = g_data.get('modificadores', [])
                    if 'disjoint' not in mods:
                        mods.append('disjoint')
                        self.erros_semanticos.append({
                            'tipo': 'Erro Semântico [Subkind Pattern]',
                            'mensagem': f"Genset '{g_name}' ({loc}) deve aplicar 'disjoint' a subkinds."
                        })
                        self.coercoes_aplicadas.append(
                            f"Coerção [Subkind]: Adicionado modificador 'disjoint' ao genset '{g_name}' ({loc})."
                        )
            if not encontrou_genset:
                linhas_sub = [str(d.get('linha')) for d in subkinds.values() if d.get('linha')]
                loc_sub = f"linhas {', '.join(linhas_sub)}" if linhas_sub else "sem linha"
                self.deducoes.append(
                    f"Dedução Semântica [Subkind] ({loc_sub}): Detectadas classes 'subkind' sem genset explícito; inferido genset com 'disjoint'."
                )

    def _validar_role_pattern(self, modo_estrito=False):
        classes = self.tabela.get('classes', {})
        gensets = self.tabela.get('gensets', {})
        roles = {n: d for n, d in classes.items() if d.get('stereotype') == 'role'}

        if roles:
            for g_name, g_data in gensets.items():
                elementos = g_data.get('elementos', [])
                if any(r in elementos for r in roles):
                    linha = g_data.get('linha')
                    loc = f"linha {linha}" if linha else "linha N/D"
                    self.padroes_encontrados.append({
                        'padrao': 'Role Pattern',
                        'elemento': g_name,
                        'linha': linha,
                        'detalhes': f"{loc} — Roles validadas no genset '{g_name}'"
                    })
                    mods = g_data.get('modificadores', [])
                    if 'disjoint' in mods:
                        mods.remove('disjoint')
                        self.erros_semanticos.append({
                            'tipo': 'Erro Semântico [Role Pattern]',
                            'mensagem': f"O genset '{g_name}' ({loc}) contém roles, mas 'disjoint' não se aplica a roles."
                        })
                        self.coercoes_aplicadas.append(
                            f"Coerção [Role]: Removido modificador 'disjoint' do genset '{g_name}' ({loc})."
                        )

    def _validar_phase_pattern(self, modo_estrito=False):
        classes = self.tabela.get('classes', {})
        gensets = self.tabela.get('gensets', {})
        phases = {n: d for n, d in classes.items() if d.get('stereotype') == 'phase'}

        if phases:
            for g_name, g_data in gensets.items():
                elementos = g_data.get('elementos', [])
                if any(p in elementos for p in phases):
                    linha = g_data.get('linha')
                    loc = f"linha {linha}" if linha else "linha N/D"
                    self.padroes_encontrados.append({
                        'padrao': 'Phase Pattern',
                        'elemento': g_name,
                        'linha': linha,
                        'detalhes': f"{loc} — Phases validadas no genset '{g_name}'"
                    })
                    mods = g_data.get('modificadores', [])
                    if 'disjoint' not in mods:
                        mods.append('disjoint')
                        self.erros_semanticos.append({
                            'tipo': 'Erro Semântico [Phase Pattern]',
                            'mensagem': f"Fases no genset '{g_name}' ({loc}) exigem obrigatoriamente 'disjoint'."
                        })
                        self.coercoes_aplicadas.append(
                            f"Coerção [Phase]: Adicionado 'disjoint' obrigatório ao genset '{g_name}' ({loc})."
                        )

    def _validar_relator_pattern(self, modo_estrito=False):
        classes = self.tabela.get('classes', {})
        relations = self.tabela.get('relations', {})

        relatores = {n: d for n, d in classes.items() if d.get('stereotype') == 'relator'}
        if relatores:
            for r, d in relatores.items():
                linha = d.get('linha')
                loc = f"linha {linha}" if linha else "linha N/D"
                self.padroes_encontrados.append({
                    'padrao': 'Relator Pattern',
                    'elemento': r,
                    'linha': linha,
                    'detalhes': f"{loc} — Relator '{r}' identificado."
                })
        else:
            mediations = [n for n, d in relations.items() if d.get('stereotype') == 'mediation']
            if mediations:
                self.deducoes.append(
                    "Dedução Semântica [Relator Pattern]: Detectadas relações de mediação sem classe 'relator' explícita."
                )

    def _validar_mode_pattern(self, modo_estrito=False):
        classes = self.tabela.get('classes', {})
        modes = {
            n: d for n, d in classes.items()
            if d.get('stereotype') in ['mode', 'intrisicMode', 'extrinsicMode']
        }

        for m, d in modes.items():
            linha = d.get('linha')
            loc = f"linha {linha}" if linha else "linha N/D"
            self.padroes_encontrados.append({
                'padrao': 'Mode Pattern',
                'elemento': m,
                'linha': linha,
                'detalhes': f"{loc} — Mode '{m}' identificado."
            })

    def _validar_role_mixin_pattern(self, modo_estrito=False):
        classes = self.tabela.get('classes', {})
        role_mixins = {n: d for n, d in classes.items() if d.get('stereotype') == 'roleMixin'}

        for rm, d in role_mixins.items():
            linha = d.get('linha')
            loc = f"linha {linha}" if linha else "linha N/D"
            self.padroes_encontrados.append({
                'padrao': 'RoleMixin Pattern',
                'elemento': rm,
                'linha': linha,
                'detalhes': f"{loc} — RoleMixin '{rm}' identificado."
            })