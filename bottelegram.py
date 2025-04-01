import telebot
import requests
from datetime import datetime
import os

# === CONFIGURAÇÕES ===
TOKEN = os.getenv ("8153287953:AAEsrLms2ICNGOY2uqKOHlm0pGUQHbxIu1A")
API_KEY = os.getenv ("177074678f6469c26f1b885a5a0fb0a6")
bot = telebot.TeleBot(TOKEN)
HEADERS = {"x-apisports-key": API_KEY}

# === FUNÇÃO: buscar jogos de hoje ===
def buscar_jogos():
    hoje = datetime.now().strftime("%Y-%m-%d")
    url = "https://v3.football.api-sports.io/fixtures"
    headers = {
        "x-apisports-key": API_KEY
    }
    params = {
        "date": hoje
    }
    resposta = requests.get(url, headers=headers, params=params)
    dados = resposta.json()
    return dados["response"]

# === FUNÇÃO: analisar jogos com over 2.5 ===
def analisar_over(jogos):
    mensagens = []
    for jogo in jogos:
        status = jogo['fixture']['status']['short']
        golos_home = jogo['goals']['home']
        golos_away = jogo['goals']['away']
        total_golos = (golos_home or 0) + (golos_away or 0)
        if status != "NS" and total_golos >= 3:
            casa = jogo['teams']['home']['name']
            fora = jogo['teams']['away']['name']
            mensagens.append(f"{casa} {total_golos} x {fora}")
    return mensagens

# === COMANDO /start ===
@bot.message_handler(commands=["start"])
def responder_inicio(mensagem):
    texto = "Olá, Daniel! Usa o comando /over para ver jogos com tendência de over 2.5 ⚽"
    bot.reply_to(mensagem, texto)

# === COMANDO /over ===
@bot.message_handler(commands=["over"])
def responder_over(mensagem):
    bot.send_message(mensagem.chat.id, "⏳ Buscando jogos com over 2.5...")
    try:
        jogos = buscar_jogos()
        resultados = analisar_over(jogos)
        if resultados:
            for linha in resultados:
                bot.send_message(mensagem.chat.id, f"🔥 {linha}")
        else:
            bot.send_message(mensagem.chat.id, "Nenhum jogo com over 2.5 até agora.")
    except:
        bot.send_message(mensagem.chat.id, "Erro ao buscar dados. Verifique a chave da API.")

# === COMANDO /hoje ===
@bot.message_handler(commands=["hoje"])
def jogos_hoje(mensagem):
    bot.send_message(mensagem.chat.id, "🔍 Procurando os jogos de hoje...")
    try:
        hoje = datetime.now().strftime("%Y-%m-%d")
        url = "https://v3.football.api-sports.io/fixtures"
        headers = {"x-apisports-key": API_KEY}
        params = {"date": hoje}
        resposta = requests.get(url, headers=headers, params=params)
        dados = resposta.json()
        jogos = dados["response"]

        if not jogos:
            bot.send_message(mensagem.chat.id, "Nenhum jogo encontrado hoje.")
            return

        for jogo in jogos[:10]:  # Limita a 10 para não sobrecarregar o bot
            casa = jogo['teams']['home']['name']
            fora = jogo['teams']['away']['name']
            hora = jogo['fixture']['date'][11:16]
            bot.send_message(mensagem.chat.id, f"⚽ {hora} | {casa} x {fora}")

    except:
        bot.send_message(mensagem.chat.id, "Erro ao buscar jogos. Verifica tua API KEY.")


# === COMANDO /oddsaltas ===
@bot.message_handler(commands=["oddsaltas"])
def jogos_com_odds_altas(mensagem):
    bot.send_message(mensagem.chat.id, "💸 Procurando jogos com odds acima de 2.50...")

    hoje = datetime.now().strftime("%Y-%m-%d")
    url = "https://v3.football.api-sports.io/odds"
    headers = {"x-apisports-key": API_KEY}
    params = {
        "date": hoje,
        "bookmaker": 8  # ID da Betclic (ou outro se preferires)
    }

    try:
        resposta = requests.get(url, headers=headers, params=params)
        dados = resposta.json()
        jogos = dados["response"]

        enviados = 0
        for jogo in jogos:
            casa = jogo['teams']['home']['name']
            fora = jogo['teams']['away']['name']
            mercados = jogo['bookmakers'][0]['bets']

            for mercado in mercados:
                if mercado['name'] == "Match Winner":
                    for op in mercado['values']:
                        if float(op['odd']) >= 2.50:
                            enviados += 1
                            bot.send_message(mensagem.chat.id, f"🔥 {casa} x {fora}\n{op['value']}: odd {op['odd']}")
                    break

        if enviados == 0:
            bot.send_message(mensagem.chat.id, "Nenhuma odd acima de 2.50 encontrada hoje.")

    except:
        bot.send_message(mensagem.chat.id, "Erro ao consultar odds. Verifica tua API KEY ou se a Betclic está disponível.")


# === COMANDO /premier ===
@bot.message_handler(commands=["premier"])
def responder_premier(msg):
    hoje = datetime.now().strftime("%Y-%m-%d")
    url = "https://v3.football.api-sports.io/fixtures"
    params = {
        "date": hoje,
        "league": 39,       # Premier League
        "season": 2023  # ou atual, se tua API permitir
    }
    try:
        res = requests.get(url, headers=HEADERS, params=params)
        dados = res.json().get("response", [])
        if not dados:
            bot.send_message(msg.chat.id, "Nenhum jogo da Premier League hoje.")
            return

        for jogo in dados:
            casa = jogo["teams"]["home"]["name"]
            fora = jogo["teams"]["away"]["name"]
            hora = jogo["fixture"]["date"][11:16]
            status = jogo["fixture"]["status"]["short"]
            resultado = jogo["goals"]
            texto = f"🏟 {hora} | {casa} {resultado['home']} x {resultado['away']} {fora} ({status})"
            bot.send_message(msg.chat.id, texto)

    except:
        bot.send_message(msg.chat.id, "Erro ao buscar jogos da Premier League.")


bot.polling()
