import os
import sys
import pygame

def open_in_editor(filepath, return_path=None):
    with open('/tmp/whoos_editor', 'w') as f:
        f.write(filepath + '\n' + 'nano')
    if return_path:
        with open('/tmp/whoos_return_path', 'w') as f:
            f.write(return_path)
    pygame.quit()
    sys.exit()
