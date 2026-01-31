from telebot.types import Message
import telebot
import os
from dotenv import load_dotenv
from conectdb_Roman import db_session
from model import Versamento, User
import game
from crypto import create_invoice
from sqlalchemy import func


load_dotenv()
bot = telebot.TeleBot(os.environ.get("TOKEN"))
game.set_bot(bot)


def is_admin(user_id):
    user = db_session.query(User).filter_by(user_id=user_id).first()
    return user and user.is_admin

@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    username = message.from_user.username or f"user_{user_id}"

    user = db_session.query(User).filter_by(user_id=user_id).first()
    if user:
        bot.reply_to(message, "Ви вже зареєстровані.")
    else:
        new_user = User(user_id=user_id, username=username, balance=0, demo_balance=100)
        db_session.add(new_user)
        db_session.commit()
        bot.reply_to(message, "✅ Реєстрація завершена. Використайте /registration для введення email.")

@bot.message_handler(commands=['registration'])
def registration(message: Message):
    user_id = message.from_user.id
    user = db_session.query(User).filter_by(user_id=user_id).first()

    if not user:
        bot.send_message(user_id, "❌ Спочатку використайте /start")
        return

    bot.send_message(user_id, "Введіть вашу email-адресу:")
    bot.register_next_step_handler(message, get_email)

def get_email(message: Message):
    user_id = message.from_user.id
    email = message.text.strip()

    user = db_session.query(User).filter_by(user_id=user_id).first()
    if user:
        user.email = email
        db_session.commit()
        bot.send_message(user_id, "📩 Email збережено. Спробуйте демо-гру з /versademo або реальну з /versareal")
    else:
        bot.send_message(user_id, "❌ Користувача не знайдено.")

@bot.message_handler(commands=['adminpanel'])
def admin_panel(message: Message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "🚫 Доступ заборонено. Тільки для адміністратора.")
        return

    total_users = db_session.query(User).count()
    sum_real = db_session.query(func.coalesce(func.sum(User.balance), 0.0)).scalar()
    sum_demo = db_session.query(func.coalesce(func.sum(User.demo_balance), 0.0)).scalar()

    demo_active = game.is_round_attivo("demo")
    real_active = game.is_round_attivo("real")
    demo_players = len(game.partecipanti["demo"])
    real_players = len(game.partecipanti["real"])

    msg = (
        f"🔐 Панель адміністратора:\n\n"
        f"👥 Зареєстровані користувачі: {total_users}\n"
        f"💰 Загальний реальний баланс: {sum_real:.2f}\n"
        f"💸 Загальний демо-баланс: {sum_demo:.2f}\n\n"
        f"🎮 Демо-гра активна: {'✅' if demo_active else '❌'} — {demo_players} гравців\n"
        f"🎯 Реальна гра активна: {'✅' if real_active else '❌'} — {real_players} гравців\n\n"
        f"🧹 /rimuovi @username — видалити користувача\n"
        f"⛔ /blocca @username — заблокувати користувача\n"
        f"➕ /aggiungicrediti @username 50 — нарахувати кредити"
    )
    bot.send_message(message.chat.id, msg)

@bot.message_handler(commands=['AddCredit'])
def aggiungi_crediti(message: Message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "🚫 У вас немає прав.")
        return

    parts = message.text.split()
    if len(parts) != 3 or not parts[1].startswith("@"):
        bot.send_message(message.chat.id, "❌ Приклад: /AddCredit @username 50")
        return

    username = parts[1][1:]
    try:
        amount = float(parts[2])
    except ValueError:
        bot.send_message(message.chat.id, "❌ Сума повинна бути числом.")
        return

    user = db_session.query(User).filter_by(username=username).first()
    if not user:
        bot.send_message(message.chat.id, "❌ Користувача не знайдено.")
        return

    user.balance += amount
    db_session.commit()
    bot.send_message(message.chat.id, f"✅ {amount} кредитів додано користувачу @{username}.")

