import pygame
import subprocess
import os
import shutil
import threading
from assets.version import *
from core.system import get_cpu_temp, get_uptime

TABS = ['WiFi', 'Bluetooth', 'Система', 'Хранилище', 'О системе', 'Звук']

# Cache для медленных операций
_wifi_cache = {'networks': [], 'ssid': '', 'ip': '', 'tick': 0}
_bt_cache = {'devices': [], 'status': False, 'tick': 0}

def refresh_wifi():
    try:
        ssid = subprocess.run(['iwgetid','-r'], capture_output=True, text=True, timeout=3).stdout.strip()
        ip = subprocess.run(['hostname','-I'], capture_output=True, text=True, timeout=2).stdout.strip().split()
        _wifi_cache['ssid'] = ssid
        _wifi_cache['ip'] = ip[0] if ip else ''
    except:
        _wifi_cache['ssid'] = ''
        _wifi_cache['ip'] = ''

def scan_wifi():
    try:
        r = subprocess.run(['sudo','iwlist','wlan0','scan'], capture_output=True, text=True, timeout=10)
        nets = []
        for line in r.stdout.split('\n'):
            if 'ESSID' in line and '"' in line:
                n = line.split('"')[1]
                if n and n not in nets:
                    nets.append(n)
        _wifi_cache['networks'] = nets
    except:
        _wifi_cache['networks'] = []

def refresh_bt():
    try:
        r = subprocess.run(['hciconfig'], capture_output=True, text=True, timeout=3)
        _bt_cache['status'] = 'UP' in r.stdout
    except:
        _bt_cache['status'] = False
    try:
        r = subprocess.run(['bluetoothctl','devices'], capture_output=True, text=True, timeout=3)
        _bt_cache['devices'] = [l for l in r.stdout.strip().split('\n') if l.strip()]
    except:
        _bt_cache['devices'] = []

