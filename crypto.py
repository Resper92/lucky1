import requests
import os
from dotenv import load_dotenv

load_dotenv()
token = os.environ.get("CRYPTOPAY")
BASE_URL = "https://testnet-pay.crypt.bot/api"

def create_invoice(amount, description="Поповнення акаунту", payload=None):
    url = f"{BASE_URL}/createInvoice"
    headers = {"Crypto-Pay-API-Token": token}

    data = {
        "asset": "TON",
        "amount": str(amount),
        "description": description,
        "payload": payload
    }

    response = requests.post(url, headers=headers, json=data)
    return response.json()