class Pokemon:
    def __init__(self, nome, evolucoes, numero_pokedex, xp_atual, nivel_evolucao, dono_id):
        self.nome = nome
        self.evolucoes = evolucoes
        self.numero_pokedex = numero_pokedex
        self.xp_atual = xp_atual
        self.nivel_evolucao = nivel_evolucao
        self.dono_id = dono_id



    def ganhar_xp(self, quantidade):
        self.xp_atual += quantidade
        print(f"⚡ {self.nome} ganhou {quantidade} XP! Total: {self.xp_atual}")

        self.verificar_evolucao()


    def verificar_evolucao(self):
        if self.xp_atual >= 100 and self.nivel_evolucao < len(self.evolucoes) -1  :
            self.nivel_evolucao += 1
            self.nome = self.evolucoes[self.nivel_evolucao]
            print(f"🌟 SEU POKÉMON EVOLUIU PARA {self.nome.upper()}!")


    def __str__(self):
        return f"🐾 {self.nome} | XP: {self.xp_atual} | Nível evolução: {self.nivel_evolucao}"