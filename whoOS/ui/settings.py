import pygame
from assets.version import *
from core.system import get_cpu_temp, get_uptime

ITEMS = [
    'CPU Temperature',
    'Uptime',
    'Version',
    'Display',
    'Network',
    'About',
]

def run_settings(screen, clock):
    font_title = pygame.font.SysFont('monospace', 20, bold=True)
    font_item = pygame.font.SysFont('monospace', 16)
    font_val = pygame.font.SysFont('monospace', 16, bold=True)

    selected = 0

    while True:
        screen.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    selected = (selected + 1) % len(ITEMS)
                elif event.key in (pygame.K_UP, pygame.K_w):
                    selected = (selected - 1) % len(ITEMS)

        header = pygame.Rect(0, 0, SCREEN_W, 36)
        pygame.draw.rect(screen, WHITE, header)
        title = font_title.render('SETTINGS', True, BLACK)
        screen.blit(title, (10, 8))
        back = font_title.render('[ESC] back', True, BLACK)
        screen.blit(back, (SCREEN_W - back.get_width() - 10, 8))

        values = {
            'CPU Temperature': get_cpu_temp() + ' C',
            'Uptime': get_uptime(),
            'Version': VERSION,
            'Display': '480x320',
            'Network': 'N/A',
            'About': 'who? Os',
        }

        for i, name in enumerate(ITEMS):
            y = 50 + i * 38
            if i == selected:
                pygame.draw.rect(screen, WHITE, (5, y - 2, SCREEN_W - 10, 34))
                col = BLACK
            else:
                pygame.draw.rect(screen, WHITE, (5, y - 2, SCREEN_W - 10, 34), 1)
                col = WHITE

            label = font_item.render(name, True, col)
            screen.blit(label, (15, y + 6))

            val = font_val.render(values.get(name, ''), True, col)
            screen.blit(val, (SCREEN_W - val.get_width() - 15, y + 6))

        pygame.display.flip()
        clock.tick(FPS)
