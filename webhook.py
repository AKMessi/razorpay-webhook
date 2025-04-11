from flask import Flask, request, jsonify
import json, random, string, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
KEYS_FILE = "keys.json"

# CONFIGURE YOUR EMAIL SENDER
EMAIL_SENDER = "dream11predictorai@gmail.com"
EMAIL_PASSWORD = "Aaryan@2007"  # Use an App Password if using Gmail

def generate_key(length=8):
    return ''.join(random.choices(string.digits, k=length))

def load_keys():
    try:
        with open(KEYS_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_keys(keys):
    with open(KEYS_FILE, "w") as f:
        json.dump(keys, f, indent=2)

def send_email(recipient, key, uses):
    subject = "🎟️ Your Dream11 Predictor Access Key"
    body = f"""
Hi there 👋,

Thank you for your payment! 🎉

Here is your access key: **{key}**
You have {uses} searches available.

Enter this key in the app to unlock predictions instantly:
👉 https://dream11predictor.streamlit.app/

Play smart, play responsibly.
Good luck! 💥

- Dream11 Predictor Team
"""

    msg = MIMEMultipart()
    msg['From'] = EMAIL_SENDER
    msg['To'] = recipient
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"✅ Email sent to {recipient}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("Webhook received:", data)

    try:
        payment = data["payload"]["payment"]["entity"]
        email = payment["email"]
        amount = int(payment["amount"]) // 100
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    price_map = {9: 2, 27: 5, 37: 10, 149: 50, 247: 100}
    uses = price_map.get(amount)

    if uses:
        keys = load_keys()

        # Ensure unique key
        key = generate_key()
        while key in keys:
            key = generate_key()

        keys[key] = {"email": email, "uses_left": uses}
        save_keys(keys)

        print(f"✅ Key generated: {key} for {email} ({uses} uses)")

        # Send access key by email
        send_email(email, key, uses)

        return jsonify({"message": "Key generated", "key": key}), 200
    else:
        return jsonify({"error": "Invalid amount"}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
