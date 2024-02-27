import os
import json
from heyoo import WhatsApp
from dotenv import load_dotenv
from flask import Flask, request


app = Flask(__name__)

# Load .env file
load_dotenv()

messenger = WhatsApp(os.getenv("TOKEN"))
VERIFY_TOKEN = "30cca545-3838-48b2-80a7-9e43b1ae8ce4"


@app.route("/", methods=["GET", "POST"])
def hook():
    if request.method == "GET":
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        return "Invalid verification token"

    data = request.get_json()
    if (changed_field := messenger.changed_field(data)) == "messages":
        if new_message := messenger.get_mobile(data):
            mobile = messenger.get_mobile(data)

            if (message_type := messenger.get_message_type(data)) == "text":
                message = messenger.get_message(data)
                name = messenger.get_name(data)
                print(f"{name} with this {mobile} number sent  {message}")
                messenger.send_message(f"Hi {name}, nice to connect with you", mobile)

            elif message_type == "interactive":
                message_response = messenger.get_interactive_response(data)
                print(message_response)

            else:
                pass
        else:
            if delivery := messenger.get_delivery(data):
                print(f"Message : {delivery}")
            else:
                print("No new message")
    return "ok"


if __name__ == "__main__":
    app.run(port=5000, debug=True)
