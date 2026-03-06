from aiohttp import web
from conectdb_Roman import db_session
from model import User

# Questa funzione verrà passata al webhook per inviare messaggi tramite il bot
send_message_to_user = None

def setup_bot_instance(bot_instance):
    """
    Imposta l'istanza del bot per poter inviare messaggi.
    """
    global send_message_to_user
    send_message_to_user = bot_instance.send_message

async def webhook_handler(request):
    """
    Gestisce le richieste in arrivo dal servizio di pagamento.
    """
    if request.method != "POST":
        return web.Response(status=405, text="Method Not Allowed")

    try:
        data = await request.json()
        # Qui assumeremo che il provider di pagamento invii 'user_id' e 'amount'
        # Dovrai adattarlo in base a ciò che il tuo provider invia
        user_id = data.get("user_id")
        amount = data.get("amount")

        if not user_id or not amount:
            print("Dati webhook incompleti:", data)
            return web.Response(status=400, text="Dati incompleti")

        # Trova l'utente e aggiorna il suo bilancio
        user = db_session.query(User).filter_by(user_id=user_id).first()
        if user:
            user.balance += float(amount)
            db_session.commit()
            print(f"Bilancio aggiornato per l'utente {user_id} di {amount}")

            # Invia un messaggio di conferma all'utente
            if send_message_to_user:
                send_message_to_user(user_id, f"✅ Il tuo pagamento di {amount} TON è stato ricevuto e il tuo bilancio è stato aggiornato!")
            
            return web.Response(status=200, text="OK")
        else:
            print(f"Utente non trovato con ID: {user_id}")
            return web.Response(status=404, text="Utente non trovato")

    except Exception as e:
        print(f"Errore nella gestione del webhook: {e}")
        return web.Response(status=500, text="Internal Server Error")

async def start_webhook_server():
    """
    Avvia il server web per il webhook.
    """
    app = web.Application()
    app.router.add_post("/webhook", webhook_handler)
    
    runner = web.AppRunner(app)
    await runner.setup()
    
    # Ascolta su tutte le interfacce sulla porta 8080
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()
    
    print("🚀 Server webhook avviato su http://0.0.0.0:8080")
