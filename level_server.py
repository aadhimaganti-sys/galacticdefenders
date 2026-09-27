from flask import Flask, request, jsonify
import uuid
import json
import os

app = Flask(__name__)
DB_FILE = 'global_levels.json'

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_db(db):
    with open(DB_FILE, 'w') as f:
        json.dump(db, f)

@app.route('/publish', methods=['POST'])
def publish():
    db = load_db()
    data = request.json
    level_id = str(uuid.uuid4())[:8]
    data['id'] = level_id
    db[level_id] = data
    save_db(db)
    return jsonify({"status": "success", "id": level_id})

@app.route('/search', methods=['GET'])
def search():
    db = load_db()
    query = request.args.get('q', '').lower()
    result = []
    for k, v in db.items():
        name = v.get('name', 'Unnamed')
        if query in name.lower() or query in k:
            result.append({"id": k, "name": name})
    return jsonify(result)

@app.route('/download/<level_id>', methods=['GET'])
def download(level_id):
    db = load_db()
    if level_id in db:
        return jsonify(db[level_id])
    return jsonify({"error": "not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
