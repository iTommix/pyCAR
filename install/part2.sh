#!/bin/bash
#if [ ! -f "./part2.bak" ]; then
#   ./install.sh
#fi
HEIGHT=15
WIDTH=40
CHOICE_HEIGHT=4
BACKTITLE="pyCAR - A Car Stereo System based on Python3 and QT4"
TITLE="Install Soundsystem"
MENU="Choose one of the following options:"

OPTIONS=(1 "Install Google-Voice-HAT"
         2 "Install WM8960-Audio-HAT"
         3 "Use RPi's bcm2835")

CHOICE=$(whiptail --clear --backtitle "$BACKTITLE" --title "$TITLE" --menu "$MENU" $HEIGHT $WIDTH $CHOICE_HEIGHT "${OPTIONS[@]}" 2>&1 >/dev/tty)

clear
case $CHOICE in
        1)
            git clone https://github.com/shivasiddharth/GassistPi
            sudo chmod +x ./GassistPi/audio-drivers/AIY-HAT/scripts/configure-driver.sh
            sudo ./GassistPi/audio-drivers/AIY-HAT/scripts/configure-driver.sh
            sudo chmod +x ./GassistPi/audio-drivers/AIY-HAT/scripts/install-alsa-config.sh
            sudo ./GassistPi/audio-drivers/AIY-HAT/scripts/install-alsa-config.sh
            #sudo sh -c "echo 'blacklist snd_bcm2835' >> /etc/modprobe.d/raspi-blacklist.conf"
            #sudo sed -i 's/dtparam=audio=on/#dtparam=audio=on/g' /boot/config.txt
            echo "*******************************************************************"
            echo "** Finished. You have to Reboot the RPi. Hit [Enter]             **"
            echo "*******************************************************************"
            read ok
            cd ../
            ./install.sh
            ;;
        2)
            git clone https://github.com/waveshare/WM8960-Audio-HAT
            cd WM8960-Audio-HAT
            sudo sed -i 's/apt-get -y install raspberrypi-kernel-headers raspberrypi-kernel/#/g' ./install.sh
            sudo ./install.sh
            while true; do
                read -p "Do you wish to disable onboard soundcard (recommended)? (y/n)" yn
                case $yn in
                    [Yy]* )
                        sudo sh -c "echo 'blacklist snd_bcm2835' >> /etc/modprobe.d/raspi-blacklist.conf"
                        sudo sed -i 's/dtparam=audio=on/#dtparam=audio=on/g' /boot/config.txt
                        break;;
                    [Nn]* ) exit;;
                    * ) echo "Please answer y or n.";;
                esac
            cd ..
            sudo rm -R ~/pyCAR/install/WM8960-Audio-HAT
            touch ./WM8960-Audio
            done
            echo "*******************************************************************"
            echo "** Finished. You have to Reboot the RPi. Hit [Enter]             **"
            echo "*******************************************************************"
            read ok
            cd ../
            ./install.sh
            ;;
        3)
            sudo sed -i 's/#dtparam=audio=on/dtparam=audio=on/g' /boot/config.txt
            sudo sed -i 's/blacklist snd_bcm2835//g' /etc/modprobe.d/raspi-blacklist.conf
            if test -f "./WM8960-Audio"; then
                sudo sed -i 's/dtoverlay=i2s-mmap/#dtoverlay=i2s-mmap/g' /boot/config.txt
                sudo sed -i 's/dtoverlay=wm8960-soundcard/#dtoverlay=wm8960-soundcard/g' /boot/config.txt
            fi
            ./install.sh
            ;;
esac