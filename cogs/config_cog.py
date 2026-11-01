import discord
from discord import app_commands
from discord.ext import commands

import config_estado


class ModalTitulo(discord.ui.Modal, title="Editar título do painel"):
    novo_titulo = discord.ui.TextInput(
        label="Novo título",
        placeholder="Ex: Bora de AP, hein?",
        max_length=100,
    )

    async def on_submit(self, interaction: discord.Interaction):
        config_estado.definir("titulo_embed", str(self.novo_titulo))
        await interaction.response.send_message(
            f"✅ Título atualizado para: **{self.novo_titulo}**\n"
            f"(painéis novos já usam o título novo; painéis já criados mantêm o título antigo)",
            ephemeral=True,
        )


class ConfigView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)

    @discord.ui.select(cls=discord.ui.RoleSelect, placeholder="Selecione o cargo mediador")
    async def selecionar_mediador(self, interaction: discord.Interaction, select: discord.ui.RoleSelect):
        cargo = select.values[0]
        config_estado.definir("mediador_role_id", cargo.id)
        await interaction.response.send_message(
            f"✅ Cargo mediador definido como {cargo.mention}", ephemeral=True
        )

    @discord.ui.select(
        cls=discord.ui.ChannelSelect,
        placeholder="Selecione o canal de logs",
        channel_types=[discord.ChannelType.text],
    )
    async def selecionar_canal_log(self, interaction: discord.Interaction, select: discord.ui.ChannelSelect):
        canal = select.values[0]
        config_estado.definir("log_channel_id", canal.id)
        await interaction.response.send_message(
            f"✅ Canal de logs definido como {canal.mention}\n"
            f"A partir de agora, partidas criadas, tickets, resultados e mudanças na blacklist "
            f"vão aparecer automaticamente lá.",
            ephemeral=True,
        )

    @discord.ui.button(label="Editar Título do Painel", style=discord.ButtonStyle.primary, emoji="✏️")
    async def editar_titulo(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ModalTitulo())


class ConfigCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="configurar", description="Abre o painel de configuração do bot.")
    @app_commands.checks.has_permissions(administrator=True)
    async def configurar(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "⚙️ **Painel de Configuração**\n"
            "Use o menu abaixo pra definir o cargo mediador, ou clique no botão pra mudar "
            "o título dos painéis de fila.",
            view=ConfigView(),
            ephemeral=True,
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(ConfigCog(bot))