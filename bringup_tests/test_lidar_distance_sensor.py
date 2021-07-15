from PiicoDev_VL53L1X import PiicoDev_VL53L1X
from time import sleep
import RPi.GPIO as GPIO

# GPIO for Sensor 1 shutdown pin
sensor1_shutdown = 20
# GPIO for Sensor 2 shutdown pin
sensor2_shutdown = 26

GPIO.setwarnings(False)

# Setup GPIO for shutdown pins on each VL53L0X
GPIO.setmode(GPIO.BCM)
GPIO.setup(sensor1_shutdown, GPIO.OUT)
GPIO.setup(sensor2_shutdown, GPIO.OUT)

# Set all shutdown pins low to turn off each VL53L0X
GPIO.output(sensor1_shutdown, GPIO.LOW)
GPIO.output(sensor2_shutdown, GPIO.LOW)

# Keep all low for 500 ms or so to make sure they reset
sleep(0.50)

# Set shutdown pin high for the first VL53L0X
GPIO.output(sensor1_shutdown, GPIO.HIGH)
try:
    distSensorA = PiicoDev_VL53L1X()
    distSensorA.change_id(45)
except:
    print("Could not connect to VL53L0X sensor 1. Ignoring")
    distSensorA = None

# Set shutdown pin high for the second VL53L0X
GPIO.output(sensor2_shutdown, GPIO.HIGH)
try:
    distSensorB = PiicoDev_VL53L1X()
    # no need to change the ID of this one
    # distSensorB.change_id(46)
except:
    print("Could not connect to VL53L0X sensor 2. Ignoring")
    distSensorB = None

while True:
    if distSensorA == None:
        distA_range = "Unavailable"
    else:
        distA_range = distSensorA.read() #read the sensor in millimeters
    if distSensorB == None:
        distB_range = "Unavailable"
    else:
        distB_range = distSensorB.read() #read the sensor in millimeters
    print("A(mm): {} ; B(mm): {}".format(distA_range,distB_range))
    sleep(0.1)
