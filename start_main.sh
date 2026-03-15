#!/usr/bin/env bash

 # ruota lo schermo
xrandr --output HDMI-1 --rotate left
xrandr --output HDMI-2 --rotate left

# nascondi cursore
unclutter -idle 0 &

# cd in questa cartella
cd "$(dirname "$0")"

for i in {1..10}; do
    echo "Controllo connessione internet ($i/10)..."
    if ping -c 1 -W 1 github.com >/dev/null 2>&1; then
        echo "Controllo aggiornamenti..."
        git pull
        break
    fi
    sleep 3
done

# lancia lo script python
# imposta il livello di difficoltà a secondo dall'argomento passato allo script
LEVEL=${1:-medium}   # livello di default = medium
python "main_screen.py" --level "$LEVEL"

# # riporta lo schermo in orizzontale
# xrandr --output HDMI-1 --rotate normal

# aspetta per user input
echo ""
echo "Programma terminato, premi invio per continuare."
read
