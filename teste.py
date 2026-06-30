# teste.py
from database import criar_tabelas, salvar_usuario, buscar_usuario, salvar_meta_global, buscar_metas_usuario, salvar_pokemon, buscar_pokemons_usuario
from datetime import datetime

# Garante que as tabelas existem
criar_tabelas()

# Salvando um usuário
print("── Testando usuário ──")
salvar_usuario(
    id_discord=123456,
    nome="Ash Ketchum",
    data_entrada=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
)

# Buscando o usuário salvo
usuario = buscar_usuario(123456)
print(f"Usuário encontrado: {usuario['nome']} | ID: {usuario['id_discord']}")

# Salvando uma meta global
print("\n── Testando meta global ──")
id_meta = salvar_meta_global(usuario_id=123456, titulo="Cuidados Pessoais")
print(f"Meta criada com ID: {id_meta}")

# Buscando metas do usuário
metas = buscar_metas_usuario(123456)
for meta in metas:
    print(f"Meta: {meta['titulo']}")

# Salvando um pokemon
print("\n── Testando pokemon ──")
id_pokemon = salvar_pokemon(
    dono_id=123456,
    nome="Bulbasaur",
    numero_pokedex=1,
    evolucoes=["Bulbasaur", "Ivysaur", "Venusaur"]
)
print(f"Pokemon salvo com ID: {id_pokemon}")

# Buscando pokemons do usuário
pokemons = buscar_pokemons_usuario(123456)
for p in pokemons:
    print(f"Pokemon: {p['nome']} | XP: {p['xp_atual']} | Evoluções: {p['evolucoes']}")