def run_settings(screen, clock):
    font = pygame.font.SysFont('monospace', 13, bold=True)
    font_sm = pygame.font.SysFont('monospace', 11)
    font_xs = pygame.font.SysFont('monospace', 9)
    tab = 0
    scroll = 0
    scanning = False
    wifi_sel = 0

    # Initial load in background
    threading.Thread(target=refresh_wifi, daemon=True).start()

    while True:
        screen.fill(BLACK)

        tw = SCREEN_W // len(TABS)
        for i, name in enumerate(TABS):
            tx = i*tw
            if i == tab:
                pygame.draw.rect(screen, (40,40,60), (tx,0,tw,22))
                pygame.draw.rect(screen, (100,100,200), (tx,0,tw,22), 1)
                tc = WHITE
            else:
                pygame.draw.rect(screen, (15,15,15), (tx,0,tw,22))
                pygame.draw.rect(screen, (40,40,40), (tx,0,tw,22), 1)
                tc = (100,100,100)
            t = font_xs.render(name, True, tc)
            screen.blit(t, (tx+(tw-t.get_width())//2, 5))
        pygame.draw.line(screen, (60,60,100), (0,22), (SCREEN_W,22), 1)

        if tab == 0:
            draw_wifi_tab(screen, font, font_sm, font_xs, scroll, wifi_sel, scanning)
        elif tab == 1:
            draw_bt_tab(screen, font, font_sm, font_xs, scroll)
        elif tab == 2:
            draw_system_info(screen, font_sm, font_xs)
        elif tab == 3:
            draw_storage(screen, font_sm, font_xs)
        elif tab == 4:
            draw_about(screen, font_sm, font_xs)
        elif tab == 5:
            draw_sound(screen, font_sm, font_xs)

        pygame.display.flip()
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    tab = (tab+1) % len(TABS)
                    scroll = 0
                    wifi_sel = 0
                    if tab == 0:
                        threading.Thread(target=refresh_wifi, daemon=True).start()
                    elif tab == 1:
                        threading.Thread(target=refresh_bt, daemon=True).start()
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    tab = (tab-1) % len(TABS)
                    scroll = 0
                    wifi_sel = 0
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    if tab == 0:
                        wifi_sel = min(wifi_sel+1, len(_wifi_cache['networks'])-1)
                    else:
                        scroll += 1
                elif event.key in (pygame.K_UP, pygame.K_w):
                    if tab == 0:
                        wifi_sel = max(wifi_sel-1, 0)
                    else:
                        scroll = max(0, scroll-1)
                elif event.key == pygame.K_r:
                    if tab == 0:
                        scanning = True
                        def do_scan():
                            scan_wifi()
                        threading.Thread(target=do_scan, daemon=True).start()
                        scanning = False
                    elif tab == 1:
                        threading.Thread(target=refresh_bt, daemon=True).start()
                elif event.key == pygame.K_RETURN:
                    if tab == 0 and _wifi_cache['networks']:
                        wifi_connect_popup(screen, clock, font, font_sm, font_xs,
                                          _wifi_cache['networks'][wifi_sel])
                    elif tab == 1:
                        threading.Thread(target=refresh_bt, daemon=True).start()
                elif event.key == pygame.K_d:
                    if tab == 0 and _wifi_cache['ssid']:
                        subprocess.Popen(['sudo','nmcli','connection','delete',
                                         _wifi_cache['ssid']])
                        threading.Thread(target=refresh_wifi, daemon=True).start()


def draw_wifi_tab(screen, font, font_sm, font_xs, scroll, wifi_sel, scanning):
    y = 28
    ssid = _wifi_cache['ssid']
    ip = _wifi_cache['ip']
    col = (100,255,100) if ssid else (200,80,80)
    screen.blit(font_sm.render('● '+(ssid or 'Не подключено'), True, col), (8,y))
    if ip:
        screen.blit(font_xs.render('IP: '+ip, True, (120,120,120)), (8,y+14))
    y += 30
    pygame.draw.line(screen, (40,40,40), (0,y), (SCREEN_W,y), 1)
    y += 4

    nets = _wifi_cache['networks']
    if not nets:
        screen.blit(font_sm.render('Нажми R для сканирования', True, (80,80,80)), (8,y))
    else:
        screen.blit(font_xs.render('Сети (R=обновить  ENTER=подключить  D=забыть):', True, (100,100,160)), (8,y))
        y += 14
        for i, net in enumerate(nets[scroll:scroll+7]):
            iy = y+i*18
            active = net == ssid
            sel = (i+scroll) == wifi_sel
            if sel:
                pygame.draw.rect(screen, (30,30,50), (4,iy-1,SCREEN_W-8,17))
                pygame.draw.rect(screen, (80,80,160), (4,iy-1,SCREEN_W-8,17), 1)
            mark = '✓ ' if active else '  '
            screen.blit(font_sm.render(mark+net[:38], True, (100,255,100) if active else WHITE if sel else (160,160,160)), (8,iy))

    if scanning:
        screen.blit(font_sm.render('Сканирование...', True, YELLOW), (8,SCREEN_H-30))
    screen.blit(font_xs.render('R=скан  ENTER=подключить  D=забыть  ESC=выход', True, (50,50,70)), (4,SCREEN_H-13))


def wifi_connect_popup(screen, clock, font, font_sm, font_xs, ssid):
    password = ''
    while True:
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0,0,0,180))
        screen.blit(overlay, (0,0))
        pw,ph = 360,90
        px,py = (SCREEN_W-pw)//2, (SCREEN_H-ph)//2
        pygame.draw.rect(screen, (20,20,35), (px,py,pw,ph))
        pygame.draw.rect(screen, (100,100,200), (px,py,pw,ph), 1)
        screen.blit(font_sm.render('Подключение: '+ssid[:24], True, WHITE), (px+8,py+8))
        pygame.draw.rect(screen, (40,40,40), (px+8,py+30,pw-16,24))
        pygame.draw.rect(screen, (80,80,120), (px+8,py+30,pw-16,24), 1)
        screen.blit(font_sm.render('*'*len(password)+'|', True, WHITE), (px+12,py+34))
        screen.blit(font_xs.render('ENTER=подключить  ESC=отмена', True, (80,80,80)), (px+8,py+62))
        pygame.display.flip()
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                elif event.key == pygame.K_BACKSPACE:
                    password = password[:-1]
                elif event.key == pygame.K_RETURN:
                    subprocess.Popen(['sudo','nmcli','dev','wifi','connect',ssid,'password',password])
                    return
                elif event.unicode.isprintable():
                    password += event.unicode


def draw_bt_tab(screen, font, font_sm, font_xs, scroll):
    y = 28
    status = _bt_cache['status']
    col = (100,255,100) if status else (200,80,80)
    screen.blit(font_sm.render('Bluetooth: '+('ВКЛ' if status else 'ВЫКЛ'), True, col), (8,y))
    y += 18

    if not status:
        screen.blit(font_xs.render('sudo systemctl enable bluetooth', True, (80,80,80)), (8,y))
        screen.blit(font_xs.render('sudo systemctl start bluetooth', True, (80,80,80)), (8,y+12))
        y += 28

    pygame.draw.line(screen, (40,40,40), (0,y), (SCREEN_W,y), 1)
    y += 4

    devices = _bt_cache['devices']
    if not devices:
        screen.blit(font_sm.render('Нажми R для сканирования', True, (80,80,80)), (8,y))
    else:
        screen.blit(font_xs.render('Устройства (R=обновить  ENTER=подключить):', True, (100,100,160)), (8,y))
        y += 14
        for i, d in enumerate(devices[scroll:scroll+8]):
            screen.blit(font_sm.render(d[:50], True, (180,180,180)), (8,y+i*18))

    screen.blit(font_xs.render('R=скан  ENTER=подключить  ESC=выход', True, (50,50,70)), (4,SCREEN_H-13))


