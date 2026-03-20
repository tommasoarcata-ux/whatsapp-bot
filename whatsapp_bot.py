import requests
import time
import json

# ============================================
# CONFIGURAZIONE — inserisci i tuoi dati qui
# ============================================
ID_INSTANCE = "YOUR_ID_INSTANCE"        # es. "1101234567"
API_TOKEN   = "YOUR_API_TOKEN_INSTANCE" # es. "abc123def456..."
# ============================================

BASE_URL = f"https://api.green-api.com/waInstance{ID_INSTANCE}"


def receive_notification():
    """Riceve una notifica dalla coda."""
    url = f"{BASE_URL}/receiveNotification/{API_TOKEN}"
    response = requests.get(url, timeout=15)
    if response.status_code == 200:
        return response.json()
    return None


def delete_notification(receipt_id):
    """Elimina la notifica dalla coda dopo averla elaborata."""
    url = f"{BASE_URL}/deleteNotification/{API_TOKEN}/{receipt_id}"
    requests.delete(url)


def send_message(chat_id, text):
    """Invia un messaggio in una chat o gruppo."""
    url = f"{BASE_URL}/sendMessage/{API_TOKEN}"
    payload = {
        "chatId": chat_id,
        "message": text
    }
    response = requests.post(url, json=payload)
    return response.json()


def handle_command(command, chat_id, sender):
    """Gestisce i comandi del bot."""
    command = command.lower().strip()

    if command == "!help":
        reply = (
            "🤖 *Comandi disponibili:*\n\n"
            "!help — mostra questo messaggio\n"
            "!info — info sul bot\n"
            "!ciao — saluto personalizzato\n"
            "!dado — lancia un dado 🎲\n"
            "!ora — mostra l'ora attuale 🕐"
        )

    elif command == "!info":
        reply = (
            "ℹ️ *Info Bot*\n\n"
            "Sono un bot WhatsApp scritto in Python 🐍\n"
            "Versione: 1.0\n"
            "Creato con Green API"
        )

    elif command == "!ciao":
        reply = f"👋 Ciao! Sono il bot del gruppo. Scrivi !help per vedere cosa so fare."

    elif command == "!dado":
        import random
        numero = random.randint(1, 6)
        facce = ["", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣"]
        reply = f"🎲 Hai ottenuto: {facce[numero]} ({numero})"

    elif command == "!ora":
        from datetime import datetime
        ora = datetime.now().strftime("%H:%M:%S")
        data = datetime.now().strftime("%d/%m/%Y")
        reply = f"🕐 Sono le *{ora}* del *{data}*"

    else:
        # Comando non riconosciuto
        reply = f"❓ Comando sconosciuto: `{command}`\nScrivi !help per vedere i comandi disponibili."

    send_message(chat_id, reply)
    print(f"[✓] Risposto a '{command}' in {chat_id}")


def main():
    print("🤖 Bot WhatsApp avviato! In ascolto...")
    print("   Premi CTRL+C per fermare.\n")

    while True:
        try:
            notification = receive_notification()

            if notification is None:
                # Nessuna notifica in coda, aspetta un po'
                time.sleep(2)
                continue

            receipt_id = notification.get("receiptId")
            body = notification.get("body", {})

            # Elabora solo messaggi in entrata
            if body.get("typeWebhook") == "incomingMessageReceived":
                message_data = body.get("messageData", {})
                msg_type = message_data.get("typeMessage")

                # Gestisci solo messaggi di testo
                if msg_type == "textMessage":
                    text = message_data.get("textMessageData", {}).get("textMessage", "")
                    chat_id = body.get("senderData", {}).get("chatId", "")
                    sender = body.get("senderData", {}).get("sender", "")

                    print(f"[MSG] {sender} in {chat_id}: {text}")

                    # Esegui il comando se inizia con "!"
                    if text.startswith("!"):
                        handle_command(text, chat_id, sender)

            # Elimina sempre la notifica dalla coda
            delete_notification(receipt_id)

        except KeyboardInterrupt:
            print("\n\n🛑 Bot fermato.")
            break
        except Exception as e:
            print(f"[ERRORE] {e}")
            time.sleep(3)


if __name__ == "__main__":
    main()
