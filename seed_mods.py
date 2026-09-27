import requests
import json
import base64

API = 'https://api.restful-api.dev/objects'

mods = [
  {
    "name": "Ultra Blasters",
    "fname": "ultra_blasters.json",
    "desc": "Increases base damage.",
    "json_data": {"powerups": {"ultra_blasters": {"name": "Ultra Blasters", "desc": "Increases base damage.", "color": [255, 50, 50], "fire_rate_multiplier": 1.5}}}
  },
  {
    "name": "Speed Demon",
    "fname": "speed_demon.json",
    "desc": "Increases player speed by 50%.",
    "json_data": {"powerups": {"speed_demon": {"name": "Speed Demon", "desc": "Increases player speed by 50%.", "color": [50, 255, 255], "speed_multiplier": 1.5}}}
  },
  {
    "name": "God Mode Lite",
    "fname": "god_mode_lite.json",
    "desc": "Massive heal pack.",
    "json_data": {"powerups": {"god_mode_lite": {"name": "God Mode Lite", "desc": "Massive heal pack.", "color": [50, 255, 50], "heal_amount": 100}}}
  }
]

payload = base64.b64encode(json.dumps(mods).encode('utf-8')).decode('utf-8')
print("Uploading...")
res = requests.post(API, json={"name": "mods", "data": {"payload": payload}})
print(res.text)
