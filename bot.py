import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
from database import criar_tabelas


load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
bot.remove_command("help")


@bot.event
async def on_ready():
    criar_tabelas()
    await bot.load_extension("commands.metas")
    await bot.load_extension("commands.pokedex")  
    print(f"✅ {bot.user} está online!")
    print(f"🎮 PokeMetas pronto para uso!")






@bot.command(name="help")
async def help_command(ctx):
    embed = discord.Embed(
        title="🎮 PokeMetas — Comandos",
        description="Transforme suas metas em aventuras Pokémon!",
        color=discord.Color.purple()
    )

    embed.add_field(
        name="🎯 Metas",
        value=(
            "`!criarmeta [titulo]` — Cria uma meta e sorteia um Pokémon\n"
            "`!criarmeta [titulo] [pokemon]` — Cria meta com Pokémon escolhido\n"
            "`!minhasmetas` — Lista suas metas e sub-metas\n"
            "`!deletarmeta [titulo]` — Remove uma meta\n"
        ),
        inline=False
    )

    embed.add_field(
        name="✅ Sub-metas",
        value=(
            "`!adicionarsubmeta [meta] [subtitulo]` — Adiciona uma sub-meta\n"
            "`!concluirsubmeta [meta] [subtitulo]` — Conclui sub-meta e ganha XP\n"
        ),
        inline=False
    )

    embed.add_field(
        name="📖 Pokédex",
        value=(
            "`!pokedex` — Vê todos seus Pokémons capturados\n"
            "`!meupokemon [nome]` — Detalhes de um Pokémon específico\n"
        ),
        inline=False
    )

    embed.add_field(
        name="⚙️ Geral",
        value=(
            "`!help` — Mostra esta mensagem\n"
        ),
        inline=False
    )

    embed.set_footer(text="PokeMetas • Produtividade gamificada!")
    await ctx.send(embed=embed)


bot.run(TOKEN)