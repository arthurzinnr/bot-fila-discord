import json
import os

CAMINHO_ARQUIVO = "filas_estado.json"


def salvar_partidas(dados: dict) -> None:
    """Salva o estado de todas as partidas ativas no arquivo JSON."""
    with open(CAMINHO_ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


def carregar_partidas() -> dict:
    """Carrega o estado salvo. Retorna {} se o arquivo ainda não existir."""
    if not os.path.exists(CAMINHO_ARQUIVO):
        return {}
    with open(CAMINHO_ARQUIVO, "r", encoding="utf-8") as f:
        return json.load(f)