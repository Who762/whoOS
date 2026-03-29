import pygame
from assets.version import *
from datetime import datetime
import subprocess
import time
import threading

_cache = {
    'wifi': False, 'bt': False, 'dht': False,
    'last_check': 0
}

def _refresh_cache():
    try:
        r = subprocess.run(['iwgetid','-r'], capture_output=True, text=True, timeout=2)
        _cache['wifi'] = r.stdout.strip() != ''
    except: _cache['wifi'] = False
    try:
        r = subprocess.run(['hciconfig'], capture_output=True, text=True, timeout=2)
        _cache['bt'] = 'UP' in r.stdout
    except: _cache['bt'] = False
    try:
        import adafruit_dht, board
        d = adafruit_dht.DHT11(board.D4, use_pulseio=False)
        t = d.temperature
        d.exit()
        _cache['dht'] = t is not None
    except: _cache['dht'] = False
    _cache['last_check'] = time.time()

threading.Thread(target=_refresh_cache, daemon=True).start()

def draw_oled_icon(screen, x, y, col):
    pygame.draw.rect(screen, col, (x,y+3,16,11), 1)
    pygame.draw.rect(screen, col, (x+3,y+1,10,2))
    pygame.draw.rect(screen, BLACK, (x+2,y+5,12,5))
    for i in range(3):
        pygame.draw.line(screen, col, (x+3+i*5,y+14),(x+3+i*5,y+16), 1)
    pygame.draw.line(screen, col, (x+3,y+16),(x+13,y+16), 1)

def draw_dht_icon(screen, x, y, col):
    pygame.draw.rect(screen, col, (x+4,y+1,5,8), 1)
    pygame.draw.circle(screen, col, (x+6,y+12), 4, 1)
    pygame.draw.line(screen, col, (x+6,y+9),(x+6,y+13), 2)
    pygame.draw.line(screen, col, (x+10,y+3),(x+13,y+3), 1)
    pygame.draw.line(screen, col, (x+10,y+6),(x+13,y+6), 1)

def draw_wifi_icon(screen, x, y, col):
    for r in [3,6,9]:
        pygame.draw.arc(screen, col, (x+5-r,y+9-r,r*2,r*2), 0.3, 2.8, 1)
    pygame.draw.circle(screen, col, (x+5,y+9), 2)

def draw_bt_icon(screen, x, y, col):
    cx = x+5
    pygame.draw.line(screen, col, (cx,y+1),(cx,y+15), 1)
    pygame.draw.line(screen, col, (cx,y+1),(cx+4,y+4), 1)
    pygame.draw.line(screen, col, (cx+4,y+4),(cx,y+8), 1)
    pygame.draw.line(screen, col, (cx,y+8),(cx+4,y+12), 1)
    pygame.draw.line(screen, col, (cx+4,y+12),(cx,y+15), 1)
    pygame.draw.line(screen, col, (cx,y+1),(cx-2,y+3), 1)
    pygame.draw.line(screen, col, (cx,y+15),(cx-2,y+13), 1)

def draw_battery(screen, x, y, pct, charging, blink, font_sm):
    bx, by = x, y
    pygame.draw.rect(screen, WHITE, (bx,by+3,3,6))
    pygame.draw.rect(screen, WHITE, (bx+3,by,20,12), 1)
    if pct is not None:
        fill_w = max(0,int(18*pct/100))
        bat_col = (255,50,50) if pct<20 else (255,200,0) if pct<50 else (50,220,50)
        pygame.draw.rect(screen, bat_col, (bx+4,by+1,fill_w,10))
        if charging:
            pts = [(bx+13,by+1),(bx+10,by+6),(bx+13,by+5),(bx+10,by+11),(bx+16,by+4),(bx+13,by+5)]
            pygame.draw.polygon(screen, (255,200,0), pts)
        if pct < 20 and blink:
            pygame.draw.line(screen, (255,50,50), (bx+13,by+2),(bx+13,by+7), 2)
            pygame.draw.circle(screen, (255,50,50), (bx+13,by+10), 1)
    else:
        if blink:
            pygame.draw.line(screen, (255,200,0), (bx+13,by+2),(bx+13,by+7), 2)
            pygame.draw.circle(screen, (255,200,0), (bx+13,by+10), 1)

def draw_statusbar(screen, font, font_sm, blink, tick,
                   oled_ok=None, dht_ok=None,
                   bat_pct=None, charging=False,
                   low_voltage=False, has_power=True):

    if time.time() - _cache['last_check'] > 30:
        threading.Thread(target=_refresh_cache, daemon=True).start()

    pygame.draw.rect(screen, (12,12,12), (0,0,SCREEN_W,34))
    pygame.draw.line(screen, (50,50,50), (0,34),(SCREEN_W,34), 1)

    now = datetime.now()
    time_str = now.strftime('%H:%M:%S')
    time_surf = font.render(time_str, True, WHITE)
    screen.blit(time_surf, ((SCREEN_W-time_surf.get_width())//2, 8))

    x, y = 4, 9

    # OLED — из oled_monitor
    try:
        from core.oled_monitor import is_connected as oled_conn
        from core.clock_settings import get_oled_on
        oled_on = get_oled_on()
        oled_hw = oled_conn()
        if not oled_on:
            oled_col = (60,60,60)       # серый — выключен
        elif oled_hw:
            oled_col = WHITE            # белый — работает
        else:
            oled_col = (255,50,50) if blink else (60,60,60)  # красный мигает — не найден
    except:
        oled_col = (60,60,60)
    draw_oled_icon(screen, x, y, oled_col)
    x += 20

    # DHT
    dht_hw = _cache['dht']
    dht_col = WHITE if dht_hw else ((255,50,50) if blink else (60,60,60))
    draw_dht_icon(screen, x, y, dht_col)
    x += 18

    draw_wifi_icon(screen, x, y, WHITE if _cache['wifi'] else (60,60,60))
    x += 16
    draw_bt_icon(screen, x, y, WHITE if _cache['bt'] else (60,60,60))

    draw_battery(screen, SCREEN_W-26, 11, bat_pct, charging, blink, font_sm)

    return None
