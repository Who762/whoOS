import pygame
import subprocess
from PIL import Image, ImageDraw, ImageFont
from assets.version import *
from core.clock_settings import save as save_clock
from datetime import datetime

OLED_W = 128
OLED_H = 64
PREVIEW_W = OLED_W
PREVIEW_H = OLED_H

FB = '/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf'
FR = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'

settings = {
    'oled_on':      True,
    'show_seconds': True,
    'show_ms':      True,
    'show_date':    True,
    'show_cpu':     True,
    'show_dht':     True,
}

def set_oled_power(on):
    try:
        from core.oled_power import set_power
        set_power(on)
    except:
        pass

def render_oled_preview():
    img = Image.new('1', (OLED_W, OLED_H))
    if not settings['oled_on']:
        return img
    draw = ImageDraw.Draw(img)
    now = datetime.now()
    try:
        font_big = ImageFont.truetype(FB, 16)
        font_sm = ImageFont.truetype(FR, 8)
    except:
        font_big = ImageFont.load_default()
        font_sm = font_big

    time_str = now.strftime('%H:%M:%S') if settings['show_seconds'] else now.strftime('%H:%M')
    draw.text((0,0), '3.3V', font=font_sm, fill=255)
    draw.text((100,0), 'BAT%', font=font_sm, fill=255)
    try:
        tw = draw.textlength(time_str, font=font_big)
    except: tw = 80
    draw.text(((OLED_W-tw)//2,10), time_str, font=font_big, fill=255)

    if settings['show_ms']:
        ms_str = '.{:03d}'.format(now.microsecond//1000)
        try: mw = draw.textlength(ms_str, font=font_sm)
        except: mw = 20
        draw.text(((OLED_W-mw)//2,28), ms_str, font=font_sm, fill=255)

    if settings['show_cpu']:
        try:
            r = subprocess.run(['vcgencmd','measure_temp'], capture_output=True, text=True)
            temp = r.stdout.strip().replace('temp=','').replace("'C",'')
            draw.text((0,38), temp+'C', font=font_sm, fill=255)
        except:
            draw.text((0,38), '-C', font=font_sm, fill=255)

    if settings['show_dht']:
        draw.text((80,38), '!DHT', font=font_sm, fill=255)

    if settings['show_date']:
        draw.text((0,50), now.strftime('%d.%m.%Y'), font=font_sm, fill=255)

    return img

def pil_to_surface(img):
    img_rgb = img.convert('RGB')
    surf = pygame.image.fromstring(img_rgb.tobytes(), img_rgb.size, 'RGB')
    return pygame.transform.scale(surf, (PREVIEW_W, PREVIEW_H))

def draw_monitor_icon(screen, x, y, on, col):
    pygame.draw.rect(screen, col, (x,y+2,16,11), 1)
    pygame.draw.line(screen, col, (x+8,y+13),(x+8,y+16), 1)
    pygame.draw.line(screen, col, (x+5,y+16),(x+11,y+16), 1)
    dot_col = (50,220,50) if on else (180,50,50)
    pygame.draw.circle(screen, dot_col, (x+16,y+2), 3)

def run_clock(screen, clock_obj):
    font = pygame.font.SysFont('monospace', 13, bold=True)
    font_sm = pygame.font.SysFont('monospace', 11)
    font_tiny = pygame.font.SysFont('monospace', 10)

    options = list(settings.keys())
    option_names = {
        'oled_on':      'OLED экран',
        'show_seconds': 'Секунды',
        'show_ms':      'Миллисекунды',
        'show_date':    'Дата',
        'show_cpu':     'Темп CPU',
        'show_dht':     'DHT датчик',
    }

    selected = 0
    prev_area_w = SCREEN_W // 3
    divider = prev_area_w

    while True:
        screen.fill(BLACK)
        pygame.draw.line(screen, (60,60,60), (divider,0),(divider,SCREEN_H), 1)

        lt = font_sm.render('PREVIEW', True, (100,100,100))
        screen.blit(lt, (prev_area_w//2 - lt.get_width()//2, 4))

        try:
            oled_surf = pil_to_surface(render_oled_preview())
            ox = prev_area_w//2 - PREVIEW_W//2
            oy = SCREEN_H//2 - PREVIEW_H//2
            if settings['oled_on']:
                pygame.draw.rect(screen, (30,30,30), (ox-3,oy-3,PREVIEW_W+6,PREVIEW_H+6))
                pygame.draw.rect(screen, (80,80,80), (ox-3,oy-3,PREVIEW_W+6,PREVIEW_H+6), 1)
                screen.blit(oled_surf, (ox,oy))
            else:
                pygame.draw.rect(screen, (10,10,10), (ox-3,oy-3,PREVIEW_W+6,PREVIEW_H+6))
                pygame.draw.rect(screen, (40,40,40), (ox-3,oy-3,PREVIEW_W+6,PREVIEW_H+6), 1)
                off_t = font_sm.render('[ OFF ]', True, (60,60,60))
                screen.blit(off_t, (ox+PREVIEW_W//2-off_t.get_width()//2, oy+PREVIEW_H//2-8))
        except: pass

        rt = font_sm.render('OLED CONFIG', True, (100,100,100))
        screen.blit(rt, (divider+(SCREEN_W-divider)//2 - rt.get_width()//2, 4))

        for i, key in enumerate(options):
            y = 22 + i*24
            rw = SCREEN_W - divider - 8
            val = settings[key]
            is_sel = i == selected

            if key == 'oled_on':
                bg = (30,30,10) if is_sel else (15,15,5)
                border = YELLOW if is_sel else (80,80,20)
            else:
                bg = (30,30,30) if is_sel else (15,15,15)
                border = WHITE if is_sel else (40,40,40)

            pygame.draw.rect(screen, bg, (divider+4,y,rw,22))
            pygame.draw.rect(screen, border, (divider+4,y,rw,22), 1)

            if key == 'oled_on':
                draw_monitor_icon(screen, divider+6, y+2, val, WHITE if is_sel else (120,120,120))
                name_x = divider+28
            else:
                name_x = divider+8

            if key != 'oled_on' and not settings['oled_on']:
                text_col = (55,55,55)
            elif is_sel:
                text_col = WHITE
            else:
                text_col = (120,120,120)

            screen.blit(font_tiny.render(option_names[key], True, text_col), (name_x, y+5))

            tog_x = SCREEN_W-36
            if val:
                tog_col = (50,200,50) if (key=='oled_on' or settings['oled_on']) else (30,80,30)
                pygame.draw.rect(screen, tog_col, (tog_x,y+5,28,12))
                pygame.draw.circle(screen, WHITE, (tog_x+21,y+11), 5)
                screen.blit(font_tiny.render('ON', True, BLACK), (tog_x+2,y+4))
            else:
                pygame.draw.rect(screen, (50,50,50), (tog_x,y+5,28,12))
                pygame.draw.circle(screen, (100,100,100), (tog_x+7,y+11), 5)
                screen.blit(font_tiny.render('OFF', True, (80,80,80)), (tog_x+10,y+4))

        hint = font_tiny.render('ENTER=toggle  ESC=back', True, (50,50,50))
        screen.blit(hint, (divider+8, SCREEN_H-14))

        pygame.display.flip()
        clock_obj.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    selected = (selected+1) % len(options)
                elif event.key in (pygame.K_UP, pygame.K_w):
                    selected = (selected-1) % len(options)
                elif event.key == pygame.K_RETURN:
                    key = options[selected]
                    settings[key] = not settings[key]
                    if key == 'oled_on':
                        set_oled_power(settings[key])
                    save_clock(settings)
