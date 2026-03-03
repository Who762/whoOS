import pygame
import subprocess
import math
from assets.version import *
from ui.statusbar import draw_statusbar, check_oled, check_dht
from ui.powermenu import draw_powermenu

ITEMS = [
    ('TERMINAL', 'terminal'),
    ('FILES', 'files'),
    ('CLOCK', 'clock'),
    ('SETTINGS', 'settings'),
    ('NETWORK', 'network'),
    ('SYSTEM', 'system'),
    ('EDITOR', 'editor'),
    ('PROGRAMS', 'programs'),
]

def draw_icon(screen, action, x, y, size, col):
    cx = x + size // 2
    cy = y + size // 2
    if action == 'terminal':
        pygame.draw.rect(screen, col, (x+2, y+2, size-4, size-4), 1)
        font = pygame.font.SysFont('monospace', 10, bold=True)
        t = font.render('$>', True, col)
        screen.blit(t, (x+4, cy-6))
    elif action == 'files':
        pygame.draw.rect(screen, col, (x+2, y+8, size-4, size-10), 1)
        pygame.draw.polygon(screen, col, [(x+2,y+8),(x+2,y+4),(x+10,y+4),(x+13,y+8)])
    elif action == 'clock':
        pygame.draw.circle(screen, col, (cx, cy), size//2-2, 1)
        pygame.draw.line(screen, col, (cx, cy), (cx, cy-7), 2)
        pygame.draw.line(screen, col, (cx, cy), (cx+5, cy+2), 2)
        pygame.draw.circle(screen, col, (cx, cy), 2)
    elif action == 'settings':
        pygame.draw.circle(screen, col, (cx, cy), 4, 1)
        for a in range(0, 360, 45):
            rx = int(cx + (size//2-3) * math.cos(math.radians(a)))
            ry = int(cy + (size//2-3) * math.sin(math.radians(a)))
            pygame.draw.circle(screen, col, (rx, ry), 2)
    elif action == 'network':
        for i, r in enumerate([4, 8, 12]):
            pygame.draw.arc(screen, col,
                (cx-r, cy+4-r, r*2, r*2), 0.3, 2.8, 1)
        pygame.draw.circle(screen, col, (cx, cy+4), 2)
    elif action == 'system':
        pygame.draw.rect(screen, col, (x+3, y+3, size-6, size-6), 1)
        pygame.draw.rect(screen, col, (x+7, y+7, size-14, size-14), 1)
        font = pygame.font.SysFont('monospace', 8)
        t = font.render('CPU', True, col)
        screen.blit(t, (cx-t.get_width()//2, cy-5))
    elif action == 'editor':
        pygame.draw.rect(screen, col, (x+3, y+3, size-6, size-6), 1)
        for i in range(3):
            pygame.draw.line(screen, col, (x+7, y+9+i*6), (x+size-7, y+9+i*6), 1)
        pygame.draw.line(screen, col, (x+7, y+9), (x+7, y+20), 1)
    elif action == 'programs':
        pygame.draw.circle(screen, col, (cx, cy-2), size//2-4, 1)
        pygame.draw.circle(screen, col, (cx-4, cy+6), 3, 1)
        pygame.draw.circle(screen, col, (cx+4, cy+6), 3, 1)
        pygame.draw.circle(screen, col, (cx, cy+2), 3, 1)
        pygame.draw.line(screen, col, (cx-2, cy-6), (cx-4, cy+3), 1)
        pygame.draw.line(screen, col, (cx+2, cy-6), (cx+4, cy+3), 1)
        pygame.draw.line(screen, col, (cx-4, cy+3), (cx+4, cy+3), 1)

def run_menu(screen, clock):
    font = pygame.font.SysFont('monospace', 14, bold=True)
    font_sm = pygame.font.SysFont('monospace', 11)
    selected = 0
    blink = False
    blink_tick = 0
    tick = 0
    oled_ok = True
    dht_ok = True
    check_tick = 0
    power_btn = None

    while True:
        screen.fill(BLACK)
        blink_tick += 1
        tick += 1
        check_tick += 1

        if check_tick > 200:
            check_tick = 0
            oled_ok = check_oled()
            dht_ok = check_dht()

        if blink_tick >= 15:
            blink = not blink
            blink_tick = 0

        power_btn = draw_statusbar(screen, font, font_sm, blink, tick,
            oled_ok=oled_ok, dht_ok=dht_ok,
            bat_pct=None, charging=False,
            low_voltage=False, has_power=True)

        cols = 4
        rows = 2
        pad = 6
        top = 38
        bw = (SCREEN_W - pad * (cols + 1)) // cols
        bh = (SCREEN_H - top - pad * (rows + 1)) // rows

        for i, (name, action) in enumerate(ITEMS):
            col_i = i % cols
            row_i = i // cols
            x = pad + col_i * (bw + pad)
            y = top + pad + row_i * (bh + pad)

            if i == selected:
                pygame.draw.rect(screen, (30,30,30), (x, y, bw, bh))
                pygame.draw.rect(screen, WHITE, (x, y, bw, bh), 2)
                tile_col = WHITE
            else:
                pygame.draw.rect(screen, (20,20,20), (x, y, bw, bh))
                pygame.draw.rect(screen, (60,60,60), (x, y, bw, bh), 1)
                tile_col = (140,140,140)

            icon_size = 26
            draw_icon(screen, action, x + (bw-icon_size)//2, y+8, icon_size, tile_col)
            label = font_sm.render(name, True, tile_col)
            screen.blit(label, (x + (bw-label.get_width())//2, y+bh-16))

        pygame.display.flip()
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RIGHT, pygame.K_d):
                    selected = (selected + 1) % len(ITEMS)
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    selected = (selected - 1) % len(ITEMS)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    selected = (selected + 4) % len(ITEMS)
                elif event.key in (pygame.K_UP, pygame.K_w):
                    selected = (selected - 4) % len(ITEMS)
                elif event.key == pygame.K_RETURN:
                    return ITEMS[selected][1]
                elif event.key == pygame.K_ESCAPE:
                    draw_powermenu(screen, clock, font)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if power_btn and power_btn.collidepoint(event.pos):
                    draw_powermenu(screen, clock, font)
