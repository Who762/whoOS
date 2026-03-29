import pygame
import os
from assets.version import *
from core.auth import check_creds, user_exists

def run_login(screen, clock):
    if os.path.exists('/tmp/whoos_nologin'):
        os.remove('/tmp/whoos_nologin')
        return True

    font_title = pygame.font.SysFont('monospace', 24, bold=True)
    font_text = pygame.font.SysFont('monospace', 16)
    font_input = pygame.font.SysFont('monospace', 18, bold=True)

    username = ''
    password = ''
    active = 'user'
    error = ''
    cursor_tick = 0

    while True:
        screen.fill(BLACK)
        cursor_tick += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    active = 'pass' if active == 'user' else 'user'
                    error = ''
                elif event.key == pygame.K_RETURN:
                    if active == 'user':
                        active = 'pass'
                    else:
                        if check_creds(username, password):
                            return True
                        else:
                            error = 'ACCESS DENIED'
                            password = ''
                elif event.key == pygame.K_BACKSPACE:
                    if active == 'user':
                        username = username[:-1]
                    else:
                        password = password[:-1]
                else:
                    if event.unicode.isprintable():
                        if active == 'user' and len(username) < 20:
                            username += event.unicode
                        elif active == 'pass' and len(password) < 20:
                            password += event.unicode

        cx = SCREEN_W // 2
        title = font_title.render('whoOS', True, WHITE)
        screen.blit(title, (cx - title.get_width()//2, 60))

        pygame.draw.rect(screen, (40,40,40), (cx-120, 130, 240, 36))
        pygame.draw.rect(screen, WHITE if active=='user' else (80,80,80), (cx-120, 130, 240, 36), 1)
        u_text = font_input.render(username + ('|' if active=='user' and cursor_tick%60<30 else ''), True, WHITE)
        screen.blit(u_text, (cx-110, 138))
        label_u = font_text.render('USER', True, (120,120,120))
        screen.blit(label_u, (cx-120, 114))

        pygame.draw.rect(screen, (40,40,40), (cx-120, 200, 240, 36))
        pygame.draw.rect(screen, WHITE if active=='pass' else (80,80,80), (cx-120, 200, 240, 36), 1)
        p_display = '*' * len(password) + ('|' if active=='pass' and cursor_tick%60<30 else '')
        p_text = font_input.render(p_display, True, WHITE)
        screen.blit(p_text, (cx-110, 208))
        label_p = font_text.render('PASSWORD', True, (120,120,120))
        screen.blit(label_p, (cx-120, 184))

        if error:
            err = font_text.render(error, True, (255,60,60))
            screen.blit(err, (cx - err.get_width()//2, 255))

        pygame.display.flip()
        clock.tick(FPS)
