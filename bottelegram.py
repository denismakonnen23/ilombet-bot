import telebot
import requests
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# === CONFIGURAÇÕES ===
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_KEY = os.getenv("API_FOOTBALL_KEY")

if not TOKEN:
    raise ValueError("❌ TELEGRAM_BOT_TOKEN não foi encontrado nas variáveis de ambiente.")
if not API_KEY:
    raise ValueError("❌ API_FOOTBALL_KEY não foi encontrado nas variáveis de ambiente.")

bot = telebot.TeleBot(TOKEN)
HEADERS = {"x-apisports-key": API_KEY}

# === FUNÇÕES ===
def buscar_jogos():
    hoje = datetime.now().strftime("%Y-%m-%d")
    url = "https://v3.football.api-sports.io/fixtures"
    params = {"date": hoje}
    resposta = requests.get(url, headers=HEADERS, params=params)
    dados = resposta.json()
    return dados["response"]

def analisar_over(jogos):
    mensagens = []
    for jogo in jogos:
        status = jogo['fixture']['status']['short']
        golos_home = jogo['goals']['home'] or 0
        golos_away = jogo['goals']['away'] or 0
        total_golos = golos_home + golos_away
        if status != "NS" and total_golos >= 3:
            casa = jogo['teams']['home']['name']
            fora = jogo['teams']['away']['name']
            mensagens.append(f"{casa} {total_golos} x {fora}")
    return mensagens

def buscar_jogos_liga(message, liga):
    hoje = datetime.now().strftime("%Y-%m-%d")
    url = "https://v3.football.api-sports.io/fixtures"
    params = {"date": hoje, "league": liga, "season": 2023}
    resposta = requests.get(url, headers=HEADERS, params=params)
    jogos = resposta.json()["response"]
    resultados = analisar_over(jogos)
    if resultados:
        for linha in resultados:
            bot.send_message(message.chat.id, f"🔥 {linha}")
    else:
        bot.send_message(message.chat.id, "Nenhum jogo com over 2.5 nesta liga.")

def buscar_jogos_time(message, time):
    hoje = datetime.now().strftime("%Y-%m-%d")
    url = "https://v3.football.api-sports.io/fixtures"
    params = {"date": hoje, "team": time, "season": 2023}
    resposta = requests.get(url, headers=HEADERS, params=params)
    jogos = resposta.json()["response"]
    resultados = analisar_over(jogos)
    if resultados:
        for linha in resultados:
            bot.send_message(message.chat.id, f"🔥 {linha}")
    else:
        bot.send_message(message.chat.id, "Nenhum jogo com over 2.5 deste time.")

# === COMANDOS ===
@bot.message_handler(commands=["start"])
def responder_inicio(msg):
    texto = "Olá, Daniel! Usa o comando /over para ver jogos com tendência de over 2.5 ⚽"
    bot.reply_to(msg, texto)

@bot.message_handler(commands=["over"])
def responder_over(msg):
    bot.send_message(msg.chat.id, "⏳ Buscando jogos com over 2.5...")
    try:
        jogos = buscar_jogos()
        resultados = analisar_over(jogos)
        if resultados:
            for linha in resultados:
                bot.send_message(msg.chat.id, f"🔥 {linha}")
        else:
            bot.send_message(msg.chat.id, "Nenhum jogo com over 2.5 até agora.")
    except:
        bot.send_message(msg.chat.id, "Erro ao buscar dados. Verifique a chave da API.")

@bot.message_handler(commands=["hoje"])
def jogos_hoje(msg):
    bot.send_message(msg.chat.id, "🔍 Procurando os jogos de hoje...")
    try:
        hoje = datetime.now().strftime("%Y-%m-%d")
        url = "https://v3.football.api-sports.io/fixtures"
        params = {"date": hoje}
        resposta = requests.get(url, headers=HEADERS, params=params)
        dados = resposta.json()["response"]

        if not dados:
            bot.send_message(msg.chat.id, "Nenhum jogo encontrado hoje.")
            return

        for jogo in dados[:10]:
            casa = jogo['teams']['home']['name']
            fora = jogo['teams']['away']['name']
            hora = jogo['fixture']['date'][11:16]
            bot.send_message(msg.chat.id, f"⚽ {hora} | {casa} x {fora}")

    except:
        bot.send_message(msg.chat.id, "Erro ao buscar jogos. Verifique sua API KEY.")

@bot.message_handler(commands=["oddsaltas"])
def jogos_com_odds_altas(msg):
    bot.send_message(msg.chat.id, "💸 Procurando jogos com odds acima de 2.50...")
    hoje = datetime.now().strftime("%Y-%m-%d")
    url = "https://v3.football.api-sports.io/odds"
    params = {"date": hoje, "bookmaker": 8}

    try:
        resposta = requests.get(url, headers=HEADERS, params=params)
        dados = resposta.json()["response"]

        enviados = 0
        for jogo in dados:
            casa = jogo['teams']['home']['name']
            fora = jogo['teams']['away']['name']
            mercados = jogo['bookmakers'][0]['bets']
            for mercado in mercados:
                if mercado['name'] == "Match Winner":
                    for op in mercado['values']:
                        if float(op['odd']) >= 2.50:
                            enviados += 1
                            bot.send_message(msg.chat.id, f"🔥 {casa} x {fora}\n{op['value']}: odd {op['odd']}")
                    break

        if enviados == 0:
            bot.send_message(msg.chat.id, "Nenhuma odd acima de 2.50 encontrada hoje.")

    except:
        bot.send_message(msg.chat.id, "Erro ao consultar odds. Verifique a API KEY.")

@bot.message_handler(commands=['premier'])
def premier(msg):
    bot.send_message(msg.chat.id, "🏴 Buscando jogos da Premier League com over 2.5 gols...")
    buscar_jogos_liga(msg, liga='39')

@bot.message_handler(commands=['bundesliga'])
def bundesliga(msg):
    bot.send_message(msg.chat.id, "🇩🇪 Buscando jogos da Bundesliga com over 2.5 gols...")
    buscar_jogos_liga(msg, liga='78')

@bot.message_handler(commands=['real'])
def real_madrid(msg):
    bot.send_message(msg.chat.id, "🤍 Buscando jogos do Real Madrid com over 2.5 gols...")
    buscar_jogos_time(msg, time='541')

@bot.message_handler(commands=['barcelona'])
def barcelona(msg):
    bot.send_message(msg.chat.id, "🔵🔴 Buscando jogos do Barcelona com over 2.5 gols...")
    buscar_jogos_time(msg, time='529')

@bot.message_handler(commands=['alertas'])
def alertas(msg):
    bot.send_message(msg.chat.id, "🚨 Ativação de alertas automáticos ainda está em desenvolvimento. Em breve 🔔")

bot.polling()
