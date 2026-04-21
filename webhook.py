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
        # Crypto Pay invia i dati dentro 'payload'
        inner_payload = data.get("payload", {})
        
        # Verifichiamo che l'evento sia effettivamente un pagamento confermato
        update_type = data.get("update_type")
        status = inner_payload.get("status")

        if update_type != "invoice_paid" or status != "paid":
            return web.Response(status=200, text="Ignored non-paid update")

        # Recuperiamo l'ID utente che abbiamo passato nel campo 'payload' durante la create_invoice
        user_id_raw = inner_payload.get("payload") 
        amount_raw = inner_payload.get("amount") # Usiamo 'amount' (prezzo richiesto)

        if not user_id_raw or not amount_raw:
            return web.Response(status=400, text="Dati incompleti")

        user_id = int(user_id_raw)
        valuta_reale = float(amount_raw)
        
        # LOGICA 1:5 (1 USDT/TON = 5 Crediti)
        crediti_da_aggiungere = valuta_reale * 5

        from model import User, Versamento
        user = db_session.query(User).filter_by(user_id=user_id).first()
        
        if user:
            # Aggiornamento saldo
            user.balance += crediti_da_aggiungere

            # Creazione record Versamento
            nuovo_v = Versamento(
                invoice_id=int(inner_payload.get("invoice_id")),
                user_id=user_id,
                username=user.username,
                importo=valuta_reale,
                valuta=inner_payload.get("asset"),
                stato=status
            )
    
            db_session.add(nuovo_v)
            db_session.commit()

            if send_message_to_user:
                messaggio = (
                    f"✅ **Баланс поповнено!**\n\n"
                    f"💰 Отримано: `{valuta_reale}` {inner_payload.get('asset')}\n"
                    f"🎮 Нараховано: `+{crediti_da_aggiungere}` кредитів\n"
                    f"💳 Поточний баланс: `{user.balance}`"
                )
                try:
                    send_message_to_user(user_id, messaggio)
                except Exception: pass
            
            return web.Response(status=200, text="OK")
        
        return web.Response(status=404, text="User not found")

    except Exception as e:
        db_session.rollback()
        print(f"🔥 Webhook Error: {e}")
        return web.Response(status=500, text="Error")

async def start_webhook_server():
    app = web.Application()
    app.router.add_post("/webhook", webhook_handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()
    print("🚀 Server Webhook attivo sulla porta 8080 (1 TON = 5 Crediti)")