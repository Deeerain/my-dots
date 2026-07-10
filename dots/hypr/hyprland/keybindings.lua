local terminal = "kitty"
local fileManager = "dolphin"
local menu = "~/.config/wofi/launchers/launcher.sh"
local mainMod = "SUPER"

hl.bind(mainMod .. " + Q", hl.dsp.exec_cmd(terminal))
hl.bind(mainMod .. " + SHIFT + Q", function() hl.dsp.exec_cmd(terminal, { float = true }) end)
hl.bind(mainMod .. " + C", hl.dsp.window.close())
hl.bind(mainMod .. " + M", hl.dsp.exit())
hl.bind(mainMod .. " + E", hl.dsp.exec_cmd(fileManager))
hl.bind(mainMod .. " + V", hl.dsp.window.float({ action = "toggle" }))
hl.bind(mainMod .. " + R", hl.dsp.exec_cmd(menu))
hl.bind(mainMod .. " + P", hl.dsp.window.pseudo({ action = "toggle" }))


hl.bind(mainMod .. " + L", hl.dsp.exec_cmd("hyprlock"))
hl.bind("ALT + F4", hl.dsp.exec_cmd("~/.config/wofi/powermenu/powermenu.sh"))
hl.bind(mainMod .. " + F", hl.dsp.window.fullscreen({ mode = "fullscreen", action = "toggle" }))


hl.bind(mainMod .. " + left", hl.dsp.window.move({ direction = "l" }))
hl.bind(mainMod .. " + right", hl.dsp.window.move({ direction = "r" }))
hl.bind(mainMod .. " + up", hl.dsp.window.move({ direction = "u" }))
hl.bind(mainMod .. " + down", hl.dsp.window.move({ direction = "d" }))


for i = 1, 10 do
    local key = tostring(i % 10)
    local ws = tostring(i)
    
    hl.bind(mainMod .. " + " .. key, hl.dsp.focus({ workspace = ws}))
    hl.bind(mainMod .. " + SHIFT + " .. key, hl.dsp.window.move({ workspace = ws }))
end


hl.bind(mainMod .. " + S", hl.dsp.workspace.toggle_special("magic"))
hl.bind(mainMod .. " + SHIFT + S", hl.dsp.window.move({ workspace = "special:magic" }))

hl.bind(mainMod .. " + mouse_down", hl.dsp.focus({workspace = "e+1" }))
hl.bind(mainMod .. " + mouse_up", hl.dsp.focus({ workspace = "e-1" }))

hl.bind(mainMod .. " + mouse:272", hl.dsp.window.drag(), { mouse = true })
hl.bind(mainMod .. " + mouse:273", hl.dsp.window.resize(), { mouse = true })


local mediaOptions = { locked = true, repeating = true }
hl.bind("XF86AudioRaiseVolume", hl.dsp.exec_cmd("wpctl set-volume -l 1 @DEFAULT_AUDIO_SINK@ 5%+"), mediaOptions)
hl.bind("XF86AudioLowerVolume", hl.dsp.exec_cmd("wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%-"), mediaOptions)
hl.bind("XF86AudioMute", hl.dsp.exec_cmd("wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle"), mediaOptions)
hl.bind("XF86AudioMicMute", hl.dsp.exec_cmd("wpctl set-mute @DEFAULT_AUDIO_SOURCE@ toggle"), mediaOptions)
hl.bind("XF86MonBrightnessUp", hl.dsp.exec_cmd("brightnessctl -e4 -n2 set 5%+"), mediaOptions)
hl.bind("XF86MonBrightnessDown", hl.dsp.exec_cmd("brightnessctl -e4 -n2 set 5%-"), mediaOptions)

local lockOnlyOptions = { locked = true }
hl.bind("XF86AudioNext", hl.dsp.exec_cmd("playerctl next"), lockOnlyOptions)
hl.bind("XF86AudioPause", hl.dsp.exec_cmd("playerctl play-pause"), lockOnlyOptions)
hl.bind("XF86AudioPlay", hl.dsp.exec_cmd("playerctl play-pause"), lockOnlyOptions)
hl.bind("XF86AudioPrev", hl.dsp.exec_cmd("playerctl previous"), lockOnlyOptions)


hl.bind("Print", hl.dsp.exec_cmd("~/.config/hypr/scpipts/screenshot.sh screen"))
hl.bind("SHIFT + Print", hl.dsp.exec_cmd("~/.config/hypr/scpipts/screenshot.sh area"))
hl.bind("ALT + Print", hl.dsp.exec_cmd("~/.config/hypr/scpipts/screenshot.sh window"))
hl.bind("CONTROL + Print", hl.dsp.exec_cmd("~/.config/hypr/scpipts/screenshot.sh edit"))
