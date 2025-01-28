import os
import json
import requests
from web3 import Web3

# Настройки
INFURA_URL = "https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID"  # Замените на ваш Infura или RPC
CONTRACT_ADDRESS = Web3.to_checksum_address("0x1cb1a5e65610aeff2551a50f76a87a7d3fb649c6")  # Адрес контракта CrypToadz
OUTPUT_DIR = "for example cryptoadz"
START_TOKEN = 0
END_TOKEN = 7025  # Всего 7025 токенов

# ABI для взаимодействия
ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_tokenId", "type": "uint256"}],
        "name": "tokenURI",
        "outputs": [{"name": "", "type": "string"}],
        "type": "function",
    }
]

# Инициализация Web3
w3 = Web3(Web3.HTTPProvider(INFURA_URL))
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=ABI)

# Создание папки для сохранения
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Функция для загрузки файла
def download_file(url, path):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(path, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        print(f"Скачано: {path}")
    except Exception as e:
        print(f"Ошибка при загрузке {url}: {e}")

# Загрузка коллекции
for token_id in range(START_TOKEN, END_TOKEN + 1):
    try:
        # Получение URI токена
        token_uri = contract.functions.tokenURI(token_id).call()
        print(f"Токен {token_id}: {token_uri}")

        # Скачивание метаданных
        metadata_path = os.path.join(OUTPUT_DIR, f"{token_id}.json")
        if not os.path.exists(metadata_path):
            response = requests.get(token_uri)
            metadata = response.json()
            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=4)
        else:
            with open(metadata_path, "r") as f:
                metadata = json.load(f)

        # Скачивание изображения
        image_url = metadata.get("image", "").replace("ipfs://", "https://ipfs.io/ipfs/")
        if image_url:
            image_path = os.path.join(OUTPUT_DIR, f"{token_id}.png")
            if not os.path.exists(image_path):
                download_file(image_url, image_path)

    except Exception as e:
        print(f"Ошибка для токена {token_id}: {e}")
