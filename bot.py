import asyncio
import logging

import discord
from discord.ext import commands

from config import DISCORD_TOKEN

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("firefire_bot")

# Intents necessárias: precisamos ver membros e conteúdo de mensagens
# (se seu bot só usa slash commands e botões, message_content pode ficar False)
intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    log.info(f"Bot conectado como {bot.user} (ID: {bot.user.id})")
    try:
        synced = await bot.tree.sync()
        log.info(f"{len(synced)} slash commands sincronizados.")
    except Exception as e:
        log.error(f"Erro ao sincronizar comandos: {e}")


async def main():
    async with bot:
        # Carrega os cogs (módulos de funcionalidades)
        await bot.load_extension("cogs.fila_cog")
        await bot.load_extension("cogs.ranking_cog")
        await bot.load_extension("cogs.blacklist_cog")
        await bot.load_extension("cogs.config_cog")
        await bot.load_extension("cogs.ajuda_cog")
        await bot.start(DISCORD_TOKEN)


if __name__ == "__main__":
    asyncio.run(main())