#!/bin/bash
headless=false
if [ ! -f "/etc/X11/default-display-manager" ]; then
    headless=true
    sudo systemctl set-default multi-user.target
    sudo ln -fs /lib/systemd/system/getty@.service /etc/systemd/system/getty.target.wants/getty@tty1.service
    sudo sh -c "echo '[Service]\nExecStart=\nExecStart=-/sbin/agetty --autologin $USER --noclear %I \$TERM\n' >> /etc/systemd/system/getty@tty1.service.d/autologin.conf"
fi
sudo dpkg-reconfigure locales
sudo dpkg-reconfigure tzdata
packages=(minecraft-pi scratch wolfram-engine debian-reference-* epiphany-browser sonic-pi supercollider* chromium-browser pulseaudio* libreoffice* claws-mail* realvnc* vlc* bluealsa)
p=$((100 / ${#packages[@]}))
c=0
for pack in "${packages[@]}"
do
    :
    sudo apt-get -y remove --purge $pack > /dev/null 2>&1
    ((c+=p))
    echo $c
done | whiptail --gauge "Remove not needed Packages" 6 50 0
sudo apt-get -y clean
rm -r /home/pi/python_games/
TERM=ansi whiptail --title "Info" --infobox "Download Kernel headers and update apt" 8 78
sudo apt-get -y autoremove
source /etc/os-release
sudo sh -c "echo 'deb-src http://archive.raspbian.org/raspbian/ $VERSION_CODENAME main contrib non-free rpi' >> /etc/apt/sources.list"
sudo apt update --allow-releaseinfo-change
sudo apt-get -y install raspberrypi-kernel-headers #raspberrypi-kernel
if (whiptail --title "Touchscreen" --yesno "Should the Touchscreen rotated upside down?" 8 78); then
    sudo sh -c "echo 'lcd_rotate=2' >> /boot/config.txt"
fi
if (whiptail --title "Wifi" --yesno "Do you want disable Wifi?" 8 78); then
    sudo sh -c "echo 'dtoverlay=disable-wifi' >> /boot/config.txt"
fi
TERM=ansi whiptail --title "Info" --infobox "Some important modifications" 8 78
sudo sh -c "echo 'dtoverlay=pi3-disable-bt' >> /boot/config.txt"
sudo sh -c "echo 'avoid_warnings=1' >> /boot/config.txt"
sudo sh -c "echo 'dtparam=i2c_arm=on' >> /boot/config.txt"
sudo sh -c "echo 'i2c-dev' >> /etc/modules"
if [ "$headless" = false ]; then
    sudo sh -c "echo '@xset s noblank' >> /etc/xdg/lxsession/LXDE-pi/autostart"
    sudo sh -c "echo '@xset s off' >> /etc/xdg/lxsession/LXDE-pi/autostart"
    sudo sh -c "echo '@xset -dpms' >> /etc/xdg/lxsession/LXDE-pi/autostart"
    #sudo sed -i 's/@lxpanel --profile LXDE-pi/#@lxpanel --profile LXDE-pi/g' /etc/xdg/lxsession/LXDE-pi/autostart
    sudo sed -i 's/show_trash=1/show_trash=0/g' /etc/xdg/pcmanfm/LXDE-pi/desktop-items-0.conf
    sudo sed -i 's/show_mounts=1/show_mounts=0/g' /etc/xdg/pcmanfm/LXDE-pi/desktop-items-0.conf
    sudo sed -i 's/#xserver-command=X/xserver-command=X -s 0 dpms/g' /etc/lightdm/lightdm.conf
fi
sudo sed -i 's/raspberrypi/pyCAR/g' /etc/hostname
sudo sed -i '$s/exit 0/ofonod\nexit 0/g' /etc/rc.local
sudo chmod +x /etc/rc.local

packages=(libtdb1 liborc-0.4-0 libsbc1 dbus-x11 xinit pulseaudio_13.99.1-45-g0547a.deb mbrola_3.4.0.deb navit-data mbrola-de5 libspeexdsp1 libfreetype6-dev ttf-liberation libdevil-dev libxmu-dev libfreeimage-dev libqt5-dev espeak gpsd gpsd-clients unclutter git ofono mc mplayer ntfs-3g ntp libbluetooth-dev zip libwebrtc-audio-processing1 rpi.gpio feh)
p=$((100 / ${#packages[@]}))
c=0
for pack in "${packages[@]}"
do
    :
    if [[ $pack == *".deb"* ]]; then
        sudo dpkg -i $pack > /dev/null 2>&1
    else
        sudo apt-get -y install $pack > /dev/null 2>&1
    fi
    ((c+=p))
    echo $c
done | whiptail --gauge "Install needed Packages" 6 50 0
TERM=ansi whiptail --title "Info" --infobox "Copy some files..." 8 78
unzip ./etc.zip
if [ "$headless" = true ]; then
    #sed -i '$s/#startx/startx/g' ~/.bashrc
    touch ~/.bashrc
    cat ./bash.txt >> ~/.bashrc
    sudo apt-get -y install plymouth rpd-plym-splash x11-xserver-utils > /dev/null 2>&1
    sudo plymouth-set-default-theme pix
    sudo sed -i '1 s_$_ quiet splash plymouth.ignore-serial-consoles_' /boot/cmdline.txt
    unzip usbmount.zip > /dev/null 2>&1
    cd automount-usb
    sudo ./CONFIGURE.sh > /dev/null 2>&1
    cd ..
    sudo rm -R automount-usb
else
    sudo cp etc/xdg/autostart/pyCar.desktop /etc/xdg/autostart/
    if (whiptail --title "Desktop System" --yesno "Do you want install pavucontrol, tightvncserver and d-feet?" 8 78); then
        sudo apt-get -y install tightvncserver autocutsel
        sudo apt-get -y install d-feet
        sudo apt-get -y install pavucontrol
    fi
fi
TERM=ansi whiptail --title "Info" --infobox "Copy some files..." 8 78
sudo mv /tmp/pulse/* /etc/pulse/
sudo cp splash.png /usr/share/plymouth/themes/pix/
unzip navit.zip
sudo cp -R nav/buttons /usr/share/navit/
sudo cp nav/icons/* /usr/share/navit/icons/
sudo chmod -R 775 /usr/share/navit/icons/
mkdir ~/.navit
cp nav/navit.xml ~/.navit
sudo cp etc/bluetooth/main.conf /etc/bluetooth/
sudo cp etc/dbus-1/system.d/ofono.conf /etc/dbus-1/system.d/
sudo cp etc/ntp.conf /etc/
sudo systemctl --system disable ofono.service > /dev/null 2>&1
sudo service ntp restart
# gpsd-py3==0.2.0', 'mplayer.py==0.7.0', 'netifaces==0.10.5', 'nobex==1.0.0', 'pillow==3.3.1', 'psutil==5.0.1', 'pyalsaaudio==0.8.2', 'pybluez==0.22', 'python-dateutil==2.5.3', 'vobject==0.9.3
packages=(python3-dbus python3-mutagen python3-pyqt5 pyqt5-dev-tools python3-espeak python3-pip pyalsaaudio pulsectl netifaces psutil pybluez pillow gpsd-py3 smbus Adafruit_MAX9744 mplayer.py https://github.com/nccgroup/nOBEX)
p=$((100 / ${#packages[@]}))
c=0
for pack in "${packages[@]}"
do
    :
    echo "$pack"
    if [[ $pack == *"python3"* ]]; then
        sudo apt-get -y install $pack > /dev/null 2>&1
    elif [[ $pack == *"github"* ]]; then
        git clone $pack git > /dev/null 2>&1
        cd git
        sudo python3 setup.py install > /dev/null 2>&1
        cd ..
        sudo rm -R git
    else
        sudo pip3 install $pack > /dev/null 2>&1
    fi
    ((c+=p))
    echo $c
done | whiptail --gauge "Install needed python3 modules" 6 50 0
whiptail --title "Finished" --msgbox "We should now reboot the System. After Reboot you can restart this install script again to choose an audio option." 8 78
sudo rm -R etc
sudo rm -R nav
sudo reboot
