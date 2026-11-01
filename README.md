# 🎮 Bot de Fila Competitiva para Discord

Bot em Python (discord.py) que organiza **filas de partidas competitivas** em servidores de Discord, com tickets privados e mediação. Feito originalmente para comunidades de Free Fire, mas funciona com qualquer jogo.

## ✨ Funcionalidades

- **Filas de partida:** painel com botões para entrar e sair, com formato (1x1, 2x2...) e valor/rótulo opcional
- **Tickets automáticos:** quando a fila enche, cria um canal privado para os jogadores
- **Mediação:** botão para chamar o mediador e declarar o vencedor
- **Ranking:** top 10 de vitórias do servidor e estatísticas pessoais
- **Blacklist:** mediadores e admins podem bloquear jogadores
- **Painel de configuração:** cargo de mediador, canal de logs e título do painel
- **Persistência** do estado em arquivos JSON

## 🧰 Tecnologias

Python 3, discord.py 2.x, python-dotenv

## 📋 Comandos

| Comando | O que faz |
|---|---|
| `/criarpartida` | Cria um painel de fila |
| `/ranking` | Mostra o top 10 de vitórias |
| `/minhasestatisticas` | Mostra suas vitórias, derrotas e taxa de vitória |
| `/blacklist adicionar` / `remover` / `consultar` | Gerencia a blacklist (mediador/admin) |
| `/configurar` | Abre o painel de configuração (admin) |
| `/ajuda` | Lista todos os comandos |

## 🚀 Como rodar

1. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
2. Crie um bot no [Discord Developer Portal](https://discord.com/developers/applications) e copie o token.
3. Copie `.env.example` para `.env` e preencha:
   ```
   DISCORD_TOKEN=seu_token
   MEDIADOR_ROLE_ID=id_do_cargo_de_mediador
   ```
4. Rode o bot:
   ```bash
   python bot.py
   ```

> ⚠️ Nunca suba o arquivo `.env` nem compartilhe o token do bot.

## 📁 Estrutura

```
bot.py            # inicialização e carregamento dos módulos
config.py         # leitura das variáveis de ambiente
cogs/             # fila, ranking, blacklist, configuração e ajuda
armazenamento.py  # salva/carrega o estado das partidas
ranking.py        # lógica do ranking
blacklist.py      # lógica da blacklist
assets/           # imagem do painel
```

## 👤 Autor

Arthur Miguel — estudante técnico de Desenvolvimento de Sistemas
