import asyncio
import os

import discord
from discord import app_commands
from discord.ext import commands

import armazenamento
import config_estado
import logs_util
import permissoes
import ranking

# ==== PERSONALIZAÇÃO DO EMBED ====
# Título padrão (pode ser sobrescrito em runtime via /configurar)
TITULO_EMBED_PADRAO = "🏆 | Bora de AP, hein?"
# Caminho da imagem que aparece do lado direito do embed (coloque o arquivo em assets/)
CAMINHO_IMAGEM = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "capa.jpg")
NOME_ARQUIVO_IMAGEM = "capa.jpg"
# ===================================

# Quantidade fixa de vagas por fila (2 representantes: um de cada lado)
VAGAS_POR_FILA = 2

# Registro de todas as partidas ativas na memória, indexado pelo ID da mensagem do embed.
# É a partir daqui que salvamos e restauramos o estado no arquivo JSON.
PARTIDAS_ATIVAS: dict[int, "FilaView"] = {}


def get_titulo_embed() -> str:
    cfg = config_estado.carregar()
    return cfg.get("titulo_embed") or TITULO_EMBED_PADRAO


def _salvar_todas_partidas():
    dados = {}
    for msg_id, view in PARTIDAS_ATIVAS.items():
        dados[str(msg_id)] = {
            "formato": view.formato,
            "valor": view.valor,
            "num_filas": view.num_filas,
            "vagas_por_fila": view.vagas_por_fila,
            "filas": view.filas,
        }
    armazenamento.salvar_partidas(dados)


class TicketView(discord.ui.View):
    """Botões dentro do canal de ticket: declarar vencedor, chamar mediador, fechar."""

    def __init__(self, jogador1_id: int, jogador2_id: int, nome1: str, nome2: str):
        super().__init__(timeout=None)
        self.jogador1_id = jogador1_id
        self.jogador2_id = jogador2_id
        self.resultado_declarado = False

        btn1 = discord.ui.Button(
            label=f"🏆 {nome1} venceu",
            style=discord.ButtonStyle.success,
            custom_id=f"vencedor1_{jogador1_id}_{jogador2_id}",
            row=0,
        )
        btn1.callback = self._make_vencedor_callback(jogador1_id, jogador2_id)
        self.add_item(btn1)

        btn2 = discord.ui.Button(
            label=f"🏆 {nome2} venceu",
            style=discord.ButtonStyle.success,
            custom_id=f"vencedor2_{jogador1_id}_{jogador2_id}",
            row=0,
        )
        btn2.callback = self._make_vencedor_callback(jogador2_id, jogador1_id)
        self.add_item(btn2)

        chamar = discord.ui.Button(
            label="Chamar Mediador",
            emoji="📣",
            style=discord.ButtonStyle.secondary,
            custom_id=f"chamarmed_{jogador1_id}_{jogador2_id}",
            row=1,
        )
        chamar.callback = self._chamar_mediador
        self.add_item(chamar)

        fechar = discord.ui.Button(
            label="Fechar Ticket",
            emoji="🔒",
            style=discord.ButtonStyle.danger,
            custom_id=f"fecharticket_{jogador1_id}_{jogador2_id}",
            row=1,
        )
        fechar.callback = self._fechar_ticket
        self.add_item(fechar)

    def _make_vencedor_callback(self, vencedor_id: int, perdedor_id: int):
        async def callback(interaction: discord.Interaction):
            if not permissoes.eh_mediador(interaction):
                await interaction.response.send_message(
                    "Só o mediador ou um admin pode declarar o vencedor.", ephemeral=True
                )
                return
            if self.resultado_declarado:
                await interaction.response.send_message(
                    "O vencedor dessa partida já foi declarado.", ephemeral=True
                )
                return

            self.resultado_declarado = True
            ranking.registrar_resultado(vencedor_id, perdedor_id)

            for item in self.children:
                item.disabled = True
            await interaction.response.edit_message(view=self)

            embed = discord.Embed(
                title="🏆 Vencedor declarado",
                description=f"<@{vencedor_id}> venceu a partida!",
                color=discord.Color.green(),
            )
            embed.set_footer(text=f"Declarado por {interaction.user.display_name}")
            await interaction.followup.send(embed=embed)

            await logs_util.enviar_log(
                interaction.guild,
                mensagem=(
                    f"🏆 **Resultado registrado** em {interaction.channel.mention}\n"
                    f"Vencedor: <@{vencedor_id}> | Perdedor: <@{perdedor_id}>\n"
                    f"Declarado por: {interaction.user.mention}"
                ),
            )

        return callback

    async def _chamar_mediador(self, interaction: discord.Interaction):
        role_id = permissoes.mediador_role_id_atual()
        mencao = f"<@&{role_id}>" if role_id else "**Mediador** (cargo não configurado)"
        await interaction.response.send_message(f"📣 {mencao}, sua presença foi solicitada neste ticket!")

    async def _fechar_ticket(self, interaction: discord.Interaction):
        if not permissoes.eh_mediador(interaction):
            await interaction.response.send_message(
                "Só o mediador ou um admin pode fechar o ticket.", ephemeral=True
            )
            return

        await interaction.response.send_message("🔒 Encerrando este ticket em 5 segundos...")
        await asyncio.sleep(5)
        await interaction.channel.delete(reason=f"Ticket encerrado por {interaction.user.display_name}")


