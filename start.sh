#!/bin/bash
xset s off         # don't activate screensaver
xset -dpms         # disable DPMS (Energy Star) features.
xset s noblank     # don't blank the video device
#unclutter &
pa=$(pidof pulseaudio)
if test -z "$pa"
then
    pulseaudio -D
    pactl load-module module-equalizer-sink
    pactl load-module module-dbus-protocol
    pactl load-module module-echo-cancel aec_method=webrtc 
fi
sudo echo -e 'discoverable on' | bluetoothctl
sudo chmod 646  /sys/class/backlight/rpi_backlight/bl_power 
#amixer sset 'Capture' 80%
#amixer set Capture nocap
# sets the output to headphones:
#pacmd set-sink-port 0 analog-output-headphones
cd /home/pi/pyCAR
./pyCAR.py

