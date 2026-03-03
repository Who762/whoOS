import pygame
import os
import subprocess
import json
from assets.version import *

PROGRAMS_FILE = '/home/who/whoOS/core/programs.json'

def load_programs():
    try:
        if os.path.exists(PROGRAMS_FILE):
            return json.load(open(PROGRAMS_FILE))
        return []
    except Exception:
        return []

def save_programs(programs):
    try:
        json.dump(programs, open(PROGRAMS_FILE, 'w'))
    except Exception:
        pass

def draw_skull(screen, x, y, col):
    pygame.draw.circle(screen, col, (x+8, y+6), 7, 1)
    pygame.draw.rect(screen, col, (x+3, y+10, 10, 6), 1)
    pygame.draw.line(screen, col, (x+6, y+10), (x+6, y+16), 1)
    pygame.draw.line(screen, col, (x+10, y+10), (x+10, y+16), 1)
    pygame.draw.circle(screen, col, (x+5, y+5), 2, 1)
    pygame.draw.circle(screen, col, (x+11, y+5), 2, 1)
    pygame.draw.arc(screen, col, (x+5, y+8, 6, 4), 3.14, 6.28, 1)

def run_programs(screen, clock):
    font = pygame.font.SysFont('monospace', 14, bold=True)
    font_sm = pygame.font.SysFont('monospace', 12)
    programs = load_programs()
    selected = 0
    scroll = 0
    max_visible = (SCREEN_H - 60) // 28
    msg = ''
    msg_timer = 0

    while True:
        screen.fill(BLACK)

        header = pygame.Rect(0, 0, SCREEN_W, 32)
        pygame.draw.rect(screen, (20,20,20), header)
        pygame.draw.line(screen, WHITE, (0, 32), (SCREEN_W, 32), 1)

        draw_skull(screen, 8, 6, WHITE)
        title = font.render('PROGRAMS', True, WHITE)
        screen.blit(title, (34, 8))

        add_t = font_sm.render('[A] Добавить  [DEL] Удалить  [ESC] Назад', True, (80,80,80))
        screen.blit(add_t, (8, SCREEN_H-20))

        if not programs:
            empty = font_sm.render('Нет программ. Нажми [A] чтобы добавить.', True, (80,80,80))
            screen.blit(empty, ((SCREEN_W-empty.get_width())//2, SCREEN_H//2-10))
        else:
            for i, prog in enumerate(programs[scroll:scroll+max_visible]):
                idx = i + scroll
                y = 38 + i * 28
                if idx == selected:
                    pygame.draw.rect(screen, (30,30,30), (4, y, SCREEN_W-8, 26))
                    pygame.draw.rect(screen, WHITE, (4, y, SCREEN_W-8, 26), 1)
                    col = WHITE
                else:
                    pygame.draw.rect(screen, (15,15,15), (4, y, SCREEN_W-8, 26))
                    pygame.draw.rect(screen, (50,50,50), (4, y, SCREEN_W-8, 26), 1)
                    col = (150,150,150)

                ext = prog['path'].split('.')[-1].lower()
                icon_col = (100,200,100) if ext == 'py' else (200,200,100)
                icon_t = font_sm.render('[{}]'.format(ext.upper()[:3]), True, icon_col)
                screen.blit(icon_t, (12, y+5))

                name_t = font_sm.render(prog['name'][:30], True, col)
                screen.blit(name_t, (60, y+5))

        if msg_timer > 0:
            msg_timer -= 1
            mt = font_sm.render(msg, True, (100,255,100))
            screen.blit(mt, ((SCREEN_W-mt.get_width())//2, SCREEN_H-40))

        pygame.display.flip()
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    selected = min(selected+1, len(programs)-1)
                    if selected >= scroll+max_visible:
                        scroll += 1
                elif event.key in (pygame.K_UP, pygame.K_w):
                    selected = max(selected-1, 0)
                    if selected < scroll:
                        scroll -= 1
                elif event.key == pygame.K_a:
                    path = draw_file_picker(screen, clock, font_sm)
                    if path:
                        name = os.path.basename(path)
                        programs.append({'name': name, 'path': path})
                        save_programs(programs)
                        msg = 'Добавлено: ' + name
                        msg_timer = 90
                elif event.key == pygame.K_DELETE:
                    if programs and 0 <= selected < len(programs):
                        removed = programs.pop(selected)
                        save_programs(programs)
                        selected = max(0, selected-1)
                        msg = 'Удалено: ' + removed['name']
                        msg_timer = 90
                elif event.key == pygame.K_RETURN:
                    if programs and 0 <= selected < len(programs):
                        prog = programs[selected]
                        ext = prog['path'].split('.')[-1].lower()
                        if ext == 'py':
                            subprocess.Popen(['python3', prog['path']])
                        elif ext == 'sh':
                            subprocess.Popen(['bash', prog['path']])
                        else:
                            subprocess.Popen([prog['path']])
                        msg = 'Запущено!'
                        msg_timer = 60

def draw_file_picker(screen, clock, font):
    current = '/home/who'
    selected = 0
    scroll = 0
    max_v = (SCREEN_H - 60) // 22

    while True:
        screen.fill(BLACK)
        pygame.draw.rect(screen, WHITE, (0, 0, SCREEN_W, 28))
        t = font.render('Выбери файл: ' + current[-30:], True, BLACK)
        screen.blit(t, (4, 6))

        try:
            raw = sorted(os.listdir(current))
            dirs = [i for i in raw if os.path.isdir(os.path.join(current, i))]
            files = [i for i in raw if not os.path.isdir(os.path.join(current, i))]
            items = ['..'] + dirs + files
        except Exception:
            items = ['..']

        for i, name in enumerate(items[scroll:scroll+max_v]):
            idx = i + scroll
            y = 32 + i * 22
            full = os.path.join(current, name)
            is_dir = name == '..' or os.path.isdir(full)
            col = WHITE if idx != selected else BLACK
            if idx == selected:
                pygame.draw.rect(screen, WHITE, (0, y, SCREEN_W, 22))
            prefix = '/ ' if is_dir else '  '
            screen.blit(font.render(prefix + name[:44], True, col), (4, y+3))

        hint = font.render('ENTER=выбрать  ESC=отмена', True, (80,80,80))
        screen.blit(hint, (4, SCREEN_H-18))
        pygame.display.flip()
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    selected = min(selected+1, len(items)-1)
                    if selected >= scroll+max_v:
                        scroll += 1
                elif event.key in (pygame.K_UP, pygame.K_w):
                    selected = max(selected-1, 0)
                    if selected < scroll:
                        scroll -= 1
                elif event.key == pygame.K_RETURN:
                    name = items[selected]
                    if name == '..':
                        current = os.path.dirname(current)
                        selected = 0
                        scroll = 0
                    else:
                        full = os.path.join(current, name)
                        if os.path.isdir(full):
                            current = full
                            selected = 0
                            scroll = 0
                        else:
                            return full
