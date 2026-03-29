import pygame
import os
import subprocess
import json
import math
from assets.version import *

PROGRAMS_FILE = '/home/who/whoOS/core/programs.json'

def load_programs():
    try:
        if os.path.exists(PROGRAMS_FILE):
            return json.load(open(PROGRAMS_FILE))
        return []
    except: return []

def save_programs(programs):
    try:
        json.dump(programs, open(PROGRAMS_FILE,'w'))
    except: pass

def draw_skull_anim(screen, x, y, tick, col):
    # Череп кусает — нижняя челюсть движется
    bite = abs(math.sin(tick * 0.15)) * 6
    cx, cy = x+13, y+10

    # Верхняя часть черепа
    pygame.draw.circle(screen, col, (cx,cy-2), 10, 1)
    # Глаза
    pygame.draw.circle(screen, col, (cx-4,cy-4), 2, 1)
    pygame.draw.circle(screen, col, (cx+4,cy-4), 2, 1)
    # Нос
    pygame.draw.line(screen, col, (cx-1,cy), (cx+1,cy), 1)

    # Верхняя челюсть
    pygame.draw.rect(screen, col, (cx-7,cy+6,14,5), 1)
    # Зубы верхние
    for i in range(3):
        pygame.draw.rect(screen, col, (cx-5+i*4,cy+9,3,3), 0)

    # Нижняя челюсть — двигается
    jaw_y = int(cy+12+bite)
    pygame.draw.rect(screen, col, (cx-7,jaw_y,14,4), 1)
    # Зубы нижние
    for i in range(3):
        pygame.draw.rect(screen, col, (cx-5+i*4,jaw_y-2,3,3), 0)

def run_programs(screen, clock):
    font = pygame.font.SysFont('monospace', 14, bold=True)
    font_sm = pygame.font.SysFont('monospace', 12)
    font_xs = pygame.font.SysFont('monospace', 10)
    programs = load_programs()
    selected = 0
    scroll = 0
    max_visible = (SCREEN_H-70)//28
    msg = ''
    msg_timer = 0
    tick = 0

    while True:
        tick += 1
        screen.fill(BLACK)

        # Заголовок с анимацией черепа
        pygame.draw.rect(screen, (15,15,15), (0,0,SCREEN_W,40))
        pygame.draw.line(screen, WHITE, (0,40), (SCREEN_W,40), 1)
        draw_skull_anim(screen, 4, 4, tick, WHITE)
        title = font.render('PROGRAMS', True, WHITE)
        screen.blit(title, (40, 10))

        hint_top = font_xs.render('[A]=add  [DEL]=remove  [ENTER]=run  [ESC]=back', True, (60,60,60))
        screen.blit(hint_top, (8,SCREEN_H-16))

        if not programs:
            empty = font_sm.render('No programs. Press [A] to add.', True, (80,80,80))
            screen.blit(empty, ((SCREEN_W-empty.get_width())//2, SCREEN_H//2-10))
        else:
            for i, prog in enumerate(programs[scroll:scroll+max_visible]):
                idx = i+scroll
                y = 44+i*28
                if idx == selected:
                    pygame.draw.rect(screen, (30,30,30), (4,y,SCREEN_W-8,26))
                    pygame.draw.rect(screen, WHITE, (4,y,SCREEN_W-8,26), 1)
                    col = WHITE
                else:
                    pygame.draw.rect(screen, (15,15,15), (4,y,SCREEN_W-8,26))
                    pygame.draw.rect(screen, (50,50,50), (4,y,SCREEN_W-8,26), 1)
                    col = (150,150,150)

                ext = prog['path'].split('.')[-1].lower()
                icon_col = (100,200,100) if ext=='py' else (200,200,100)
                screen.blit(font_xs.render('[{}]'.format(ext.upper()[:3]), True, icon_col), (12,y+5))
                screen.blit(font_sm.render(prog['name'][:36], True, col), (50,y+5))

        if msg_timer > 0:
            msg_timer -= 1
            mt = font_sm.render(msg, True, (100,255,100))
            screen.blit(mt, ((SCREEN_W-mt.get_width())//2, SCREEN_H-36))

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
                    if selected >= scroll+max_visible: scroll += 1
                elif event.key in (pygame.K_UP, pygame.K_w):
                    selected = max(selected-1, 0)
                    if selected < scroll: scroll -= 1
                elif event.key == pygame.K_a:
                    path = draw_file_picker(screen, clock, font_sm)
                    if path:
                        name = os.path.basename(path)
                        programs.append({'name':name,'path':path})
                        save_programs(programs)
                        msg = 'Added: '+name; msg_timer = 90
                elif event.key == pygame.K_DELETE:
                    if programs and 0 <= selected < len(programs):
                        removed = programs.pop(selected)
                        save_programs(programs)
                        selected = max(0,selected-1)
                        msg = 'Removed: '+removed['name']; msg_timer = 90
                elif event.key == pygame.K_RETURN:
                    if programs and 0 <= selected < len(programs):
                        prog = programs[selected]
                        ext = prog['path'].split('.')[-1].lower()
                        if ext == 'py':
                            subprocess.Popen(['python3',prog['path']])
                        elif ext == 'sh':
                            subprocess.Popen(['bash',prog['path']])
                        else:
                            subprocess.Popen([prog['path']])
                        msg = 'Running!'; msg_timer = 60

def draw_file_picker(screen, clock, font):
    current = '/home/who'
    selected = 0
    scroll = 0
    max_v = (SCREEN_H-60)//22
    font_xs = pygame.font.SysFont('monospace', 9)

    while True:
        screen.fill(BLACK)
        pygame.draw.rect(screen, WHITE, (0,0,SCREEN_W,28))
        screen.blit(font.render('Select: '+current[-34:], True, BLACK), (4,6))

        try:
            raw = sorted(os.listdir(current))
            dirs = [i for i in raw if os.path.isdir(os.path.join(current,i))]
            files = [i for i in raw if not os.path.isdir(os.path.join(current,i))]
            items = ['..'] + dirs + files
        except: items = ['..']

        for i,name in enumerate(items[scroll:scroll+max_v]):
            idx = i+scroll
            y = 32+i*22
            full = os.path.join(current,name)
            is_dir = name=='..' or os.path.isdir(full)
            col = WHITE if idx!=selected else BLACK
            if idx == selected:
                pygame.draw.rect(screen, WHITE, (0,y,SCREEN_W,22))
            prefix = '▶ ' if is_dir else '  '
            screen.blit(font.render(prefix+name[:44], True, col), (4,y+3))

        screen.blit(font_xs.render('ENTER=select  ESC=cancel', True, (80,80,80)), (4,SCREEN_H-16))
        pygame.display.flip()
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: return None
                elif event.key in (pygame.K_DOWN,pygame.K_s):
                    selected = min(selected+1,len(items)-1)
                    if selected >= scroll+max_v: scroll += 1
                elif event.key in (pygame.K_UP,pygame.K_w):
                    selected = max(selected-1,0)
                    if selected < scroll: scroll -= 1
                elif event.key == pygame.K_RETURN:
                    name = items[selected]
                    if name == '..':
                        current = os.path.dirname(current)
                        selected = 0; scroll = 0
                    else:
                        full = os.path.join(current,name)
                        if os.path.isdir(full):
                            current = full; selected = 0; scroll = 0
                        else:
                            return full
