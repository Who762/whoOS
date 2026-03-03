#!/bin/bash
xset s off
xset -dpms
xset s noblank
unclutter -idle 0 &
cd /home/who/whoOS
python3 main.py
