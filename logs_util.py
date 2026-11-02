import discord

import config_estado


async def enviar_log(guild: discord.Guild, mensagem: str | None = None, embed: discord.Embed | None = None):
    """Envia uma mensagem/embed pro canal de logs configurado via /configurar.
    Se nenhum canal foi definido ainda, simplesmente não faz nada (sem quebrar o resto do bot)."""
    cfg = config_estado.carregar()
    canal_id = cfg.get("log_channel_id")
    if not canal_id:
        return

    canal = guild.get_channel(canal_id)
    if canal is None:
        return

    try:
        await canal.send(content=mensagem, embed=embed)
    except discord.Forbidden:
        
        pass
