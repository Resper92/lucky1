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

def transfer(user_id, amount, description="вывод выигрыша", payload=None):
    url = f"{BASE_URL}/transfer"
    headers = {"Crypto-Pay-API-Token": token}

    data = {
        "user_id": int(user_id),    
        "asset": "TON",            
        "amount": str(amount),      
        "description": description, 
        "spend_id": payload
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        return response.json()
    except Exception as e:
        return {"ok": False, "error": str(e)}