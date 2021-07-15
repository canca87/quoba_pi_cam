#Libraries
import RPi.GPIO as GPIO
import time
 
#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)
 
#set GPIO Pins
GPIO_TRIGGER = [19,16]
GPIO_ECHO = [6,13]
 
#set GPIO direction (IN / OUT)
for pin_num in GPIO_TRIGGER:
    GPIO.setup(pin_num, GPIO.OUT)
for pin_num in GPIO_ECHO:
    GPIO.setup(pin_num, GPIO.IN)
 
def distance(device_num = 0):
    if device_num > len(GPIO_TRIGGER) or device_num > len(GPIO_ECHO):
        print("An invalid US sensor number was given.")
        return -1
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER[device_num], True)
 
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER[device_num], False)
    
    TriggeredTime = time.time()
    StartTime = time.time()
    StopTime = time.time()
 
    # save StartTime
    while GPIO.input(GPIO_ECHO[device_num]) == 0:
        StartTime = time.time()
        if StartTime - TriggeredTime > 0.03:
            #if the echo has not reached zero by 30 ms then it likely was not triggered properly
            return -2
 
    # save time of arrival
    while GPIO.input(GPIO_ECHO[device_num]) == 1:
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
 
    return distance
 
if __name__ == '__main__':
    try:
        while True:
            print ("Measured Distance = {:.2f} cm, {:.2f} cm".format(distance(0),distance(1)))
            time.sleep(1)
 
        # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        GPIO.cleanup()