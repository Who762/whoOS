import json
import os

SETTINGS_FILE = '/home/who/clock/settings.json'

DEFAULT = {
    'show_seconds': True,
    'show_ms': True,
    'show_date': True,
    'show_cpu': True,
    'show_dht': True,
}

def load():
    try:
        if os.path.exists(SETTINGS_FILE):
            return json.load(open(SETTINGS_FILE))
        return DEFAULT.copy()
    except Exception:
        return DEFAULT.copy()

def save(settings):
    try:
        json.dump(settings, open(SETTINGS_FILE, 'w'))
        return True
    except Exception:
        return False
