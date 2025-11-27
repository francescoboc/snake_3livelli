# Pacchetti da installare (`sudo apt install`)
    python3-tqdm
    unclutter
    xdotool

# Impostare ambiente grafico `X11`
    sudo raspi-config > advanced options > switch from Wayland to X11 > reboot

# Impostare l'autostart
    mkdir ~/.config/autostart
    cp ~/snake_3livelli/StartSnake.desktop ~/.config/autostart
    vi ~/.config/autostart/StartSnake.desktop > edit the level of difficulty
