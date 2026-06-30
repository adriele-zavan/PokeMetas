from datetime import datetime

class Usuario:

    def  __init__(self, id_discord, nome):

        self.id_discord = id_discord
        self.nome = nome
        self.metas = []
        self.data_entrada = datetime.now()



    def  adicionar_meta(self, meta):
        self.metas.append(meta)


    def __str__(self):
        return f"Treinador {self.nome} | Metas: {len(self.metas)}"

