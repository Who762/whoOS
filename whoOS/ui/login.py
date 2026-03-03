import pygame
from assets.version import *
from core.auth import check_creds, user_exists

def run_login(screen, clock):
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

        border = pygame.Rect(40, 40, SCREEN_W - 80, SCREEN_H - 80)
        pygame.draw.rect(screen, WHITE, border, 1)

        title = font_title.render('[ who? Os - LOGIN ]', True, WHITE)
        screen.blit(title, ((SCREEN_W - title.get_width()) // 2, 60))

        line = pygame.Rect(40, 95, SCREEN_W - 80, 1)
        pygame.draw.rect(screen, WHITE, line)

        y = 120
        screen.blit(font_text.render('> SYSTEM ACCESS REQUIRED', True, GREEN), (60, y))
        y += 40

        user_col = WHITE if active == 'user' else GRAY
        screen.blit(font_text.render('LOGIN:', True, GRAY), (60, y))
        user_text = username + ('_' if active == 'user' and cursor_tick % 60 < 30 else '')
        screen.blit(font_input.render(user_text, True, user_col), (160, y))
        y += 35

        pass_col = WHITE if active == 'pass' else GRAY
        screen.blit(font_text.render('PASS: ', True, GRAY), (60, y))
        pass_text = '*' * len(password) + ('_' if active == 'pass' and cursor_tick % 60 < 30 else '')
        screen.blit(font_input.render(pass_text, True, pass_col), (160, y))
        y += 50

        screen.blit(font_text.render('[TAB] switch  [ENTER] confirm', True, GRAY), (60, y))

        if error:
            err = font_title.render(error, True, WHITE)
            screen.blit(err, ((SCREEN_W - err.get_width()) // 2, SCREEN_H - 80))

        pygame.display.flip()
        clock.tick(FPS)
