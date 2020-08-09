import RPi.GPIO as GPIO
import smbus
import time
import json
import socket
import sys
import threading
from PyQt5 import QtCore

isMono = False
rdsmsg = ""
rdsText = ""
index = 9999

my_unix_command = ['bc']

GPIO.setwarnings(False)

i2c = smbus.SMBus(1)      #use 0 for older RasPi
GPIO.setmode(GPIO.BCM)
GPIO.setup(26, GPIO.OUT)

# I2C-Device
SI4703 = 0x10;

# Define constants
DEVICEID = 0x00;
CHIPID = 0x01;
POWERCFG = 0x02;
CHANNEL = 0x03;
SYSCONFIG1 = 0x04;
SYSCONFIG2 = 0x05;
STATUSRSSI = 0x0A;
READCHAN = 0x0B;
RDSA = 0x0C;
RDSB = 0x0D;
RDSC = 0x0E;
RDSD = 0x0F;

# Register 0x02 - POWERCFG
SMUTE = 15;
DMUTE = 14;
SKMODE = 10;
SEEKUP = 9;
SEEK = 8;
MONO = 13;

# Register 0x03 - CHANNEL
TUNE = 15;

# Register 0x04 - SYSCONFIG1
RDS = 12;
DE = 11;

# Register 0x05 - SYSCONFIG2
SPACE1 = 5;
SPACE0 = 4;

# Register 0x0A - STATUSRSSI
RDSR = 15;
STC = 14;
SFBL = 13;
AFCRL = 12;
RDSS = 11;
STEREO = 8;

#create list to write registers
#only need to write registers 2-7 and since first byte is in the write
# command then only need 11 bytes to write
writereg = [0] * 11
 
#read 32 bytes
readreg = [0] * 32


#create 16 registers for SI4703
reg = [0] * 16

z = "000000000000000"

