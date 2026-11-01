import json
import os

CAMINHO_ARQUIVO = "config_estado.json"

_PADRAO = {
    "mediador_role_id": None,
    "titulo_embed": None,  # None = usa o padrão definido no código
    "log_channel_id": None,  # canal onde os eventos (partida, ticket, blacklist) são registrados
}


def carregar() -> dict:
    if not os.path.exists(CAMINHO_ARQUIVO):
        return dict(_PADRAO)
    with open(CAMINHO_ARQUIVO, "r", encoding="utf-8") as f:
        dados = json.load(f)
    return {**_PADRAO, **dados}


def salvar(dados: dict) -> None:
    with open(CAMINHO_ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


def definir(chave: str, valor) -> None:
    dados = carregar()
    dados[chave] = valor
    salvar(dados)