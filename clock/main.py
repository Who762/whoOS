import time
import board
import busio
import subprocess
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
from datetime import datetime
from errors.error_handler import ErrorHandler
from modules.dht_reader import read_dht

OLED_ADDRESS = 0x3C
SETTINGS_FILE = "/home/who/clock/settings.json"

def load_settings():
    import json, os
    default = {"show_seconds":True,"show_ms":True,"show_date":True,"show_cpu":True,"show_dht":True}
    try:
        if os.path.exists(SETTINGS_FILE):
            return json.load(open(SETTINGS_FILE))
        return default
    except Exception:
        return default
WIDTH = 128
HEIGHT = 64
CHECK_DISPLAY_INTERVAL = 45
DHT_READ_INTERVAL = 1
CPU_TEMP_MAX = 70.0
error_handler = ErrorHandler()
FB = '/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf'
FR = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'

def get_cpu_temp():
    try:
        r = subprocess.run(['vcgencmd', 'measure_temp'], capture_output=True, text=True, timeout=2)
        temp = float(r.stdout.strip().replace('temp=', '').replace("'C", ''))
        error_handler.clear_error('cpu')
        return temp
    except Exception:
        error_handler.set_error('cpu', 'CPU')
        return None

def init_display():
    try:
        i2c = busio.I2C(board.SCL, board.SDA)
        oled = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=OLED_ADDRESS)
        oled.fill(0)
        oled.show()
        error_handler.clear_error('display')
        return oled
    except Exception:
        error_handler.set_error('display', 'DISP')
        return None

def draw_screen(oled, blink_state, cpu_temp, dht_temp=None, dht_hum=None):
        s = load_settings()
    try:
        now = datetime.now()
        time_str = now.strftime('%H:%M:%S') if s.get('show_seconds', True) else now.strftime('%H:%M')
        sec_str = now.strftime(':%S')
        ms_str = '.{:03d}'.format(now.microsecond // 1000)
        date_str = now.strftime('%d.%m.%Y')
        image = Image.new('1', (WIDTH, HEIGHT))
        draw = ImageDraw.Draw(image)
        try:
            font_big = ImageFont.truetype(FB, 28)
            font_med = ImageFont.truetype(FB, 9)
            font_ms = ImageFont.truetype(FR, 9)
        except Exception:
            font_big = ImageFont.load_default()
            font_med = font_big
            font_ms = font_big
        draw.text((0, 0), '3.3V', font=font_med, fill=255)
        if error_handler.has_errors() and blink_state:
            draw.text((60, 0), '!', font=font_med, fill=255)
        bat_text = 'BAT%'
        try:
            bat_w = draw.textlength(bat_text, font=font_med)
        except Exception:
            bat_w = 22
        draw.text((WIDTH - bat_w - 1, 0), bat_text, font=font_med, fill=255)
        try:
            time_w = draw.textlength(time_str, font=font_big)
        except Exception:
            time_w = 100
        draw.text(((WIDTH - time_w) // 2, 10), time_str, font=font_big, fill=255)
        try:
            ms_w = draw.textlength(ms_str, font=font_ms)
        except Exception:
            ms_w = 25
        draw.text(((WIDTH - ms_w) // 2, 39), ms_str, font=font_ms, fill=255)
        if cpu_temp is not None:
            if cpu_temp >= CPU_TEMP_MAX and blink_state:
                cpu_text = '!{}C'.format(int(cpu_temp))
            else:
                cpu_text = '{}C'.format(int(cpu_temp))
        else:
            cpu_text = '!CPU' if blink_state else 'CPU'
        draw.text((0, 46), cpu_text, font=font_med, fill=255)
        if dht_temp is not None:
            dht_str = '{}C {}%'.format(int(dht_temp), int(dht_hum))
        else:
            dht_str = '!DHT' if blink_state else 'DHT'
        try:
            dht_w = draw.textlength(dht_str, font=font_med)
        except Exception:
            dht_w = 40
        draw.text((WIDTH - dht_w - 1, 46), dht_str, font=font_med, fill=255)
        draw.text((0, 55), date_str, font=font_ms, fill=255)
        errors = [e for k, e in error_handler.errors.items() if k not in ('cpu', 'dht')]
        if errors:
            err_text = ('!' if blink_state else '') + ' '.join(errors)
            try:
                err_w = draw.textlength(err_text, font=font_ms)
            except Exception:
                err_w = 25
            draw.text((WIDTH - err_w - 1, 55), err_text, font=font_ms, fill=255)
        oled.image(image)
        oled.show()
    except Exception as e:
        print('draw error: ' + str(e))
        raise

def main():
    oled = init_display()
    last_display_check = time.time()
    last_dht_read = 0
    last_cpu_read = 0
    blink_state = False
    blink_tick = 0
    cpu_temp = None
    dht_temp = None
    dht_hum = None
    while True:
        try:
            now_ts = time.time()
            blink_tick += 1
            if blink_tick >= 5:
                blink_state = not blink_state
                blink_tick = 0
            if oled is None and (now_ts - last_display_check >= CHECK_DISPLAY_INTERVAL):
                last_display_check = now_ts
                oled = init_display()
            if now_ts - last_dht_read >= DHT_READ_INTERVAL:
                last_dht_read = now_ts
                try:
                    dht_temp, dht_hum = read_dht(error_handler)
                except Exception:
                    error_handler.set_error('dht', 'DHT')
            if now_ts - last_cpu_read >= 3:
                last_cpu_read = now_ts
                try:
                    cpu_temp = get_cpu_temp()
                except Exception:
                    cpu_temp = None
            if oled is not None:
                try:
                    draw_screen(oled, blink_state, cpu_temp, dht_temp, dht_hum)
                except Exception as e:
                    print('screen error: ' + str(e))
                    error_handler.set_error('display', 'DISP')
                    oled = None
                    last_display_check = time.time()
        except Exception as e:
            print('main error: ' + str(e))
        time.sleep(0.1)

if __name__ == '__main__':
    main()
