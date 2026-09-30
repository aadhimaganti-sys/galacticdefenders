import json
import random

observations = [
    "I'm detecting anomalies", "sensors show a massive spike", "radar is lighting up",
    "there's a hull breach on deck 4", "the shields are fluctuating",
    "energy levels are dropping", "we have incoming bogeys", "they're flanking us",
    "the warp drive is unstable", "I see a weakness in their formation",
    "communications are jammed", "weapons are overheating", "life support is failing",
    "I've locked onto their leader", "there's a dimensional tear opening",
    "a nebula is approaching", "the asteroid field is dense", "enemy reinforcements just arrived",
    "our cargo bay is venting", "we're caught in a tractor beam", "a solar flare is hitting us",
    "their shields are down", "our targeting computer is glitching"
]

exclamations = [
    "Watch out", "Brace for impact", "Hold on", "By the stars",
    "Incoming", "Evasive maneuvers", "We're taking fire", "Shields down",
    "Look out", "Great Scott", "Holy supernova", "Red alert",
    "Mayday", "We're hit", "Take cover", "Target acquired"
]

actions = [
    "rerouting power", "initializing jump", "firing all batteries",
    "patching the leak", "boosting thrusters", "locking on",
    "sending a distress signal", "deploying countermeasures",
    "charging the hyperdrive", "rebooting the mainframe",
    "venting plasma", "arming proton torpedoes", "scanning the area",
    "jamming their comms", "initiating self-destruct sequence",
    "calling for backup"
]

statuses = [
    "Engines are stable", "Shields at 50%", "Weapons hot", "Core is critical",
    "Life support is nominal", "Hull integrity failing", "Ammo depleted",
    "Power reserves low", "Nav computer offline", "Hyperdrive engaged",
    "Armor is cracking", "Radar is blind", "Thrusters are unresponsive",
    "Gravity plating is failing", "We're running on fumes", "Sensors are green"
]

suggestions = [
    "we should retreat", "push the advantage", "focus fire on the big one",
    "try spinning, that's a good trick", "divert power to shields",
    "launch the torpedoes", "maintain formation", "prepare for boarding",
    "let's get out of here", "stay on target", "break formation",
    "barrel roll", "hit them with everything we've got", "surrender is not an option",
    "maybe we can talk this out", "ramming speed"
]

adverbs = ["quickly", "immediately", "now", "if possible", "Captain"]

chatter_list = []
for obs in observations:
    chatter_list.append(f"Captain, {obs}!")
    for adv in adverbs:
        chatter_list.append(f"{obs.capitalize()}, {adv}!")

for exc in exclamations:
    for act in actions:
        chatter_list.append(f"{exc}! {act.capitalize()}.")
        chatter_list.append(f"{exc}! I am {act}.")

for stat in statuses:
    for sug in suggestions:
        chatter_list.append(f"{stat}. {sug.capitalize()}!")
        chatter_list.append(f"{stat}... {sug.capitalize()}?")

chatter_list = list(set(chatter_list))
with open('/home/grogulover5/Desktop/GalacticDefenders/assets/chatter.json', 'w') as f:
    json.dump(chatter_list, f)

print(f"Generated {len(chatter_list)} chatters.")
