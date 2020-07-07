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
size=$(xdpyinfo  | grep -oP 'dimensions:\s+\K\S+')
if [ "$size" = "800x480" ]
then
    fs="fullscreen"
else
    fs=""
fi
./pyCAR.py $fs
sudo killall navit
