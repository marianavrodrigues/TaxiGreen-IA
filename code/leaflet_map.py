from __future__ import annotations

import json
from pathlib import Path

from data import (
    CIDADES_JSON,
    DISTS_JSON,
    LEAFLET_HTML,
    COMBS_LOCAL_JSON,
    ELETRIC_LOCAL_JSON,
)


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def gerar_mapa_html(
    output_path: str | Path = LEAFLET_HTML,
    nodes_path: str | Path = CIDADES_JSON,
    edges_path: str | Path = DISTS_JSON,
    combs_path: str | Path = COMBS_LOCAL_JSON,
    eletric_path: str | Path = ELETRIC_LOCAL_JSON,
    highlight_path: list[str] | None = None,
) -> str:
    nodes_file = Path(nodes_path).resolve()
    edges_file = Path(edges_path).resolve()
    out_file = Path(output_path).resolve()
    combs_file = Path(combs_path).resolve()
    eletric_file = Path(eletric_path).resolve()

    nodes_raw = _load_json(nodes_file)
    edges_raw = _load_json(edges_file)
    combs_raw = _load_json(combs_file) if combs_file.exists() else []
    eletric_raw = _load_json(eletric_file) if eletric_file.exists() else []

    nodes = {name: (float(x), float(y)) for name, x, y in nodes_raw}
    combs_set = {str(x) for x in combs_raw}
    eletric_set = {str(x) for x in eletric_raw}

    xs = [coord[0] for coord in nodes.values()]
    ys = [coord[1] for coord in nodes.values()]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    markers_js = []
    for name, (x, y) in nodes.items():
        dot = ""
        if name in combs_set and name in eletric_set:
            dot = (
                "<span class='dot dot-comb'></span>"
                "<span class='dot dot-eletric'></span> "
            )
        elif name in combs_set:
            dot = "<span class='dot dot-comb'></span> "
        elif name in eletric_set:
            dot = "<span class='dot dot-eletric'></span> "
        markers_js.append(
            "L.marker([{y}, {x}]).addTo(map)"
            ".bindPopup({label})"
            ".bindTooltip({label}, {{permanent: true, direction: 'bottom', offset: [0, 8], className: 'node-label'}});"
            .format(y=y, x=x, label=json.dumps(f"{dot}{name}"))
        )

    edges_js = []
    for n1, n2, _dist in edges_raw:
        if n1 not in nodes or n2 not in nodes:
            continue
        x1, y1 = nodes[n1]
        x2, y2 = nodes[n2]
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2
        edges_js.append(
            f"L.polyline([[{y1}, {x1}], [{y2}, {x2}]], "
            "{color: '#1f2937', weight: 2, opacity: 0.7}).addTo(map);"
        )
        label = json.dumps(str(_dist))
        edges_js.append(
            f"L.marker([{mid_y}, {mid_x}], "
            f"{{icon: L.divIcon({{className: 'edge-label', html: {label}}}), interactive: false}})"
            ".addTo(map);"
        )

    highlight_js = ""
    if highlight_path:
        coords = []
        for nome in highlight_path:
            if nome in nodes:
                x, y = nodes[nome]
                coords.append([y, x])
        if len(coords) >= 2:
            highlight_js = (
                "L.polyline({coords}, "
                "{{color: '#dc2626', weight: 4, opacity: 0.9}}).addTo(map);"
            ).format(coords=json.dumps(coords))

    html = f"""<!doctype html>
<html lang="pt">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width,initial-scale=1" />
    <title>Mapa do Grafo</title>
    <link
      rel="stylesheet"
      href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
      integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY="
      crossorigin=""
    />
    <style>
      html, body, #map {{
        height: 100%;
        margin: 0;
      }}
      .edge-label {{
        color: #b91c1c;
        font-size: 12px;
        font-weight: 600;
        text-shadow: 0 1px 2px rgba(255,255,255,0.9);
        white-space: nowrap;
      }}
      .leaflet-tooltip.node-label {{
        background: transparent;
        border: none;
        box-shadow: none;
        color: #111827;
        font-size: 12px;
        font-weight: 600;
        text-shadow: 0 1px 2px rgba(255,255,255,0.9);
        padding: 0;
      }}
      .dot {{
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        margin-right: 4px;
        vertical-align: middle;
        box-shadow: 0 0 0 1px rgba(0,0,0,0.2);
      }}
      .dot-comb {{ background: #f97316; }}
      .dot-eletric {{ background: #16a34a; }}
    </style>
  </head>
  <body>
    <div id="map"></div>
    <script
      src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
      integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo="
      crossorigin=""
    ></script>
    <script>
      const map = L.map('map', {{
        crs: L.CRS.Simple,
        zoomControl: true
      }});

      const bounds = L.latLngBounds(
        [{min_y}, {min_x}],
        [{max_y}, {max_x}]
      );
      map.fitBounds(bounds.pad(0.1));

      {chr(10).join(edges_js)}
      {highlight_js}
      {chr(10).join(markers_js)}
    </script>
  </body>
</html>
"""

    out_file.write_text(html, encoding="utf-8")
    return str(out_file)


if __name__ == "__main__":
    caminho = gerar_mapa_html()
    print(f"Mapa gerado em: {caminho}")
