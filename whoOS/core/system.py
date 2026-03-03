import subprocess
import os

def shutdown():
    subprocess.run(['sudo', 'shutdown', '-h', 'now'])

def reboot():
    subprocess.run(['sudo', 'reboot'])

def get_uptime():
    try:
        with open('/proc/uptime', 'r') as f:
            seconds = float(f.read().split()[0])
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        return '{}h {}m'.format(h, m)
    except Exception:
        return 'N/A'

def get_cpu_temp():
    try:
        r = subprocess.run(['vcgencmd', 'measure_temp'], capture_output=True, text=True)
        return r.stdout.strip().replace('temp=', '').replace("'C", '')
    except Exception:
        return 'N/A'

def run_command(cmd):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return r.stdout + r.stderr
    except Exception as e:
        return str(e)
