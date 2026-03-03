import board
import adafruit_dht

DHT_PIN = board.D4
_dht = None

def read_dht(error_handler):
    global _dht
    try:
        if _dht is None:
            _dht = adafruit_dht.DHT11(DHT_PIN, use_pulseio=False)
        t = _dht.temperature
        h = _dht.humidity
        if t is not None and h is not None:
            error_handler.clear_error('dht')
            return round(t, 1), round(h, 1)
        else:
            error_handler.set_error('dht', 'DHT')
            return None, None
    except Exception:
        error_handler.set_error('dht', 'DHT')
        return None, None
