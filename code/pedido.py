from Graph import Grafo

def pedir(txt: str) -> str:
    try:
        return input(txt).strip()
    except EOFError:
        return ""

class Pedido:
    def __init__(self, numero, mapa):

        while True:
            origem = input("Local de origem: ").strip()
            if mapa.valido(origem) is not None:
                self.origem = origem
                break
            else:
                print(f"'{origem}' não é um ponto válido. Tente novamente.")

        #Verifica destino
        while True:
            destino = input("Local de destino: ").strip()
            if mapa.valido(destino) is not None:
                self.destino = destino
                break
            else:
                print(f"'{destino}' não é um ponto válido. Tente novamente.")

        while True:
            try:
                self.num_pax = int(pedir("Número de passageiros: "))
                if self.num_pax > 0:
                    break
                print("O número de passageiros deve ser maior que zero.")
            except ValueError:
                print("Introduza um número válido.")

        while True:
            try:
                self.tipo_veiculo = int(pedir("Tipo de veículo (0 = combustão, 1 = elétrico): "))
                if self.tipo_veiculo in (0, 1):
                    break
                print("Escolha 0 ou 1.")
            except ValueError:
                print("Introduza um número válido.")

        # Conta premium
        resp = pedir("Conta premium? (s/n): ").lower()
        self.premium = resp == "s"

        resp = pedir("Aceita viagem partilhada? (s/n): ").lower()
        self.partilha = resp == "s"

        while True:
            try:
                self.tempo_max_espera = (float(pedir("Tempo máximo de espera (em minutos): "))/60)
                if self.tempo_max_espera >= 0:
                    break
                print("O tempo máximo deve ser maior ou igual a zero.")
            except ValueError:
                print("Introduza um número válido.")

        self.numero = numero

    def __str__(self):
        return (
            f"Pedido(\n"
            f"  Origem: {self.origem}\n"
            f"  Destino: {self.destino}\n"
            f"  Passageiros: {self.num_pax}\n"
            f"  Tipo veículo: {self.tipo_veiculo}\n"
            f"  Premium: {'Sim' if self.premium else 'Não'}\n"
            f"  Partilha: {'Sim' if self.partilha else 'Não'}\n"
            f"  Tempo máx. espera: {self.tempo_max_espera} h\n"
            f"  Pedido Nº: {self.numero}\n"
            f")"
        )

