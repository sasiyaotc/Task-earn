from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import config

app = Flask(__name__)
CORS(app)

users_db = {}
tasks_db = {
    "demo1": {"id":"demo1", "link":"@your_channel_1", "title":"Join Our Official Channel", "reward_user": config.TASK_JOIN_USER, "reward_owner": config.TASK_JOIN_OWNER}
}

@app.route('/')
def home():
    return "Neon Bot Backend Running - AppID 000530"

@app.route('/api/me')
def me():
    uid = str(request.args.get('user_id'))
    u = users_db.get(uid, {"balance":0, "today":0, "refs":0, "claimed_tasks":[]})
    return jsonify(balance=f"{u['balance']:.4f}", today=u["today"], refs=u["refs"])

@app.route('/api/watch', methods=['POST'])
def watch():
    uid = str(request.json.get('user_id'))
    ip = request.remote_addr
    u = users_db.setdefault(uid, {"balance":0, "today":0, "refs":0, "claimed_tasks":[], "ip":ip})
    if u["today"] >= config.ADS_PER_DAY:
        return jsonify(ok=False, error="Daily limit reached! You watched 30 ads today. Come back tomorrow!")
    # Full watch only - called from .then()
    u["balance"] += config.AD_REWARD_USER
    u["today"] += 1
    return jsonify(ok=True, profit=config.AD_PROFIT_OWNER)

@app.route('/api/tasks')
def get_tasks():
    return jsonify(list(tasks_db.values()))

@app.route('/api/task/verify', methods=['POST'])
def verify_task():
    uid = request.json.get('user_id')
    task_id = request.json.get('task_id')
    task = tasks_db.get(task_id)
    if not task:
        return jsonify(ok=False, error="Task not found!")

    u = users_db.setdefault(str(uid), {"balance":0, "today":0, "refs":0, "claimed_tasks":[], "ip":request.remote_addr})
    
    if task_id in u["claimed_tasks"]:
        return jsonify(ok=False, error="You already claimed this task! Touching does not add balance.")

    try:
        chat_id = task['link']
        resp = requests.get(f"https://api.telegram.org/bot{config.BOT_TOKEN}/getChatMember?chat_id={chat_id}&user_id={uid}", timeout=10).json()
        status = resp.get('result', {}).get('status','left')
        if status in ['left','kicked','banned','left']:
            return jsonify(ok=False, error="You haven't joined yet! Please click JOIN GROUP, join the group, then click VERIFY!")
        
        u["balance"] += task["reward_user"]
        u["claimed_tasks"].append(task_id)
        return jsonify(ok=True, reward=task["reward_user"], owner_profit=task["reward_owner"])
    except Exception as e:
        return jsonify(ok=False, error="Verification failed! Make sure bot is admin in the target group/channel!")

@app.route('/api/add_task', methods=['POST'])
def add_task():
    d = request.json
    try:
        members = int(d.get('members',0))
    except:
        members = 0
    price = config.TASK_PRICE_2000 if members <= 2000 else config.TASK_PRICE_UNLIMITED
    text = f"🆕 NEW TASK REQUEST\n\nUser: {d['user_id']}\nLink: {d['link']}\nMembers Needed: {members}\nPrice: ${price}\nTxID: {d['txid']}\nPay Address: {config.USDT_BEP20_ADDRESS}\n\nApprove / Reject?"
    try:
        requests.post(f"https://api.telegram.org/bot{config.BOT_TOKEN}/sendMessage", json={"chat_id":config.ADMIN_ID, "text":text}, timeout=10)
    except: pass
    return jsonify(ok=True)

@app.route('/api/withdraw', methods=['POST'])
def withdraw():
    uid = str(request.json.get('user_id'))
    wallet = request.json.get('wallet')
    u = users_db.get(uid)
    if not u:
        return jsonify(msg="User not found!")
    if u["balance"] < config.MIN_WITHDRAW:
        return jsonify(msg=f"Minimum ${config.MIN_WITHDRAW} required to withdraw!")
    if u["refs"] < config.MIN_REFS:
        return jsonify(msg=f"You need {config.MIN_REFS} real referrals! Fake referrals are auto-banned!")
    if not wallet or len(wallet) < 10:
        return jsonify(msg="Please enter a valid USDT BEP20 wallet address!")
    
    text = f"💸 WITHDRAW REQUEST\n\nUser: {uid}\nBalance: ${u['balance']:.4f}\nReferrals: {u['refs']}\nWallet (BEP20): {wallet}\n\nApprove / Reject?"
    try:
        requests.post(f"https://api.telegram.org/bot{config.BOT_TOKEN}/sendMessage", json={"chat_id":config.ADMIN_ID, "text":text}, timeout=10)
    except: pass
    return jsonify(msg="Withdraw request sent to admin! You will be notified after review!")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
