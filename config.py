
import os
from dotenv import load_dotenv
 
load_dotenv()
 
# Token do bot lido de variável de ambiente (NUNCA coloque o token direto no código)
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
 
if not DISCORD_TOKEN:
    raise RuntimeError(
        "DISCORD_TOKEN não encontrado. Crie um arquivo .env com DISCORD_TOKEN=seu_token_aqui"
    )
 
# ID do cargo que será notificado e adicionado em todo ticket criado
_mediador_id_str = os.getenv("MEDIADOR_ROLE_ID")
MEDIADOR_ROLE_ID = int(_mediador_id_str) if _mediador_id_str else None