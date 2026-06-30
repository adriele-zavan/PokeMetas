# commands/pokedex.py

import discord
from discord.ext import commands
from database import buscar_pokemons_usuario


class PokedexCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def pokedex(self, ctx):
        usuario_id = ctx.author.id
        pokemons = buscar_pokemons_usuario(usuario_id)

        if not pokemons:
            await ctx.send("❌ Você ainda não capturou nenhum Pokémon!\nCrie uma meta com `!criarmeta [titulo]`")
            return

        embed = discord.Embed(
            title=f"📖 Pokédex de {ctx.author.display_name}",
            color=discord.Color.red()
        )

        for p in pokemons:
            evolucoes = p["evolucoes"].split(",")
            xp_necessario = 50 if len(evolucoes) == 2 else 100
            embed.add_field(
                name=f"#{p['numero_pokedex']} {p['nome'].capitalize()}",
                value=f"XP: {p['xp_atual']}/{xp_necessario} | Nível: {p['nivel_evolucao']}",
                inline=True
            )

        embed.set_footer(text=f"Total: {len(pokemons)} Pokémon(s) capturado(s)")
        await ctx.send(embed=embed)

    @commands.command()
    async def meupokemon(self, ctx, *, nome: str):
        usuario_id = ctx.author.id
        pokemons = buscar_pokemons_usuario(usuario_id)

        # Busca o pokemon pelo nome
        pokemon = None
        for p in pokemons:
            if nome.lower() in p["nome"].lower():
                pokemon = p
                break

        if not pokemon:
            await ctx.send(f"❌ Pokémon **'{nome}'** não encontrado na sua Pokédex!\nUse `!pokedex` para ver seus Pokémons.")
            return

        evolucoes = pokemon["evolucoes"].split(",")
        xp_necessario = 50 if len(evolucoes) == 2 else 100
        numero = pokemon["numero_pokedex"]

        embed = discord.Embed(
            title=f"#{numero} {pokemon['nome'].capitalize()}",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(
            url=f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{numero}.png"
        )
        embed.add_field(name="Treinador", value=ctx.author.display_name, inline=True)
        embed.add_field(name="Nível de Evolução", value=f"{pokemon['nivel_evolucao']}/{len(evolucoes)-1}", inline=True)
        embed.add_field(name="XP", value=f"{pokemon['xp_atual']}/{xp_necessario}", inline=True)
        embed.add_field(name="Cadeia de Evolução", value=" → ".join(evolucoes), inline=False)

        # Barra de progresso de XP
        progresso = int((pokemon["xp_atual"] / xp_necessario) * 10)
        barra = "🟩" * progresso + "⬜" * (10 - progresso)
        embed.add_field(name="Progresso", value=barra, inline=False)

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(PokedexCommands(bot))