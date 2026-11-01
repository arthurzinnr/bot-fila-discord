import discord
from discord import app_commands
from discord.ext import commands

import blacklist
import logs_util
import permissoes


class BlacklistCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    grupo = app_commands.Group(name="blacklist", description="Gerenciar a blacklist do servidor.")

    @grupo.command(name="adicionar", description="Adiciona um jogador na blacklist.")
    @app_commands.describe(jogador="Jogador a adicionar", motivo="Motivo do banimento da blacklist")
    async def adicionar(self, interaction: discord.Interaction, jogador: discord.Member, motivo: str):
        if not permissoes.eh_mediador(interaction):
            await interaction.response.send_message(
                "Só mediador/admin pode usar esse comando.", ephemeral=True
            )
            return

        blacklist.adicionar(jogador.id, motivo, interaction.user.id)
        await interaction.response.send_message(
            f"🚫 {jogador.mention} adicionado à blacklist.\nMotivo: {motivo}"
        )
        await logs_util.enviar_log(
            interaction.guild,
            embed=discord.Embed(
                title="🚫 Jogador adicionado à blacklist",
                description=f"Jogador: {jogador.mention}\nMotivo: {motivo}\nPor: {interaction.user.mention}",
                color=discord.Color.red(),
            ),
        )

    @grupo.command(name="remover", description="Remove um jogador da blacklist.")
    @app_commands.describe(jogador="Jogador a remover da blacklist")
    async def remover(self, interaction: discord.Interaction, jogador: discord.Member):
        if not permissoes.eh_mediador(interaction):
            await interaction.response.send_message(
                "Só mediador/admin pode usar esse comando.", ephemeral=True
            )
            return

        removeu = blacklist.remover(jogador.id)
        if not removeu:
            await interaction.response.send_message(
                f"{jogador.mention} não está na blacklist.", ephemeral=True
            )
            return

        await interaction.response.send_message(f"✅ {jogador.mention} removido da blacklist.")
        await logs_util.enviar_log(
            interaction.guild,
            embed=discord.Embed(
                title="✅ Jogador removido da blacklist",
                description=f"Jogador: {jogador.mention}\nPor: {interaction.user.mention}",
                color=discord.Color.green(),
            ),
        )

    @grupo.command(name="consultar", description="Consulta se um jogador está na blacklist.")
    @app_commands.describe(jogador="Jogador a consultar")
    async def consultar(self, interaction: discord.Interaction, jogador: discord.Member):
        info = blacklist.consultar(jogador.id)
        if not info:
            await interaction.response.send_message(
                f"{jogador.mention} não está na blacklist. ✅", ephemeral=True
            )
            return

        embed = discord.Embed(title="🚫 Jogador na Blacklist", color=discord.Color.red())
        embed.add_field(name="Jogador", value=jogador.mention, inline=False)
        embed.add_field(name="Motivo", value=info["motivo"], inline=False)
        embed.add_field(name="Registrado por", value=f"<@{info['registrado_por']}>", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(BlacklistCog(bot))