from aiohttp import web
from conectdb_Roman import db_session

# Funzione per inviare messaggi tramite il bot (configurata in main.py)
send_message_to_user = None

def setup_bot_instance(bot_instance):
    global send_message_to_user
    send_message_to_user = bot_instance.send_message

async def webhook_handler(request):
    if request.method != "POST":
        return web.Response(status=405, text="Method Not Allowed")

    try:
        data = await request.json()
        inner_payload = data.get("payload", {})
        
        # ID utente (inviato come stringa nel payload di CryptoBot)
        user_id_raw = inner_payload.get("payload") 
        # Quantità di TON effettivamente pagata
        amount_raw = inner_payload.get("paid_amount")

        if not user_id_raw or not amount_raw:
            print(f"⚠️ Dati incompleti ricevuti: {data}")
            return web.Response(status=400, text="Dati incompleti")

        user_id = int(user_id_raw)
        ton_versati = float(amount_raw)
        
        # LOGICA DI CONVERSIONE: 1 TON = 5 CREDITI
        moltiplicatore = 5
        crediti_da_aggiungere = ton_versati * moltiplicatore

        from model import User, Versamento
        user = db_session.query(User).filter_by(user_id=user_id).first()
        
        if user:
    # Calcoli
            ton_versati = float(amount_raw)
            crediti_da_aggiungere = ton_versati * 5
            user.balance += crediti_da_aggiungere

    # Recuperiamo i dati mancanti dal JSON di CryptoBot (data)
    # inner_payload è data.get("payload")
            invoice_id = inner_payload.get("invoice_id")
            valuta = inner_payload.get("asset")  # es. "TON"
            stato = inner_payload.get("status") # es. "paid"

    # CREAZIONE DEL VERSAMENTO (usando i nomi del tuo __init__)
            nuovo_v = Versamento(
                invoice_id=invoice_id,
                user_id=user_id,
                username=user.username, # Lo prendiamo dall'utente trovato nel DB
                importo=ton_versati,    # Qui usiamo 'importo' come nel tuo model
                valuta=valuta,
                stato=stato
            )
    
            db_session.add(nuovo_v)
            db_session.commit()
            # Notifica l'utente
            if send_message_to_user:
                messaggio = (
                    f"✅ **Pagamento Confermato!**\n\n"
                    f"💰 Hai versato: `{ton_versati}` TON\n"
                    f"🎮 Crediti aggiunti: `+{crediti_da_aggiungere}`\n"
                    f"💳 Nuovo saldo: `{user.balance}` crediti"
                )
                try:
                    # Usiamo il metodo del bot passato da main.py
                    send_message_to_user(user_id, messaggio)
                except Exception as e:
                    print(f"Errore invio messaggio bot: {e}")
            
            return web.Response(status=200, text="OK")
        else:
            print(f"❌ Utente {user_id} non trovato nel database.")
            return web.Response(status=404, text="Utente non trovato")

    except Exception as e:
        db_session.rollback()
        print(f"🔥 Errore nel processare il webhook: {e}")
        return web.Response(status=500, text="Internal Server Error")

async def start_webhook_server():
    app = web.Application()
    app.router.add_post("/webhook", webhook_handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()
    print("🚀 Server Webhook attivo sulla porta 8080 (1 TON = 5 Crediti)")