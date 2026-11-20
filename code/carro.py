from __future__ import annotations

import json
import sys
from pathlib import Path

from data import COMBS_LOCAL_JSON, ELETRIC_LOCAL_JSON

percetMinimaComb = 0.2


class Carro:
    def __init__(self, tamanho: int, deposito: int, tipo: int, nome: str, autonomia: int):
        self.tamanho = tamanho
        self.deposito = deposito
        self.tipo = tipo  # 0 = combustão, 1 = elétrico
        self.nome = nome
        self.combustivel_atual = 100
        self.autonomia = autonomia
        self.alcance = autonomia
        self.local = "Porto"
        self.ocupado = 0
        self.proximaStop = None  
        self.ondeCarregar = None  
        self.viagem_principal = None  

        self.rota_atual: list[str] = []  
        self.posicao_atual: str = self.local
        self.viagens_ativas: list[Viagem] = [] 

        self.postos_comb = self._carrega_postos(COMBS_LOCAL_JSON)
        self.postos_eletro = self._carrega_postos(ELETRIC_LOCAL_JSON)

    def _carrega_postos(self, caminho: str | Path) -> list[str]:
        caminho_arquivo = Path(caminho)
        try:
            with open(caminho_arquivo, "r", encoding="utf-8") as f:
                dados = json.load(f)
        except FileNotFoundError:
            return []
        return [str(x) for x in dados]

    def procuraPostos(self, caminho: list[str], mapa) -> tuple[bool, str | None]:
        postos = self.postos_comb if self.tipo == 0 else self.postos_eletro
        for cidade in caminho:
            if cidade not in postos:
                continue
            sub_caminho = []
            for c in caminho:
                sub_caminho.append(c)
                if c == cidade:
                    break
            if mapa.calcula_custo(sub_caminho) <= self.autonomia:
                return True, cidade

        origem = self.posicao_atual
        melhor_posto = None
        melhor_dist = float("inf")
        for posto in postos:
            caminho_posto, dist_posto, _ = mapa.procura_BFS_bi(origem, posto)
            if not caminho_posto:
                continue
            if dist_posto <= self.autonomia and dist_posto < melhor_dist:
                melhor_dist = dist_posto
                melhor_posto = posto

        return False, melhor_posto

    def precisaCarregar(self, mapa) -> bool:
        if not self.viagens_ativas:
            return False

        viagem_principal = self.viagens_ativas[0]
        dist_restante = mapa.calcula_custo(viagem_principal.rota)

        if dist_restante <= self.autonomia:
            return False

        no_caminho, posto = self.procuraPostos(viagem_principal.rota, mapa)
        if not posto:
            return False

        self.ondeCarregar = posto
        if no_caminho:
            return True

        from cidades import Cidades
        c = Cidades()
        origem = self.posicao_atual

        for v in self.viagens_ativas:
            mapa_posto = c.reconstruir_de_origem(origem, posto)
            cam1, _, _ = mapa_posto.procura_aStar(origem, posto)
            mapa_destino = c.reconstruir_de_origem(posto, v.destino)
            cam2, _, _ = mapa_destino.procura_aStar(posto, v.destino)
            if cam1 and cam2 and cam1[-1] == cam2[0]:
                v.rota = cam1 + cam2[1:]
            else:
                v.rota = (cam1 or []) + (cam2 or [])

        print(f"\033[33mRota do carro {self.nome} alterou rota para poder abastecer\033[0m")
        self.rota_atual = self.viagens_ativas[0].rota[:]
        if self.rota_atual:
            self.posicao_atual = self.rota_atual[0]
        return True

    def abastecer(self):
        quantidade = self.alcance - self.autonomia
        self.autonomia = self.alcance
        return quantidade

    def abastecerEletro(self):
        quantidade = self.alcance - self.autonomia
        self.autonomia = self.alcance
        return quantidade

    def finalizaViagem(self, dist: int):
        self.autonomia -= dist

    def getCapacidade(self):
        return self.tamanho

    def atualizarLocal(self, newLocal: str):
        self.local = newLocal

    def tick(self, mapa, stat):
        """
        Avança um 'tick' para este carro:
        - trata carregamento em ondeCarregar (elétricos),
        - anda um arco na rota_atual,
        - atualiza todas as viagens_ativas,
        - se uma viagem terminar e houver proximaStop, cria a viagem cliente -> destino final.
        """

        # se não tiver rota, não faz nada
        if not self.rota_atual or len(self.rota_atual) < 2:
            return

        # Carro elétrico parado a carregar num posto específico
        if self.tipo == 1 and self.ondeCarregar is not None and self.local == self.ondeCarregar:
            for v in self.viagens_ativas:
                v.tempo += 1
            quantidadeLuz = self.abastecerEletro()
            stat.abastecerEletro(quantidadeLuz)
            self.ondeCarregar = None
            return


        origem = self.rota_atual[0]
        destino = self.rota_atual[1]
        dist = mapa.get_arc_cost(origem, destino)

        # verificar combustível/autonomia
        self.precisaCarregar(mapa)
        if self.rota_atual and len(self.rota_atual) >= 2:
            origem = self.rota_atual[0]
            destino = self.rota_atual[1]
            dist = mapa.get_arc_cost(origem, destino)
        print(f"[DEBUG] Carro {self.nome} | local={self.local} | autonomia={self.autonomia} | ondeCarregar={self.ondeCarregar} | prox={origem}->{destino} ({dist})")
        # se é combustão
        if self.tipo == 0:  
            if self.ondeCarregar is not None and self.local == self.ondeCarregar:
                for v in self.viagens_ativas:
                    v.tempo += 0.10
                combustivel = self.abastecer()
                stat.abastecerCombustao(combustivel)
                print(f"\033[32mAbasteci carro {self.nome} || local: {self.local} || quantidade: {combustivel}\033[0m")
                self.ondeCarregar = None

        else: 
            if self.ondeCarregar is not None and self.local == self.ondeCarregar:
                for v in self.viagens_ativas:
                    v.tempo += 1
                quantidadeLuz = self.abastecerEletro()
                stat.abastecerEletro(quantidadeLuz)
                print("\033[34mCarro Carregado --- " + str(self.autonomia) + "\033[0m")
                print(f"\033[32mAbasteci carro {self.nome} || local: {self.local} || quantidade: {quantidadeLuz}\033[0m")
                self.ondeCarregar = None

        
        if self.autonomia < dist:
            print("\033[31mERRO FIQUEI PARADO SEM PODER ANDAR\033[0m")
            sys.exit("Esta a arder")
        else:
            self.autonomia -= dist

        self.rota_atual.pop(0)
        self.posicao_atual = destino
        self.local = destino

        # 2. atualizar as viagens ativas consoante a cidade
        viagens_finalizadas = []
        for viagem in self.viagens_ativas:
            if len(viagem.rota) >= 2 and viagem.rota[0] == origem and viagem.rota[1] == destino:
                viagem.rota.pop(0)
                if len(self.viagens_ativas) == 1:
                    from cidades import Cidades
                    c = Cidades()
                    mapa_novo = c.reconstruir_de_origem(self.posicao_atual, viagem.destino)
                    novo_path, _, _ = mapa_novo.procura_aStar(self.posicao_atual, viagem.destino)
                    if novo_path:
                        viagem.rota = novo_path
            viagem.progresso += dist
            viagem.tempo += dist / 80
            viagem.posicao_atual = self.posicao_atual
            if not viagem.rota_feita or viagem.rota_feita[-1] != viagem.posicao_atual:
                viagem.rota_feita.append(viagem.posicao_atual)

            if self.posicao_atual == viagem.destino:
                viagens_finalizadas.append(viagem)

        # 3. tratar das viagens que acabaram
        for v in viagens_finalizadas:
            # CASO ESPECIAL: era só a ida até ao cliente (carro noutra cidade)
            if self.proximaStop is not None and self.posicao_atual == v.destino:
                from cidades import Cidades     
                from viagem import Viagem

                stat.registraIdaPassageiro(v.nodos, v.tempo, v.progresso)

                destino_novo = self.proximaStop  
                self.proximaStop = None

                #cria nova viagem
                c = Cidades()
                mapa_cliente_destino = c.reconstruir_de_origem(self.posicao_atual, destino_novo)
                caminho, dist_nova, temp_novo = mapa_cliente_destino.procura_aStar(
                    self.posicao_atual, destino_novo
                )

                stat.addTempoPrevisto(temp_novo)
                ValorPagoCliente = dist_nova * 0.6

                numPedidoAUX = v.numPedido
                nova_viagem = Viagem(caminho, dist_nova, temp_novo, numPedidoAUX, ValorPagoCliente)

                self.rota_atual = caminho[:]
                self.posicao_atual = caminho[0]

                self.viagens_ativas.remove(v)
                self.viagens_ativas.append(nova_viagem)

            #viagem já com passageiro a bordo
            else:
                print(f"\033[92m Viagem concluida do carro {self.nome}: {v.origem} -> {v.destino}\033[0m")
                print(f"Distância percorrida: {v.progresso} km")
                print(f"Tempo estimado total: {v.tempo_totalPrevisto}h")
                print(f"Distância estimada: {v.distancia_total} km")
                print(f"Tempo Total: {v.tempo}h")
                try:
                    from leaflet_map import gerar_mapa_html
                    gerar_mapa_html(highlight_path=v.rota_feita)
                except Exception:
                    pass
                if self.tipo == 0:
                    stat.addViagemCombustao(v.progresso, v.tempo, v.faturado, v.origem)
                else:
                    stat.addViagemEletro(v.progresso, v.tempo, v.faturado, v.origem)

                self.viagens_ativas.remove(v)

        # 4. se já não há viagens ativas, marca o carro como livre
        if not self.viagens_ativas:
            self.ocupado = 0
            self.rota_atual = []


    def printCarro(self):
        tipo_str = "Combustão" if self.tipo == 0 else "Elétrico"
        status = "Ocupado" if self.ocupado else "Livre"
        print(f" {self.nome}")
        print(f"   Tamanho: {self.tamanho}")
        if self.tipo == 0:
            print(f"   Depósito: {self.deposito} L")
            print("   Tipo: Combustão")
        else:
            print(f"   Depósito: {self.deposito} Kwh")
            print("   Tipo: Elétrico")
        combustivel_atual = self.autonomia / self.alcance
        print(f"   Combustível atual: {combustivel_atual}%")
        print(f"   Autonomia: {self.autonomia} km")
        print(f"   Localização: {self.local}")
        print(f"   Estado: {status}")

