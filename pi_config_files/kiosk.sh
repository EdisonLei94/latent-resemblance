#!/usr/bin/env bash
export DISPLAY=:0.0

sleep 30

xset -dpms
xset s noblank
xset s off

#Hide mouse cursor
unclutter -idle 1 -root &

#Chromium exit cleanly
sed -i 's/"exited_cleanly":false/"exited_cleanly":true/' '~/.config/chromium/Default/Preferences'
sed -i 's/"exit_type":"Crashed"/"exit_type":"Normal"/' '~/.config/chromium/Default/Preferences'

#Start Chromium
chromium-browser --kiosk --noerrdialogs --disable-infobars --hide-scrollbars 'http://localhost:5000' &
