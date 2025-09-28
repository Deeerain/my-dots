#!/bin/bash

style=~/.config/wofi/style.css

# Только иконки (Nerd Fonts)
options="\n\n\n"

chosen=$(echo -e "$options" | wofi --dmenu -j -b -L 1 -w 4 -s "$style")

case "$chosen" in
"") systemctl poweroff ;;
"") systemctl reboot ;;
"") systemctl suspend ;;
"") hyprctl dispatch exit ;;
esac
