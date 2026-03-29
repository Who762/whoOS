import pygame
from assets.version import *
from core.system import shutdown, reboot
import subprocess
import sys
import os

ITEMS = [
    ('  Выключить',        'shutdown'),
    ('  Перезагрузить',    'reboot'),
    ('  Спящий режим',     'sleep'),
    ('  Терминал',         'terminal'),
    ('  Выйти в LXQt',     'lxqt'),
    ('  Разлогиниться',    'logout'),
    ('  Отмена',           'cancel'),
]

def draw_power_icon(screen, x, y, col):
    cx, cy = x+10, y+10
    pygame.draw.arc(screen, col, (cx-7,cy-7,14,14), 0.6, 2.5, 2)
    pygame.draw.line(screen, col, (cx,cy-8), (cx,cy-3), 2)

def draw_powermenu(screen, clock, font):
    selected = 0
    w, h = 240, len(ITEMS)*34+30
    x = (SCREEN_W-w)//2
    y = (SCREEN_H-h)//2

    while True:
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0,0,0,200))
        screen.blit(overlay, (0,0))
        pygame.draw.rect(screen, (25,25,25), (x,y,w,h))
        pygame.draw.rect(screen, (100,100,100), (x,y,w,h), 1)
        draw_power_icon(screen, x+10, y+4, WHITE)
        title = font.render('ПИТАНИЕ', True, WHITE)
        screen.blit(title, (x+30, y+8))
        pygame.draw.line(screen, (60,60,60), (x,y+28), (x+w,y+28), 1)

        for i, (name, action) in enumerate(ITEMS):
            iy = y+32+i*34
            if i == selected:
                pygame.draw.rect(screen, (50,50,50), (x+4,iy,w-8,30))
                pygame.draw.rect(screen, WHITE, (x+4,iy,w-8,30), 1)
                col = WHITE
            else:
                col = (150,150,150)
            text = font.render(name, True, col)
            screen.blit(text, (x+16, iy+7))

        pygame.display.flip()
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'cancel'
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_DOWN, pygame.K_s):
                    selected = (selected+1) % len(ITEMS)
                elif event.key in (pygame.K_UP, pygame.K_w):
                    selected = (selected-1) % len(ITEMS)
                elif event.key == pygame.K_ESCAPE:
                    return 'cancel'
                elif event.key == pygame.K_RETURN:
                    action = ITEMS[selected][1]
                    if action == 'shutdown':
                        pygame.quit()
                        shutdown()
                        sys.exit()
                    elif action == 'reboot':
                        pygame.quit()
                        reboot()
                        sys.exit()
                    elif action == 'sleep':
                        subprocess.run(['sudo','systemctl','suspend'])
                    elif action == 'terminal':
                        pygame.quit()
                        open('/tmp/whoos_return', 'w').close()
                        sys.exit()
                    elif action == 'lxqt':
                        pygame.quit()
                        open('/tmp/whoos_lxqt', 'w').close()
                        sys.exit()
                    elif action == 'logout':
                        return 'logout'
                    elif action == 'cancel':
                        return 'cancel'