class FilaView(discord.ui.View):
    """
    Guarda o estado de uma partida (várias filas) e os botões de interação.
    Cada instância dessa View corresponde a UM embed de partida.
    """

    def __init__(self, formato: str, valor: str | None, num_filas: int, vagas_por_fila: int):
        super().__init__(timeout=None)  # botões não expiram
        self.formato = formato
        self.valor = valor
        self.num_filas = num_filas
        self.vagas_por_fila = vagas_por_fila

        # filas[i] = lista de IDs dos jogadores na fila i
        self.filas: list[list[int]] = [[] for _ in range(num_filas)]

        self._montar_botoes()

    def _montar_botoes(self):
        """Cria dinamicamente um botão 'Entrar na Fila N' para cada fila configurada."""
        for i in range(self.num_filas):
            botao = discord.ui.Button(
                label=f"Entrar na Fila {i + 1}",
                emoji="✅",
                style=discord.ButtonStyle.success,
                custom_id=f"entrar_fila_{i}",
                row=0,
            )
            botao.callback = self._make_entrar_callback(i)
            self.add_item(botao)

        sair = discord.ui.Button(
            label="Sair da Fila",
            emoji="❌",
            style=discord.ButtonStyle.danger,
            custom_id="sair_fila",
            row=1,
        )
        sair.callback = self.sair_callback
        self.add_item(sair)

    def _make_entrar_callback(self, indice_fila: int):
        async def callback(interaction: discord.Interaction):
            await self.entrar_callback(interaction, indice_fila)
        return callback

    def _fila_do_jogador(self, user_id: int) -> int | None:
        """Retorna em qual fila (índice) o jogador já está, ou None."""
        for i, fila in enumerate(self.filas):
            if user_id in fila:
                return i
        return None

    async def entrar_callback(self, interaction: discord.Interaction, indice_fila: int):
        user_id = interaction.user.id
        fila_atual = self._fila_do_jogador(user_id)

        if fila_atual is not None:
            await interaction.response.send_message(
                f"Você já está na Fila {fila_atual + 1}. Saia dela antes de entrar em outra.",
                ephemeral=True,
            )
            return

        if len(self.filas[indice_fila]) >= self.vagas_por_fila:
            await interaction.response.send_message(
                f"A Fila {indice_fila + 1} já está cheia.", ephemeral=True
            )
            return

        # Checa blacklist antes de deixar entrar
        import blacklist
        info_blacklist = blacklist.consultar(user_id)
        if info_blacklist:
            await interaction.response.send_message(
                f"🚫 Você está na blacklist e não pode entrar em filas. Motivo: {info_blacklist['motivo']}",
                ephemeral=True,
            )
            return

        self.filas[indice_fila].append(user_id)
        PARTIDAS_ATIVAS[interaction.message.id] = self

        # Se a fila encheu, cria o ticket e reseta a fila pra liberar pra outras pessoas
        if len(self.filas[indice_fila]) >= self.vagas_por_fila:
            jogadores_ids = list(self.filas[indice_fila])
            self.filas[indice_fila] = []
            _salvar_todas_partidas()
            await interaction.response.edit_message(embed=self._montar_embed(), view=self)
            await self._criar_ticket(interaction, indice_fila, jogadores_ids)
        else:
            _salvar_todas_partidas()
            await interaction.response.edit_message(embed=self._montar_embed(), view=self)

    async def _criar_ticket(
        self, interaction: discord.Interaction, indice_fila: int, jogadores_ids: list[int]
    ):
        """Cria um canal privado só pros jogadores da fila cheia + o cargo mediador."""
        guild = interaction.guild
        mediador_role_id = permissoes.mediador_role_id_atual()

        if mediador_role_id is None:
            await interaction.followup.send(
                "⚠️ Fila fechou, mas nenhum cargo mediador está configurado ainda "
                "(use /configurar ou defina MEDIADOR_ROLE_ID no .env) — ticket não pôde ser criado.",
                ephemeral=True,
            )
            return

        mediador_role = guild.get_role(mediador_role_id)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True),
        }
        if mediador_role:
            overwrites[mediador_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)

        membros_mencionados = []
        membros_objs = {}
        for uid in jogadores_ids:
            membro = guild.get_member(uid)
            if membro:
                overwrites[membro] = discord.PermissionOverwrite(view_channel=True, send_messages=True)
                membros_mencionados.append(membro.mention)
                membros_objs[uid] = membro

        nome_canal = f"ticket-fila{indice_fila + 1}-{self.formato}".lower().replace(" ", "-")

        try:
            canal = await guild.create_text_channel(
                name=nome_canal,
                overwrites=overwrites,
                reason="Fila cheia - ticket de partida criado automaticamente",
            )
        except discord.Forbidden:
            await interaction.followup.send(
                "⚠️ Fila fechou, mas não tenho permissão de 'Gerenciar Canais' para criar o ticket. "
                "Peça pra um admin me dar essa permissão.",
                ephemeral=True,
            )
            return

        aviso_mediador = mediador_role.mention if mediador_role else "@Mediador (cargo não encontrado)"
        mensagem = (
            f"🎮 **Partida fechada — Fila {indice_fila + 1}**\n"
            f"Formato: **{self.formato}**\n"
            + (f"Valor: **{self.valor}**\n" if self.valor else "")
            + f"\nJogadores: {' '.join(membros_mencionados)}\n"
            f"Mediador: {aviso_mediador}\n\n"
            f"Cliquem em um dos botões abaixo quando a partida acabar."
        )

        # Nomes pra aparecer nos botões (se o membro não for encontrado, usa "Jogador N")
        nome1 = membros_objs[jogadores_ids[0]].display_name if jogadores_ids[0] in membros_objs else "Jogador 1"
        nome2 = membros_objs[jogadores_ids[1]].display_name if jogadores_ids[1] in membros_objs else "Jogador 2"

        ticket_view = TicketView(jogadores_ids[0], jogadores_ids[1], nome1, nome2)
        await canal.send(mensagem, view=ticket_view)

        await logs_util.enviar_log(
            guild,
            mensagem=(
                f"🎫 **Ticket criado**: {canal.mention}\n"
                f"Formato: {self.formato} | Fila: {indice_fila + 1}\n"
                f"Jogadores: {' '.join(membros_mencionados)}"
            ),
        )

        await interaction.followup.send(
            f"✅ Fila {indice_fila + 1} fechou! Ticket criado: {canal.mention}", ephemeral=True
        )

    async def sair_callback(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        fila_atual = self._fila_do_jogador(user_id)

        if fila_atual is None:
            await interaction.response.send_message(
                "Você não está em nenhuma fila.", ephemeral=True
            )
            return

        self.filas[fila_atual].remove(user_id)
        PARTIDAS_ATIVAS[interaction.message.id] = self
        _salvar_todas_partidas()
        await interaction.response.edit_message(embed=self._montar_embed(), view=self)

    def _montar_embed(self) -> discord.Embed:
        embed = discord.Embed(title=get_titulo_embed(), color=discord.Color.gold())
        embed.add_field(name="Formato", value=self.formato, inline=True)
        if self.valor:
            embed.add_field(name="Valor", value=self.valor, inline=True)

        linhas = []
        for i, fila in enumerate(self.filas):
            for uid in fila:
                linhas.append(f"<@{uid}> | Fila {i + 1}")

        jogadores_texto = "\n".join(linhas) if linhas else "Nenhum jogador na espera."
        embed.add_field(name="Jogadores:", value=jogadores_texto, inline=False)

        if os.path.exists(CAMINHO_IMAGEM):
            embed.set_thumbnail(url=f"attachment://{NOME_ARQUIVO_IMAGEM}")

        return embed

    def _arquivo_imagem(self) -> discord.File | None:
        """Retorna o attachment da imagem, se o arquivo existir."""
        if os.path.exists(CAMINHO_IMAGEM):
            return discord.File(CAMINHO_IMAGEM, filename=NOME_ARQUIVO_IMAGEM)
        return None


class FilaCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="criarpartida", description="Cria um painel de fila para uma partida.")
    @app_commands.describe(
        formato="Ex: 4x4 Mobile, 3x3 Emulador",
        num_filas="Quantas filas paralelas (ex: 3)",
        valor="Ex: R$ 3,00 (texto informativo, não processa pagamento)",
    )
    async def criarpartida(
        self,
        interaction: discord.Interaction,
        formato: str,
        num_filas: app_commands.Range[int, 1, 5],
        valor: str,
    ):
        view = FilaView(formato=formato, valor=valor, num_filas=num_filas, vagas_por_fila=VAGAS_POR_FILA)
        embed = view._montar_embed()
        arquivo = view._arquivo_imagem()

        if arquivo:
            await interaction.response.send_message(embed=embed, view=view, file=arquivo)
        else:
            await interaction.response.send_message(embed=embed, view=view)

        mensagem = await interaction.original_response()
        PARTIDAS_ATIVAS[mensagem.id] = view
        _salvar_todas_partidas()

    async def cog_load(self):
        """Roda automaticamente quando o cog é carregado (bot ligando).
        Lê o arquivo salvo e recria os painéis de fila com os botões funcionando."""
        dados = armazenamento.carregar_partidas()
        for msg_id_str, info in dados.items():
            msg_id = int(msg_id_str)
            view = FilaView(
                formato=info["formato"],
                valor=info.get("valor"),
                num_filas=info["num_filas"],
                vagas_por_fila=info["vagas_por_fila"],
            )
            view.filas = info["filas"]
            PARTIDAS_ATIVAS[msg_id] = view
            self.bot.add_view(view, message_id=msg_id)


async def setup(bot: commands.Bot):
    await bot.add_cog(FilaCog(bot))