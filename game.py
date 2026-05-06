import random
import threading
import uuid
from model import GiocataDemo, GiocataReal, User
from conectdb_Roman import db_session

bot_instance = None
round_attivi = {"demo": False, "real": False}
chat_gioco = {"demo": None, "real": None}
timer_round = {"demo": None, "real": None}
partecipanti = {"demo": set(), "real": set()}
giocate_correnti = {"demo": [], "real": []}
round_ids = {"demo": None, "real": None}


def set_bot(bot):
    global bot_instance
    bot_instance = bot


def avvia_round(chat_id, mode="demo"):
    round_attivi[mode] = True
    chat_gioco[mode] = chat_id
    round_ids[mode] = str(uuid.uuid4())[:8] # Generiamo un ID corto
    bot_instance.send_message(chat_id, f"🎮 Раунд '{mode}' розпочато (ID: {round_ids[mode]}). Зробіть ставку через /versareal або /versademo")
    timer = threading.Timer(60, chiudi_round, args=[mode])
    timer_round[mode] = timer
    timer.start()


def start_partecipazione(chat_id, user_id, username, importo, mode="demo"):
    if not round_attivi[mode]:
        bot_instance.send_message(chat_id, f"❌ Раунд '{mode}' наразі не активний.")
        return

    if user_id in partecipanti[mode]:
        bot_instance.send_message(chat_id, "Ви вже берете участь у цьому раунді.")
        return

    if importo < 5:
        bot_instance.send_message(chat_id, "❌ Мінімальна ставка: 5 HivePoint.")
        return

    user = db_session.query(User).filter_by(user_id=user_id).first()
    if not user:
        bot_instance.send_message(chat_id, "❌ Користувача не знайдено.")
        return

    saldo = user.demo_balance if mode == "demo" else user.balance
    if saldo < importo:
        bot_instance.send_message(chat_id, "❌ Недостатньо HivePoint.")
        return

    if mode == "demo":
        user.demo_balance -= importo
        giocata = GiocataDemo(round_id=round_ids[mode], user_id=user_id, username=username, puntata=importo)
    else:
        user.balance -= importo
        giocata = GiocataReal(round_id=round_ids[mode], user_id=user_id, username=username, puntata=importo)

    db_session.add(giocata)
    db_session.commit()

    giocate_correnti[mode].append({
        'user_id': user_id,
        'username': username,
        'importo': importo,
        'giocata_id': giocata.id
    })

    partecipanti[mode].add(user_id)
    bot_instance.send_message(chat_id, f"✅ {username} зробив ставку {importo} HivePoint!")


def chiudi_round(mode):
    chat_id = chat_gioco[mode]
    correnti = giocate_correnti[mode]
    partecipanti_data = {}

    for g in correnti:
        partecipanti_data[g['username']] = partecipanti_data.get(g['username'], 0) + g['importo']

    # Якщо менше 2 унікальних учасників — повернення ставок
    if len(partecipanti_data) < 2:
        for g in correnti:
            user = db_session.query(User).filter_by(user_id=g['user_id']).first()
            if user:
                if mode == "demo":
                    user.demo_balance += g['importo']
                else:
                    user.balance += g['importo']
            
            # Rimuoviamo la giocata dallo storico visto che è annullata
            if mode == "demo":
                db_session.query(GiocataDemo).filter_by(id=g['giocata_id']).delete()
            else:
                db_session.query(GiocataReal).filter_by(id=g['giocata_id']).delete()

        db_session.commit()

        msg_annullato = "❌ Недостатньо учасників. Раунд скасовано. HivePoint повернуто."
        inviati = set()
        try:
            bot_instance.send_message(chat_id, msg_annullato)
            inviati.add(chat_id)
        except Exception:
            pass
            
        for g in correnti:
            uid = g['user_id']
            if uid not in inviati:
                try:
                    bot_instance.send_message(uid, msg_annullato)
                    inviati.add(uid)
                except Exception:
                    pass

        reset_round(mode)
        return

    # Інакше — обрати переможця
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

    # Salviamo la vincita nella tabella
    for g in correnti:
        if g['username'] == vincitore:
            if mode == "demo":
                giocata = db_session.query(GiocataDemo).filter_by(id=g['giocata_id']).first()
                if giocata:
                    giocata.vincita += premio
            else:
                giocata = db_session.query(GiocataReal).filter_by(id=g['giocata_id']).first()
                if giocata:
                    giocata.vincita += premio

    admin_user = db_session.query(User).filter_by(is_admin=True).first()
    if admin_user:
        if mode == "demo":
            admin_user.demo_balance += commissione
        else:
            admin_user.balance += commissione

    db_session.commit()

    msg_finale = (f"🏁 Раунд '{mode}' завершено!\n"
                  f"🏆 Переможець: {vincitore}\n"
                  f"💰 Приз: {premio} HivePoint\n"
                  f"👑 Комісія для адміна: {commissione} HivePoint")

    inviati = set()
    try:
        bot_instance.send_message(chat_id, msg_finale)
        inviati.add(chat_id)
    except Exception:
        pass
        
    # Invia notifica a tutti i partecipanti
    for g in correnti:
        uid = g['user_id']
        if uid not in inviati:
            try:
                bot_instance.send_message(uid, msg_finale)
                inviati.add(uid)
            except Exception:
                pass

    reset_round(mode)


def reset_round(mode):
    round_attivi[mode] = False
    chat_gioco[mode] = None
    round_ids[mode] = None
    partecipanti[mode].clear()
    giocate_correnti[mode].clear()
    if timer_round[mode]:
        timer_round[mode].cancel()
        timer_round[mode] = None


def is_round_attivo(mode):
    return round_attivi[mode]
