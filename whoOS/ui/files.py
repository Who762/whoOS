import pygame
import os
import shutil
from assets.version import *

clipboard = None

def get_icon(name, is_dir):
    if is_dir:
        return 'dir'
    ext = name.split('.')[-1].lower() if '.' in name else ''
    if ext in ('py', 'sh'):
        return 'script'
    if ext in ('txt', 'md', 'log'):
        return 'text'
    if ext in ('jpg', 'jpeg', 'png', 'gif', 'bmp'):
        return 'image'
    if ext in ('mp3', 'wav', 'ogg'):
        return 'audio'
    return 'file'

def draw_icon(screen, kind, x, y, col):
    if kind == 'dir':
        pygame.draw.rect(screen, col, (x, y+4, 16, 11), 1)
        pygame.draw.polygon(screen, col, [(x,y+4),(x,y+2),(x+7,y+2),(x+9,y+4)])
    elif kind == 'script':
        pygame.draw.rect(screen, col, (x+2, y+1, 12, 14), 1)
        font = pygame.font.SysFont('monospace', 8)
        t = font.render('py', True, col)
        screen.blit(t, (x+3, y+4))
    elif kind == 'text':
        pygame.draw.rect(screen, col, (x+2, y+1, 12, 14), 1)
        for i in range(3):
            pygame.draw.line(screen, col, (x+4, y+5+i*4), (x+12, y+5+i*4), 1)
    elif kind == 'image':
        pygame.draw.rect(screen, col, (x+2, y+1, 12, 14), 1)
        pygame.draw.circle(screen, col, (x+7, y+6), 2, 1)
        pygame.draw.lines(screen, col, False, [(x+2,y+12),(x+6,y+8),(x+9,y+10),(x+14,y+5)], 1)
    elif kind == 'audio':
        pygame.draw.rect(screen, col, (x+2, y+1, 12, 14), 1)
        pygame.draw.arc(screen, col, (x+4, y+4, 8, 8), 0, 3.14, 1)
        pygame.draw.line(screen, col, (x+8, y+8), (x+8, y+13), 1)
    else:
        pygame.draw.rect(screen, col, (x+2, y+1, 12, 14), 1)

def draw_popup(screen, clock, font, filepath, is_dir):
    global clipboard
    items = ['Открыть', 'Скопировать', 'Вставить', 'Переименовать', 'Удалить', 'Отмена']
    if is_dir:
        items = ['Открыть', 'Скопировать', 'Вставить', 'Переименовать', 'Удалить', 'Отмена']
    selected = 0
    w, h = 200, len(items) * 30 + 16
    x = (SCREEN_W - w) // 2
    y = (SCREEN_H - h) // 2

    while True:
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))
        pygame.draw.rect(screen, (30, 30, 30), (x, y, w, h))
        pygame.draw.rect(screen, WHITE, (x, y, w, h), 1)
        name = os.path.basename(filepath)
        title = font.render(name[:22], True, WHITE)
        screen.blit(title, (x + 8, y + 4))
        pygame.draw.line(screen, WHITE, (x, y+20), (x+w, y+20), 1)

        for i, item in enumerate(items):
            iy = y + 24 + i * 30
            if i == selected:
                pygame.draw.rect(screen, WHITE, (x+4, iy, w-8, 26))
                col = BLACK
            else:
                col = WHITE
            text = font.render(item, True, col)
            screen.blit(text, (x+10, iy+5))

        pygame.display.flip()
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_DOWN, pygame.K_s):
                    selected = (selected + 1) % len(items)
                elif event.key in (pygame.K_UP, pygame.K_w):
                    selected = (selected - 1) % len(items)
                elif event.key == pygame.K_ESCAPE:
                    return None
                elif event.key == pygame.K_RETURN:
                    action = items[selected]
                    if action == 'Отмена':
                        return None
                    elif action == 'Скопировать':
                        clipboard = filepath
                        return None
                    elif action == 'Вставить':
                        if clipboard:
                            try:
                                dest = os.path.join(os.path.dirname(filepath), os.path.basename(clipboard))
                                if os.path.isdir(clipboard):
                                    shutil.copytree(clipboard, dest)
                                else:
                                    shutil.copy2(clipboard, dest)
                            except Exception as e:
                                print(str(e))
                        return None
                    elif action == 'Удалить':
                        return draw_delete_confirm(screen, clock, font, filepath)
                    elif action == 'Переименовать':
                        return draw_rename(screen, clock, font, filepath)
                    else:
                        return action

