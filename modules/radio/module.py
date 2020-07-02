import time, smbus
import RPi.GPIO as GPIO
GPIO.setwarnings(False)
i2c = smbus.SMBus(1)
GPIO.setmode(GPIO.BCM)
GPIO.setup(26, GPIO.OUT)
GPIO.output(26, GPIO.LOW);
time.sleep(.5);
GPIO.output(26, GPIO.HIGH);
try:
    i2c.read_byte(0x10)
    from modules.radio.Si4703 import radio
except:
    from modules.radio.internet import radio


