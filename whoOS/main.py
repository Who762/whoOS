import pygame
import subprocess
import os
import sys
from assets.version import *
from ui.boot import run_boot
from ui.login import run_login
from ui.menu import run_menu
from ui.files import run_files
from ui.settings import run_settings
from ui.terminal import run_terminal
from ui.clock import run_clock
from ui.programs import run_programs
from core.system import shutdown, reboot

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.FULLSCREEN)
    pygame.display.set_caption(OS_NAME)
    clock = pygame.time.Clock()

    if not run_boot(screen, clock):
        pygame.quit()
        sys.exit()

    if not run_login(screen, clock):
        pygame.quit()
        sys.exit()

    while True:
        action = run_menu(screen, clock)

        if action == 'terminal':
            run_terminal()
            pygame.init()
            screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.FULLSCREEN)
            clock = pygame.time.Clock()
        elif action == 'files':
            run_files(screen, clock)
        elif action == 'settings':
            run_settings(screen, clock)
        elif action == 'clock':
            run_clock(screen, clock)
        elif action == 'programs':
            run_programs(screen, clock)
        elif action == 'network':
            pass
        elif action == 'system':
            pass
        elif action == 'editor':
            pass
        elif action == 'reboot':
            pygame.quit()
            reboot()
            sys.exit()
        elif action == 'shutdown':
            pygame.quit()
            shutdown()
            sys.exit()
        elif action == 'quit':
            pygame.quit()
            sys.exit()

if __name__ == '__main__':
    main()
