import threading
import time
import subprocess

_state = {
    'connected': False,
    'last_check': 0,
    'error': '',
}

def _check():
    while True:
        try:
            r = subprocess.run(['i2cdetect','-y','1'], capture_output=True, text=True, timeout=3)
            found = '3c' in r.stdout.lower()
            _state['connected'] = found
            _state['error'] = '' if found else 'OLED not found at 0x3C'
        except Exception as e:
            _state['connected'] = False
            _state['error'] = str(e)[:40]
        _state['last_check'] = time.time()
        time.sleep(5)

threading.Thread(target=_check, daemon=True).start()

def is_connected():
    return _state['connected']

def get_error():
    return _state['error']
