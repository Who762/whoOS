import pygame
import os
import subprocess
import shutil
from assets.version import *

def get_icon(name, is_dir):
    if is_dir:
        return '[DIR]', (100,180,255)
    ext = name.split('.')[-1].lower() if '.' in name else ''
    icons = {
        'py':   ('[PY] ', (100,220,100)),
        'sh':   ('[SH] ', (220,220,100)),
        'txt':  ('[TXT]', (200,200,200)),
        'json': ('[JSN]', (255,180,100)),
        'md':   ('[MD] ', (180,255,180)),
        'log':  ('[LOG]', (180,100,100)),
        'mp3':  ('[MP3]', (180,100,255)),
        'jpg':  ('[IMG]', (255,150,150)),
        'png':  ('[IMG]', (255,150,150)),
    }
    return icons.get(ext, ('[   ]', (160,160,160)))

def input_text(screen, clock, font, font_sm, prompt, default=''):
    text = default
    while True:
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0,0,0,200))
        screen.blit(overlay, (0,0))
        pw, ph = 360, 70
        px, py = (SCREEN_W-pw)//2, (SCREEN_H-ph)//2
        pygame.draw.rect(screen, (20,20,35), (px,py,pw,ph))
        pygame.draw.rect(screen, WHITE, (px,py,pw,ph), 1)
        screen.blit(font_sm.render(prompt, True, WHITE), (px+8,py+8))
        pygame.draw.rect(screen, (40,40,40), (px+8,py+28,pw-16,24))
        pygame.draw.rect(screen, (80,80,120), (px+8,py+28,pw-16,24), 1)
        # Текст с курсором — мигание
        disp = text + '|'
        screen.blit(font_sm.render(disp[:40], True, WHITE), (px+12,py+32))
        pygame.display.flip()
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
                elif event.key == pygame.K_RETURN:
                    return text if text else None
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                elif event.unicode.isprintable():
                    text += event.unicode

