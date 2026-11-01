import json
import os
import time

CAMINHO_ARQUIVO = "blacklist_estado.json"


def _carregar() -> dict:
    if not os.path.exists(CAMINHO_ARQUIVO):
        return {}
    with open(CAMINHO_ARQUIVO, "r", encoding="utf-8") as f:
        return json.load(f)


def _salvar(dados: dict) -> None:
    with open(CAMINHO_ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


def adicionar(user_id: int, motivo: str, registrado_por_id: int) -> None:
    dados = _carregar()
    dados[str(user_id)] = {
        "motivo": motivo,
        "registrado_por": registrado_por_id,
        "data": int(time.time()),
    }
    _salvar(dados)


def remover(user_id: int) -> bool:
    """Retorna True se removeu, False se a pessoa não estava na blacklist."""
    dados = _carregar()
    if str(user_id) in dados:
        del dados[str(user_id)]
        _salvar(dados)
        return True
    return False


def consultar(user_id: int) -> dict | None:
    dados = _carregar()
    return dados.get(str(user_id))


def listar() -> dict:
    return _carregar()