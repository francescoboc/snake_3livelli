#!/usr/bin/env bash

# ruota lo schermo
xrandr --output HDMI-1 --rotate right
xrandr --output HDMI-2 --rotate right

# nascondi cursore
unclutter -idle 0 &

# chiudi lxpanel (la taskbar in alto)
pkill lxpanel

# cd in questa cartella
cd "$(dirname "$0")"

# lancia lo script python
# imposta il livello di difficoltà a secondo dall'argomento passato allo script
LEVEL=${1:-medium}   # livello di default = medium
python "main_screen.py" --level "$LEVEL"

# # riporta lo schermo in orizzontale
# xrandr --output HDMI-1 --rotate normal

# rilancia lxpanel
# lxpanel --profile LXDE-pi &
lxpanel --profile LXDE-pi >/dev/null 2>&1 &

# aspetta per user input
echo ""
echo "Programma terminato, premi invio per continuare"
read
