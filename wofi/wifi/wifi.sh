#!/bin/bash

bssid=$(iwctl station wlan0 get-networks |
  sed 's/\x1b\[[0-9;]*m//g' | sed '1,4d' |
  sed "s/>//" |
  sed "s/ \*\*\*\*//" |
  sed 's/[[:blank:]]\+/ /g' |
  sed 's/^ *//;s/ *$//' |
  sed 's/\s\+\S\+$//' |
  sed '/^$/d' |
  wofi --dmenu -l top_right -W 300)

[ -z "$bssid" ] && exit 1

echo "$bssid"

notify-send "📶 WiFi Connected"
