--$polkit = /usr/lib/polkit-gnome/polkit-gnome-authentication-agent-1
--$player = spotify

hl.on("hyprland.start", function ()
	hl.exec_cmd("awww-daemon")
	hl.exec_cmd("mako")
	hl.exec_cmd("waybar")
	hl.exec_cmd("kitty")
	hl.exec_cmd("firefox")
	hl.exec_cmd("Telegram")
end)

--exec = mako
--exec-once = waybar & hyprpaper & awww-daemon & $polkit
--exec-once = [workspace 1 silent] kitty
--exec-once = [workspace 2 silent] firefox
--exec-once = [workspace 3 silent] $player
--exec-once = [workspace 3 silent] Telegram
