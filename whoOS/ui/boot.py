import pygame
import time
from assets.version import *

def run_boot(screen, clock):
    font_big = pygame.font.SysFont('monospace', 48, bold=True)
    font_small = pygame.font.SysFont('monospace', 18)
    
    frames = 60
    for i in range(frames):
        screen.fill(BLACK)
        
        alpha = min(255, int(255 * i / 30))
        
        title = font_big.render(OS_NAME, True, WHITE)
        title.set_alpha(alpha)
        tx = (SCREEN_W - title.get_width()) // 2
        ty = (SCREEN_H - title.get_height()) // 2 - 20
        screen.blit(title, (tx, ty))
        
        ver = font_small.render(VERSION, True, GRAY)
        ver.set_alpha(alpha)
        vx = (SCREEN_W - ver.get_width()) // 2
        vy = SCREEN_H - 40
        screen.blit(ver, (vx, vy))
        
        if i > 20:
            bar_w = int(300 * (i - 20) / 40)
            bar_x = (SCREEN_W - 300) // 2
            bar_y = SCREEN_H // 2 + 30
            pygame.draw.rect(screen, GRAY, (bar_x, bar_y, 300, 4))
            pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_w, 4))
        
        pygame.display.flip()
        clock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
    
    time.sleep(0.5)
    return True
