import time
import datetime
import logging
import os
import json
import RPi.GPIO as GPIO

class us_distance_device:

    def __init__(self,trigger_pins=[19,16],echo_pins=[6,13]):
        # Gather the variables
        self.trigger_pins = trigger_pins
        self.echo_pins = echo_pins

        GPIO.setwarnings(False)
        #GPIO Mode (BOARD / BCM)
        GPIO.setmode(GPIO.BCM)

        # Setup the logger:
        self.mylogs = logging.getLogger(__name__)
        file = logging.FileHandler( os.path.join( "logs","us_distance_device_log_{}.txt".format( time.strftime( "%Y%m%d_%H%M%S" ) ) ) )
        fileformat = logging.Formatter("%(asctime)s [%(levelname)s] - [%(filename)s > %(funcName)s() > %(lineno)s] - %(message)s",datefmt="%H:%M:%S")
        file.setFormatter(fileformat)
        self.mylogs.addHandler(file)
        self.mylogs.setLevel(logging.DEBUG)
        stream = logging.StreamHandler()
        stream.setLevel(logging.DEBUG)
        streamformat = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
        stream.setFormatter(streamformat)
        #self.mylogs.addHandler(stream)
        self.mylogs.info("Initalised the ultrasonic distance sensor device driver.")

        #set GPIO direction (IN / OUT)
        for pin_num in self.trigger_pins:
            GPIO.setup(pin_num, GPIO.OUT)
        for pin_num in self.echo_pins:
            GPIO.setup(pin_num, GPIO.IN)

    def distance(self,device_num = 0):
        if device_num > len(self.trigger_pins) or device_num > len(self.echo_pins):
            self.mylogs.warning("An invalid US sensor number was given.")
            return -1
        # set Trigger to HIGH
        GPIO.output(self.trigger_pins[device_num], True)
    
        # set Trigger after 0.01ms to LOW
        time.sleep(0.00001)
        GPIO.output(self.trigger_pins[device_num], False)
        
        TriggeredTime = time.time()
        StartTime = time.time()
        StopTime = time.time()
    
        # save StartTime
        while GPIO.input(self.echo_pins[device_num]) == 0:
            StartTime = time.time()
            if StartTime - TriggeredTime > 0.03:
                #if the echo has not reached zero by 30 ms then it likely was not triggered properly
                return -2
    
        # save time of arrival
        while GPIO.input(self.echo_pins[device_num]) == 1:
            StopTime = time.time()
            if StopTime - StartTime > 0.038:
                #38ms then there was no object to detect
                return -3
    
        # time difference between start and arrival
        TimeElapsed = StopTime - StartTime
        if TimeElapsed == 0.038:
            #38ms then there was no object to detect
            return -4
        # multiply with the sonic speed (34300 cm/s)
        # and divide by 2, because there and back
        distance = (TimeElapsed * 34300) / 2
 
        self.mylogs.info("Device {} measure {} raw ({} cm)".format(device_num,TimeElapsed,distance))
        return distance

    def getText(self):
        # Get distances from all units
        data = []
        for i in range(0,len(self.echo_pins)):
            data.append(self.distance(i))
        if len(data) > 1:
            msg = "{:.2f} cm, ".format(data[0])
            for i in range(1,len(data)):
                msg = "{}{:.2f} cm, ".format(msg,data[i])
        else:
            msg = ""
        self.mylogs.info("String data requested. Packet is {}.".format(data))
        return msg

    def getJson(self):
        data = {}
        for i in range(0,len(self.echo_pins)):
            data[str(i)] = self.distance(i)
        #print(json.dumps(data))
        self.mylogs.info("JSON data requested. Packet is {}.".format(json.dumps(data)))
        return json.dumps(data)
        
    def getDict(self):
        data = {}
        for i in range(0,len(self.echo_pins)):
            data[str(i)] = self.distance(i)
        self.mylogs.info("Dictionary data requested. Packet is {}.".format(json.dumps(data)))
        return data
        
if __name__ == '__main__':
    try:
        print("Demo US distance sensor application started!")
        my_device = us_distance_device()
        while True:
            print(my_device.getText())
            print(my_device.getJson())
            time.sleep(1.0)

    except (KeyboardInterrupt):
        running = False
        print("Application closed!")