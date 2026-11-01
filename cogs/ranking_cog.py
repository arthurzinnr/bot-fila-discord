import discord
from discord import app_commands
from discord.ext import commands

import ranking


class RankingCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="ranking", description="Mostra o ranking de vitórias do servidor.")
    async def ranking_cmd(self, interaction: discord.Interaction):
        top = ranking.obter_ranking(top_n=10)

        if not top:
            await interaction.response.send_message(
                "Ainda não tem nenhuma partida registrada.", ephemeral=True
            )
            return

        linhas = []
        for i, (uid, stats) in enumerate(top, start=1):
            linhas.append(
                f"**#{i}** <@{uid}> — Vitórias: {stats['vitorias']} | "
                f"Derrotas: {stats['derrotas']} | Taxa: {stats['taxa_vitoria']:.0f}%"
            )

        embed = discord.Embed(
            title="🏆 Ranking Global",
            description="\n".join(linhas),
            color=discord.Color.gold(),
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="minhasestatisticas", description="Mostra suas próprias estatísticas.")
    async def minhas_estatisticas(self, interaction: discord.Interaction):
        stats = ranking.obter_stats(interaction.user.id)
        embed = discord.Embed(title=f"📊 Estatísticas de {interaction.user.display_name}", color=discord.Color.blurple())
        embed.add_field(name="Vitórias", value=str(stats["vitorias"]), inline=True)
        embed.add_field(name="Derrotas", value=str(stats["derrotas"]), inline=True)
        embed.add_field(name="Taxa de vitória", value=f"{stats['taxa_vitoria']:.0f}%", inline=True)
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(RankingCog(bot))