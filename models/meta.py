class MetaMenor:
    def __init__(self, titulo,xp_recompensa):
        self.titulo = titulo
        self.xp_recompensa = xp_recompensa
        self.concluida = False

    def concluir(self):
            self.concluida = True
            print(f"✅ Meta '{self.titulo}' concluída! + {self.xp_recompensa} XP!")

class MetaGlobal:
    def __init__(self, titulo, usuario_id):
        self.titulo = titulo
        self.usuario_id = usuario_id
        self.metas_menores = []
        self.pokemon_id = None 

    
    def adicionar_meta_menor(self, meta_menor):
        self.metas_menores.append(meta_menor)
    
    def xp_total(self):
        total = 0
        for meta in self.metas_menores:
            if meta.concluida:
                total += meta.xp_recompensa
        return total

    
    def __str__(self):
        return f"🎯 {self.titulo} | XP acumulado: {self.xp_total()}"