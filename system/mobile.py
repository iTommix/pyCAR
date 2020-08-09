import bluetooth, os, struct, sys, time
from xml.etree import ElementTree
from nOBEX import client, headers, responses
from nOBEX.bluez_helper import find_service
from subprocess import call, check_output
from random import randint
import locale
import sqlite3
#from PyQt4 import QtGui
from PyQt5.QtWidgets import QApplication

class mobile():
    
    def __init__(self):
        self.parent=None
        self.connectedDevice=""
        self.phonebook=0
       
    def pair(self, mac):
        try:
            s = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            s.connect((mac,1))
        except bluetooth.btcommon.BluetoothError as err:
            print(err)
    
    def connect(self, mac):
        command='echo "connect ' + mac + '" | bluetoothctl'
        call(command, shell=True)
        self.connectedDevice=mac
        #getPhonebook(mac)
    
    def disconnect(self, mac):
        command='echo "disconnect ' + mac + '" | bluetoothctl'
        call(command, shell=True)
        
    def isTrusted(self, mac):
        local=self.getLocalAddress()
        p="/var/lib/bluetooth/"+local+"/"+mac
        try:
            check_output(["sudo", "ls", p])
        except:
            return False
        return True
    
    def untrust(self, mac):
        if mac==self.getConnectedDevice():
            self.disconnect(mac)
        command='echo "remove ' + mac + '" | bluetoothctl'
        call(command, shell=True)
        database="/media/pi/pyCar/Phone/Phonebooks/" + mac.replace(":", "_") + ".db"
        ### delete database ###
        if os.path.exists(database):
            os.remove(database)
        
    def findNearBy(self):
        try:
            nearby_devices = bluetooth.discover_devices(duration=10, lookup_names = True)
        except:
            nearby_devices = False
        return nearby_devices
    
    def getLocalAddress(self):
        encoding = locale.getdefaultlocale()[1]
        r=check_output(["hcitool", "dev"]).decode(encoding).replace("\n\t","").replace("Devices:","")
        if r.find(":")>-1:
            s=r.find(":")-2
            device=r[s:s+17]
            if r.find("handle 0")>-1:
                return False
            else:
                return device
        return False
    
    def getConnectedDevice(self):
        encoding = locale.getdefaultlocale()[1]
        r=check_output(["hcitool", "con"]).decode(encoding).replace("\n\t","").replace("Connections:","")
        if r.find(":")>-1:
            s=r.find(":")-2
            device=r[s:s+17]
            if r.find("handle 0")>-1:
                return False
            else:
                return device
        return False
    
    def getConnectedName(self, mac):
        encoding = locale.getdefaultlocale()[1]
        r=check_output(["hcitool", "name", mac]).decode(encoding)
        return r
    
    def findService(self, service):
        device_address=self.getConnectedDevice()
        services = bluetooth.find_service(address=device_address)
        if len(services) > 0:      
            for svc in services:
                print("Service Name: %s"    % svc["name"])
                print("    Host:        %s" % svc["host"])
                print("    Description: %s" % svc["description"])
                print("    Provided By: %s" % svc["provider"])
                print("    Protocol:    %s" % svc["protocol"])
                print("    channel/PSM: %s" % svc["port"])
                print("    svc classes: %s "% svc["service-classes"])
                print("    profiles:    %s "% svc["profiles"])
                print("    service id:  %s "% svc["service-id"])
                print("")
                if svc["name"] == service:
                    return svc
        return False
    
    def loadPhonebook(self):
        device_address=self.getConnectedDevice()
        deviceName=self.getConnectedName(device_address)
        encoding = locale.getdefaultlocale()[1]
        service = self.findService("Phonebook")
        if service:
            port = find_service("pbap", device_address)
            c = client.Client(device_address, port)
            uuid = b"\x79\x61\x35\xf0\xf0\xc5\x11\xd8\x09\x66\x08\x00\x20\x0c\x9a\x66"
            c.connect(header_list=[headers.Target(uuid)]) 
            prefix = ""
            database="/media/pi/pyCar/Phone/Phonebooks/" + device_address.replace(":", "_") + ".db"
            ### delete database ###
            if os.path.exists(database):
                os.remove(database)
            ### create the database ###
            conn = sqlite3.connect(database)
            cursor = conn.cursor()
            cursor.execute("""CREATE TABLE names (uid text, first_name text, surname text)""")
            cursor.execute("""CREATE TABLE numbers (uid text, number text, type text)""")
            cursor = conn.cursor()
                
                
            
            # Access the list of vcards in the phone's internal phone book.
            hdrs, cards = c.get(prefix+"telecom/pb", header_list=[headers.Type(b"x-bt/vcard-listing")])
            
            # Parse the XML response to the previous request.
            root = ElementTree.fromstring(cards)
            
            
            # Examine each XML element, storing the file names we find in a list, and
            # printing out the file names and their corresponding contact names.
            names = []
            for card in root.findall("card"):
                try:
                    names.append(card.attrib["handle"])
                except:
                    pass
            
            
            # Request all the file names obtained earlier.
            c.setpath(prefix + "telecom/pb")
            uid=1
            self.parent.showMessage("Telefonbuch", "Lade "+str(len(names))+" Rufnummern von "+deviceName, progress=len(names))
            QApplication.processEvents()
            for name in names:
                hdrs, card = c.get(name, header_list=[headers.Type(b"x-bt/vcard")])
                #print(card)
                parsed=self.parse(card)
                gotNumber=False
                if len(parsed["phone"])>0:
                    for value in parsed["phone"]:
                        self.parent.dialogProgress.setValue(uid)
                        QApplication.processEvents()
                        try:
                            number=parsed["phone"][value]["number"]
                            cursor.execute("INSERT INTO numbers VALUES ('" + str(uid) +"', '"+ number +"', '"+ parsed["phone"][value]["type"] +"')")
                            conn.commit()
                            if number[:1]=="0":
                                number="+49"+number[1:]
                                cursor.execute("INSERT INTO numbers VALUES ('" + str(uid) +"', '"+ number +"', '"+ parsed["phone"][value]["type"] +"')")
                                conn.commit()
                            gotNumber=True
                        except:
                            pass
                    if(gotNumber):
                        print("INSERT INTO names VALUES ('" + str(uid) +"', '"+ parsed["first_name"] +"', '"+ parsed["surname"] +"')")
                        cursor.execute("INSERT INTO names VALUES ('" + str(uid) +"', '"+ parsed["first_name"] +"', '"+ parsed["surname"] +"')")
                        conn.commit()
                    
                    uid+=1
        
            
            c.disconnect()
            self.parent.closeMessage()
        
    def parse(self, raw):
        encoding = locale.getdefaultlocale()[1]
        raw=raw.decode(encoding)
        phones=0
        card={}
        card["phone"]={}
        phonetypes = {"CELL" : "Mobil", "HOME" : "Privat", "WORK" : "Dienstlich"}
        for line in raw.split("\r\n"):
            p=line.split(":")
            if line[:2]=="FN":
                card["name"]=p[1]
                
            if line[:1]=="N":
                n=p[1].split(";")
                try:
                    card["first_name"]=n[1]
                except:
                    card["first_name"]=""
                try:
                    card["surname"]=n[0]
                except:
                    card["surname"]=""
                
            if line[:3]=="UID":
                card["uid"]=p[1]
            
            if line[:3]=="TEL":
                try:
                    t=p[0].split(";")
                    typ=t[1].replace("TYPE=","")
                    if typ!="FAX":
                        card["phone"][phones]={}
                        card["phone"][phones]["type"]=phonetypes[typ]
                        card["phone"][phones]["number"]=p[1].replace(" ","")
                        phones+=1
                except:
                    pass
        
        return card

