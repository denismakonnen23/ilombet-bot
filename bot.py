import telebot

TOKEN = "8153287953:AAEsrLms2ICNGOY2uqKOHlm0pGUQHbxIu1A"

bot=telebot.TeleBot (TOKEN)

def verificar(mensagem):
    if mensagem.text == "start":
        return True


@bot.message_handler(func=verificar)
def responder (mensagem):
    bot.reply_to(mensagem, "Olá, aqui é o ILØMBetBot!")


bot.polling()
