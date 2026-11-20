from __future__ import annotations

from Graph import Grafo
from cidades import Cidades


class Viagem:
    def __init__(self, rota: list[str], distancia_total: float, tempo_totalPrevisto: float,numeroPedido: int | None = None,valorPago: int | None = None):

        self.rota = rota
        self.rota_original = rota[:]
        self.rota_feita = [rota[0]] if rota else []
        self.origem = rota[0]
        self.destino = rota[-1]
        self.distancia_total = distancia_total
        self.tempo_totalPrevisto = tempo_totalPrevisto
        self.tempo = 0
        self.posicao_atual = self.origem
        self.progresso = 0
        self.numPedido = numeroPedido
        self.nodos = 0
        if valorPago == None:
            self.faturado = 0
        else:
            self.faturado = valorPago

    def avancar(self, mapa:Grafo):
        if not self.rota or len(self.rota) < 2:
            return 0
        n = mapa.get_arc_cost(self.posicao_atual,self.rota[1])
        self.progresso += n
        self.tempo += n/80
        self.posicao_atual = self.rota[1]
        self.rota.pop(0)
        if len(self.rota) == 1:
            return 0
        c = Cidades()
        mapa = c.reconstruir_de_origem(self.rota[0], self.destino)
        caminho, distancia, tempo = mapa.procura_aStar(self.rota[0], self.rota[-1])
        self.rota = caminho
        self.nodos += 1
        return n


    def status(self):
        print(f"Numero de pedido: {self.numPedido}")
        print(f"Origem: {self.origem}")
        print(f"Destino: {self.destino}")
        print(f"Local atual: {self.posicao_atual}")
        print(f"Distância percorrida: {self.progresso:.1f} km / {self.distancia_total} km")
        print(f"Tempo estimado total: {self.tempo_totalPrevisto}h")
        print(f"Rota: {self.rota}")

