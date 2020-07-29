#!/bin/bash
headless=false
if [ ! -f "/etc/X11/default-display-manager" ]; then
    headless=true
fi
clear
echo "***************************************"
echo "** Install needed Packages           **"
echo "***************************************"
sudo apt-get -y install libtdb1
sudo apt-get -y install liborc-0.4-0
sudo apt-get -y install libsbc1
sudo apt-get -y install dbus-x11
sudo apt-get -y install xinit
sudo dpkg -i pulseaudio_13.99.1-45-g0547a.deb
sudo dpkg -i mbrola_3.4.0.deb
sudo apt-get -y install navit-data
sudo apt-get -y install mbrola-de5
sudo apt-get -y install libspeexdsp1
sudo apt-get -y install libfreetype6-dev
sudo apt-get -y install ttf-liberation
sudo apt-get -y install libdevil-dev
sudo apt-get -y install libxmu-dev
sudo apt-get -y install libfreeimage-dev
sudo apt-get -y install libqt4-dev
sudo apt-get -y install espeak
sudo apt-get -y install gpsd
sudo apt-get -y install gpsd-clients
sudo apt-get -y install unclutter
sudo apt-get -y install git
sudo apt-get -y install ofono
sudo apt-get -y install mc
sudo apt-get -y install mplayer
sudo apt-get -y install ntfs-3g
sudo apt-get -y install ntp
sudo apt-get -y install libbluetooth-dev
sudo apt-get -y install zip
echo "***************************************"
echo "** Finished. Hit [Enter]             **"
echo "***************************************"
read ok
clear
echo "***************************************"
echo "** Copy some files                   **"
echo "***************************************"
unzip ./etc.zip
if [ "$headless" = true ]; then
    cp .xinitrc ~/
    sh -c "echo 'startx' >> ~/.bashrc"
    sudo apt-get -y install plymouth
    sudo mkdir /usr/share/plymouth/themes/pix/
    sudo plymouth-set-default-theme pix
    #TODO: add "quiet splash plymouth.ignore-serial-consoles" to  /boot/cmdline.txt
    unzip usbmount.zip
    cd automount-usb
    sudo ./CONFIGURE.sh
    cd ..
    sudo rm -R automount-usb
else
    sudo cp etc/xdg/autostart/pyCar.desktop /etc/xdg/autostart/
    clear
    while true; do
        read -p "This is a Desktop system. Do you want install usefull tools like Pavucontrol, tightvncserver and d-feet ? (y/n)" yn
        case $yn in
            [Yy]* )
                sudo apt-get -y install tightvncserver autocutsel
                sudo apt-get -y install d-feet
                sudo apt-get -y install pavucontrol
                break;;
            [Nn]* ) break;;
            * ) echo "Please answer y or n.";;
        esac
    done
fi
sudo cp splash.png /usr/share/plymouth/themes/pix/
unzip navit.zip
sudo cp -R nav/buttons /usr/share/navit/
mkdir ~/.navit
cp nav/navit.xml ~/.navit
sudo cp etc/bluetooth/main.conf /etc/bluetooth/
mv /home/pi/.asoundrc /home/pi/.asoundrc.bak
sudo cp etc/dbus-1/system.d/ofono.conf /etc/dbus-1/system.d/
sudo cp etc/ntp.conf /etc/
sudo systemctl --system disable ofono.service 
sudo echo -e 'discoverable on' | bluetoothctl
sudo service ntp restart

echo "***************************************"
echo "** Finished. Hit [Enter]             **"
echo "***************************************"
read ok
clear
echo "***************************************"
echo "** install needed python3 modules    **"
echo "***************************************"
# gpsd-py3==0.2.0', 'mplayer.py==0.7.0', 'netifaces==0.10.5', 'nobex==1.0.0', 'pillow==3.3.1', 'psutil==5.0.1', 'pyalsaaudio==0.8.2', 'pybluez==0.22', 'python-dateutil==2.5.3', 'vobject==0.9.3
sudo apt-get -y install python3-dbus python3-mutagen python3-pyqt4 pyqt4-dev-tools python3-espeak python3-pip
sudo pip3 install pyalsaaudio
sudo pip3 install pulsectl
sudo pip3 install netifaces
sudo pip3 install psutil
sudo pip3 install pybluez
sudo pip3 install --upgrade pillow
sudo pip3 install gpsd-py3
sudo pip3 install smbus
sudo pip3 install Adafruit_MAX9744
sudo pip3 install mplayer.py
git clone https://github.com/nccgroup/nOBEX
cd nOBEX
sudo python3 setup.py install
cd ..
mv ./part2.sh ./part2.bak
echo "****************************************************************************************************"
echo "** Finished. We should now reboot the System. After Reboot start the installscript again.         **"
echo "** You can then choose an Audio-Option [ENTER]                                                    **"
echo "****************************************************************************************************"
read ok
sudo rm -R etc
sudo rm -R nOBEX
sudo rm -R nav
sudo reboot
