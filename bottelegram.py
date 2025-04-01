import telebot
import requests
from datetime import datetime
import os
CHAT_ID = None

# === CONFIGURAÇÕES ===
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_KEY = os.getenv("API_FOOTBALL_KEY")
bot = telebot.TeleBot(TOKEN)
HEADERS = {"x-apisports-key": API_KEY}

# === FUNÇÃO: buscar jogos de hoje ===
def buscar_jogos():
    hoje = datetime.now().strftime("%Y-%m-%d")
    url = "https://v3.football.api-sports.io/fixtures"
    headers = {"x-apisports-key": API_KEY}
    params = {"date": hoje}
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

        for jogo in jogos[:10]:
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
        "bookmaker": 8
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

# === COMANDO /premier (ligado à liga) ===
@bot.message_handler(commands=['premier'])
def premier_league(message):
    bot.send_message(message.chat.id, "🏴 Buscando jogos da Premier League com over 2.5 gols...")
    buscar_jogos_liga(message, liga='Premier League')

@bot.message_handler(commands=['bundesliga'])
def bundesliga(message):
    bot.send_message(message.chat.id, "🇩🇪 Buscando jogos da Bundesliga com over 2.5 gols...")
    buscar_jogos_liga(message, liga='Bundesliga')

@bot.message_handler(commands=['real'])
def real_madrid(message):
    bot.send_message(message.chat.id, "🤍 Buscando jogos do Real Madrid com over 2.5 gols...")
    buscar_jogos_time(message, time='Real Madrid')

@bot.message_handler(commands=['barcelona'])
def barcelona(message):
    bot.send_message(message.chat.id, "🔵🔴 Buscando jogos do Barcelona com over 2.5 gols...")
    buscar_jogos_time(message, time='Barcelona')

# === FUNÇÃO: buscar jogos por liga ===
def buscar_jogos_liga(message, liga):
    hoje = datetime.now().strftime("%Y-%m-%d")
    url = "https://v3.football.api-sports.io/fixtures"
    headers = {"x-apisports-key": API_KEY}
    params = {"date": hoje}
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    resultados = []
    for jogo in data['response']:
        nome_liga = jogo['league']['name']
        gols = jogo['goals']
        if nome_liga.lower() == liga.lower() and gols['home'] is not None and gols['away'] is not None:
            total = gols['home'] + gols['away']
            if total > 2:
                time1 = jogo['teams']['home']['name']
                time2 = jogo['teams']['away']['name']
                resultados.append(f"🔥 {time1} {gols['home']} x {gols['away']} {time2}")
    if resultados:
        for res in resultados:
            bot.send_message(message.chat.id, res)
    else:
        bot.send_message(message.chat.id, f"Nenhum jogo com over 2.5 na {liga} hoje.")

# === FUNÇÃO: buscar jogos por time ===
def buscar_jogos_time(message, time):
    hoje = datetime.now().strftime("%Y-%m-%d")
    url = "https://v3.football.api-sports.io/fixtures"
    headers = {"x-apisports-key": API_KEY}
    params = {"date": hoje}
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    resultados = []
    for jogo in data['response']:
        time1 = jogo['teams']['home']['name']
        time2 = jogo['teams']['away']['name']
        gols = jogo['goals']
        if time.lower() in time1.lower() or time.lower() in time2.lower():
            if gols['home'] is not None and gols['away'] is not None:
                total = gols['home'] + gols['away']
                if total > 2:
                    resultados.append(f"🔥 {time1} {gols['home']} x {gols['away']} {time2}")
    if resultados:
        for res in resultados:
            bot.send_message(message.chat.id, res)
    else:
        bot.send_message(message.chat.id, f"Nenhum jogo do {time} com over 2.5 hoje.")
import threading
import time

# === FUNÇÃO: verificar alertas over 2.5 em loop ===
def verificar_alertas():
    while True:
        try:
            jogos = buscar_jogos()
            resultados = analisar_over(jogos)
            if resultados:
                for linha in resultados:
                    bot.send_message(CHAT_ID, f"🚨 ALERTA: Jogo com over 2.5 gols!\n🔥 {linha}")
        except:
            print("Erro ao verificar alertas.")
        time.sleep(3600)  # Verifica a cada 1 hora (3600 segundos)

# === COMANDO /alertas ===
@bot.message_handler(commands=['alertas'])
def ativar_alertas(message):
    global CHAT_ID
    CHAT_ID = message.chat.id
    bot.send_message(message.chat.id, "🔔 Alertas de jogos com over 2.5 ativados! A cada 1 hora será feita uma verificação automática.")
    thread = threading.Thread(target=verificar_alertas)
    thread.daemon = True
    thread.start()

# === INICIAR O BOT ===
bot.polling()
