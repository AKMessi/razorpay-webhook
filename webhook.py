from flask import Flask, request, jsonify
import json, random, string, smtplib, hmac, hashlib
from email.mime.text import MIMEText
import requests
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

app = Flask(__name__)

# Razorpay webhook secret
RAZORPAY_SECRET = "messiisthegoat"

# Google Drive keys.json public download URL and File ID
KEYS_URL = "https://drive.google.com/uc?export=download&id=1iDyBB5lTaXcR5TYLVYc8XAFCHwVwRrJH"
DRIVE_FILE_ID = "1iDyBB5lTaXcR5TYLVYc8XAFCHwVwRrJH"
KEYS_FILE = "keys.json"

# Gmail setup
GMAIL_USER = "dream11predictorai@gmail.com"
GMAIL_PASSWORD = "yxrt jion rmix ltmt"  # App password

# Price-to-uses mapping
PRICE_MAP = {
    9: 2,
    27: 5,
    37: 10,
    149: 50,
    247: 100
}

# ----------------- Utilities -----------------

def generate_unique_key(existing_keys, length=8):
    while True:
        key = ''.join(random.choices(string.digits, k=length))
        if key not in existing_keys:
            return key

def download_keys():
    try:
        r = requests.get(KEYS_URL)
        if r.status_code == 200:
            with open(KEYS_FILE, "w") as f:
                f.write(r.text)
    except Exception as e:
        print(f"⚠️ Error downloading keys.json: {e}")

def load_keys():
    try:
        with open(KEYS_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_keys(keys):
    with open(KEYS_FILE, "w") as f:
        json.dump(keys, f, indent=2)

def upload_keys_to_drive():
    try:
        gauth = GoogleAuth()
        gauth.LocalWebserverAuth()
        drive = GoogleDrive(gauth)

        file = drive.CreateFile({'id': DRIVE_FILE_ID})
        file.SetContentFile(KEYS_FILE)
        file.Upload()
        print("✅ keys.json uploaded to Google Drive.")
    except Exception as e:
        print(f"❌ Upload to Drive failed: {e}")

def send_email(to_email, key, uses):
    subject = "🎟️ Your Dream11 Predictor Access Key"
    body = f"""
Hi there 👋,

Thanks for your payment! Your Dream11 Predictor access key is:

🔑 Key: {key}
📊 Uses: {uses} times

Enter this in the app to unlock predictions. Good luck! 🏏

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

# ----------------- Webhook Route -----------------

@app.route("/webhook", methods=["POST"])
def webhook():
    payload = request.data
    signature = request.headers.get("X-Razorpay-Signature")

    # Validate signature
    generated = hmac.new(
        RAZORPAY_SECRET.encode(),
        msg=payload,
        digestmod=hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(generated, signature):
        return jsonify({"error": "❌ Invalid signature"}), 403

    # Parse verified payload
    data = json.loads(payload)
    print("✅ Webhook verified:", data)

    try:
        payment = data["payload"]["payment"]["entity"]
        email = payment["email"]
        amount = int(payment["amount"]) // 100
    except Exception as e:
        return jsonify({"error": f"Payload error: {e}"}), 400

    uses = PRICE_MAP.get(amount)
    if not uses:
        return jsonify({"error": "Unsupported amount"}), 400

    download_keys()
    keys = load_keys()

    key = generate_unique_key(keys)
    keys[key] = {"email": email, "uses_left": uses}
    save_keys(keys)
    upload_keys_to_drive()

    send_email(email, key, uses)
    return jsonify({"message": "Key generated and emailed", "key": key}), 200

# ----------------- Run Server -----------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
