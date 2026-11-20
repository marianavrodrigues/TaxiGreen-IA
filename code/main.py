from __future__ import annotations
from typing import Optional


from cidades import Cidades
from Graph import Grafo
from metricas import metrica
from estatistica import Stat

from parsing import carregar_carros
from empresa import Empresa
from carro import Carro
from pedido import Pedido

def pedir(txt: str) -> str:
    try: return input(txt).strip()
    except EOFError: return ""

def pausa(): input("prima Enter para continuar...")

def menu():
    print("\n=== MENU ===")
    print("1 - Imprimir grafo (estrutura interna)")
    print("2 - Desenhar Grafo")
    print("3 - Listar nodos")
    print("4 - Listar arestas")
    print("5 - DFS")
    print("6 - BFS")
    print("7 - Greedy (Best-First)")
    print("8 - A*")
    print("11 - App uber")
    print("29 - Testa as 4 procuras")
    print("0 - Saír")


def uberApp(mapa: Grafo):
    listaCidades = list(mapa.m_graph.keys())
    conduzAI = Empresa(listaCidades)
    carros = carregar_carros()
    for c in carros:
        conduzAI.carregaCarro(c)

    listaPedidos = []
    npedido = 1
    print("\n--- Teste ---")

    while True:
        print("\n=== MENU ===")
        print("1 - Adicionar pedido")
        print("2 - Sem pedido/avançar")
        print("3 - Ver estatistica")
        print("4 - Voltar")
        print("5 - Listar Carros")
        print("6 - Desenhar mapa (Leaflet)")
        try:
            op = int(pedir("introduza a sua opcao -> "))
        except ValueError:
            print("opção inválida.")
            continue

        if op == 1:
            novoPedido = Pedido(npedido, mapa)
            listaPedidos.append(novoPedido)
            print(f"Pedido realizado com sucesso -> Pedido nº{npedido}")
            npedido += 1

        if op == 2:
            print("Lista de pedidos")
            print(listaPedidos)
            print("Lista Pedidos Ordenada")
            # premium primeiro
            listaPedidos.sort(key=lambda p: not p.premium)

            # atribuir todos os pedidos pendentes
            while listaPedidos:
                pedidoLido = listaPedidos.pop(0)
                carroAtribuido = conduzAI.getCarroMaisPerto(
                    mapa,
                    pedidoLido.origem,
                    pedidoLido.destino,
                    pedidoLido.tipo_veiculo,
                    pedidoLido.numero,
                    pedidoLido.num_pax,
                    pedidoLido.tempo_max_espera,
                    pedidoLido.partilha, 
                )
                print(("\033[33m*\033[0m" * 20))
                print(f"Pedido nº {pedidoLido.numero}")
                print("Carro atribuido")
                if carroAtribuido:
                    carroAtribuido.printCarro()
                else:
                    print("Não foi possivel encontrar carro. Tente mais tarde ou aumente tempo máximo de espera")
                print(("\033[33m*\033[0m" * 20))

            skip = int(pedir("introduza tempo a passar -> "))
            while skip != 0:
                conduzAI.tick_viagens(mapa)

                # mostrar estado das viagens ativas em cada carro
                for carro in conduzAI.carros:
                    if not carro.viagens_ativas:
                        continue
                    for viagem in carro.viagens_ativas:
                        print(f"[Carro {carro.nome}]")
                        print(f"Carro autonomia {carro.autonomia}")
                        viagem.status()
                        print("-" * 40)

                skip -= 1

        if op == 3:
            print(conduzAI.stat)
            continue

        if op == 4:
            break

        if op == 5:
            for i, c in enumerate(conduzAI.carros):
                tipo_str = "Combustão" if c.tipo == 0 else "Elétrico"
                print(f"[{i}] {c.nome} | {tipo_str} | Autonomia: {c.autonomia} km | Local: {c.local}")
            continue

        if op == 6:
            from leaflet_map import gerar_mapa_html
            import webbrowser
            caminho = gerar_mapa_html()
            print(f"Mapa gerado em: {caminho}")
            webbrowser.open(f"file://{caminho}")
            continue

    

def main():
    c = Cidades()
    braga = True
    if braga:
        g: Grafo = c.reconstruir_de_origem(origem="Braga_0012", destino="Braga_0412")
    else:
        g: Grafo = c.reconstruir_de_origem(origem="Porto", destino="Lisboa")

    while True:
        menu()
        try:
            op = int(pedir("introduza a sua opcao -> "))
        except ValueError:
            print("opção inválida.")
            continue

        if op == 0:
            print("saindo.......")
            break

        elif op == 1:
            print(g.m_graph); pausa()

        elif op == 2:
            try: g.desenha()
            except Exception as e: print("Erro a desenhar grafo:", e)
            pausa()

        elif op == 3:
            print(list(g.m_graph.keys())); pausa()

        elif op == 4:
            try: print(g.imprime_aresta())
            except Exception as e: print("Erro a imprimir arestas:", e)
            pausa()

        elif op == 11:
                    uberApp(g)

        elif op in (5, 6, 7, 8, 29):
            inicio = pedir("Nodo inicial -> ")
            fim    = pedir("Nodo final   -> ")
            try:
                g = c.reconstruir_de_origem(inicio, fim)

                if op == 5:
                    res = g.procura_DFS(inicio, fim, path=[], visited=set())
                    print("DFS:", res)

                elif op == 6:
                    res = g.procura_BFS_bi(inicio, fim)
                    print("BFS:", res)

                elif op == 7:
                    res = g.greedy(inicio, fim)
                    print("Greedy:", res)

                elif op == 8:
                    res = g.procura_aStar(inicio, fim)
                    print("A*:", res)

                elif op == 29:
                    resEstrela = metrica(g.procura_aStar, (inicio, fim))
                    resGreedy  = metrica(g.greedy, (inicio, fim))
                    resBFS     = metrica(g.procura_BFS, (inicio, fim))
                    resBFSBi   = metrica(g.procura_BFS_bi, (inicio, fim))
                    resDij     = metrica(g.procura_dijkstra, (inicio, fim))
                    resDFS     = metrica(g.procura_DFS, (inicio, fim), {'path': [], 'visited': set()})
                    print("A*:", resEstrela)
                    print("Greedy:", resGreedy)
                    print("BFS:", resBFS)
                    print("BFS Bi:", resBFSBi)
                    print("Dijkstra:", resDij)
                    print("DFS:", resDFS)
                

            except Exception as e:
                print("Erro:", e)
            pausa()

        else:
            print("opção desconhecida."); pausa()


if __name__ == "__main__":
    main()
