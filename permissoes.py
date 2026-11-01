import discord

import config_estado
from config import MEDIADOR_ROLE_ID as MEDIADOR_ROLE_ID_ENV


def mediador_role_id_atual() -> int | None:
    """O cargo definido via /configurar tem prioridade sobre o do .env."""
    cfg = config_estado.carregar()
    return cfg.get("mediador_role_id") or MEDIADOR_ROLE_ID_ENV


def eh_mediador(interaction: discord.Interaction) -> bool:
    """Verifica se quem usou o comando/botão tem o cargo mediador ou é admin do servidor."""
    membro = interaction.user
    if membro.guild_permissions.administrator:
        return True
    role_id = mediador_role_id_atual()
    if role_id is None:
        return False
    return any(cargo.id == role_id for cargo in membro.roles)