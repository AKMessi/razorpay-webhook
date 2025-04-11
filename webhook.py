from flask import Flask, request, jsonify
import json, random, string

app = Flask(__name__)
KEYS_FILE = "keys.json"

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

        print(f"✅ Key generated: {key} for {email} ({uses} uses)")
        # Send email logic here

        return jsonify({"message": "Key generated", "key": key}), 200
    else:
        return jsonify({"error": "Invalid amount"}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
