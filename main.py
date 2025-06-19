from telebot.types import Message
import telebot
from conectdb import db_session ,init_db
from model import Versamento,User
import game

TOKEN = '7771460111:AAFqpxCVzdRKP8Pz-UZxaRnYHWgOsOtjFvg'
bot = telebot.TeleBot(TOKEN)

# Passa bot a game
game.set_bot(bot)

@bot.message_handler(commands=['start'])
def handle_start(message):
    username = message.from_user.username
    user_id = message.from_user.id 
    user  = User(username=username,user_id=user_id,balance=0,n_card=0,pay_pal=0)
    db_session.add(user)
    db_session.commit()
    bot.reply_to(message, "per giocare fai la registrazione completando il comando /registraion")
   
@bot.message_handler(commands=['registration'])
def registration(message: Message):
    user_id = message.from_user.id
    session = db_session
    user = session.query(User).filter_by(user_id=user_id).first()

    if not user:
        bot.send_message(user_id, "Prima usa /start per registrarti.")
        return

    bot.send_message(user_id, "Inserisci la tua email:")
    bot.register_next_step_handler(message, get_email)


def get_email(message: Message):
    user_id = message.from_user.id
    email = message.text.strip()

    session = db_session
    user = session.query(User).filter_by(user_id=user_id).first()
    if user:
        user.email = email
        session.commit()
        bot.send_message(user_id, "Inserisci il numero della tua carta (o scrivi 'skip'):")
        bot.register_next_step_handler(message, get_card)
    else:
        bot.send_message(user_id, "Errore: utente non trovato.")


def get_card(message: Message):
    user_id = message.from_user.id
    card_text = message.text.strip()
    n_card = int(card_text) if card_text.lower() != 'skip' and card_text.isdigit() else None

    session = db_session
    user = session.query(User).filter_by(user_id=user_id).first()
    if user:
        user.n_card = n_card
        session.commit()
        bot.send_message(user_id, "Inserisci la tua email PayPal (o scrivi 'skip'):")
        bot.register_next_step_handler(message, get_paypal)
    else:
        bot.send_message(user_id, "Errore: utente non trovato.")


def get_paypal(message: Message):
    user_id = message.from_user.id
    paypal = message.text.strip()
    paypal = paypal if paypal.lower() != 'skip' else None

    session = db_session
    user = session.query(User).filter_by(user_id=user_id).first()
    if user:
        user.pay_pal = paypal
        session.commit()
        bot.send_message(user_id, "Registrazione completata con successo!")
    else:
        bot.send_message(user_id, "Errore: utente non trovato.")


    

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
