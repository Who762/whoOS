import pygame
import math
from assets.version import *

TOOLS = [
    {'id':'subghz',  'name':'Sub-GHz',       'desc':'300-928 MHz  CC1101',      'color':(100,255,100)},
    {'id':'ghz24',   'name':'2.4 GHz',        'desc':'WiFi / BT / NRF24',        'color':(100,180,255)},
    {'id':'nfc',     'name':'NFC / RFID',     'desc':'13.56 MHz  RC522',          'color':(255,200,80)},
    {'id':'usb',     'name':'USB Script',     'desc':'HID payload inject',        'color':(200,100,255)},
    {'id':'tiny',    'name':'Tiny Gadgets',   'desc':'Gates  remotes  IR',        'color':(255,120,80)},
    {'id':'gpio',    'name':'GPIO Monitor',   'desc':'Pins  I2C  SPI',            'color':(80,255,200)},
    {'id':'network', 'name':'Net Scanner',    'desc':'LAN  ping  ports',          'color':(180,180,255)},
    {'id':'sysmon',  'name':'System Monitor', 'desc':'CPU  RAM  temp',            'color':(255,255,80)},
]

def draw_subghz_anim(screen, x, y, tick, col):
    cx = x+20
    pygame.draw.line(screen, col, (cx,y+30),(cx,y+10), 2)
    pygame.draw.line(screen, col, (cx-6,y+16),(cx,y+10), 2)
    pygame.draw.line(screen, col, (cx+6,y+16),(cx,y+10), 2)
    t = tick % 40
    for i,r in enumerate([8,14,20]):
        alpha = max(0, 255-abs(t*6-i*60))
        if alpha > 30:
            wc = (int(col[0]*alpha/255), int(col[1]*alpha/255), int(col[2]*alpha/255))
            pygame.draw.arc(screen, wc, (cx-r,y+10-r//2,r*2,r), 0, math.pi, 1)

def draw_wifi_anim(screen, x, y, tick, col):
    cx, cy = x+20, y+24
    t = tick % 30
    for i,r in enumerate([6,11,16]):
        alpha = max(0, 255-abs(t*8-i*80))
        if alpha > 30:
            wc = (int(col[0]*alpha/255),int(col[1]*alpha/255),int(col[2]*alpha/255))
            pygame.draw.arc(screen, wc, (cx-r,cy-r,r*2,r*2), 0.4, 2.7, 2)
    pygame.draw.circle(screen, col, (cx,cy), 3)

def draw_nfc_anim(screen, x, y, tick, col):
    cx, cy = x+20, y+20
    pygame.draw.rect(screen, col, (cx-12,cy-8,24,16), 1)
    pygame.draw.rect(screen, col, (cx-8,cy-4,16,8), 1)
    t = tick % 20
    if t < 10:
        pygame.draw.circle(screen, col, (cx+18,cy), 3)
    else:
        pygame.draw.circle(screen, col, (cx-18,cy), 3)

def draw_usb_anim(screen, x, y, tick, col):
    cx, cy = x+20, y+20
    pygame.draw.rect(screen, col, (cx-8,cy-4,16,10), 1)
    pygame.draw.rect(screen, col, (cx-3,cy+6,6,8), 1)
    t = tick % 30
    for i in range(3):
        px = cx-14+(t+i*10)%30
        if cx-14 < px < cx-2:
            pygame.draw.circle(screen, col, (px,cy+10), 1)

def draw_tiny_anim(screen, x, y, tick, col):
    cx, cy = x+20, y+18
    pygame.draw.rect(screen, col, (cx-8,cy-12,16,24), 1)
    pygame.draw.circle(screen, col, (cx,cy-6), 3, 1)
    pygame.draw.rect(screen, col, (cx-5,cy+2,4,4), 1)
    pygame.draw.rect(screen, col, (cx+1,cy+2,4,4), 1)
    t = tick % 40
    r = (t*2) % 20
    if r > 2:
        pygame.draw.arc(screen, col, (cx-r,cy-18-r//2,r*2,r), 0, math.pi, 1)

def draw_gpio_anim(screen, x, y, tick, col):
    for i in range(4):
        px = x+6+i*9
        h = int(8+8*math.sin((tick+i*8)*0.2))
        pygame.draw.rect(screen, col, (px,y+28-h,5,h), 1)

def draw_network_anim(screen, x, y, tick, col):
    cx, cy = x+20, y+20
    pygame.draw.circle(screen, col, (cx,cy), 12, 1)
    pygame.draw.line(screen, col, (cx-12,cy),(cx+12,cy), 1)
    pygame.draw.line(screen, col, (cx,cy-12),(cx,cy+12), 1)
    r = int(6+6*math.sin(tick*0.1))
    pygame.draw.circle(screen, col, (cx,cy), r, 1)

def draw_sysmon_anim(screen, x, y, tick, col):
    for i in range(5):
        h = int(8+12*abs(math.sin(tick*0.1+i*0.8)))
        pygame.draw.rect(screen, col, (x+4+i*7,y+32-h,5,h), 1)

    # Гайка стоит, ключ подлетает и закручивает
    cx, cy = x+20, y+20
    # Гайка (шестиугольник)
    for i in range(6):
        a1 = math.radians(i*60)
        a2 = math.radians((i+1)*60)
        x1 = int(cx + 8*math.cos(a1))
        y1 = int(cy + 8*math.sin(a1))
        x2 = int(cx + 8*math.cos(a2))
        y2 = int(cy + 8*math.sin(a2))
        pygame.draw.line(screen, col, (x1,y1),(x2,y2), 1)
    pygame.draw.circle(screen, col, (cx,cy), 4, 1)

    # Ключ анимация — подлетает, закручивает, отъезжает
    t = tick % 90
    if t < 30:
        # Подлетает справа
        kx = int(cx + 30 - t)
        ky = cy - 5
    elif t < 60:
        # Закручивает — вращение вокруг гайки
        angle = math.radians((t-30)*6)
        kx = int(cx + 14*math.cos(angle))
        ky = int(cy + 14*math.sin(angle))
    else:
        # Отъезжает
        kx = int(cx + (t-60))
        ky = cy - 5

    # Рисуем ключ
    pygame.draw.line(screen, col, (kx,ky),(kx+12,ky+4), 2)
    pygame.draw.circle(screen, col, (kx,ky), 4, 1)

ANIM_FUNCS = {
    'subghz':  draw_subghz_anim,
    'ghz24':   draw_wifi_anim,
    'nfc':     draw_nfc_anim,
    'usb':     draw_usb_anim,
    'tiny':    draw_tiny_anim,
    'gpio':    draw_gpio_anim,
    'network': draw_network_anim,
    'sysmon':  draw_sysmon_anim,
}

def run_tools(screen, clock):
    font = pygame.font.SysFont('monospace', 13, bold=True)
    font_sm = pygame.font.SysFont('monospace', 11)
    font_xs = pygame.font.SysFont('monospace', 9)

    selected = 0
    tick = 0
    scroll = 0
    max_v = 5

    while True:
        tick += 1
        screen.fill(BLACK)

        pygame.draw.rect(screen, (15,15,15), (0,0,SCREEN_W,22))
        pygame.draw.line(screen, (80,80,80), (0,22), (SCREEN_W,22), 1)
        t = font.render('< TOOLS >', True, WHITE)
        screen.blit(t, ((SCREEN_W-t.get_width())//2, 4))

        list_w = 160
        pygame.draw.line(screen, (50,50,50), (list_w,22),(list_w,SCREEN_H), 1)

        for i in range(max_v):
            idx = i+scroll
            if idx >= len(TOOLS): break
            tool = TOOLS[idx]
            y = 26+i*((SCREEN_H-26)//max_v)
            h = (SCREEN_H-26)//max_v-2

            if idx == selected:
                pygame.draw.rect(screen, (25,25,35), (0,y,list_w-1,h))
                pygame.draw.rect(screen, (3,3,3), (0,y,3,h))
                pygame.draw.rect(screen, tool['color'], (0,y,3,h))
                pygame.draw.rect(screen, (60,60,90), (0,y,list_w-1,h), 1)
                nc = WHITE; dc = (180,180,180)
            else:
                pygame.draw.rect(screen, (10,10,10), (0,y,list_w-1,h))
                pygame.draw.rect(screen, (30,30,30), (0,y,list_w-1,h), 1)
                nc = (120,120,120); dc = (70,70,70)

            pygame.draw.circle(screen, tool['color'] if idx==selected else (60,60,60), (10,y+h//2), 4)
            screen.blit(font_sm.render(tool['name'], True, nc), (18,y+4))
            screen.blit(font_xs.render(tool['desc'], True, dc), (18,y+16))

        # Скроллбар
        if len(TOOLS) > max_v:
            sb_h = (SCREEN_H-26)*max_v//len(TOOLS)
            sb_y = 26+(SCREEN_H-26)*scroll//len(TOOLS)
            pygame.draw.rect(screen, (50,50,50), (list_w-4,26,3,SCREEN_H-26))
            pygame.draw.rect(screen, (120,120,120), (list_w-4,sb_y,3,sb_h))

        # Правая панель
        tool = TOOLS[selected]
        rx = list_w+8
        rw = SCREEN_W-list_w-8

        nt = font.render(tool['name'], True, tool['color'])
        screen.blit(nt, (rx+(rw-nt.get_width())//2, 28))

        # Анимация инструментов (гаечный ключ) поверх основной

        anim_fn = ANIM_FUNCS.get(tool['id'])
        if anim_fn:
            anim_fn(screen, rx+rw//2-20, 80, tick, tool['color'])

        pygame.draw.line(screen, (40,40,40), (rx,195),(SCREEN_W-4,195), 1)
        screen.blit(font_xs.render('NOT INSTALLED', True, (150,80,80)), (rx,198))
        screen.blit(font_xs.render('ENTER=open  ESC=back', True, (50,50,70)), (rx,SCREEN_H-14))

        pygame.display.flip()
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    if selected < len(TOOLS)-1:
                        selected += 1
                        if selected >= scroll+max_v: scroll += 1
                elif event.key in (pygame.K_UP, pygame.K_w):
                    if selected > 0:
                        selected -= 1
                        if selected < scroll: scroll -= 1
                elif event.key == pygame.K_RETURN:
                    show_tool_screen(screen, clock, font, font_sm, font_xs, TOOLS[selected])


def show_tool_screen(screen, clock, font, font_sm, font_xs, tool):
    tick = 0
    install_hints = {
        'subghz':  'pip3 install spidev RPi.GPIO',
        'ghz24':   'sudo apt install wireless-tools',
        'nfc':     'pip3 install mfrc522',
        'usb':     'pip3 install pyusb',
        'tiny':    'pip3 install RPi.GPIO pigpio',
        'gpio':    'pip3 install RPi.GPIO smbus2',
        'network': 'sudo apt install nmap',
        'sysmon':  'pip3 install psutil',
    }
    while True:
        tick += 1
        screen.fill(BLACK)
        pygame.draw.rect(screen, (15,15,15), (0,0,SCREEN_W,22))
        pygame.draw.line(screen, tool['color'], (0,22),(SCREEN_W,22), 1)
        screen.blit(font.render(tool['name'], True, tool['color']), (8,4))

        anim_fn = ANIM_FUNCS.get(tool['id'])
        if anim_fn:
            anim_fn(screen, SCREEN_W//2-20, 60, tick, tool['color'])

        screen.blit(font_sm.render('Module not installed', True, (150,80,80)), (8,160))
        hint = install_hints.get(tool['id'],'')
        if hint:
            screen.blit(font_xs.render('Install: '+hint, True, (80,80,80)), (8,178))
        screen.blit(font_xs.render('ESC = back', True, (50,50,70)), (8,SCREEN_H-14))

        pygame.display.flip()
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
