import requests
import telebot
import schedule
import time
from datetime import datetime
#Chat ID
@bot.message_handler(commands=['start'])
def send_chat_id(message):
    bot.send_message(message.chat.id, f"🆔 Teu Chat ID é: {message.chat.id}")
# === Configurações ===
API_KEY = "177074678f6469c26f1b885a5a0fb0a6"
TELEGRAM_TOKEN = "8153287953:AAEsrLms2ICNGOY2uqKOHlm0pGUQHbxIu1A"
CHAT_ID = "SEU_CHAT_ID"  # ou mensagem.chat.id se for dinâmico
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# IDs das ligas e dos times
LIGAS = [39, 78]  # Premier League, Bundesliga
TIMES_FIXOS = [541, 529]  # Real Madrid, Barcelona

def buscar_jogos_hoje():
    hoje = datetime.today().strftime("%Y-%m-%d")
    headers = {"x-apisports-key": API_KEY}
    url = "https://v3.football.api-sports.io/fixtures"

    jogos_interessantes = []

    for liga_id in LIGAS:
        params = {"league": liga_id, "date": hoje}
        r = requests.get(url, headers=headers, params=params).json()
        jogos_interessantes.extend(r["response"])

    for team_id in TIMES_FIXOS:
        params = {"team": team_id, "date": hoje}
        r = requests.get(url, headers=headers, params=params).json()
        jogos_interessantes.extend(r["response"])

    return jogos_interessantes

def calcular_over25_percent(team_id):
    url = "https://v3.football.api-sports.io/fixtures"
    headers = {"x-apisports-key": API_KEY}
    params = {"team": team_id, "last": 10}
    r = requests.get(url, headers=headers, params=params).json()
    jogos = r["response"]

    if not jogos:
        return 0

    over25 = 0
    for jogo in jogos:
        gols = jogo["goals"]["home"] + jogo["goals"]["away"]
        if gols >= 3:
            over25 += 1

    return round((over25 / len(jogos)) * 100, 1)

def analisar_jogos():
    jogos = buscar_jogos_hoje()
    headers = {"x-apisports-key": API_KEY}

    for jogo in jogos:
        id_home = jogo["teams"]["home"]["id"]
        id_away = jogo["teams"]["away"]["id"]
        nome_home = jogo["teams"]["home"]["name"]
        nome_away = jogo["teams"]["away"]["name"]
        hora = jogo["fixture"]["date"][11:16]

        over_home = calcular_over25_percent(id_home)
        over_away = calcular_over25_percent(id_away)

        if over_home >= 70 and over_away >= 70:
            mensagem = (
                f"⚽ *Oportunidade de Over 2.5 Detetada!*\n\n"
                f"🆚 {nome_home} x {nome_away}\n"
                f"🕒 {hora} de hoje\n\n"
                f"📊 Over 2.5 últimos 10 jogos:\n"
                f"- {nome_home}: {over_home}%\n"
                f"- {nome_away}: {over_away}%\n\n"
                f"🔥 Tendência: *Over 2.5*\n"
            )
            bot.send_message(chat_id=CHAT_ID, text=mensagem, parse_mode="Markdown")

# === Scheduler: roda a cada 1 hora ===
schedule.every(1).hours.do(analisar_jogos)

print("Bot de alertas iniciado...")

while True:
    schedule.run_pending()
    time.sleep(60)
