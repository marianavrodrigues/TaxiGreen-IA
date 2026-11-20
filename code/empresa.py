from carro import Carro
from viagem import Viagem
from Graph import Grafo
from cidades import Cidades
from estatistica import Stat


def pagoCliente(km: int):
    total = km * 0.6
    print(f"Calculei os custos - {total}")
    return total


def posto_no_caminho(rota, autonomia: int, mapa: Grafo):
    POSTOS_CARREGAMENTO = {
        "Lisboa", "Setubal", "Evora", "Sines",
        "Coimbra", "Porto", "Braga", "Madrid"
    }
    rotaAux = []
    for cidade in rota:
        if cidade in POSTOS_CARREGAMENTO:
            rotaAux.clear()
            for c in rota:
                rotaAux.append(c)
                if c == cidade:
                    break
            if mapa.calcula_custo(rotaAux) > autonomia:
                continue
            else:
                return True, cidade
    return False, None


def checkdisponi(car: Carro, distAteDestino: int, destino: str,
                 mapa: Grafo, pax: int) -> bool:
    if car.tipo == 0 or car.ocupado == 1 or pax > car.tamanho:
        return False

    res = mapa.procura_BFS_bi(car.local, destino)
    if not res:
        return False

    lista, distAtecliente, _ = res
    if len(lista) > 2:
        return False

    if car.autonomia >= distAtecliente + distAteDestino:
        return True

    return False


