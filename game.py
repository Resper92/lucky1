import random
import threading
from model import Versamento, User
from conectdb import db_session

bot_instance = None
round_attivi = {"demo": False, "real": False}
chat_gioco = {"demo": None, "real": None}
timer_round = {"demo": None, "real": None}
partecipanti = {"demo": set(), "real": set()}


def set_bot(bot):
    global bot_instance
    bot_instance = bot


def avvia_round(chat_id, mode="demo"):
    round_attivi[mode] = True
    chat_gioco[mode] = chat_id
    bot_instance.send_message(chat_id, f"🎮 Round '{mode}' avviato. Fai la tua puntata con /versareal o /versademo")
    timer = threading.Timer(60, chiudi_round, args=[mode])
    timer_round[mode] = timer
    timer.start()


def start_partecipazione(chat_id, user_id, username, importo, mode="demo"):
    if not round_attivi[mode]:
        bot_instance.send_message(chat_id, f"❌ Il round '{mode}' non è attivo.")
        return

    if user_id in partecipanti[mode]:
        bot_instance.send_message(chat_id, "Hai già partecipato a questo round.")
        return

    if importo < 5:
        bot_instance.send_message(chat_id, "❌ Importo minimo: 5 hivepoint.")
        return

    user = db_session.query(User).filter_by(user_id=user_id).first()
    if not user:
        bot_instance.send_message(chat_id, "❌ Utente non trovato.")
        return

    saldo = user.demo_balance if mode == "demo" else user.balance
    if saldo < importo:
        bot_instance.send_message(chat_id, "❌ Saldo insufficiente.")
        return

    if mode == "demo":
        user.demo_balance -= importo
    else:
        user.balance -= importo

    vers = Versamento(user_id=user_id, username=username, importo=importo, tipo=mode)
    db_session.add(vers)
    db_session.commit()

    partecipanti[mode].add(user_id)
    bot_instance.send_message(chat_id, f"✅ {username} ha partecipato con {importo} crediti!")


def chiudi_round(mode):
    chat_id = chat_gioco[mode]
    versamenti = db_session.query(Versamento).filter_by(tipo=mode).all()
    partecipanti_data = {}

    for v in versamenti:
        partecipanti_data[v.username] = partecipanti_data.get(v.username, 0) + v.importo

    # Se ci sono meno di 2 partecipanti unici, annulla e rimborsa
    if len(partecipanti_data) < 2:
        for v in versamenti:
            user = db_session.query(User).filter_by(user_id=v.user_id).first()
            if user:
                if mode == "demo":
                    user.demo_balance += v.importo
                else:
                    user.balance += v.importo
        db_session.commit()

        bot_instance.send_message(chat_id, "❌ Partecipanti insufficienti. Round annullato. I crediti sono stati restituiti.")
        db_session.query(Versamento).filter_by(tipo=mode).delete()
        db_session.commit()
        reset_round(mode)
        return

    # Altrimenti procedi normalmente
    nomi = list(partecipanti_data.keys())
    pesi = list(partecipanti_data.values())
    vincitore = random.choices(nomi, weights=pesi, k=1)[0]

    somma_totale = sum(pesi)
    commissione = len(nomi)
    premio = round(somma_totale - commissione, 2)

    user_vincitore = db_session.query(User).filter_by(username=vincitore).first()
    if user_vincitore:
        if mode == "demo":
            user_vincitore.demo_balance += premio
        else:
            user_vincitore.balance += premio

    admin_user = db_session.query(User).filter_by(is_admin=True).first()
    if admin_user:
        if mode == "demo":
            admin_user.demo_balance += commissione
        else:
            admin_user.balance += commissione

    db_session.commit()

    bot_instance.send_message(chat_id, f"🏁 Round '{mode}' terminato!\n"
                                       f"Vincitore: {vincitore}\n"
                                       f"Premio: {premio} crediti\n"
                                       f"Commissione admin: {commissione} crediti")

    db_session.query(Versamento).filter_by(tipo=mode).delete()
    db_session.commit()
    reset_round(mode)


def reset_round(mode):
    round_attivi[mode] = False
    chat_gioco[mode] = None
    partecipanti[mode].clear()
    if timer_round[mode]:
        timer_round[mode].cancel()
        timer_round[mode] = None


def is_round_attivo(mode):
    return round_attivi[mode] 