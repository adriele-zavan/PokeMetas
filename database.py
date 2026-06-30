import sqlite3

CAMINHO_DB = "pokemetas.db"

def conectar():
    conexao = sqlite3.connect(CAMINHO_DB)
    conexao.row_factory = sqlite3.Row
    return conexao

def criar_tabelas():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id_discord INTEGER PRIMARY KEY,
            nome TEXT NOT NULL,
            data_entrada TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS metas_globais (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            titulo TEXT NOT NULL,
            pokemon_id INTEGER,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id_discord)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS metas_menores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            meta_global_id INTEGER NOT NULL,
            titulo TEXT NOT NULL,
            xp_recompensa INTEGER NOT NULL,
            concluida INTEGER DEFAULT 0,
            FOREIGN KEY (meta_global_id) REFERENCES metas_globais(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pokemons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dono_id INTEGER NOT NULL,
            nome TEXT NOT NULL,
            numero_pokedex INTEGER NOT NULL,
            xp_atual INTEGER DEFAULT 0,
            nivel_evolucao INTEGER DEFAULT 0,
            evolucoes TEXT NOT NULL,
            FOREIGN KEY (dono_id) REFERENCES usuarios(id_discord)
        )
    """)

    conexao.commit()
    conexao.close()
    print("✅ Tabelas criadas com sucesso!")

def salvar_usuario(id_discord, nome, data_entrada):
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("""
        INSERT OR IGNORE INTO usuarios (id_discord, nome, data_entrada)
        VALUES (?, ?, ?)
    """, (id_discord, nome, data_entrada))
    conexao.commit()
    conexao.close()

def buscar_usuario(id_discord):
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("""
        SELECT * FROM usuarios WHERE id_discord = ?
    """, (id_discord,))
    usuario = cursor.fetchone()
    conexao.close()
    return usuario

def salvar_meta_global(usuario_id, titulo):
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("""
        INSERT INTO metas_globais (usuario_id, titulo)
        VALUES (?, ?)
    """, (usuario_id, titulo))
    id_gerado = cursor.lastrowid
    conexao.commit()
    conexao.close()
    return id_gerado

def buscar_metas_usuario(usuario_id):
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("""
        SELECT * FROM metas_globais WHERE usuario_id = ?
    """, (usuario_id,))
    metas = cursor.fetchall()
    conexao.close()
    return metas

def salvar_pokemon(dono_id, nome, numero_pokedex, evolucoes):
    conexao = conectar()
    cursor = conexao.cursor()
    evolucoes_texto = ",".join(evolucoes)
    cursor.execute("""
        INSERT INTO pokemons (dono_id, nome, numero_pokedex, xp_atual, nivel_evolucao, evolucoes)
        VALUES (?, ?, ?, 0, 0, ?)
    """, (dono_id, nome, numero_pokedex, evolucoes_texto))
    id_gerado = cursor.lastrowid
    conexao.commit()
    conexao.close()
    return id_gerado

def buscar_pokemons_usuario(dono_id):
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("""
        SELECT * FROM pokemons WHERE dono_id = ?
    """, (dono_id,))
    pokemons = cursor.fetchall()
    conexao.close()
    return pokemons

def salvar_meta_menor(meta_global_id, titulo, xp_recompensa=30):
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("""
        INSERT INTO metas_menores (meta_global_id, titulo, xp_recompensa)
        VALUES (?, ?, ?)
    """, (meta_global_id, titulo, xp_recompensa))
    id_gerado = cursor.lastrowid
    conexao.commit()
    conexao.close()
    return id_gerado

def buscar_meta_por_titulo(usuario_id, titulo):
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("""
        SELECT * FROM metas_globais
        WHERE usuario_id = ? AND titulo LIKE ?
    """, (usuario_id, f"%{titulo}%"))
    meta = cursor.fetchone()
    conexao.close()
    return meta

def buscar_metas_menores(meta_global_id):
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("""
        SELECT * FROM metas_menores WHERE meta_global_id = ?
    """, (meta_global_id,))
    metas = cursor.fetchall()
    conexao.close()
    return metas

def concluir_meta_menor_db(meta_menor_id):
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("""
        UPDATE metas_menores SET concluida = 1 WHERE id = ?
    """, (meta_menor_id,))
    conexao.commit()
    conexao.close()

def atualizar_xp_pokemon(pokemon_id, xp_novo, nivel_novo, nome_novo):
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("""
        UPDATE pokemons
        SET xp_atual = ?, nivel_evolucao = ?, nome = ?
        WHERE id = ?
    """, (xp_novo, nivel_novo, nome_novo, pokemon_id))
    conexao.commit()
    conexao.close()

def buscar_pokemon_da_meta(usuario_id, meta_global_id):
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("""
        SELECT p.* FROM pokemons p
        JOIN metas_globais m ON m.pokemon_id = p.id
        WHERE m.id = ? AND m.usuario_id = ?
    """, (meta_global_id, usuario_id))
    pokemon = cursor.fetchone()
    conexao.close()
    return pokemon

def buscar_meta_menor_por_titulo(meta_global_id, titulo):
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("""
        SELECT * FROM metas_menores
        WHERE meta_global_id = ? AND titulo LIKE ? AND concluida = 0
    """, (meta_global_id, f"%{titulo}%"))
    meta = cursor.fetchone()
    conexao.close()
    return meta


def vincular_pokemon_meta(meta_id, pokemon_id):
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("""
        UPDATE metas_globais SET pokemon_id = ? WHERE id = ?
    """, (pokemon_id, meta_id))
    conexao.commit()
    conexao.close()
def deletar_meta(meta_id, usuario_id):
    conexao = conectar()
    cursor = conexao.cursor()

    # Busca o pokemon_id antes de deletar
    cursor.execute("""
        SELECT pokemon_id FROM metas_globais 
        WHERE id = ? AND usuario_id = ?
    """, (meta_id, usuario_id))
    meta = cursor.fetchone()

    if meta and meta["pokemon_id"]:
        # Deleta o pokemon vinculado
        cursor.execute("DELETE FROM pokemons WHERE id = ?", (meta["pokemon_id"],))

    # Deleta as sub-metas
    cursor.execute("DELETE FROM metas_menores WHERE meta_global_id = ?", (meta_id,))

    # Deleta a meta
    cursor.execute("""
        DELETE FROM metas_globais WHERE id = ? AND usuario_id = ?
    """, (meta_id, usuario_id))

    conexao.commit()
    conexao.close()
    
if __name__ == "__main__":
    criar_tabelas()