class Empresa:
    def __init__(self, cidadesLista):
        self.carros: list[Carro] = []
        self.stat = Stat(cidadesLista)

    def carregaCarro(self, newcarro: Carro):
        self.carros.append(newcarro)

    # =======================================================
    #  0) HELPER: tentar encaixar pedido em partilha
    #     Caso 1: Loc1->Loc3 e Loc1->Loc2 (destino dentro da rota)
    #     Caso 2: Loc1->Loc2 e Loc1->Loc3 (extensão da rota)
    # =======================================================
    def _tenta_partilha(self, mapa: Grafo, locCliente: str, obj: str,
                        tipoCombustivel: int, numerPedido: int,
                        pax: int) -> Carro | None:
        c = Cidades()

        for carro in self.carros:
            if carro.ocupado == 0:
                continue
            if pax > carro.tamanho:
                continue
            if not carro.rota_atual or not carro.viagens_ativas:
                continue

            #combustível:
            #cliente pede elétrico (1) -> só elétrico
            #cliente pede combustão (0) -> aceita combustão ou elétrico 
            if carro.tipo != tipoCombustivel:
                if not (tipoCombustivel == 0 and carro.tipo == 1):
                    continue

            viagem_principal = carro.viagens_ativas[0]
            rota_principal = viagem_principal.rota

            #Casos 1 e 2 exigem MESMA ORIGEM e carro parado na origem 
            if carro.posicao_atual != locCliente:
                continue

            # -----------------------------
            # Caso 1: pedido 2 termina dentro da rota principal
            # Pedido1: Loc1 -> Loc3
            # Pedido2: Loc1 -> Loc2
            # -----------------------------
            if obj in rota_principal:
                idx_o = rota_principal.index(locCliente)
                idx_d = rota_principal.index(obj)
                if idx_o < idx_d:
                    sub_rota = rota_principal[idx_o: idx_d + 1]

                    # calcula distância/tempo dessa sub-rota
                    mapa_sub = c.reconstruir_de_origem(locCliente, obj)
                    dist_sub = mapa_sub.calcula_custo(sub_rota)
                    tempo_sub = dist_sub / 80.0
                    custo = pagoCliente(dist_sub)

                    nova_viagem = Viagem(sub_rota, dist_sub, tempo_sub,
                                         numerPedido, custo)
                    carro.viagens_ativas.append(nova_viagem)
                    carro.tamanho -= pax

                    self.stat.addTempoPrevisto(tempo_sub)
                    self.stat.addViagensPorCidade(locCliente)

                    print(f"\033[38;5;208m[PARTILHA] Pedido {numerPedido} encaixado (prefixo) no carro {carro.nome}.\033[0m")
                    return carro

            # -----------------------------
            # Caso 2: pedido 2 quer ir mais longe
            # Pedido1: Loc1 -> Loc2
            # Pedido2: Loc1 -> Loc3  (Loc3 fora da rota principal)
            # -----------------------------
            dest_principal = viagem_principal.destino
            if obj != dest_principal:
                #calcular rota extra de dest_principal até obj
                mapa_extra = c.reconstruir_de_origem(dest_principal, obj)
                rota_extra, dist_extra, tempo_extra = mapa_extra.procura_dijkstra(
                    dest_principal, obj
                )

                #rota do carro passa a ser principal + extra 
                rota_nova_carro = rota_principal[:] + rota_extra[1:]
                carro.rota_atual = rota_nova_carro[:]

                rota_nova_pass = rota_nova_carro[:]

                mapa_total = c.reconstruir_de_origem(locCliente, obj)
                dist_total = mapa_total.calcula_custo(rota_nova_pass)
                tempo_total = dist_total / 80.0
                custo_total = pagoCliente(dist_total)

                nova_viagem = Viagem(rota_nova_pass, dist_total, tempo_total,
                                     numerPedido, custo_total)
                carro.viagens_ativas.append(nova_viagem)
                carro.tamanho -= pax

                self.stat.addTempoPrevisto(tempo_total)
                self.stat.addViagensPorCidade(locCliente)

                print(f"\033[38;5;208m[PARTILHA] Pedido {numerPedido} encaixado (extensão) no carro {carro.nome}.\033[0m")
                return carro
        return None
    
    def getCarroMaisPerto(self, mapa: Grafo, locCliente: str, obj: str,
                          tipoCombustivel: int, numerPedido: int,
                          pax: int, tempo_max_espera: float,
                          partilha: bool) -> Carro | None:
        c = Cidades()
        eco = 0

        # tenta partilhar
        if partilha:
            carro_partilha = self._tenta_partilha(
                mapa, locCliente, obj, tipoCombustivel, numerPedido, pax
            )
            if carro_partilha is not None:
                return carro_partilha

        # se não houver parilha
        escolhido = -1
        melhor_tempo = float("inf")
        melhor_caminho = None
        melhor_distancia = None

        # 1) Escolher o carro mais perto do cliente
        for i, carro in enumerate(self.carros):
            if carro.ocupado == 1 or pax > carro.tamanho:
                continue
            if carro.tipo == tipoCombustivel:
                mapa_aux = c.reconstruir_de_origem(carro.local, locCliente)
                caminho, distancia, tempo = mapa_aux.procura_aStar(carro.local, locCliente)
                if tempo > tempo_max_espera:
                    continue
                if tempo <= melhor_tempo:
                    escolhido = i
                    melhor_tempo = tempo
                    melhor_caminho = caminho
                    melhor_distancia = distancia

        # 2) Não há carros
        if escolhido == -1:
            print("Acabei 1 procura nao ha")
            return None

        # 3) Verificar se é possível trocar para carro elétrico (opção ecológica)
        if tipoCombustivel == 0:  # cliente pediu combustão -> tentar trocar para elétrico
            print("Vou testar opçoes ecologicas")
            mapa_cliente_destino = c.reconstruir_de_origem(locCliente, obj)
            aestrelaClienteDestino, _, _ = mapa_cliente_destino.procura_aStar(locCliente, obj)
            distAteDestino = mapa_cliente_destino.calcula_custo(aestrelaClienteDestino)

            for n, carro in enumerate(self.carros):
                if checkdisponi(carro, distAteDestino, locCliente, mapa_cliente_destino, pax):
                    mapa_aux = c.reconstruir_de_origem(carro.local, locCliente)
                    melhor_caminho, melhor_distancia, melhor_tempo = mapa_aux.procura_aStar(carro.local, locCliente)
                    if melhor_tempo > tempo_max_espera:
                        continue
                    escolhido = n
                    eco = 1
                    break

        carro_escolhido = self.carros[escolhido]

        if eco == 1:
            print("Trocamos o seu carro para um carro eletrico")

        # 4) Condutor já está na cidade do cliente
        if carro_escolhido.local == locCliente:
            carro_escolhido.ocupado = 1
            carro_escolhido.tamanho -= pax
            carro_escolhido.proximaStop = None

            mapa_cliente_destino = c.reconstruir_de_origem(locCliente, obj)
            caminhoAStar, distanciaAStar, calculatempoAStar = mapa_cliente_destino.procura_aStar(
                locCliente, obj
            )

            ValorPagoCliente = pagoCliente(distanciaAStar)

            viagem = Viagem(caminhoAStar, distanciaAStar, calculatempoAStar,
                            numerPedido, ValorPagoCliente)

            carro_escolhido.rota_atual = caminhoAStar[:]  
            carro_escolhido.posicao_atual = caminhoAStar[0]
            carro_escolhido.viagens_ativas.append(viagem)

            self.stat.addTempoPrevisto(calculatempoAStar)
            if eco == 1:
                self.stat.registraCarbono("troca", distanciaAStar, carro_escolhido.tipo)
            self.stat.addViagensPorCidade(locCliente)

            return carro_escolhido

        # 5) Ainda tem de ir ter com o cliente (carro noutra cidade)
        else:
            carro_escolhido.ocupado = 1
            carro_escolhido.tamanho -= pax
            carro_escolhido.proximaStop = obj  

            viagem_ate_cliente = Viagem(melhor_caminho, melhor_distancia, melhor_tempo,
                                        numerPedido)

            carro_escolhido.rota_atual = melhor_caminho[:]  
            carro_escolhido.posicao_atual = melhor_caminho[0]
            carro_escolhido.viagens_ativas.append(viagem_ate_cliente)

            if eco == 1:
                self.stat.registraCarbono("troca", melhor_distancia, carro_escolhido.tipo)
            self.stat.addViagensPorCidade(locCliente)

            return carro_escolhido

    def tick_viagens(self, mapa: Grafo):
        for carro in self.carros:
            carro.tick(mapa, self.stat)

