#!/bin/bash
#unclutter
#cp ../install/etc/.asoundrc ../
#pulseaudio -D
sudo echo -e 'discoverable on' | bluetoothctl
sudo chmod 646  /sys/class/backlight/rpi_backlight/bl_power 
amixer sset 'Capture' 80%
amixer set Capture nocap
# sets the output to headphones:
#pacmd set-sink-port 0 analog-output-headphones
cd /home/pi/pyCAR
./pyCAR.py fullscreen
sudo killall navit
