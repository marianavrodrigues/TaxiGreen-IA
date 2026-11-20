from __future__ import annotations
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import math

from data import CIDADES_JSON, DISTS_JSON, INCIDENTES_JSON
from parsing import read_nodes, read_edges, read_incidents
from Graph import Grafo
from nodo import Node


class Cidades:
    def __init__(
        self,
        locFicheiroCidades: str | Path = CIDADES_JSON,
        locFicheiroRotas: str | Path = DISTS_JSON,
        locFicheiroIncidentes: Optional[str | Path] = INCIDENTES_JSON,
    ):
        
        self._nodes_src = locFicheiroCidades
        self._edges_src = locFicheiroRotas
        self._inc_src   = locFicheiroIncidentes

        self.cidadesLista: List[tuple[str, int, int]] = read_nodes(self._nodes_src)
        self.rotasLista: List[tuple[str, str, float]] = read_edges(self._edges_src)
        try:
            self.incidentesLista: List[tuple[str, str, str, float]] = read_incidents(self._inc_src)
        except Exception:
            self.incidentesLista = []


        self.coords: Dict[str, tuple[int, int]] = {name: (x, y) for name, x, y in self.cidadesLista}


        self._g: Optional[Grafo] = None
        self._origem: Optional[str] = None
        self._destino: Optional[str] = None

    def criar_grafo(self, origem: str, destino: str, directed: bool = False) -> Grafo:
        if origem not in self.coords or destino not in self.coords:
            raise KeyError(f"Origem/destino inválido(s): {origem}, {destino}")

        g = Grafo(directed=directed)
        
        for nome in self.coords.keys():
            n = Node(nome)
            if n not in g.m_nodes:
                g.m_nodes.append(n)
                if nome not in g.m_graph:
                    g.m_graph[nome] = list()

        self._g = g
        self._origem = origem
        self._destino = destino
        return g

    def calcular_heuristicas(self) -> None:
        if self._g is None or self._destino is None:
            raise RuntimeError("Chama criar_grafo(origem, destino) primeiro.")
        (xg, yg) = self.coords[self._destino]
        for nome, (xu, yu) in self.coords.items():
            base = math.hypot(xu - xg, yu - yg)
            self._g.add_heuristica(nome, base)


    def adicionar_arestas(self) -> None:
        if self._g is None:
            raise RuntimeError("Chama criar_grafo(origem, destino) primeiro.")
        for u, v, d in self.rotasLista:
            self._g.add_edge(u, v, d)


    def aplicar_incidentes_em_arestas(self, undirected: bool = True) -> None:
        if self._g is None:
            raise RuntimeError("Chama criar_grafo(...) e adicionar_arestas() primeiro.")

        g = self._g

        for (inc_u, inc_v, _tipo, fator) in self.incidentesLista:
            f = float(fator)

            for u in g.m_graph.keys():
                adj = g.m_graph[u]
                for i, (v, peso) in enumerate(adj):
                    if u == inc_u and v == inc_v:
                        adj[i] = (v, peso * f)

                    if undirected and u == inc_v and v == inc_u:
                        adj[i] = (v, peso * f)





    def reconstruir_de_origem(self, origem: str, destino: str, directed: bool = False) -> Grafo:
        
        g = self.criar_grafo(origem, destino, directed=directed)
        self.calcular_heuristicas()
        self.adicionar_arestas()
        self.aplicar_incidentes_em_arestas()
        return g

    def caminho_astar(self, start: str, goal: str):
        if self._g is None or self._destino != goal:
            raise RuntimeError("Reconstrói com destino correto antes de correr A*.")
        return self._g.procura_aStar(start, goal)

    def nodos(self) -> list[str]:
        return list(self.coords.keys())

    def arestas(self) -> list[tuple[str, str, float]]:
        return list(self.rotasLista)

    def incidentes(self) -> list[tuple[str, str, str, float]]:
        return list(self.incidentesLista)
