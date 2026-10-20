from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests, os, config
app = Flask(__name__, static_folder='frontend', static_url_path='')
CORS(app)

users_db = {}
tasks_db = {
    "demo1": {"id":"demo1", "link":config.CHANNEL_1, "title":"Join Our Official Channel", "reward_user": config.TASK_JOIN_USER, "reward_owner": config.TASK_JOIN_OWNER}
}

@app.route('/')
def index():
    return send_from_directory('frontend', 'index.html')

@app.route('/api/me')
def me():
    uid = str(request.args.get('user_id'))
    u = users_db.get(uid, {"balance":0, "today":0, "refs":0, "claimed_tasks":[]})
    return jsonify(balance=f"{u['balance']:.4f}", today=u["today"], refs=u["refs"])

@app.route('/api/watch', methods=['POST'])
def watch():
    uid = str(request.json.get('user_id'))
    u = users_db.setdefault(uid, {"balance":0, "today":0, "refs":0, "claimed_tasks":[]})
    if u["today"] >= config.ADS_PER_DAY:
        return jsonify(ok=False, error="Daily limit reached! 30/30 completed!")
    u["balance"] += config.AD_REWARD_USER
    u["today"] += 1
    return jsonify(ok=True)

@app.route('/api/tasks')
def get_tasks():
    return jsonify(list(tasks_db.values()))

@app.route('/api/task/verify', methods=['POST'])
def verify_task():
    uid = request.json.get('user_id')
    task_id = request.json.get('task_id')
    task = tasks_db.get(task_id)
    if not task: return jsonify(ok=False, error="Task not found!")
    u = users_db.setdefault(str(uid), {"balance":0, "today":0, "refs":0, "claimed_tasks":[]})
    if task_id in u["claimed_tasks"]:
        return jsonify(ok=False, error="You already claimed this task!")
    try:
        r = requests.get(f"https://api.telegram.org/bot{config.BOT_TOKEN}/getChatMember?chat_id={task['link']}&user_id={uid}", timeout=10).json()
        status = r.get('result', {}).get('status','left')
        if status in ['left','kicked','banned']:
            return jsonify(ok=False, error="You haven't joined yet! Click JOIN GROUP first!")
        u["balance"] += task["reward_user"]
        u["claimed_tasks"].append(task_id)
        return jsonify(ok=True, reward=task["reward_user"])
    except Exception as e:
        return jsonify(ok=False, error="Verification failed! Make bot admin in group!")

@app.route('/api/add_task', methods=['POST'])
def add_task():
    d = request.json
    members = int(d.get('members',0) or 0)
    price = config.TASK_PRICE_2000 if members <= 2000 else config.TASK_PRICE_UNLIMITED
    text = f"🆕 NEW TASK REQUEST\nUser:{d['user_id']}\nLink:{d['link']}\nMembers:{members}\nPrice:${price}\nTxID:{d['txid']}"
    try: requests.post(f"https://api.telegram.org/bot{config.BOT_TOKEN}/sendMessage", json={"chat_id":config.ADMIN_ID, "text":text}, timeout=10)
    except: pass
    return jsonify(ok=True)

@app.route('/api/withdraw', methods=['POST'])
def withdraw():
    uid = str(request.json.get('user_id'))
    wallet = request.json.get('wallet')
    u = users_db.get(uid)
    if not u or u["balance"] < config.MIN_WITHDRAW: return jsonify(msg=f"Minimum ${config.MIN_WITHDRAW} required!")
    if u["refs"] < config.MIN_REFS: return jsonify(msg=f"You need {config.MIN_REFS} real referrals!")
    text = f"💸 WITHDRAW REQUEST\nUser:{uid}\nAmount:${u['balance']:.4f}\nWallet BEP20:{wallet}"
    try: requests.post(f"https://api.telegram.org/bot{config.BOT_TOKEN}/sendMessage", json={"chat_id":config.ADMIN_ID, "text":text}, timeout=10)
    except: pass
    return jsonify(msg="Withdraw request sent to admin!")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
