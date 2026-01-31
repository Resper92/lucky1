import os
import requests
from dotenv import load_dotenv

load_dotenv()

token = os.environ.get("CRYPTOPAY")
BASE_URL = "https://testnet-pay.crypt.bot/api"


def get_me(token):
    url = "https://testnet-pay.crypt.bot/api/getMe"
    headers = {
        "Crypto-Pay-API-Token": token
    }
    response = requests.get(url, headers=headers)
    return response.json()  # ritorna direttamente il JSON

print(get_me(token))

def create_invoice(amount, asset="JET", description="Test payment"):
    url = f"{BASE_URL}/createInvoice"
    headers = {
        "Crypto-Pay-API-Token": token
    }
    data = {
        "asset": asset,
        "amount": str(amount),
        "description": description
    }

    response = requests.post(url, headers=headers, json=data)
    return response.json()

invoice = create_invoice(1.5, "TON", "Поповнення акаунту (тест)")
print(invoice)