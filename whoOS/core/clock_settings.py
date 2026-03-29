import json
import os

SETTINGS_FILE = '/home/who/clock/settings.json'

DEFAULT = {
    'oled_on':      True,
    'show_seconds': True,
    'show_ms':      True,
    'show_date':    True,
    'show_cpu':     True,
    'show_dht':     True,
}

def load():
    try:
        if os.path.exists(SETTINGS_FILE):
            data = json.load(open(SETTINGS_FILE))
            for k,v in DEFAULT.items():
                if k not in data:
                    data[k] = v
            return data
        return DEFAULT.copy()
    except:
        return DEFAULT.copy()

def save(settings):
    try:
        os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
        json.dump(settings, open(SETTINGS_FILE,'w'))
        return True
    except:
        return False

def get_oled_on():
    return load().get('oled_on', True)
