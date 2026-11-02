
import os
from dotenv import load_dotenv
 
load_dotenv()
 
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
 
if not DISCORD_TOKEN:
    raise RuntimeError(
        "DISCORD_TOKEN não encontrado. Crie um arquivo .env com DISCORD_TOKEN=seu_token_aqui"
    )
 
_mediador_id_str = os.getenv("MEDIADOR_ROLE_ID")
MEDIADOR_ROLE_ID = int(_mediador_id_str) if _mediador_id_str else None
