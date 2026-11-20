from __future__ import annotations

from pathlib import Path

CODE_DIR = Path(__file__).resolve().parent
PROJETO_ROOT = CODE_DIR.parent
DATA_DIR = PROJETO_ROOT / "data"

DATASET_ATIVO = "braga"

LEAFLET_HTML = DATA_DIR / "mapa_leaflet.html"

if DATASET_ATIVO == "braga":
    CIDADES_JSON = DATA_DIR / "cidades_braga.json"
    DISTS_JSON = DATA_DIR / "dists_braga.json"
    INCIDENTES_JSON = DATA_DIR / "incidentes_braga.json"
    CARROS_JSON = DATA_DIR / "carros_braga.json"
    COMBS_LOCAL_JSON = DATA_DIR / "combsLocal_braga.json"
    ELETRIC_LOCAL_JSON = DATA_DIR / "eletricLocal_braga.json"
else:
    CIDADES_JSON = DATA_DIR / "cidades.json"
    DISTS_JSON = DATA_DIR / "dists.json"
    INCIDENTES_JSON = DATA_DIR / "incidentes.json"
    CARROS_JSON = DATA_DIR / "carros.json"
    COMBS_LOCAL_JSON = DATA_DIR / "combsLocal.json"
    ELETRIC_LOCAL_JSON = DATA_DIR / "eletricLocal.json"
