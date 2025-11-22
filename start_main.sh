#!/usr/bin/env bash

# nascondi cursore
unclutter -idle 0 &

# ruota lo schermo
xrandr --output HDMI-1 --rotate left

# chiudi lxpanel (la taskbar in alto)
# (commentato per adesso perchè lo nascondiamo e lo mettiamo a 0 pixel di spessore)
# pkill lxpanel

# cd in questa cartella
cd "$(dirname "$0")"

# lancia lo script python
python "main_screen.py"

xrandr --output HDMI-1 --rotate normal

# aspetta per user input
echo ""
echo "Programma terminato, premi invio per continuare"
read
