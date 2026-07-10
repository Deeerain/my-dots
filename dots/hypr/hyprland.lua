require("hyprland.lib")

require("hyprland.monitors")
require("hyprland.autostart")
require("hyprland.env")
require("hyprland.keybindings")
require("hyprland.general")

-- Custom configurations
if is_file_exists(HOME .. "/.config/hypr/custom/monitors.lua") then
    require("custom.monitors")
end
if is_file_exists(HOME .. "/.config/hypr/custom/autostart.lua") then
    require("custom.monitors")
end
if is_file_exists(HOME .. "/.config/hypr/custom/env.lua") then
    require("custom.monitors")
end
if is_file_exists(HOME .. "/.config/hypr/custom/keybindings.lua") then
    require("custom.monitors")
end
if is_file_exists(HOME .. "/.config/hypr/custom/general.lua") then
    require("custom.monitors")
end