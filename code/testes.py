import sys
import os
import random

from parsing import carregar_carros

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def setup_cenario():
    from empresa import Empresa
    from cidades import Cidades
    from carro import Carro

    c = Cidades()
    mapa = c.reconstruir_de_origem("Braga_0012", "Braga_0412")
    conduzAI = Empresa(c.nodos())
    return mapa, conduzAI, Carro, c.nodos()


# TESTE 1: CARGA (Stress Test com muitos pedidos)
def teste_carga_braga():
    print("\n" + "=" * 50)
    print("TESTE DE CARGA: Stress Test em Braga")
    print("=" * 50)
    mapa, conduzAI, Carro, todos_nodos = setup_cenario()

    nodos_braga = [n for n in todos_nodos if "Braga_" in n]
    carros = carregar_carros()
    for c in carros:
        conduzAI.carregaCarro(c)

    print(f"A disparar 10 pedidos simultâneos em Braga...")
    for p in range(1, 11):
        orig = random.choice(nodos_braga)
        dest = random.choice(nodos_braga)
        if orig == dest: continue

        carro = conduzAI.getCarroMaisPerto(
            mapa, orig, dest, tipoCombustivel=0, numerPedido=p, pax=1,
            tempo_max_espera=999.0, partilha=False
        )
        if carro:
            print(f"Pedido {p}: Atribuído a {carro.nome} (Local: {carro.local})")
        else:
            print(f"Pedido {p}: \033[91mCARROS ESGOTADOS\033[0m")

    # Avançar 30 ticks
    for t in range(1, 30):
        print(f"\n--- TICK {t} ---")
        conduzAI.tick_viagens(mapa)

    print(conduzAI.stat)


# TESTE 2: VIAGENS PARTILHADAS (Boleias no mesmo trajeto)
def teste_partilha_em_transito():
    print("\n" + "=" * 50)
    print("TESTE: Partilha Dinâmica (Origem -> Trânsito -> Extensão)")
    print("=" * 50)
    mapa, conduzAI, Carro, _ = setup_cenario()

    carro = Carro(6, 100, 1, "Uber_Dinamico", 600)
    carro.atualizarLocal("Braga_0012")
    conduzAI.carregaCarro(carro)

    #Partilha na Origem
    print("\n[Passo 1] Pedidos 101 e 102 em Braga_0012 Destino 412")
    conduzAI.getCarroMaisPerto(
        mapa, "Braga_0012", "Braga_0412", 1, 101, 1, 999.0, partilha=True
    )
    carro_p1 = conduzAI.getCarroMaisPerto(
        mapa, "Braga_0012", "Braga_0412", 1, 102, 1, 999.0, partilha=True
    )

    if carro_p1 and len(carro_p1.viagens_ativas) > 1:
        print("\033[92mSUCESSO: Partilha na origem concluída.\033[0m")

    #Avançar e tentar Partilha em Trânsito (Mesmo Destino)
    conduzAI.tick_viagens(mapa)
    nova_posicao = carro.local
    print(f"\n[Passo 2] Carro moveu-se para {nova_posicao}. Novo Pedido 103 aqui.")

    carro_p2 = conduzAI.getCarroMaisPerto(
        mapa, nova_posicao, "Braga_0412", 1, 103, 1, 999.0, partilha=True
    )

    if carro_p2 and len(carro_p2.viagens_ativas) > 2:
        print("\033[92mSUCESSO: Partilha em trânsito (mesmo destino) aceite.\033[0m")

    #Avançar e tentar Partilha com Extensão de Rota
    conduzAI.tick_viagens(mapa)
    nova_posicao = carro.local
    print(f"\n[Passo 3] Carro em {nova_posicao}. Pedido 104 para NOVO destino: Braga_0413.")

    #Braga_0413 deve ser um nodo vizinho ou além de Braga_0412 para testar a extensão
    carro_p4 = conduzAI.getCarroMaisPerto(
        mapa, nova_posicao, "Braga_0413", 1, 104, 1, 999.0, partilha=True
    )

    #Relatório Final das Viagens Ativas
    print("\n" + "-"*30)
    if carro_p4 and len(carro_p4.viagens_ativas) > 0:
        print(f"RELATÓRIO FINAL: Carro {carro.nome}")
        print(f"Estado: {'Ocupado' if carro.ocupado else 'Livre'} | Lugares Livres: {carro.tamanho}")
        for v in carro.viagens_ativas:
            print(f" - Viagem {v.numPedido}: {v.origem} -> {v.destino} (Rota restante: {len(v.rota)} nodos)")
    else:
        print("\033[91mAVISO: Algumas partilhas falharam ou o carro ficou livre inesperadamente.\033[0m")
    print("-"*30)


def main():
    while True:
        print("\n=== MENU DE TESTES (BRAGA NODOS) ===")
        print("1 - Teste de Carga Intensiva")
        print("2 - Teste de Viagem Partilhada")
        print("0 - Sair")

        escolha = input("\nEscolha: ")
        if escolha == "1":
            teste_carga_braga()
        elif escolha == "2":
            teste_partilha_em_transito()
        elif escolha == "0":
            break


if __name__ == "__main__":
    main()

