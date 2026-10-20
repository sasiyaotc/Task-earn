from flask import Flask
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "Neon Bot Backend is LIVE! Railway Success!"

@app.route('/api/test')
def test():
    return {"status": "ok", "message": "Backend Working"}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
