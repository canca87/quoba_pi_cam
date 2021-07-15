import time
import datetime
import logging
import os
import json
import RPi.GPIO as GPIO
from PiicoDev_VL53L1X import PiicoDev_VL53L1X

class lidar_distance_device:

    def __init__(self,shutdown_pins=[20,26]):
        # Gather the variables
        self.shudown_pins = shutdown_pins

        GPIO.setwarnings(False)

        # Setup GPIO for shutdown pins on each VL53L0X
        GPIO.setmode(GPIO.BCM)
        for i in self.shudown_pins:
            GPIO.setup(i, GPIO.OUT)

        # Set all shutdown pins low to turn off each VL53L0X
        for i in self.shudown_pins:
            GPIO.output(i, GPIO.LOW)

        # Keep all low for 500 ms or so to make sure they reset
        time.sleep(0.50)

        # Setup the logger:
        self.mylogs = logging.getLogger(__name__)
        file = logging.FileHandler( os.path.join( "logs","lidar_distance_device_log_{}.txt".format( time.strftime( "%Y%m%d_%H%M%S" ) ) ) )
        fileformat = logging.Formatter("%(asctime)s [%(levelname)s] - [%(filename)s > %(funcName)s() > %(lineno)s] - %(message)s",datefmt="%H:%M:%S")
        file.setFormatter(fileformat)
        self.mylogs.addHandler(file)
        self.mylogs.setLevel(logging.DEBUG)
        stream = logging.StreamHandler()
        stream.setLevel(logging.DEBUG)
        streamformat = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
        stream.setFormatter(streamformat)
        #self.mylogs.addHandler(stream)
        
        device_id = 0
        self.distSensors = []
        for i in self.shudown_pins:
            GPIO.output(i, GPIO.HIGH)
            try:
                time.sleep(0.2)
                self.distSensors.append(PiicoDev_VL53L1X())
                self.distSensors[device_id].change_id(40+device_id)
                self.distance(device_id)
            except:
                self.mylogs.warning("Could not connect to VL53L0X sensor {}. Ignoring".format(device_id))
                continue
            device_id = device_id + 1

        self.mylogs.info("Initalised the lidar distance sensor device driver.")

    def distance(self,device_num = 0):
        if device_num > len(self.distSensors):
            self.mylogs.warning("An invalid sensor number was given.")
            return -1
        distance = self.distSensors[device_num].read()
 
        self.mylogs.info("Device {} measure {} raw ({} cm)".format(device_num,distance,distance/10))
        return distance/10

    def getText(self):
        # Get distances from all units
        data = []
        for i in range(0,len(self.distSensors)):
            data.append(self.distance(i))
        if len(data) >= 1:
            msg = "{:.2f} cm, ".format(data[0])
            for i in range(1,len(data)):
                msg = "{}{:.2f} cm, ".format(msg,data[i])
        else:
            msg = ""
        self.mylogs.info("String data requested. Packet is {}.".format(data))
        return msg

    def getJson(self):
        data = {}
        for i in range(0,len(self.distSensors)):
            data[str(i)] = self.distance(i)
        #print(json.dumps(data))
        self.mylogs.info("JSON data requested. Packet is {}.".format(json.dumps(data)))
        return json.dumps(data)
        
    def getDict(self):
        data = {}
        for i in range(0,len(self.distSensors)):
            data[str(i)] = self.distance(i)
        self.mylogs.info("Dictionary data requested. Packet is {}.".format(json.dumps(data)))
        return data
        
if __name__ == '__main__':
    try:
        print("Demo lidar distance sensor application started!")
        my_device = lidar_distance_device()
        while True:
            print(my_device.getText())
            print(my_device.getJson())
            time.sleep(1.0)

    except (KeyboardInterrupt):
        running = False
        print("Application closed!")