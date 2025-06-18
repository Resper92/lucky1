# game.py
import random
import threading
from model import Versamento
from conectdb import db_session

round_attivo = False
chat_di_gioco = None
bot_instance = None  # sarà impostato da main.py


def set_bot(bot):
    global bot_instance
    bot_instance = bot


def is_round_attivo():
    return round_attivo


def start_round_timer(chat_id):
    global round_attivo, chat_di_gioco
    round_attivo = True
    chat_di_gioco = chat_id
    bot_instance.send_message(chat_id, "⏳ Il round è iniziato! Hai 30 secondi per partecipare...")
    threading.Timer(30, chiudi_round).start()


def chiudi_round():
    global round_attivo
    round_attivo = False

    partecipanti = {}
    for row in db_session.query(Versamento).all():
        partecipanti[row.username] = partecipanti.get(row.username, 0) + row.importo

    if not partecipanti:
        bot_instance.send_message(chat_di_gioco, "⛔️ Nessun partecipante. Round annullato.")
        return

    nomi = list(partecipanti.keys())
    pesi = list(partecipanti.values())

    vincitore = random.choices(nomi, weights=pesi, k=1)[0]
    somma_totale = sum(pesi)
    premio_admin = round(somma_totale * 0.15, 2)
    premio_vincitore = round(somma_totale * 0.85, 2)

    messaggio = (
        f"🎉 Round terminato!\n"
        f"🏆 Vincitore: {vincitore}\n\n"
        f"💰 Totale raccolto: {somma_totale:.2f}€\n"
        f"👑 Premio al vincitore: {premio_vincitore:.2f}€\n"
        f"🛠️ Commissione admin: {premio_admin:.2f}€"
    )

    bot_instance.send_message(chat_di_gioco, messaggio)
    db_session.query(Versamento).delete()
    db_session.commit()
