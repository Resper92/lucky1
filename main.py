# main.py
import telebot
from conectdb import db_session
from model import Versamento
import game

TOKEN = '7131483801:AAH1g63A1VJS83j1MCdbTnuAi92w_6OIUlk'
bot = telebot.TeleBot(TOKEN)

# Passa bot a game
game.set_bot(bot)

@bot.message_handler(commands=['versa'])
def versa(message):
    try:
        importo = float(message.text.split()[1])
        if importo <= 0:
            bot.reply_to(message, "L'importo deve essere positivo.")
            return

        user_id = message.from_user.id
        username = message.from_user.username or message.from_user.first_name

        nuovo_versamento = Versamento(user_id=user_id, username=username, importo=importo)
        db_session.add(nuovo_versamento)
        db_session.commit()

        total = sum([v[0] for v in db_session.query(Versamento)
                     .filter_by(user_id=user_id)
                     .with_entities(Versamento.importo).all()])

        bot.reply_to(message, f"{username} ha versato {importo}€. Totale attuale: {total:.2f}€")

        if not game.is_round_attivo():
            game.start_round_timer(message.chat.id)

    except (IndexError, ValueError):
        bot.reply_to(message, "Uso corretto: /versa <importo>")

@bot.message_handler(commands=['lista'])
def lista(message):
    partecipanti = {}
    for row in db_session.query(Versamento).all():
        partecipanti[row.username] = partecipanti.get(row.username, 0) + row.importo

    if not partecipanti:
        bot.reply_to(message, "Nessun partecipante.")
        return

    msg = "📋 Partecipanti:\n"
    for nome, importo in partecipanti.items():
        msg += f"- {nome}: {importo:.2f}€\n"

    bot.send_message(message.chat.id, msg)

bot.polling()
