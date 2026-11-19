# gerador_arvore.py
import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch


class GeradorArvoreGrafica:
    def __init__(self, nome_arquivo, tabela_simbolos, resultado_semantico):
        self.nome_arquivo = os.path.basename(nome_arquivo)
        self.tabela = tabela_simbolos.tabela
        self.resultado = resultado_semantico

    def _medir_caixa(self, titulo):
        linhas = titulo.split("\n")
        max_chars = max(len(linha) for linha in linhas)
        largura = max(2.2, max_chars * 0.115)
        altura = 0.55 + len(linhas) * 0.28
        return largura, altura

    def _construir_estrutura(self):
        pacotes = list(self.tabela.get("packages", {}).keys())
        nome_pacote = pacotes[0] if pacotes else "global"

        raiz = {
            "titulo": f"Compilação TONTO\n[{self.nome_arquivo}]\nPacote: {nome_pacote}",
            "cor": "#1E293B",
            "texto": "#FFFFFF",
            "filhos": []
        }

        # 1. Tipos de Dados / Enums
        tipos = self.tabela.get("types", {})
        no_tipos = {
            "titulo": f"Tipos de Dados\n({len(tipos)} itens)",
            "cor": "#0369A1",
            "texto": "#FFFFFF",
            "filhos": [
                {
                    "titulo": f"{nome}\n({dados.get('kind', 'type')})",
                    "cor": "#E0F2FE",
                    "texto": "#0C4A6E",
                    "filhos": []
                }
                for nome, dados in tipos.items()
            ]
        }
        raiz["filhos"].append(no_tipos)

        # 2. Classes por Estereótipo
        classes = self.tabela.get("classes", {})
        por_estereotipo = {}
        for nome_cls, dados in classes.items():
            st = dados.get("stereotype") or "sem_estereotipo"
            por_estereotipo.setdefault(st, []).append(nome_cls)

        no_classes = {
            "titulo": f"Classes ({len(classes)})\nEstereótipos",
            "cor": "#0F766E",
            "texto": "#FFFFFF",
            "filhos": [
                {
                    "titulo": f"<<{st}>>\n{', '.join(lista[:2])}{' ...' if len(lista) > 2 else ''}",
                    "cor": "#CCFBF1",
                    "texto": "#134E4A",
                    "filhos": []
                }
                for st, lista in por_estereotipo.items()
            ]
        }
        raiz["filhos"].append(no_classes)

        # 3. Relações / Atributos (amostra da Tabela de Síntese)
        relacoes = self.tabela.get("relations", {})
        no_relacoes = {
            "titulo": f"Relações & Atributos\n({len(relacoes)} itens)",
            "cor": "#334155",
            "texto": "#FFFFFF",
            "filhos": [
                {
                    "titulo": f"{r_nome}\n({r_dados.get('stereotype') or r_dados.get('tipo', 'rel')})",
                    "cor": "#E2E8F0",
                    "texto": "#0F172A",
                    "filhos": []
                }
                for r_nome, r_dados in list(relacoes.items())[:8]
            ]
        }
        raiz["filhos"].append(no_relacoes)

        # 4. Gensets
        gensets = self.tabela.get("gensets", {})
        no_gensets = {
            "titulo": f"Gensets\n({len(gensets)} conjuntos)",
            "cor": "#B45309",
            "texto": "#FFFFFF",
            "filhos": [
                {
                    "titulo": f"{g_nome}\n{', '.join(dados.get('modificadores') or ['sem_mod'])}",
                    "cor": "#FEF3C7",
                    "texto": "#78350F",
                    "filhos": []
                }
                for g_nome, dados in gensets.items()
            ]
        }
        raiz["filhos"].append(no_gensets)

        # 5. Análise Semântica (ODPs, Coerções e Deduções)
        padroes = self.resultado.get("padroes", [])
        coercoes = self.resultado.get("coercoes", [])
        deducoes = self.resultado.get("deducoes", [])

        filhos_odp = []
        for p in padroes:
            linha = f" (L.{p['linha']})" if p.get("linha") else ""
            filhos_odp.append({
                "titulo": f"{p['padrao']}\n{p['elemento']}{linha}",
                "cor": "#EDE9FE",
                "texto": "#4C1D95",
                "filhos": []
            })

        for c in coercoes:
            tag = c.split(":")[0].replace("Coerção ", "Coerção\n")
            filhos_odp.append({
                "titulo": tag,
                "cor": "#FEE2E2",
                "texto": "#7F1D1D",
                "filhos": []
            })

        for d in deducoes:
            tag = d.split(":")[0].replace("Dedução Semântica ", "Dedução\n")
            filhos_odp.append({
                "titulo": tag,
                "cor": "#FEF9C3",
                "texto": "#713F12",
                "filhos": []
            })

        no_semantica = {
            "titulo": f"Semântica ODPs\n({len(padroes)} padrões)",
            "cor": "#6D28D9",
            "texto": "#FFFFFF",
            "filhos": filhos_odp
        }
        raiz["filhos"].append(no_semantica)

        return raiz

    def _largura_subarvore(self, no, margem=0.65):
        largura_propria, _ = self._medir_caixa(no["titulo"])
        if not no["filhos"]:
            no["_largura_sub"] = largura_propria + margem
            return no["_largura_sub"]

        soma_filhos = sum(self._largura_subarvore(f, margem=margem) for f in no["filhos"])
        no["_largura_sub"] = max(largura_propria + margem, soma_filhos)
        return no["_largura_sub"]

    def _posicionar_nos(self, no, x_esquerda, nivel, espacamento_y, posicoes, arestas):
        largura_sub = no["_largura_sub"]
        x_centro = x_esquerda + largura_sub / 2.0
        y = -nivel * espacamento_y
        posicoes.append((x_centro, y, no))

        if no["filhos"]:
            soma_filhos = sum(f["_largura_sub"] for f in no["filhos"])
            cursor = x_esquerda + (largura_sub - soma_filhos) / 2.0
            y_filho = -(nivel + 1) * espacamento_y
            for filho in no["filhos"]:
                x_filho = cursor + filho["_largura_sub"] / 2.0
                arestas.append(((x_centro, y), (x_filho, y_filho)))
                self._posicionar_nos(filho, cursor, nivel + 1, espacamento_y, posicoes, arestas)
                cursor += filho["_largura_sub"]

    def gerar_imagem(self, caminho_saida="arvore_compilacao.png", abrir=True):
        raiz = self._construir_estrutura()
        largura_total = self._largura_subarvore(raiz, margem=0.75)

        posicoes = []
        arestas = []
        espacamento_y = 2.4
        self._posicionar_nos(raiz, 0.0, 0, espacamento_y, posicoes, arestas)

        fig_w = max(18, largura_total * 0.72)
        fig_h = 9.5
        fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=150)
        ax.set_facecolor("#F8FAFC")
        fig.patch.set_facecolor("#F8FAFC")

        for (x1, y1), (x2, y2) in arestas:
            ym = (y1 + y2) / 2.0
            ax.plot([x1, x1, x2, x2], [y1, ym, ym, y2], color="#94A3B8", linewidth=1.5, zorder=1)

        min_y = 0.0
        for x, y, no in posicoes:
            box_w, box_h = self._medir_caixa(no["titulo"])
            min_y = min(min_y, y - box_h / 2.0)

            caixa = FancyBboxPatch(
                (x - box_w / 2.0, y - box_h / 2.0),
                box_w,
                box_h,
                boxstyle="round,pad=0.06,rounding_size=0.12",
                facecolor=no["cor"],
                edgecolor="#475569",
                linewidth=1.1,
                zorder=2
            )
            ax.add_patch(caixa)
            ax.text(
                x, y, no["titulo"],
                ha="center", va="center",
                fontsize=8.0, fontweight="bold",
                color=no["texto"], zorder=3
            )

        ax.set_xlim(-0.8, largura_total + 0.8)
        ax.set_ylim(min_y - 0.6, 1.3)
        ax.axis("off")
        plt.title(
            f"Árvore de Compreensão do Compilador TONTO — {self.nome_arquivo}",
            fontsize=13, fontweight="bold", color="#0F172A", pad=14
        )
        plt.tight_layout()
        plt.savefig(caminho_saida, bbox_inches="tight")
        plt.close(fig)

        print(f"\n🌳 Árvore gráfica gerada com sucesso em: {os.path.abspath(caminho_saida)}")
        if abrir and os.name == "nt":
            os.startfile(caminho_saida)