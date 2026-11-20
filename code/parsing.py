from __future__ import annotations
from typing import List, Tuple, Any
from pathlib import Path
import json

from carro import Carro
from data import CARROS_JSON


def _load_text(source: str | Path) -> str:
    p = Path(str(source))
    if p.exists():
        return p.read_text(encoding="utf-8").strip()
    return str(source).strip()


def _coerce_to_python(data_str: str) -> Any:
    try:
        return json.loads(data_str)
    except json.JSONDecodeError:
        pass


def _ensure_list_of_lists(obj: Any) -> List[List[Any]]:
    if isinstance(obj, list) and all(not isinstance(x, (list, tuple)) for x in obj):
        return [list(obj)]
    if isinstance(obj, list):
        return [list(x) if not isinstance(x, list) else x for x in obj]
    raise ValueError("Formato inesperado")


def read_nodes(source: str | Path) -> List[Tuple[str, int, int]]:
    data = _coerce_to_python(_load_text(source))
    rows = _ensure_list_of_lists(data)
    out: List[Tuple[str, int, int]] = []
    for r in rows:
        if len(r) < 3:
            raise ValueError(f"Nodo inválido: {r}")
        name, x, y = r[0], int(r[1]), int(r[2])
        out.append((str(name), x, y))
    return out


def read_edges(source: str | Path) -> List[Tuple[str, str, float]]:
    data = _coerce_to_python(_load_text(source))
    rows = _ensure_list_of_lists(data)
    out: List[Tuple[str, str, float]] = []
    for r in rows:
        if len(r) < 3:
            raise ValueError(f"Aresta inválida: {r}")
        n1, n2, dist = str(r[0]), str(r[1]), float(r[2])
        out.append((n1, n2, dist))
    return out


def read_incidents(source: str | Path) -> List[Tuple[str, str, str, float]]:
    data = _coerce_to_python(_load_text(source))
    rows = _ensure_list_of_lists(data)
    out: List[Tuple[str, str, str, float]] = []
    for r in rows:
        if len(r) < 4:
            raise ValueError(f"Incidente inválido: {r}")
        n1, n2, tipo, fator = str(r[0]), str(r[1]), str(r[2]), float(r[3])
        out.append((n1, n2, tipo, fator))
    return out


def carregar_carros() -> list[Carro]:
    with open(CARROS_JSON, "r", encoding="utf-8") as f:
        dados = json.load(f)

    carros = []
    for d in dados:
        c = Carro(
            tamanho=d["tamanho"],
            deposito=d["deposito"],
            tipo=d["tipo"],
            nome=d["nome"],
            autonomia=d["autonomia"],
        )
        if "local" in d:
            c.atualizarLocal(d["local"])
        carros.append(c)
    return carros