def draw_delete_confirm(screen, clock, font, filepath):
    name = os.path.basename(filepath)
    frames = 40
    for f in range(frames):
        screen.fill(BLACK)
        cx, cy = SCREEN_W // 2, SCREEN_H // 2

        progress = f / frames
        bin_y = int(cy - 20 + 10 * progress)
        pygame.draw.rect(screen, WHITE, (cx-20, bin_y, 40, 35), 2)
        pygame.draw.rect(screen, WHITE, (cx-22, bin_y-6, 44, 6), 1)
        pygame.draw.line(screen, WHITE, (cx-8, bin_y-6), (cx-8, bin_y-10), 2)
        pygame.draw.line(screen, WHITE, (cx+8, bin_y-6), (cx+8, bin_y-10), 2)
        for i in range(3):
            pygame.draw.line(screen, WHITE, (cx-10+i*10, bin_y+5), (cx-10+i*10, bin_y+28), 1)

        if f > 10:
            paper_y = int(cy - 30 - 20 * (1 - (f-10)/30))
            paper_x = cx - 8
            pygame.draw.rect(screen, WHITE, (paper_x, paper_y, 16, 20))
            pygame.draw.line(screen, BLACK, (paper_x+3, paper_y+5), (paper_x+13, paper_y+5), 1)
            pygame.draw.line(screen, BLACK, (paper_x+3, paper_y+9), (paper_x+13, paper_y+9), 1)
            pygame.draw.line(screen, BLACK, (paper_x+3, paper_y+13), (paper_x+10, paper_y+13), 1)

        if f > 30:
            msg = font.render('УДАЛЕНО', True, WHITE)
            screen.blit(msg, (cx - msg.get_width()//2, cy+30))

        pygame.display.flip()
        clock.tick(30)

    try:
        if os.path.isdir(filepath):
            shutil.rmtree(filepath)
        else:
            os.remove(filepath)
    except Exception as e:
        print(str(e))

    pygame.time.wait(500)
    return 'deleted'

def draw_rename(screen, clock, font, filepath):
    name = os.path.basename(filepath)
    new_name = name
    cursor_tick = 0

    while True:
        screen.fill(BLACK)
        w, h = 280, 80
        x = (SCREEN_W - w) // 2
        y = (SCREEN_H - h) // 2
        pygame.draw.rect(screen, (30,30,30), (x, y, w, h))
        pygame.draw.rect(screen, WHITE, (x, y, w, h), 1)
        title = font.render('Переименовать:', True, WHITE)
        screen.blit(title, (x+8, y+8))
        cursor_tick += 1
        cursor = '_' if cursor_tick % 40 < 20 else ''
        inp = font.render(new_name + cursor, True, WHITE)
        pygame.draw.rect(screen, (50,50,50), (x+8, y+32, w-16, 24))
        screen.blit(inp, (x+12, y+36))
        hint = font.render('ENTER=ok  ESC=отмена', True, (100,100,100))
        screen.blit(hint, (x+8, y+60))
        pygame.display.flip()
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
                elif event.key == pygame.K_RETURN:
                    try:
                        new_path = os.path.join(os.path.dirname(filepath), new_name)
                        os.rename(filepath, new_path)
                    except Exception as e:
                        print(str(e))
                    return 'renamed'
                elif event.key == pygame.K_BACKSPACE:
                    new_name = new_name[:-1]
                elif event.unicode.isprintable():
                    new_name += event.unicode

def run_files(screen, clock):
    font = pygame.font.SysFont('monospace', 14)
    font_title = pygame.font.SysFont('monospace', 14, bold=True)

    current_path = '/home/who'
    selected = 0
    scroll = 0
    indent = 0
    max_visible = (SCREEN_H - 50) // 22

    while True:
        screen.fill(BLACK)

        try:
            raw = sorted(os.listdir(current_path))
            dirs = [i for i in raw if os.path.isdir(os.path.join(current_path, i))]
            files = [i for i in raw if not os.path.isdir(os.path.join(current_path, i))]
            items = ['..'] + dirs + files
        except Exception:
            items = ['..']

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    selected = min(selected + 1, len(items) - 1)
                    if selected >= scroll + max_visible:
                        scroll += 1
                elif event.key in (pygame.K_UP, pygame.K_w):
                    selected = max(selected - 1, 0)
                    if selected < scroll:
                        scroll -= 1
                elif event.key == pygame.K_RETURN:
                    name = items[selected]
                    if name == '..':
                        current_path = os.path.dirname(current_path)
                        selected = 0
                        scroll = 0
                    else:
                        full = os.path.join(current_path, name)
                        if os.path.isdir(full):
                            current_path = full
                            selected = 0
                            scroll = 0
                        else:
                            result = draw_popup(screen, clock, font, full, False)
                elif event.key == pygame.K_SPACE:
                    name = items[selected]
                    if name != '..':
                        full = os.path.join(current_path, name)
                        is_dir = os.path.isdir(full)
                        if is_dir:
                            result = draw_popup(screen, clock, font, full, True)

        header = pygame.Rect(0, 0, SCREEN_W, 30)
        pygame.draw.rect(screen, WHITE, header)
        path_text = current_path[-40:] if len(current_path) > 40 else current_path
        title = font_title.render(path_text, True, BLACK)
        screen.blit(title, (5, 8))

        for i, name in enumerate(items[scroll:scroll + max_visible]):
            idx = i + scroll
            y = 35 + i * 22
            full = os.path.join(current_path, name)
            is_dir = name == '..' or os.path.isdir(full)
            kind = get_icon(name, is_dir)

            level_indent = 0 if name == '..' else (16 if is_dir else 32)

            if idx == selected:
                pygame.draw.rect(screen, WHITE, (0, y, SCREEN_W, 22))
                col = BLACK
            else:
                col = WHITE

            if name != '..':
                draw_icon(screen, kind, level_indent + 4, y + 2, col)

            prefix = '../' if name == '..' else ''
            display = prefix + name if name == '..' else name
            text = font.render(display[:42], True, col)
            screen.blit(text, (level_indent + 24, y + 3))

        pygame.display.flip()
        clock.tick(FPS)
