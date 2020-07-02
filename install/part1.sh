#!/bin/bash
clear
echo "***************************************"
echo "** Remove not needed Packages        **"
echo "***************************************"
sudo apt-get -y remove --purge minecraft-pi 
sudo apt-get -y remove --purge scratch
sudo apt-get -y remove --purge wolfram-engine
sudo apt-get -y remove --purge debian-reference-*
sudo apt-get -y remove --purge epiphany-browser*
sudo apt-get -y remove --purge sonic-pi 
sudo apt-get -y remove --purge supercollider*
sudo apt-get -y remove --purge chromium-browser
sudo apt-get -y remove --purge pulseaudio*
sudo apt-get -y remove --purge libreoffice*
sudo apt-get -y remove --purge claws-mail*
sudo apt-get -y remove --purge realvnc*
sudo apt-get -y remove --purge vlc*
sudo apt-get -y remove --purge bluealsa
sudo apt-get -y clean
rm -r /home/pi/python_games/
sudo apt-get -y autoremove
echo "***************************************"
echo "** Finished. Hit [Enter]             **"
echo "***************************************"
read ok
clear
echo "***************************************"
echo "** Update apt and upgrade System     **"
echo "***************************************"
source /etc/os-release
sudo sh -c "echo 'deb-src http://archive.raspbian.org/raspbian/ $VERSION_CODENAME main contrib non-free rpi' >> /etc/apt/sources.list"
sudo apt-get update
sudo apt-get -y install raspberrypi-kernel-headers raspberrypi-kernel
echo "***************************************"
echo "** Finished. Hit [Enter]             **"
echo "***************************************"
read ok
clear
echo "***************************************"
echo "** Some Modifications                **"
echo "***************************************"
while true; do
    read -p "Should the Touchscreen rotated upside down? (y/n)" yn
    case $yn in
        [Yy]* )
            sudo sh -c "echo 'lcd_rotate=2' >> /boot/config.txt"
            break;;
        [Nn]* ) exit;;
        * ) echo "Please answer y or n.";;
    esac
done

sudo sh -c "echo 'dtoverlay=pi3-disable-bt' >> /boot/config.txt"
sudo sh -c "echo 'avoid_warnings=1' >> /boot/config.txt"
sudo sh -c "echo 'dtparam=i2c_arm=on' >> /boot/config.txt"
sudo sh -c "echo 'i2c-dev' >> /etc/modules"
sudo sh -c "echo '@xset s noblank' >> /etc/xdg/lxsession/LXDE-pi/autostart"
sudo sh -c "echo '@xset s off' >> /etc/xdg/lxsession/LXDE-pi/autostart"
sudo sh -c "echo '@xset -dpms' >> /etc/xdg/lxsession/LXDE-pi/autostart"
sudo sed -i 's/@lxpanel --profile LXDE-pi/#@lxpanel --profile LXDE-pi/g' /etc/xdg/lxsession/LXDE-pi/autostart
sudo sed -i 's/show_trash=1/show_trash=0/g' /etc/xdg/pcmanfm/LXDE-pi/desktop-items-0.conf
sudo sed -i 's/show_mounts=1/show_mounts=0/g' /etc/xdg/pcmanfm/LXDE-pi/desktop-items-0.conf
sudo sed -i 's/#xserver-command=X/xserver-command=X -s 0 dpms/g' /etc/lightdm/lightdm.conf
sudo sed -i 's/raspberrypi/pyCAR/g' /etc/hostname
sudo sed -i '$s/exit 0/ofonod\nexit 0/g' /etc/rc.local
sudo chmod +x /etc/rc.local
echo "****************************************************************************************************"
echo "** Finished. We should now reboot the System. After Reboot start the installscript again. [ENTER] **"
echo "****************************************************************************************************"
read ok
mv ./part1.sh ./part1.bak
sudo reboot