@bot.message_handler(commands=['rimuve'])
def rimuovi_user(message: Message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "🚫 Доступ заборонено.")
        return

    parts = message.text.split()
    if len(parts) != 2 or not parts[1].startswith("@"):
        bot.send_message(message.chat.id, "❌ Приклад: /rimuve @username")
        return

    username = parts[1][1:]
    user = db_session.query(User).filter_by(username=username).first()
    if not user:
        bot.send_message(message.chat.id, "❌ Користувача не знайдено.")
        return

    db_session.delete(user)
    db_session.commit()
    bot.send_message(message.chat.id, f"✅ Користувача @{username} видалено.")

@bot.message_handler(commands=['blocca'])
def blocca_user(message: Message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "🚫 Доступ заборонено.")
        return

    parts = message.text.split()
    if len(parts) != 2 or not parts[1].startswith("@"):
        bot.send_message(message.chat.id, "❌ Приклад: /blocca @username")
        return

    username = parts[1][1:]
    user = db_session.query(User).filter_by(username=username).first()
    if not user:
        bot.send_message(message.chat.id, "❌ Користувача не знайдено.")
        return

    user.is_blocked = True
    db_session.commit()
    bot.send_message(message.chat.id, f"⛔ Користувача @{username} заблоковано.")

@bot.message_handler(commands=["startdemo"])
def versademo_handler(message):
    try:
        importo = float(message.text.split()[1])
    except (IndexError, ValueError):
        bot.send_message(message.chat.id, "❌ Формат неправильний. Використайте: /versademo 5")
        return

    if not game.is_round_attivo("demo"):
        game.avvia_round(message.chat.id, mode="demo")

    user_id = message.from_user.id
    username = message.from_user.username or f"user_{user_id}"
    game.start_partecipazione(message.chat.id, user_id, username, importo, mode="demo")

@bot.message_handler(commands=["real"])
def versareal_handler(message):
    try:
        importo = float(message.text.split()[1])
    except (IndexError, ValueError):
        bot.send_message(message.chat.id, "❌ Формат неправильний. Використайте: /versareal 5")
        return

    if not game.is_round_attivo("real"):
        game.avvia_round(message.chat.id, mode="real")

    user_id = message.from_user.id
    username = message.from_user.username or f"user_{user_id}"
    game.start_partecipazione(message.chat.id, user_id, username, importo, mode="real")
@bot.message_handler(commands=["balence"])
def balance_handler(message):
    user = db_session.query(User).filter_by(user_id=message.from_user.id).first()
    if not user:
        bot.send_message(message.chat.id, "❌ Користувача не знайдено.")
        return

    balance = user.balance
    demo_balance = user.demo_balance
    bot.send_message(message.chat.id, f"Ваш баланс: {balance}"
                     f"\nБаланс демо-гри: {demo_balance}")
    
@bot.message_handler(commands=["pay"])
def ask_amount(message):
    bot.send_message(message.chat.id, "💰 Введіть суму, яку хочете поповнити (у TON):")
    bot.register_next_step_handler(message, process_amount)

def process_amount(message):
    try:
        amount = float(message.text.strip())
        if amount <= 0:
            raise ValueError
    except ValueError:
        bot.send_message(message.chat.id, "❌ Введіть правильне число (наприклад: 5)")
        return
    
    bot.send_message(message.chat.id, "⏳ Створюю рахунок...")
    invoice = create_invoice(amount, f"Поповнення від @{message.from_user.username}")

    if invoice.get("ok"):
        pay_url = invoice["result"]["pay_url"]
        bot.send_message(message.chat.id, f"✅ Ваш рахунок готовий!\nСплатіть тут:\n{pay_url}")
    else:
        error = invoice.get("error", "Невідома помилка")
        bot.send_message(message.chat.id, f"⚠️ Помилка під час створення рахунку: {error}")
        
        
bot.polling()
