# TaxiGreen — Sistema Inteligente de Gestão de Táxis

Projeto desenvolvido para a unidade curricular de Inteligência Artificial da Licenciatura em Engenharia Informática da Universidade do Minho, no ano letivo 2025/2026.

## Grupo 11

- Diogo Alves Ferreira - A106904
- Hugo Araújo Cunha - A106808
- José Miguel da Silva Santos - A72443
- Mariana Vivas Rodrigues - A106898

## Sobre o projeto

O TaxiGreen é uma simulação de um sistema de gestão de uma frota de táxis elétricos e a combustão, com o objetivo de otimizar a atribuição de veículos aos passageiros e a escolha dos percursos numa rede de cidades.

O projeto implementa e compara diferentes algoritmos de procura em grafos (DFS, BFS, BFS bidirecional, Dijkstra, Greedy e A*). A simulação considera fatores como a distância, a disponibilidade e a autonomia dos veículos, o tempo máximo de espera e os incidentes rodoviários.
Inclui ainda viagens partilhadas, gestão de abastecimentos e carregamentos, prioridade para pedidos premium, visualização de percursos e estatísticas de desempenho.

## Tecnologias utilizadas

- **Python** - Implementação dos algoritmos de procura e da simulação.
- **NetworkX** - Representação e manipulação de grafos.
- **Matplotlib** - Visualização dos grafos.
- **Leaflet (HTML/JavaScript)** - Visualização da rede de cidades num mapa interativo.
- **JSON** - Armazenamento dos dados dos cenários, veículos, distâncias e incidentes.

## Executar

Python 3.10 ou superior instalado.

Na pasta raiz do projeto, instala as dependências:

```bash
python -m pip install networkx matplotlib
```

Inicia a aplicação:

```bash
python code/main.py
```

O programa apresenta um menu no terminal para consultar o grafo, executar os algoritmos de procura e aceder à simulação de gestão de táxis.

Para experimentar a simulação, escolhe a opção 11 - App uber. Nesse submenu, podes criar pedidos, avançar o tempo, consultar os veículos e visualizar estatísticas. Depois de selecionar essa opção, vai surgir um novo menu onde a opção 6 - Desenhar mapa (Leaflet) gera o ficheiro `data/mapa_leaflet.html` e tenta abri-lo no navegador.

O cenário utilizado por predefinição é o de Braga.

### Executar os testes

Para abrir o menu de testes:

```bash
python code/testes.py
```

Estão disponíveis dois cenários:
- **Teste de carga intensiva:** simula vários pedidos de transporte numa frota limitada.
- **Teste de viagens partilhadas:** verifica a partilha na origem, durante o percurso e com extensão da rota.

## Estrutura do projeto

```text
TaxiGreen/
├── code/
│   ├── main.py          
│   ├── Graph.py        
│   ├── nodo.py       
│   ├── cidades.py       
│   ├── empresa.py       
│   ├── carro.py         
│   ├── pedido.py       
│   ├── viagem.py       
│   ├── parsing.py       
│   ├── data.py         
│   ├── leaflet_map.py   
│   ├── metricas.py      
│   ├── estatistica.py   
│   └── testes.py        
├── data/
│   ├── cidades_braga.json   
│   ├── dists_braga.json     
│   ├── carros_braga.json   
│   ├── incidentes_braga.json #
│   ├── ...                  
│   └── mapa_leaflet.html    
└── README.md
```

Os ficheiros `code/data.py` e `code/main.py` contêm a configuração utilizada para o cenário inicial.
