import pygame
import subprocess
from PIL import Image, ImageDraw, ImageFont
from assets.version import *
from core.clock_settings import save as save_clock
from datetime import datetime

OLED_W = 128
OLED_H = 64
SCALE = 2
PREVIEW_W = OLED_W * SCALE
PREVIEW_H = OLED_H * SCALE

FB = '/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf'
FR = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'

settings = {
    'show_seconds': True,
    'show_ms': True,
    'show_date': True,
    'show_cpu': True,
    'show_dht': True,
}

def render_oled_preview(dht_temp=None, dht_hum=None):
    img = Image.new('1', (OLED_W, OLED_H))
    draw = ImageDraw.Draw(img)
    now = datetime.now()

    try:
        font_big = ImageFont.truetype(FB, 16)
        font_sm = ImageFont.truetype(FR, 8)
    except Exception:
        font_big = ImageFont.load_default()
        font_sm = font_big

    if settings['show_seconds']:
        time_str = now.strftime('%H:%M:%S')
    else:
        time_str = now.strftime('%H:%M')

    draw.text((0, 0), '3.3V', font=font_sm, fill=255)
    draw.text((100, 0), 'BAT%', font=font_sm, fill=255)

    try:
        tw = draw.textlength(time_str, font=font_big)
    except Exception:
        tw = 80
    draw.text(((OLED_W - tw) // 2, 10), time_str, font=font_big, fill=255)

    if settings['show_ms']:
        ms_str = '.{:03d}'.format(now.microsecond // 1000)
        try:
            mw = draw.textlength(ms_str, font=font_sm)
        except Exception:
            mw = 20
        draw.text(((OLED_W - mw) // 2, 28), ms_str, font=font_sm, fill=255)

    if settings['show_cpu']:
        try:
            r = subprocess.run(['vcgencmd', 'measure_temp'], capture_output=True, text=True)
            temp = r.stdout.replace('temp=', '').replace("'C\n", '')
            draw.text((0, 38), '~{}C'.format(int(float(temp))), font=font_sm, fill=255)
        except Exception:
            draw.text((0, 38), '!CPU', font=font_sm, fill=255)

    if settings['show_dht'] and dht_temp is not None:
        dht_str = '{}C {}%'.format(int(dht_temp), int(dht_hum))
        try:
            dw = draw.textlength(dht_str, font=font_sm)
        except Exception:
            dw = 40
        draw.text((OLED_W - dw - 1, 38), dht_str, font=font_sm, fill=255)
    elif settings['show_dht']:
        draw.text((80, 38), '!DHT', font=font_sm, fill=255)

    if settings['show_date']:
        draw.text((0, 50), now.strftime('%d.%m.%Y'), font=font_sm, fill=255)

    return img

def pil_to_surface(img):
    img_rgb = img.convert('RGB')
    data = img_rgb.tobytes()
    surf = pygame.image.fromstring(data, img_rgb.size, 'RGB')
    return pygame.transform.scale(surf, (PREVIEW_W, PREVIEW_H))

def run_clock(screen, clock):
    font = pygame.font.SysFont('monospace', 14, bold=True)
    font_sm = pygame.font.SysFont('monospace', 12)
    font_tiny = pygame.font.SysFont('monospace', 11)

    selected = 0
    options = list(settings.keys())
    option_names = {
        'show_seconds': 'Секунды',
        'show_ms': 'Миллисекунды',
        'show_date': 'Дата',
        'show_cpu': 'Темп CPU',
        'show_dht': 'DHT датчик',
    }

    divider = SCREEN_W // 2

    while True:
        screen.fill(BLACK)

        pygame.draw.line(screen, (60,60,60), (divider, 0), (divider, SCREEN_H), 1)

        left_title = font_sm.render('PREVIEW', True, (100,100,100))
        screen.blit(left_title, (divider//2 - left_title.get_width()//2, 6))

        try:
            oled_img = render_oled_preview()
            oled_surf = pil_to_surface(oled_img)
            ox = divider//2 - PREVIEW_W//2
            oy = SCREEN_H//2 - PREVIEW_H//2
            pygame.draw.rect(screen, (30,30,30), (ox-4, oy-4, PREVIEW_W+8, PREVIEW_H+8))
            pygame.draw.rect(screen, (80,80,80), (ox-4, oy-4, PREVIEW_W+8, PREVIEW_H+8), 1)
            screen.blit(oled_surf, (ox, oy))
        except Exception as e:
            err = font_sm.render('Не обнаружен', True, (150,50,50))
            screen.blit(err, (divider//2 - err.get_width()//2, SCREEN_H//2))

        right_title = font_sm.render('НАСТРОЙКИ', True, (100,100,100))
        screen.blit(right_title, (divider + (divider//2 - right_title.get_width()//2), 6))

        for i, key in enumerate(options):
            y = 30 + i * 30
            rx = divider + 8
            val = settings[key]

            if i == selected:
                pygame.draw.rect(screen, (30,30,30), (divider+4, y, divider-8, 26))
                pygame.draw.rect(screen, WHITE, (divider+4, y, divider-8, 26), 1)
                col = WHITE
            else:
                col = (120,120,120)

            name_t = font_tiny.render(option_names[key], True, col)
            screen.blit(name_t, (rx+4, y+6))

            tog_x = SCREEN_W - 36
            if val:
                pygame.draw.rect(screen, (50,200,50), (tog_x, y+7, 28, 12), 0)
                pygame.draw.circle(screen, WHITE, (tog_x+20, y+13), 6)
                on_t = font_tiny.render('ON', True, BLACK)
                screen.blit(on_t, (tog_x+2, y+5))
            else:
                pygame.draw.rect(screen, (60,60,60), (tog_x, y+7, 28, 12), 0)
                pygame.draw.circle(screen, (120,120,120), (tog_x+8, y+13), 6)
                off_t = font_tiny.render('OFF', True, (100,100,100))
                screen.blit(off_t, (tog_x+10, y+5))

        hint = font_tiny.render('[ENTER] toggle  [ESC] back', True, (60,60,60))
        screen.blit(hint, (divider + 8, SCREEN_H-18))

        pygame.display.flip()
        clock.tick(FPS)

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
                    save_clock(settings)