def draw_system_info(screen, font_sm, font_xs):
    y = 28
    rows = []
    try:
        rows.append(('CPU темп', get_cpu_temp()+'°C'))
    except:
        rows.append(('CPU темп', 'N/A'))
    try:
        with open('/proc/meminfo') as f:
            mem = {l.split(':')[0]: int(l.split()[1]) for l in f if ':' in l}
        total = mem.get('MemTotal',0)//1024
        free = mem.get('MemAvailable',0)//1024
        rows.append(('RAM всего', '{}MB'.format(total)))
        rows.append(('RAM занято', '{}MB'.format(total-free)))
        rows.append(('RAM свободно', '{}MB'.format(free)))
    except:
        pass
    rows.append(('Uptime', get_uptime()))
    try:
        r = subprocess.run(['uname','-r'], capture_output=True, text=True)
        rows.append(('Ядро', r.stdout.strip()))
    except:
        pass
    try:
        r = subprocess.run(['vcgencmd','get_throttled'], capture_output=True, text=True)
        rows.append(('Throttle', r.stdout.strip()))
    except:
        pass
    try:
        with open('/proc/cpuinfo') as f:
            for l in f:
                if 'Hardware' in l or 'Revision' in l:
                    k,v = l.split(':')
                    rows.append((k.strip()[:16], v.strip()[:30]))
    except:
        pass

    for k,v in rows:
        pygame.draw.rect(screen, (18,18,28), (4,y,SCREEN_W-8,17))
        pygame.draw.rect(screen, (35,35,55), (4,y,SCREEN_W-8,17), 1)
        screen.blit(font_xs.render(k, True, (140,140,200)), (8,y+3))
        screen.blit(font_xs.render(str(v), True, WHITE), (SCREEN_W//2,y+3))
        y += 19
        if y > SCREEN_H-20: break


def draw_storage(screen, font_sm, font_xs):
    y = 28
    try:
        r = subprocess.run(['df','-h'], capture_output=True, text=True)
        for line in r.stdout.strip().split('\n')[1:6]:
            parts = line.split()
            if len(parts) >= 6:
                try: pct_val = int(parts[4].replace('%',''))
                except: pct_val = 0
                bar_col = RED if pct_val>90 else YELLOW if pct_val>70 else (60,180,60)
                screen.blit(font_xs.render(parts[5]+' — '+parts[2]+'/'+parts[1], True, (180,180,255)), (8,y))
                y += 11
                bw = SCREEN_W-16
                pygame.draw.rect(screen, (30,30,30), (8,y,bw,8))
                pygame.draw.rect(screen, bar_col, (8,y,bw*pct_val//100,8))
                pygame.draw.rect(screen, (60,60,60), (8,y,bw,8), 1)
                screen.blit(font_xs.render(parts[4], True, (120,120,120)), (bw+10,y))
                y += 14
    except Exception as e:
        screen.blit(font_sm.render('Ошибка: '+str(e)[:40], True, RED), (8,y))
        y += 20

    pygame.draw.line(screen, (40,40,40), (0,y), (SCREEN_W,y), 1)
    y += 4
    for cname, cpath in [('whoOS','/home/who/whoOS'),('Дом','/home/who'),('Tmp','/tmp')]:
        try:
            r = subprocess.run(['du','-sh',cpath], capture_output=True, text=True, timeout=3)
            sz = r.stdout.split()[0] if r.stdout else '?'
        except: sz = '?'
        screen.blit(font_xs.render(cname+': '+sz+'  '+cpath, True, (140,140,140)), (8,y))
        y += 13
        if y > SCREEN_H-10: break


def draw_about(screen, font_sm, font_xs):
    y = 28
    rows = [
        ('Система','whoOS'), ('Версия',VERSION), ('Автор','Who762'),
        ('Платформа','Raspberry Pi 3A+'), ('Дисплей','Waveshare 3.5" 480x320'),
        ('OLED','SSD1309 I2C 0x3C'), ('Сенсор','DHT11 GPIO4'),
        ('Клавиатура','HS6209 event0'), ('GUI','pygame + X11/fbdev'),
    ]
    try:
        r = subprocess.run(['python3','--version'], capture_output=True, text=True)
        rows.append(('Python', r.stdout.strip()))
    except: pass
    for k,v in rows:
        pygame.draw.rect(screen, (15,15,25), (4,y,SCREEN_W-8,16))
        screen.blit(font_xs.render(k, True, (140,140,200)), (8,y+2))
        screen.blit(font_xs.render(v, True, WHITE), (SCREEN_W//2,y+2))
        y += 18
        if y > SCREEN_H-10: break


def draw_sound(screen, font_sm, font_xs):
    y = 34
    screen.blit(font_sm.render('Звук — в разработке', True, (120,120,120)), (8,y))
    y += 20
    try:
        r = subprocess.run(['amixer','get','Master'], capture_output=True, text=True, timeout=3)
        for line in r.stdout.split('\n')[:8]:
            screen.blit(font_xs.render(line[:60], True, (80,80,80)), (8,y))
            y += 12
    except:
        screen.blit(font_xs.render('amixer недоступен', True, (60,60,60)), (8,y))
