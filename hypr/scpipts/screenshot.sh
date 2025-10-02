#!/bin/bash

screenshots_dir="$HOME/Pictures/Screenshots"
mkdir -p "$screenshots_dir"

case $1 in
"area")
  filename="$screenshots_dir/$(date +%Y%m%d_%H%M%S).png"
  grim -g "$(slurp)" "$filename"
  if [ -f "$filename" ]; then
    wl-copy <"$filename"
    notify-send "Скриншот" "Область сохранена и скопирована в буфер" -i "$filename"
  fi
  ;;
"screen")
  filename="$screenshots_dir/$(date +%Y%m%d_%H%M%S).png"
  grim "$filename"
  wl-copy <"$filename"
  notify-send "Скриншот" "Весь экран сохранен и скопирован" -i "$filename"
  ;;
"window")
  filename="$screenshots_dir/$(date +%Y%m%d_%H%M%S).png"
  grim -g "$(hyprctl activewindow -j | jq -r '"\(.at[0]),\(.at[1]) \(.size[0])x\(.size[1])"')" "$filename"
  wl-copy <"$filename"
  notify-send "Скриншот" "Активное окно сохранено и скопировано" -i "$filename"
  ;;
"edit")
  temp_file=$(mktemp).png
  grim -g "$(slurp)" "$temp_file"
  swappy -f "$temp_file" -o "$screenshots_dir/$(date +%Y%m%d_%H%M%S).png"
  rm "$temp_file"
  ;;
esac
