from flask import Flask, request, jsonify
import json, random, string, smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
KEYS_FILE = "keys.json"

# Your Gmail credentials
GMAIL_USER = "dream11predictorai@gmail.com"   # replace with your Gmail
GMAIL_PASSWORD = "yxrt jion rmix ltmt"  # App Password (not your Gmail login password)

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

def send_email(to_email, key, uses):
    subject = "🎟️ Your Dream11 Predictor Access Key"
    body = f"""
    Hi there 👋,

    Thank you for your payment!

    Here is your access key: **{key}**
    This key is valid for **{uses} uses**.

    Enter it in the app to unlock predictions.

    Enjoy and good luck! 🏏

    — Dream11 Predictor Team
    """

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = GMAIL_USER
    msg["To"] = to_email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_USER, GMAIL_PASSWORD)
            server.sendmail(GMAIL_USER, to_email, msg.as_string())
        print(f"✅ Email sent to {to_email}")
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
        key = generate_key()
        keys = load_keys()
        keys[key] = {"email": email, "uses_left": uses}
        save_keys(keys)

        send_email(email, key, uses)

        return jsonify({"message": "Key generated and emailed", "key": key}), 200
    else:
        return jsonify({"error": "Invalid amount"}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
