import discord
from discord import app_commands
from discord.ext import commands


class AjudaCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="ajuda", description="Mostra a lista de todos os comandos disponíveis.")
    async def ajuda(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📖 CENTRAL DE AJUDA — COMANDOS SLASH",
            description="Lista de todos os comandos de barra disponíveis no servidor:",
            color=discord.Color.blurple(),
        )

        embed.add_field(
            name="🎮 Filas e Partidas",
            value=(
                "`/criarpartida` — Cria um painel de fila para uma partida\n"
                "*(dentro do ticket, use os botões pra declarar o vencedor, "
                "chamar o mediador ou fechar o ticket)*"
            ),
            inline=False,
        )

        embed.add_field(
            name="🏆 Ranking",
            value=(
                "`/ranking` — Mostra o top 10 de vitórias do servidor\n"
                "`/minhasestatisticas` — Mostra suas próprias vitórias, derrotas e taxa de vitória"
            ),
            inline=False,
        )

        embed.add_field(
            name="🚫 Blacklist",
            value=(
                "`/blacklist adicionar` — Adiciona um jogador na blacklist (mediador/admin)\n"
                "`/blacklist remover` — Remove um jogador da blacklist (mediador/admin)\n"
                "`/blacklist consultar` — Consulta se um jogador está na blacklist"
            ),
            inline=False,
        )

        embed.add_field(
            name="⚙️ Configuração",
            value=(
                "`/configurar` — Abre o painel de configuração (cargo mediador, "
                "canal de logs, título do painel) — só admin\n"
                "`/ajuda` — Mostra esta lista de comandos"
            ),
            inline=False,
        )

        embed.set_footer(text="Dúvidas? Chame um mediador ou admin do servidor.")
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(AjudaCog(bot))