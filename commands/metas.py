# commands/metas.py

import discord
from discord.ext import commands
import random
import aiohttp
from database import (
    salvar_usuario,
    salvar_meta_global,
    salvar_pokemon,
    buscar_metas_usuario,
    buscar_pokemons_usuario,
    buscar_meta_por_titulo,
    salvar_meta_menor,
    buscar_pokemon_da_meta,
    atualizar_xp_pokemon,
    concluir_meta_menor_db,
    buscar_meta_menor_por_titulo,
    vincular_pokemon_meta,
    buscar_metas_menores,
    deletar_meta
)
from datetime import datetime


class MetasCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.pendente_deletar = {}

    async def buscar_pokemon_api(self, nome_ou_numero):
        async with aiohttp.ClientSession() as session:
            url = f"https://pokeapi.co/api/v2/pokemon-species/{nome_ou_numero}"
            async with session.get(url) as resposta:
                if resposta.status == 404:
                    return None
                dados = await resposta.json()
                nome = dados["name"]
                for nome_traduzido in dados["names"]:
                    if nome_traduzido["language"]["name"] == "pt-BR":
                        nome = nome_traduzido["name"]
                        break
                evo_url = dados["evolution_chain"]["url"]
                async with session.get(evo_url) as evo_resposta:
                    evo_dados = await evo_resposta.json()
                    evolucoes = []
                    evo_atual = evo_dados["chain"]
                    while evo_atual:
                        evolucoes.append(evo_atual["species"]["name"])
                        if evo_atual["evolves_to"]:
                            evo_atual = evo_atual["evolves_to"][0]
                        else:
                            break
                    if len(evolucoes) < 2:
                        return None
                    nome_base = evolucoes[0]
                    async with session.get(f"https://pokeapi.co/api/v2/pokemon/{nome_base}") as base_resposta:
                        base_dados = await base_resposta.json()
                        numero = base_dados["id"]
                    nome = nome_base
                    return numero, nome, evolucoes

    async def sortear_pokemon(self):
        while True:
            numero = random.randint(1, 1025)
            resultado = await self.buscar_pokemon_api(numero)
            if resultado is not None:
                return resultado

    def calcular_xp_necessario(self, evolucoes):
        if len(evolucoes) == 2:
            return 50
        else:
            return 100

    @commands.command()
    async def criarmeta(self, ctx, titulo: str, *, pokemon_escolhido: str = None):
        usuario_id = ctx.author.id
        usuario_nome = ctx.author.display_name
        salvar_usuario(
            id_discord=usuario_id,
            nome=usuario_nome,
            data_entrada=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        meta_id = salvar_meta_global(usuario_id=usuario_id, titulo=titulo)
        if pokemon_escolhido:
            await ctx.send(f"🔍 Procurando {pokemon_escolhido}...")
            resultado = await self.buscar_pokemon_api(pokemon_escolhido.lower())
            if resultado is None:
                await ctx.send(
                    f"⚠️ **{pokemon_escolhido}** não foi encontrado ou não possui evolução!\n"
                    f"Tente outro nome. Exemplo: `!criarmeta {titulo} Bulbasaur`"
                )
                return
        else:
            await ctx.send("🎲 Sorteando seu Pokémon...")
            resultado = await self.sortear_pokemon()
        numero, nome, evolucoes = resultado
        xp_necessario = self.calcular_xp_necessario(evolucoes)
        pokemon_id = salvar_pokemon(dono_id=usuario_id, nome=nome, numero_pokedex=numero, evolucoes=evolucoes)
        vincular_pokemon_meta(meta_id, pokemon_id)
        embed = discord.Embed(title="🎯 Nova Meta Criada!", color=discord.Color.green())
        embed.set_thumbnail(url=f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{numero}.png")
        embed.add_field(name="Meta", value=titulo, inline=False)
        embed.add_field(name="Pokémon Capturado", value=f"#{numero} {nome.capitalize()}", inline=True)
        embed.add_field(name="Evoluções", value=" → ".join(evolucoes), inline=True)
        embed.add_field(name="XP para evoluir", value=f"{xp_necessario} XP", inline=True)
        embed.set_footer(text=f"Treinador: {usuario_nome}")
        await ctx.send(embed=embed)

    @commands.command()
    async def minhasmetas(self, ctx):
        usuario_id = ctx.author.id
        metas = buscar_metas_usuario(usuario_id)
        if not metas:
            await ctx.send("❌ Você não tem nenhuma meta ainda! Use `!criarmeta [titulo]`")
            return
        embed = discord.Embed(title="📋 Suas Metas", color=discord.Color.blue())
        for meta in metas:
            submetas = buscar_metas_menores(meta["id"])
            if submetas:
                texto_submetas = "\n".join([f"{'✅' if sub['concluida'] else '•'} {sub['titulo']}" for sub in submetas])
            else:
                texto_submetas = "*Nenhuma submeta criada.*"
            embed.add_field(name=f"🎯 {meta['titulo']}", value=texto_submetas, inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def adicionarsubmeta(self, ctx, meta_titulo: str, *, subtitulo: str):
        usuario_id = ctx.author.id
        meta = buscar_meta_por_titulo(usuario_id, meta_titulo)
        if not meta:
            await ctx.send(f"❌ Meta **'{meta_titulo}'** não encontrada!\nUse `!minhasmetas` para ver suas metas.")
            return
        salvar_meta_menor(meta_global_id=meta["id"], titulo=subtitulo, xp_recompensa=30)
        embed = discord.Embed(title="✅ Sub-meta Adicionada!", color=discord.Color.yellow())
        embed.add_field(name="Meta Global", value=meta["titulo"], inline=False)
        embed.add_field(name="Sub-meta", value=subtitulo, inline=False)
        embed.add_field(name="XP ao concluir", value="30 XP", inline=False)
        embed.set_footer(text=f"Treinador: {ctx.author.display_name}")
        await ctx.send(embed=embed)

    @commands.command()
    async def concluirsubmeta(self, ctx, meta_titulo: str, *, subtitulo: str):
        usuario_id = ctx.author.id
        meta = buscar_meta_por_titulo(usuario_id, meta_titulo)
        if not meta:
            await ctx.send(f"❌ Meta **'{meta_titulo}'** não encontrada!\nUse `!minhasmetas` para ver suas metas.")
            return
        sub_meta = buscar_meta_menor_por_titulo(meta["id"], subtitulo)
        if not sub_meta:
            await ctx.send(f"❌ Sub-meta **'{subtitulo}'** não encontrada ou já concluída!")
            return
        concluir_meta_menor_db(sub_meta["id"])
        pokemon = buscar_pokemon_da_meta(usuario_id, meta["id"])
        if not pokemon:
            await ctx.send("❌ Nenhum Pokémon encontrado para essa meta!")
            return
        xp_ganho = sub_meta["xp_recompensa"]
        xp_novo = pokemon["xp_atual"] + xp_ganho
        evolucoes = pokemon["evolucoes"].split(",")
        nivel_atual = pokemon["nivel_evolucao"]
        nome_atual = pokemon["nome"]
        xp_necessario = self.calcular_xp_necessario(evolucoes)
        evoluiu = False
        if xp_novo >= xp_necessario and nivel_atual < len(evolucoes) - 1:
            nivel_atual += 1
            nome_atual = evolucoes[nivel_atual]
            xp_novo = 0
            evoluiu = True
        atualizar_xp_pokemon(
            pokemon_id=pokemon["id"],
            xp_novo=xp_novo,
            nivel_novo=nivel_atual,
            nome_novo=nome_atual
        )
        numero_pokedex = pokemon["numero_pokedex"]
        embed = discord.Embed(title="⚡ Sub-meta Concluída!", color=discord.Color.gold())
        embed.set_thumbnail(url=f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{numero_pokedex}.png")
        embed.add_field(name="Sub-meta", value=sub_meta["titulo"], inline=False)
        embed.add_field(name="XP Ganho", value=f"+{xp_ganho} XP", inline=True)
        embed.add_field(name="XP Total", value=f"{xp_novo}/{xp_necessario}", inline=True)
        if evoluiu:
            nivel_pokedex = numero_pokedex + nivel_atual
            embed.add_field(name="🌟 EVOLUÇÃO!", value=f"Seu Pokémon evoluiu para **{nome_atual.capitalize()}**!", inline=False)
            embed.set_image(url=f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{nivel_pokedex}.png")
        embed.set_footer(text=f"Treinador: {ctx.author.display_name}")
        await ctx.send(embed=embed)

    @commands.command()
    async def deletarmeta(self, ctx, *, titulo: str):
        usuario_id = ctx.author.id
        meta = buscar_meta_por_titulo(usuario_id, titulo)
        if not meta:
            await ctx.send(f"❌ Meta **'{titulo}'** não encontrada!\nUse `!minhasmetas` para ver suas metas.")
            return
        self.pendente_deletar[usuario_id] = meta["id"]
        embed = discord.Embed(
            title="⚠️ Confirmar exclusão",
            description=f"Tem certeza que deseja deletar a meta **'{meta['titulo']}'**?\n\nIsso irá deletar também todas as sub-metas e o Pokémon vinculado!",
            color=discord.Color.red()
        )
        embed.add_field(name="Confirmar", value="`!confirmar` para deletar", inline=True)
        embed.add_field(name="Cancelar", value="`!cancelar` para manter", inline=True)
        await ctx.send(embed=embed)

    @commands.command()
    async def confirmar(self, ctx):
        usuario_id = ctx.author.id
        if usuario_id not in self.pendente_deletar:
            await ctx.send("❌ Nenhuma ação pendente de confirmação!")
            return
        meta_id = self.pendente_deletar.pop(usuario_id)
        deletar_meta(meta_id, usuario_id)
        embed = discord.Embed(
            title="🗑️ Meta deletada!",
            description="A meta, sub-metas e Pokémon foram removidos com sucesso.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def cancelar(self, ctx):
        usuario_id = ctx.author.id
        if usuario_id not in self.pendente_deletar:
            await ctx.send("❌ Nenhuma ação pendente de confirmação!")
            return
        self.pendente_deletar.pop(usuario_id)
        await ctx.send("✅ Ação cancelada! Sua meta continua salva.")


async def setup(bot):
    await bot.add_cog(MetasCommands(bot))