def run_files(screen, clock, start_path=None):
    font = pygame.font.SysFont('monospace', 13, bold=True)
    font_sm = pygame.font.SysFont('monospace', 11)
    font_xs = pygame.font.SysFont('monospace', 9)

    current = start_path if start_path else '/home/who'
    selected = 0
    scroll = 0
    max_v = (SCREEN_H-50)//22
    clipboard = None
    clipboard_op = None
    msg = ''
    msg_timer = 0
    show_action_menu = False
    action_sel = 0

    def get_items(path):
        try:
            raw = sorted(os.listdir(path))
            dirs = ['..'] + [i for i in raw if os.path.isdir(os.path.join(path,i))]
            files = [i for i in raw if not os.path.isdir(os.path.join(path,i))]
            return dirs + files
        except:
            return ['..']

    def get_actions(name, is_dir):
        if name == '..': return []
        if is_dir:
            return ['Открыть', 'Копировать', 'Переименовать', 'Удалить']
        ext = name.split('.')[-1].lower() if '.' in name else ''
        actions = []
        if ext in ('py','sh'):
            actions.append('Запустить')
        actions += ['Открыть в nano', 'Открыть как...', 'Копировать', 'Вырезать', 'Переименовать', 'Удалить']
        return actions

    items = get_items(current)

    while True:
        screen.fill(BLACK)

        # Header
        pygame.draw.rect(screen, (15,15,15), (0,0,SCREEN_W,26))
        pygame.draw.line(screen, WHITE, (0,26), (SCREEN_W,26), 1)
        path_short = ('..'+current[-38:]) if len(current)>40 else current
        screen.blit(font_sm.render(path_short, True, WHITE), (6,6))
        if clipboard:
            cb = font_xs.render('['+clipboard_op.upper()+': '+os.path.basename(clipboard)+']', True, (100,200,100))
            screen.blit(cb, (SCREEN_W-cb.get_width()-4, 8))

        # File list
        for i, name in enumerate(items[scroll:scroll+max_v]):
            idx = i+scroll
            y = 30+i*22
            full = os.path.join(current, name)
            is_dir = name == '..' or os.path.isdir(full)
            icon, col = get_icon(name, is_dir)

            if idx == selected and not show_action_menu:
                pygame.draw.rect(screen, (35,35,35), (0,y,SCREEN_W,21))
                pygame.draw.rect(screen, WHITE, (0,y,SCREEN_W,21), 1)
                text_col = WHITE
            else:
                text_col = (180,180,180)

            indent = 4 if is_dir else 20
            screen.blit(font_xs.render(icon, True, col if idx!=selected or show_action_menu else WHITE), (indent,y+5))

            if is_dir and name != '..':
                screen.blit(font_sm.render('▶', True, text_col), (indent+30,y+3))
                screen.blit(font_sm.render(name[:36], True, text_col), (indent+44,y+3))
            elif name == '..':
                screen.blit(font_sm.render('.. (назад)', True, text_col), (indent+30,y+3))
            else:
                screen.blit(font_sm.render(name[:38], True, text_col), (indent+30,y+3))
                try:
                    sz = os.path.getsize(full)
                    ss = '{:.0f}K'.format(sz/1024) if sz>1024 else '{}B'.format(sz)
                    screen.blit(font_xs.render(ss, True, (70,70,70)), (SCREEN_W-36,y+6))
                except: pass

        # Bottom
        pygame.draw.line(screen, (40,40,40), (0,SCREEN_H-18), (SCREEN_W,SCREEN_H-18), 1)
        screen.blit(font_xs.render('ENTER=действия  N=новый файл  D=новая папка  V=вставить  ESC=назад', True, (60,60,60)), (4,SCREEN_H-13))

        if msg_timer > 0:
            msg_timer -= 1
            ms = font_sm.render(msg, True, (100,255,100))
            screen.blit(ms, ((SCREEN_W-ms.get_width())//2, SCREEN_H-36))

        # Action menu
        if show_action_menu:
            name = items[selected]
            full = os.path.join(current, name) if name != '..' else None
            is_dir = name == '..' or (full and os.path.isdir(full))
            actions = get_actions(name, is_dir)

            if actions:
                pw = 200
                ph = len(actions)*26+8
                px = min(80, SCREEN_W-pw-4)
                py_m = min(selected*22+30-scroll*22, SCREEN_H-ph-20)
                py_m = max(py_m, 30)
                pygame.draw.rect(screen, (20,20,20), (px,py_m,pw,ph))
                pygame.draw.rect(screen, WHITE, (px,py_m,pw,ph), 1)
                for ai, aname in enumerate(actions):
                    ay = py_m+4+ai*26
                    if ai == action_sel:
                        pygame.draw.rect(screen, (50,50,50), (px+2,ay,pw-4,24))
                        pygame.draw.rect(screen, WHITE, (px+2,ay,pw-4,24), 1)
                    screen.blit(font_sm.render(aname, True, WHITE if ai==action_sel else (160,160,160)), (px+8,ay+4))

        pygame.display.flip()
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

            if event.type == pygame.KEYDOWN:

                if show_action_menu:
                    name = items[selected]
                    full = os.path.join(current, name) if name != '..' else None
                    is_dir = name == '..' or (full and os.path.isdir(full))
                    actions = get_actions(name, is_dir)

                    if event.key == pygame.K_ESCAPE:
                        show_action_menu = False
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        action_sel = (action_sel+1) % len(actions)
                    elif event.key in (pygame.K_UP, pygame.K_w):
                        action_sel = (action_sel-1) % len(actions)
                    elif event.key == pygame.K_RETURN:
                        act = actions[action_sel]
                        show_action_menu = False

                        if act == 'Открыть':
                            if is_dir and full:
                                current = full
                                items = get_items(current)
                                selected = 0; scroll = 0
                        elif act == 'Запустить':
                            ext = name.split('.')[-1].lower()
                            if ext == 'py':
                                open('/tmp/whoos_editor', 'w').write('python3 '+full)
                            else:
                                open('/tmp/whoos_editor', 'w').write('bash '+full)
                            import pygame as pg; pg.quit()
                            import sys; sys.exit()
                        elif act == 'Открыть в nano':
                            from core.editor import open_in_editor
                            open_in_editor(full)
                        elif act == 'Открыть как...':
                            show_open_as(screen, clock, font, font_sm, full)
                        elif act == 'Копировать':
                            clipboard = full; clipboard_op = 'copy'
                            msg = 'Скопировано'; msg_timer = 60
                        elif act == 'Вырезать':
                            clipboard = full; clipboard_op = 'cut'
                            msg = 'Вырезано'; msg_timer = 60
                        elif act == 'Переименовать':
                            new_name = input_text(screen, clock, font, font_sm, 'Новое имя:', name)
                            if new_name:
                                try:
                                    os.rename(full, os.path.join(current, new_name))
                                    items = get_items(current)
                                    msg = 'Переименовано'; msg_timer = 60
                                except Exception as e:
                                    msg = 'Ошибка: '+str(e)[:30]; msg_timer = 90
                        elif act == 'Удалить':
                            try:
                                shutil.rmtree(full) if os.path.isdir(full) else os.remove(full)
                                items = get_items(current)
                                selected = max(0, selected-1)
                                msg = 'Удалено'; msg_timer = 60
                            except Exception as e:
                                msg = 'Ошибка: '+str(e)[:30]; msg_timer = 90
                    continue

                # Normal nav
                if event.key == pygame.K_ESCAPE:
                    if current != '/home/who':
                        current = os.path.dirname(current)
                        items = get_items(current)
                        selected = 0; scroll = 0
                    else:
                        return
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    selected = min(selected+1, len(items)-1)
                    if selected >= scroll+max_v: scroll += 1
                elif event.key in (pygame.K_UP, pygame.K_w):
                    selected = max(selected-1, 0)
                    if selected < scroll: scroll -= 1
                elif event.key == pygame.K_RETURN:
                    name = items[selected]
                    if name == '..':
                        current = os.path.dirname(current)
                        items = get_items(current)
                        selected = 0; scroll = 0
                    else:
                        full = os.path.join(current, name)
                        if os.path.isdir(full):
                            current = full
                            items = get_items(current)
                            selected = 0; scroll = 0
                        else:
                            show_action_menu = True
                            action_sel = 0
                elif event.key == pygame.K_TAB:
                    if items[selected] != '..':
                        show_action_menu = True
                        action_sel = 0
                elif event.key == pygame.K_n:
                    # Новый файл
                    # Найти свободное имя
                    counter = 1
                    base = 'new_file.txt'
                    while os.path.exists(os.path.join(current, base)):
                        base = 'new_file({}).txt'.format(counter)
                        counter += 1
                    new_name = input_text(screen, clock, font, font_sm, 'Имя файла:', base)
                    if new_name:
                        try:
                            open(os.path.join(current, new_name), 'w').close()
                            items = get_items(current)
                            msg = 'Создан: '+new_name; msg_timer = 60
                        except Exception as e:
                            msg = 'Ошибка: '+str(e)[:30]; msg_timer = 90
                elif event.key == pygame.K_d:
                    # Новая папка
                    counter = 1
                    base = 'Новая папка'
                    while os.path.exists(os.path.join(current, base)):
                        base = 'Новая папка({})'.format(counter)
                        counter += 1
                    new_name = input_text(screen, clock, font, font_sm, 'Имя папки:', base)
                    if new_name:
                        try:
                            os.makedirs(os.path.join(current, new_name))
                            items = get_items(current)
                            msg = 'Создана: '+new_name; msg_timer = 60
                        except Exception as e:
                            msg = 'Ошибка: '+str(e)[:30]; msg_timer = 90
                elif event.key == pygame.K_v:
                    if clipboard:
                        dst = os.path.join(current, os.path.basename(clipboard))
                        try:
                            if os.path.isdir(clipboard):
                                shutil.copytree(clipboard, dst)
                            else:
                                shutil.copy2(clipboard, dst)
                            if clipboard_op == 'cut':
                                shutil.rmtree(clipboard) if os.path.isdir(clipboard) else os.remove(clipboard)
                                clipboard = None
                            items = get_items(current)
                            msg = 'Вставлено'; msg_timer = 60
                        except Exception as e:
                            msg = 'Ошибка: '+str(e)[:30]; msg_timer = 90


def show_open_as(screen, clock, font, font_sm, filepath):
    options = [
        ('nano',    None),
        ('python3', None),
        ('less',    None),
        ('hexdump', None),
    ]
    sel = 0
    font_xs = pygame.font.SysFont('monospace', 9)
    while True:
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0,0,0,180))
        screen.blit(overlay, (0,0))
        pw, ph = 200, len(options)*26+30
        px, py = (SCREEN_W-pw)//2, (SCREEN_H-ph)//2
        pygame.draw.rect(screen, (20,20,20), (px,py,pw,ph))
        pygame.draw.rect(screen, WHITE, (px,py,pw,ph), 1)
        screen.blit(font_sm.render('Открыть как:', True, WHITE), (px+8,py+6))
        for i,(name,_) in enumerate(options):
            ay = py+26+i*26
            if i == sel:
                pygame.draw.rect(screen, (50,50,50), (px+2,ay,pw-4,24))
                pygame.draw.rect(screen, WHITE, (px+2,ay,pw-4,24), 1)
            screen.blit(font_sm.render(name, True, WHITE if i==sel else (140,140,140)), (px+10,ay+4))
        pygame.display.flip()
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    sel = (sel+1) % len(options)
                elif event.key in (pygame.K_UP, pygame.K_w):
                    sel = (sel-1) % len(options)
                elif event.key == pygame.K_RETURN:
                    # Открываем через флаг — как nano
                    prog = options[sel][0]
                    with open('/tmp/whoos_editor', 'w') as f:
                        f.write(filepath + '\n' + prog)
                    import pygame as pg; pg.quit()
                    import sys; sys.exit()
