import pygame
from assets.version import *
from datetime import datetime
import subprocess
import math

def get_wifi_status():
    try:
        r = subprocess.run(['iwgetid', '-r'], capture_output=True, text=True)
        return r.stdout.strip() != ''
    except Exception:
        return False

def get_bt_status():
    try:
        r = subprocess.run(['hciconfig'], capture_output=True, text=True)
        return 'UP' in r.stdout
    except Exception:
        return False

def check_oled():
    try:
        r = subprocess.run(['i2cdetect', '-y', '1'], capture_output=True, text=True)
        return '3c' in r.stdout.lower()
    except Exception:
        return False

def check_dht():
    try:
        import adafruit_dht, board
        d = adafruit_dht.DHT11(board.D4, use_pulseio=False)
        t = d.temperature
        d.exit()
        return t is not None
    except Exception:
        return False

def draw_oled_icon(screen, x, y, col):
    pygame.draw.rect(screen, col, (x, y+3, 16, 11), 1)
    pygame.draw.rect(screen, col, (x+3, y+1, 10, 2))
    pygame.draw.rect(screen, BLACK, (x+2, y+5, 12, 5))
    for i in range(3):
        pygame.draw.line(screen, col, (x+3+i*5, y+14), (x+3+i*5, y+16), 1)
    pygame.draw.line(screen, col, (x+3, y+16), (x+13, y+16), 1)

def draw_dht_icon(screen, x, y, col):
    pygame.draw.rect(screen, col, (x+4, y+1, 5, 8), 1)
    pygame.draw.circle(screen, col, (x+6, y+12), 4, 1)
    pygame.draw.line(screen, col, (x+6, y+9), (x+6, y+13), 2)
    pygame.draw.line(screen, col, (x+10, y+3), (x+13, y+3), 1)
    pygame.draw.line(screen, col, (x+10, y+6), (x+13, y+6), 1)

def draw_bt_icon(screen, x, y, col):
    cx = x + 5
    pygame.draw.lines(screen, col, False, [
        (cx-3, y+4), (cx+3, y+8), (cx, y+6), (cx+3, y+4),
        (cx-3, y+8), (cx, y+6), (cx, y+2), (cx, y+14)
    ], 1)

def draw_battery(screen, x, y, pct, charging, has_power, blink, font_sm):
    bx, by = x, y+1
    pygame.draw.rect(screen, WHITE, (bx, by+2, 3, 8), 0)
    pygame.draw.rect(screen, WHITE, (bx+3, by, 20, 12), 1)

    if pct is not None:
        fill_w = int(18 * pct / 100)
        if pct < 20:
            bat_col = (255, 50, 50)
        elif pct < 50:
            bat_col = (255, 200, 0)
        else:
            bat_col = (50, 220, 50)
        pygame.draw.rect(screen, bat_col, (bx+4, by+1, fill_w, 10))
        if pct < 20 and blink:
            pts = [(bx+13,by+1),(bx+10,by+6),(bx+13,by+5),(bx+10,by+11),(bx+16,by+4),(bx+13,by+5)]
            pygame.draw.polygon(screen, (255,50,50), pts)
        if charging:
            pts = [(bx+13,by+1),(bx+10,by+6),(bx+13,by+5),(bx+10,by+11),(bx+16,by+4),(bx+13,by+5)]
            pygame.draw.polygon(screen, (255,200,0), pts)
    else:
        if blink:
            t = font_sm.render('!', True, (255,200,0))
            screen.blit(t, (bx+10, by))

    if has_power:
        px = bx + 26
        pygame.draw.circle(screen, (200,200,200), (px+5, by+5), 5, 1)
        pygame.draw.line(screen, (200,200,200), (px+5, by-1), (px+5, by+1), 2)
        pygame.draw.line(screen, (200,200,200), (px+2, by+10), (px+2, by+12), 1)
        pygame.draw.line(screen, (200,200,200), (px+8, by+10), (px+8, by+12), 1)

def draw_power_btn(screen, x, y, col):
    cx, cy = x+8, y+8
    pygame.draw.arc(screen, col, (cx-6, cy-6, 12, 12), 0.6, 2.5, 2)
    pygame.draw.line(screen, col, (cx, cy-7), (cx, cy-2), 2)

def draw_statusbar(screen, font, font_sm, blink, tick,
                   oled_ok=True, dht_ok=True,
                   bat_pct=None, charging=False,
                   low_voltage=False, has_power=True):

    pygame.draw.rect(screen, (12,12,12), (0, 0, SCREEN_W, 34))
    pygame.draw.line(screen, (50,50,50), (0, 34), (SCREEN_W, 34), 1)

    now = datetime.now()
    time_str = now.strftime('%H:%M:%S')
    time_surf = font.render(time_str, True, WHITE)
    screen.blit(time_surf, ((SCREEN_W - time_surf.get_width()) // 2, 8))

    x = 5
    y = 8

    oled_col = WHITE if oled_ok else ((255,60,60) if blink else (40,40,40))
    draw_oled_icon(screen, x, y, oled_col)
    x += 22

    dht_col = WHITE if dht_ok else ((255,60,60) if blink else (40,40,40))
    draw_dht_icon(screen, x, y, dht_col)
    x += 20

    wifi = get_wifi_status()
    wifi_col = WHITE if wifi else (50,50,50)
    for r in [3, 6, 9]:
        pygame.draw.arc(screen, wifi_col, (x+5-r, y+9-r, r*2, r*2), 0.3, 2.8, 1)
    pygame.draw.circle(screen, wifi_col, (x+5, y+9), 2)
    x += 18

    bt = get_bt_status()
    bt_col = WHITE if bt else (50,50,50)
    draw_bt_icon(screen, x, y, bt_col)
    x += 16

    if low_voltage and blink:
        pts = [(x+5,y),(x+2,y+7),(x+5,y+6),(x+2,y+14),(x+8,y+5),(x+5,y+6)]
        pygame.draw.polygon(screen, (255,200,0), pts)

    bat_x = SCREEN_W - 58
    draw_battery(screen, bat_x, y, bat_pct, charging, has_power, blink, font_sm)

    btn_x = SCREEN_W - 14
    btn_y = y + 7
    draw_power_btn(screen, btn_x-8, btn_y-8, (180,180,180))

    return pygame.Rect(btn_x-14, btn_y-8, 16, 16)
