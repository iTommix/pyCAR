#!/bin/bash
if [ -f "./part1.bak" ]; then
    if [ -f "./part2.sh" ]; then
        ./part2.sh
    fi
fi
HEIGHT=15
WIDTH=40
CHOICE_HEIGHT=4
BACKTITLE="pyCAR - A Car Stereo System based on Python3 and QT4"
TITLE="Install"
MENU="Choose one of the following options:"

OPTIONS=(1 "Install Base-System"
         2 "Select Audio-Options"
         3 "Reboot to pyCAR")

CHOICE=$(whiptail --clear --backtitle "$BACKTITLE" --title "$TITLE" --menu "$MENU" $HEIGHT $WIDTH $CHOICE_HEIGHT "${OPTIONS[@]}" 2>&1 >/dev/tty)

clear
case $CHOICE in
        1)
            ./part1.sh
            ;;
        2)
            ./part2.sh
            ;;
        3)
            sudo reboot
            ;;
esac