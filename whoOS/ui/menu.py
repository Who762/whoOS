import pygame
from assets.version import *
from ui.statusbar import draw_statusbar
from ui.powermenu import draw_powermenu
import math

ITEMS = [
    ('TERMINAL', 'terminal'),
    ('FILES',    'files'),
    ('CLOCK',    'clock'),
    ('SETTINGS', 'settings'),
    ('TOOLS',    'tools'),
    ('SYSTEM',   'system'),
    ('EDITOR',   'editor'),
    ('PROGRAMS', 'programs'),
]

def draw_icon(screen, action, x, y, size, col):
    s = size
    if action == 'terminal':
        pygame.draw.rect(screen, col, (x,y,s,s), 1)
        pygame.draw.line(screen, col, (x+3,y+s//2), (x+8,y+s//2), 1)
        pygame.draw.line(screen, col, (x+8,y+s//2-3), (x+8,y+s//2+3), 1)
    elif action == 'files':
        pygame.draw.rect(screen, col, (x,y+4,s,s-4), 1)
        pygame.draw.rect(screen, col, (x,y,s//2,6))
    elif action == 'clock':
        pygame.draw.circle(screen, col, (x+s//2,y+s//2), s//2, 1)
        pygame.draw.line(screen, col, (x+s//2,y+s//2), (x+s//2,y+4), 1)
        pygame.draw.line(screen, col, (x+s//2,y+s//2), (x+s-4,y+s//2), 1)
    elif action == 'settings':
        cx,cy = x+s//2,y+s//2
        for a in range(0,360,60):
            r = math.radians(a)
            pygame.draw.circle(screen, col, (int(cx+9*math.cos(r)),int(cy+9*math.sin(r))), 2)
        pygame.draw.circle(screen, col, (cx,cy), 4, 1)
    elif action == 'tools':
        # Гаечный ключ
        cx, cy = x+s//2, y+s//2
        # Рукоятка
        pygame.draw.line(screen, col, (cx-8,cy+8), (cx+4,cy-4), 3)
        # Головка ключа
        pygame.draw.circle(screen, col, (cx+6,cy-6), 6, 1)
        pygame.draw.circle(screen, col, (cx+6,cy-6), 2)
        # Зев ключа
        pygame.draw.line(screen, col, (cx+2,cy-10), (cx+4,cy-12), 2)
        pygame.draw.line(screen, col, (cx+10,cy-2), (cx+12,cy-4), 2)
    elif action == 'system':
        for i in range(4):
            h = 6+i*4
            pygame.draw.rect(screen, col, (x+2+i*6,y+s-h,5,h), 1)
    elif action == 'editor':
        pygame.draw.rect(screen, col, (x+2,y+2,s-4,s-4), 1)
        for i in range(3):
            pygame.draw.line(screen, col, (x+6,y+8+i*6), (x+s-6,y+8+i*6), 1)
    elif action == 'programs':
        # Череп
        cx, cy = x+s//2, y+s//2-2
        # Верхняя часть черепа
        pygame.draw.circle(screen, col, (cx, cy-2), 8, 1)
        # Нижняя челюсть
        pygame.draw.rect(screen, col, (cx-6, cy+4, 12, 6), 1)
        # Зубы
        for i in range(3):
            pygame.draw.line(screen, col, (cx-4+i*4, cy+4), (cx-4+i*4, cy+7), 1)
        # Глаза
        pygame.draw.circle(screen, col, (cx-3, cy-3), 2, 1)
        pygame.draw.circle(screen, col, (cx+3, cy-3), 2, 1)
        # Нос
        pygame.draw.line(screen, col, (cx-1, cy+1), (cx+1, cy+1), 1)

def run_menu(screen, clock):
    font = pygame.font.SysFont('monospace', 14, bold=True)
    font_sm = pygame.font.SysFont('monospace', 10)
    selected = 0
    tick = 0
    blink = False
    oled_ok = True
    dht_ok = True

    cols = 4
    rows = 2
    pad = 8
    top = 34
    bw = (SCREEN_W - pad*(cols+1)) // cols
    bh = (SCREEN_H - top - pad*(rows+1)) // rows
    power_btn = None

    while True:
        tick += 1
        if tick % 30 == 0:
            blink = not blink

        screen.fill(BLACK)
        power_btn = draw_statusbar(screen, font, font_sm, blink, tick,
                                   oled_ok=None, dht_ok=None)

        for i, (name, action) in enumerate(ITEMS):
            col_i = i % cols
            row_i = i // cols
            x = pad + col_i * (bw + pad)
            y = top + pad + row_i * (bh + pad)

            if i == selected:
                pygame.draw.rect(screen, (30,30,30), (x,y,bw,bh))
                pygame.draw.rect(screen, WHITE, (x,y,bw,bh), 2)
                tile_col = WHITE
            else:
                pygame.draw.rect(screen, (20,20,20), (x,y,bw,bh))
                pygame.draw.rect(screen, (60,60,60), (x,y,bw,bh), 1)
                tile_col = (140,140,140)

            icon_size = 26
            draw_icon(screen, action, x+(bw-icon_size)//2, y+8, icon_size, tile_col)
            label = font_sm.render(name, True, tile_col)
            screen.blit(label, (x+(bw-label.get_width())//2, y+bh-16))

        pygame.display.flip()
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RIGHT, pygame.K_d):
                    selected = (selected+1) % len(ITEMS)
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    selected = (selected-1) % len(ITEMS)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    selected = (selected+4) % len(ITEMS)
                elif event.key in (pygame.K_UP, pygame.K_w):
                    selected = (selected-4) % len(ITEMS)
                elif event.key == pygame.K_RETURN:
                    return ITEMS[selected][1]
                elif event.key == pygame.K_l and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                    pygame.quit()
                    open("/tmp/whoos_lxqt","w").close()
                    import sys; sys.exit()
                elif event.key == pygame.K_ESCAPE:
                    result = draw_powermenu(screen, clock, font)
                    if result == 'logout':
                        return 'logout'
            if event.type == pygame.MOUSEBUTTONDOWN:
                if power_btn and power_btn.collidepoint(event.pos):
                    result = draw_powermenu(screen, clock, font)
                    if result == 'logout':
                        return 'logout'
