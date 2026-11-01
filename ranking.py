import json
import os

CAMINHO_ARQUIVO = "ranking_estado.json"


def _carregar() -> dict:
    if not os.path.exists(CAMINHO_ARQUIVO):
        return {}
    with open(CAMINHO_ARQUIVO, "r", encoding="utf-8") as f:
        return json.load(f)


def _salvar(dados: dict) -> None:
    with open(CAMINHO_ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


def registrar_resultado(vencedor_id: int, perdedor_id: int) -> None:
    """Soma 1 vitória pro vencedor e 1 derrota pro perdedor."""
    dados = _carregar()

    v = dados.setdefault(str(vencedor_id), {"vitorias": 0, "derrotas": 0})
    v["vitorias"] += 1

    p = dados.setdefault(str(perdedor_id), {"vitorias": 0, "derrotas": 0})
    p["derrotas"] += 1

    _salvar(dados)


def obter_stats(user_id: int) -> dict:
    """Retorna {vitorias, derrotas, taxa_vitoria} de um jogador."""
    dados = _carregar()
    info = dados.get(str(user_id), {"vitorias": 0, "derrotas": 0})
    total = info["vitorias"] + info["derrotas"]
    taxa = (info["vitorias"] / total * 100) if total > 0 else 0.0
    return {"vitorias": info["vitorias"], "derrotas": info["derrotas"], "taxa_vitoria": taxa}


def obter_ranking(top_n: int = 10) -> list[tuple[int, dict]]:
    """Retorna os top_n jogadores ordenados por número de vitórias (desc)."""
    dados = _carregar()
    lista = []
    for uid_str, info in dados.items():
        total = info["vitorias"] + info["derrotas"]
        taxa = (info["vitorias"] / total * 100) if total > 0 else 0.0
        lista.append((int(uid_str), {**info, "taxa_vitoria": taxa}))

    lista.sort(key=lambda item: item[1]["vitorias"], reverse=True)
    return lista[:top_n]