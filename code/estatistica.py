class Stat:
    def __init__(self, cidades):

        self.viagensRealizadasEletro = 0
        self.viagensRealizadasCombustao = 0
        self.ViagensPorCidade: dict[str, int] = {cidade: 0 for cidade in cidades}  
        self.carbonoPoupado = 0
        self.totalKmEmviagem = 0
        self.totalKmAtePasagiro = 0
        self.totalHopsAtePassageiro = 0  
        self.tempoTotalPrevisto = 0  
        self.tempoEmViagem = 0  
        self.tempoDeEsperaPassageiro = 0  
        self.ganhoComCombustao = 0  
        self.ganhoComEletrico = 0 
        self.gastoCombustao = 0  
        self.gastoEletrico = 0  
        self.totalTrocasParaEletrico = 0  
        self.totalDePartilhas = 0  
        
    def addTempoPrevisto(self, horas: int):
        self.tempoTotalPrevisto += horas

    def addViagensPorCidade(self, cidade: str):
        self.ViagensPorCidade[cidade] += 1

    def addViagemEletro(self, km: int, horas: int, receita: int, origem: str):
        self.totalKmEmviagem += km
        self.tempoEmViagem += horas
        self.viagensRealizadasEletro += 1
        self.ganhoComEletrico += receita

    def addViagemCombustao(self, km: int, horas: int, receita: int, origem: str):
        self.totalKmEmviagem += km
        self.tempoEmViagem += horas
        self.viagensRealizadasCombustao += 1
        self.ganhoComCombustao += receita

    def abastecerEletro(self, km: int):
        self.gastoEletrico += km * 0.12

    def abastecerCombustao(self, km: int):
        self.gastoCombustao += km * 0.16

    def registraCarbono(self, tipo: str, km: int, tipoCarro: int):
        if tipo == "partilha":
            # eletro gasta 14g e combs gasta 170g
            if tipoCarro:
                self.carbonoPoupado += km * 0.014
            else:
                self.carbonoPoupado += km * 0.170
        if tipo == "troca":
            self.totalTrocasParaEletrico += 1
            self.carbonoPoupado += km * 0.155

    def registraIdaPassageiro(self, nodos: int, horas: int, dist: int):
        self.tempoDeEsperaPassageiro += horas
        self.totalHopsAtePassageiro += nodos
        self.totalKmAtePasagiro += dist

    def __str__(self):
        lucro = self.ganhoComCombustao + self.ganhoComEletrico - self.gastoCombustao - self.gastoEletrico
        linhas = [
            "=== Estatísticas Gerais ===",
            f"Viagens realizadas: {self.viagensRealizadasEletro + self.viagensRealizadasCombustao}",
            f"Viagens por cidade: {self.ViagensPorCidade if self.ViagensPorCidade else '(nenhuma)'}",
            f"Carbono poupado: {self.carbonoPoupado:.2f} kg",
            f"Trocas para elétrico: {self.totalTrocasParaEletrico}",
            f"Viagens partilhadas: {self.totalDePartilhas}",
            "=== Estatísticas Viagens ===",
            f"Total km em viagem: {self.totalKmEmviagem:.2f}",
            f"Total km até passageiro: {self.totalKmAtePasagiro:.2f}",
            f"Total hops até passageiro: {self.totalHopsAtePassageiro}",
            "=== Estatísticas Tempo ===",
            f"Tempo total em viagem: {self.tempoEmViagem:.2f} h",
            f"Tempo de espera passageiro: {self.tempoDeEsperaPassageiro:.2f} h",
            "=== Contabilidade ===",
            f"Ganho com combustão: {self.ganhoComCombustao:.2f} €",
            f"Ganho com elétrico: {self.ganhoComEletrico:.2f} €",
            f"Abastecimentos combustão: {self.gastoCombustao}",
            f"Abastecimentos elétrico: {self.gastoEletrico}",
            f"LucroTotal: {lucro}"
        ]
        return "\n".join(linhas)