class control():
    
    def __init__(self, pyCAR):
        self.pyCAR=pyCAR
        self.init()
    
    def updateRegisters(self):
        #starts writing at register 2
        #but first byte is in the i2c write command
        global writereg
        global reg
        global readreg
        cmd, writereg[0] = divmod(reg[2], 1<<8)
        writereg[1], writereg[2] = divmod(reg[3], 1<<8)
        writereg[3], writereg[4] = divmod(reg[4], 1<<8)
        writereg[5], writereg[6] = divmod(reg[5], 1<<8)
        writereg[7], writereg[8] = divmod(reg[6], 1<<8)
        writereg[9], writereg[10] = divmod(reg[7], 1<<8)
        w6 = i2c.write_i2c_block_data(SI4703, cmd, writereg)
        readreg[16] = cmd #readreg
        self.readRegisters()
        return
     
    def readRegisters(self):
        global readreg
        global reg
        readreg = i2c.read_i2c_block_data(SI4703, readreg[16], 32)
        reg[10] = readreg[0] * 256 + readreg[1]
        reg[11] = readreg[2] * 256 + readreg[3]
        reg[12] = readreg[4] * 256 + readreg[5]
        reg[13] = readreg[6] * 256 + readreg[7]
        reg[14] = readreg[8] * 256 + readreg[9]
        reg[15] = readreg[10] * 256 + readreg[11]
        reg[0] = readreg[12] * 256 + readreg[13]
        reg[1] = readreg[14] * 256 + readreg[15]
        reg[2] = readreg[16] * 256 + readreg[17]
        reg[3] = readreg[18] * 256 + readreg[19]
        reg[4] = readreg[20] * 256 + readreg[21]
        reg[5] = readreg[22] * 256 + readreg[23]
        reg[6] = readreg[24] * 256 + readreg[25]
        reg[7] = readreg[26] * 256 + readreg[27]
        reg[8] = readreg[28] * 256 + readreg[29]
        reg[9] = readreg[30] * 256 + readreg[31]
        return
    
    def init(self):
        # init code needs to activate 2-wire (i2c) mode
        # the si4703 will not show up in i2cdetect until
        # you do these steps to put it into 2-wire (i2c) mode
        global reg;
        GPIO.output(26, GPIO.LOW);
        time.sleep(.5);
        GPIO.output(26, GPIO.HIGH);
        time.sleep(.5);
    
        self.readRegisters();
        # do init step, turn on oscillator
        reg[0x07] = 0x8100;
        self.updateRegisters();
        time.sleep(1);
    
        self.readRegisters();
        reg[POWERCFG] = 0x4001; #Enable the Radio IC and turn off muted
    
        reg[SYSCONFIG1] |= (1<<RDS); #Enable RDS
        reg[SYSCONFIG1] |= (1<<DE); #50kHz Europe setup
        reg[SYSCONFIG2] |= (1<<SPACE0); #100kHz channel spacing for Europe
    
        self.updateRegisters();
        time.sleep(.11);
        self.setVolume(0);
        self.statusTimer = QtCore.QTimer()
        self.statusTimer.timeout.connect(lambda: self.getStatus())
        self.statusTimer.start(100)
        #threading.Timer(2, self.getRDS).start()
        return
    
    def setVolume(self, newvolume):
        global reg
        newvolume = int(newvolume)
        if newvolume > 15:
            newvolume = 15;
        if newvolume < 0:
            newvolume = 0;
        self.readRegisters();
        reg[SYSCONFIG2] &= 0xFFF0; #Clear volume bits
        reg[SYSCONFIG2] = newvolume; #Set volume to lowest
        self.updateRegisters();
        return;
    
    def getVolume(self):
        global reg
        self.readRegisters();
        return int(reg[SYSCONFIG2])
        
    def setMono(self, dummy):
        global isMono
        global reg
        self.readRegisters();
        if isMono==False:
            print("Set to Mono")
            isMono=True
            reg[POWERCFG] |= (1 << 13);
        else:
            print("Set to Stereo")
            isMono=False
            reg[POWERCFG] &= ~(1 << 13);
        self.updateRegisters();
        time.sleep(.11);
    
    def setChannel(self, newchannel):
        global reg
        global rdsText
        rdsText=""
        newchannel = float(newchannel)
        newchannel *= 10;
        newchannel -= 8750;
        newchannel /= 10;
    
        self.readRegisters();
        reg[CHANNEL] &= 0xFE00; #Clear out the channel bits
        reg[CHANNEL] |= int(newchannel); #Mask in the new channel
        reg[CHANNEL] |= (1<<15); #Set the TUNE bit to start
        reg[5]=0x1F;
        self.updateRegisters();
        time.sleep(.1);
    
        while 1:
            self.readRegisters();
            if ((reg[STATUSRSSI] & (1<<14)) != 0):
                break;
        reg[CHANNEL] &= ~(1<<15);
        self.updateRegisters();
        
        while 1:
            self.readRegisters();
            if ((reg[STATUSRSSI] & (1<<14)) == 0):
                break;
        self.setVolume(15);
        return;
    
    def getChannel(self):
        self.readRegisters();
        channel = reg[READCHAN] & 0x03FF;
        channel += 875;
        return channel/10;
    
    def getStatus(self):
        global rdsmsg
        global index
        global rdsText
        self.readRegisters()
        if reg[STATUSRSSI] & (1<<15):
            rds = "yes";
            blockerr = reg[STATUSRSSI] & 0x0600 >> 9
            if blockerr == 0:
                rds = "yes"; #"Available";
            #else:
            #    rds = "Errors";
        else:
            rds = "no"; #"Not Available";
           
        if reg[STATUSRSSI] & (1<<8):
            quality = "stereo";
        else:
            quality = "mono";
        
        if index==0:
            rdsText = rdsmsg
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect(("127.0.0.1", 2001))
            #MESSAGE = '{"' + command + '" : "' + str(value) + '"}'
            #print("SEND :" + MESSAGE)
            #s.send((MESSAGE).encode('utf-8'))
            data = s.recv(1024)
            s.close()
            print(data.decode('utf-8').replace("'", '"'))
        except:
            pass
        """
        
        self.pyCAR.setControlInfo("frequence", str(self.getChannel()))
        #if reg[SYSCONFIG2]>0:
        #    self.pyCAR.parent.lbl_Artist.setText("")
        #    self.pyCAR.parent.lbl_Title.setText(str(self.getChannel()))
        self.pyCAR.btnQuality.setStyleSheet("background-image: url(./images/"+quality+".png);background-repeat: none; border: 0px;background-position: center");
        self.pyCAR.btnRDS.setStyleSheet("background-image: url(./images/rds_"+rds+".png);background-repeat: none; border: 0px;background-position: center");
        #if rds=="yes": self.getRDS()
    
    def seek(self, direction):
        currchan = self.getChannel()*10;
        self.setChannel(currchan);
        self.readRegisters();
        reg[POWERCFG] |= (1<<10);
        if direction == 0:  #down
            reg[POWERCFG] &= ~(1<<9);
        else:               #up
            reg[POWERCFG] |= (1<<9);
        
        reg[POWERCFG] |= (1<<8);
        self.updateRegisters();
        while 1:
            self.readRegisters();
            if ((reg[STATUSRSSI] & (1<<14)) != 0):
                break;
        print ("Trying Station ", float(float(self.getChannel())/float(10)));
        self.readRegisters();
        valuesfbl = reg[STATUSRSSI] & (1<<13);
        reg[POWERCFG] &= ~(1<<8);
        self.updateRegisters();
        
        while 1:
            self.readRegisters();
            if ((reg[STATUSRSSI] & (1<<14)) == 0):
                break;
        return
    
    def tuneUp(self):
        currchan = self.getChannel()*10;
        wc = currchan + 1;
        if wc >= 878 and wc <= 1080:
            currchan = wc;
            self.setChannel(currchan);
            
    def tuneDown(self):
        currchan = self.getChannel()*10;
        wc = currchan - 1;
        if wc >= 878 and wc <= 1080:
            currchan = wc;
            self.setChannel(currchan);
            
    
    def seekUp(self):
        self.seek(1);
        return;
    def seekDown(self):
        self.seek(0)
        return;
    
    def getRDS(self):
        global rdsmsg
        global index
        msg = ""
        mi = 0
        h2=""       
        h3=""
        h4=""
        wc = 0
        #self.rdsTimer.stop()
        print("RDS")
        #threading.Timer(5, self.getRDS).cancel()
        while 1:
            self.readRegisters()
            if reg[STATUSRSSI] & (1<<15):
                r2 = z[:16 - len(bin(reg[RDSB])[2:])] + bin(reg[RDSB])[2:]
                r3 = z[:16 - len(bin(reg[RDSC])[2:])] + bin(reg[RDSC])[2:]
                r4 = z[:16 - len(bin(reg[RDSD])[2:])] + bin(reg[RDSD])[2:]
                if h2 != r2 or h3 != r3 or h4 != r4:
                    #f.write(r2 + "," + r3 + "," + r4 + "\n")
                    #print wc
                    wc += 1
                    #h1 = r1
                    h2 = r2
                    h3 = r3
                    h4 = r4
                    value = int(r2[:4],2)
                    value2 = int(r2[5:-5],2)
                    if value2 == 0:
                        type = "A"
                    else:
                        type = "B"
                    code =  str(value) + type
                    #time.sleep(.)
                    #print code
                    if code == "2B":
                        chars = chr(int(r3[:8],2)) + chr(int(r3[9:],2)) + chr(int(r4[:8],2)) + chr(int(r4[9:],2))
                        index = int(r2[12:],2)
                        #print hex(int(r3[:8],2)) + '-' + hex(int(r3[9:],2)) + '-' + hex(int(r4[:8],2)) + '-' + hex(int(r4[9:],2))
                        #print (str(index) + '-' +  chars)
                        if index == 0 and mi != 0:
                            #print ("RDS MSG = " + msg)
                            rdsmsg = msg
                            break
                        if index == mi:
                            msg += chars
                            mi += 1
        
                    if wc == 500:
                        #f.close
                        break
        print(rdsmsg)
        pyCAR.lbl_Text.setText(rdsmsg)
        #threading.Timer(2, self.getRDS).start()
        #self.rdsTimer.start(5000)
        #return rdsmsg
    
    



