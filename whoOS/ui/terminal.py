import os
import subprocess

def run_terminal():
    subprocess.Popen(['sudo', 'chvt', '2'])
    subprocess.run(['sudo', '-u', 'who', 'bash', '-c', 
        'echo "=== who?Os Terminal ===" && echo "Type exit to return" && bash; sudo chvt 7'],
        stdin=open('/dev/tty2', 'r'),
        stdout=open('/dev/tty2', 'w'),
        stderr=open('/dev/tty2', 'w'))
