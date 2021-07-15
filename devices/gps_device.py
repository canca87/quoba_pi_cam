import gpsd
import time
import datetime
import logging
import os
import json

running = True


class gps_device:

    def __init__(self):
        # Gather the variables
        #  -- none to gather

        # Setup the logger:
        self.mylogs = logging.getLogger(__name__)
        file = logging.FileHandler( os.path.join( "logs","gps_device_log_{}.txt".format( time.strftime( "%Y%m%d_%H%M%S" ) ) ) )
        fileformat = logging.Formatter("%(asctime)s [%(levelname)s] - [%(filename)s > %(funcName)s() > %(lineno)s] - %(message)s",datefmt="%H:%M:%S")
        file.setFormatter(fileformat)
        self.mylogs.addHandler(file)
        self.mylogs.setLevel(logging.DEBUG)
        stream = logging.StreamHandler()
        stream.setLevel(logging.DEBUG)
        streamformat = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
        stream.setFormatter(streamformat)
        #self.mylogs.addHandler(stream)
        self.mylogs.info("Initalised the gps device driver.")

        #Startup the gpsd connection
        # Connect to the local gpsd
        gpsd.connect()
        # Connect somewhere else if not hosted locally
        #gpsd.connect(host="127.0.0.1", port=2947)

    def getText(self):
        # Get gps position
        try:
            packet = gpsd.get_current()
        except:
            #print("GPS not ready/found")
            self.mylogs.error("No gps device found, or not available.")
            packet = None
        msg = ""
        if packet != None:    
            # See the inline docs for GpsResponse for the available data
            msg = "{}\n ************ PROPERTIES ************* ".format(msg)
            msg = "{}\n Mode: {}".format(msg,str(packet.mode))
            msg = "{}\n Satellites: {}".format(msg,str(packet.sats))
            if packet.mode >= 2:
                msg = "{}\n Latitude: {}".format(msg,str(packet.lat))
                msg = "{}\n Longitude: {}".format(msg,str(packet.lon))
                msg = "{}\n Track: {}".format(msg,str(packet.track))
                msg = "{}\n Horizontal Speed: {}".format(msg,str(packet.hspeed))
                msg = "{}\n Time: {}".format(msg,str(packet.time))
                msg = "{}\n Error: {}".format(msg,str(packet.error))
            else:
                msg = "{}\n Latitude: NOT AVAILABLE".format(msg)
                msg = "{}\n Longitude: NOT AVAILABLE".format(msg)
                msg = "{}\n Track: NOT AVAILABLE".format(msg)
                msg = "{}\n Horizontal Speed: NOT AVAILABLE".format(msg)
                msg = "{}\n Error: NOT AVAILABLE".format(msg)

            if packet.mode >= 3:
                msg = "{}\n Altitude: {}".format(msg,str(packet.alt))
                msg = "{}\n Climb: {}".format(msg,str(packet.climb))
            else:
                msg = "{}\n Altitude: NOT AVAILABLE".format(msg)
                msg = "{}\n Climb: NOT AVAILABLE".format(msg)

            msg = "{}\n ************** METHODS ************** ".format(msg)
            if packet.mode >= 2:
                msg = "{}\n Location: {}".format(msg,str(packet.position()))
                msg = "{}\n Speed: {}".format(msg,str(packet.speed()))
                msg = "{}\n Position Precision: {}".format(msg,str(packet.position_precision()))
                msg = "{}\n Time UTC: {}".format(msg,str(packet.get_time()))
                msg = "{}\n Time Local: {}".format(msg,str(packet.get_time(local_time=True)))
                msg = "{}\n Map URL: {}".format(msg,str(packet.map_url()))
            else:
                msg = "{}\n Location: NOT AVAILABLE".format(msg)
                msg = "{}\n Speed: NOT AVAILABLE".format(msg)
                msg = "{}\n Position Precision: NOT AVAILABLE".format(msg)
                msg = "{}\n Time UTC: NOT AVAILABLE".format(msg)
                msg = "{}\n Time Local: NOT AVAILABLE".format(msg)
                msg = "{}\n Map URL: NOT AVAILABLE".format(msg)

            if packet.mode >= 3:
                msg = "{}\n Altitude: {}".format(msg,str(packet.altitude()))
            else:
                msg = "{}\n Altitude: NOT AVAILABLE".format(msg)
            msg = "{}\n ************* FUNCTIONS ************* ".format(msg)
            try:
                msg = "{}\n Device: {}".format(msg,str(gpsd.device()))
            except:
                msg = msg
        self.mylogs.info("String data requested. Packet is {}.".format(msg))
        return msg

    def getJson(self):
        # Get gps position
        try:
            packet = gpsd.get_current()
        except:
            #print("GPS not ready/found")
            self.mylogs.error("No gps device found, or not available.")
            packet = None
        if packet != None:  
            if packet.mode >= 2:
                data = {"Mode" : packet.mode,
                        "Satellites" : packet.sats,
                        "Latitude" : packet.lat,
                        "Longitude" : packet.lon,
                        "Track" : packet.track,
                        "Horizontal Speed" : packet.hspeed,
                        "Time" : packet.time,
                        "Error" : packet.error,
                        "Location" : packet.position(),
                        "Speed" : packet.speed(),
                        "Position Precision" : packet.position_precision(),
                        "Time UTC" : packet.get_time().isoformat(),
                        "Time Local" : packet.get_time(local_time=True).isoformat(),
                        "Map URL" : packet.map_url()}
            elif packet.mode >= 3:
                data = {"Mode" : packet.mode,
                    "Satellites" : packet.sats,
                    "Latitude" : packet.lat,
                    "Longitude" : packet.lon,
                    "Track" : packet.track,
                    "Horizontal Speed" : packet.hspeed,
                    "Time" : packet.time,
                    "Error" : packet.error,
                    "Location" : packet.position(),
                    "Speed" : packet.speed(),
                    "Position Precision" : packet.position_precision(),
                    "Time UTC" : packet.get_time().isoformat(),
                    "Time Local" : packet.get_time(local_time=True).isoformat(),
                    "Map URL" : packet.map_url(),
                    "Altitude" : packet.altitude(),
                    "Climb" : packet.climb}
            else:
                data = {"Mode" : packet.mode,
                    "Satellites" : packet.sats,
                    "Data" : "Not Available"}
            #print(json.dumps(data))
            self.mylogs.info("JSON data requested. Packet is {}.".format(json.dumps(data)))
            return json.dumps(data)
        
    def getDict(self):
        # Get gps position
        try:
            packet = gpsd.get_current()
        except:
            #print("GPS not ready/found")
            self.mylogs.error("No gps device found, or not available.")
            packet = None
        if packet != None:  
            if packet.mode >= 2:
                data = {"Mode" : packet.mode,
                        "Satellites" : packet.sats,
                        "Latitude" : packet.lat,
                        "Longitude" : packet.lon,
                        "Track" : packet.track,
                        "Horizontal Speed" : packet.hspeed,
                        "Time" : packet.time,
                        "Error" : packet.error,
                        "Location" : packet.position(),
                        "Speed" : packet.speed(),
                        "Position Precision" : packet.position_precision(),
                        "Time UTC" : packet.get_time().isoformat(),
                        "Time Local" : packet.get_time(local_time=True).isoformat(),
                        "Map URL" : packet.map_url()}
            elif packet.mode >= 3:
                data = {"Mode" : packet.mode,
                    "Satellites" : packet.sats,
                    "Latitude" : packet.lat,
                    "Longitude" : packet.lon,
                    "Track" : packet.track,
                    "Horizontal Speed" : packet.hspeed,
                    "Time" : packet.time,
                    "Error" : packet.error,
                    "Location" : packet.position(),
                    "Speed" : packet.speed(),
                    "Position Precision" : packet.position_precision(),
                    "Time UTC" : packet.get_time().isoformat(),
                    "Time Local" : packet.get_time(local_time=True).isoformat(),
                    "Map URL" : packet.map_url(),
                    "Altitude" : packet.altitude(),
                    "Climb" : packet.climb}
            else:
                data = {"Mode" : packet.mode,
                    "Satellites" : packet.sats,
                    "Data" : "Not Available"}
            #print(json.dumps(data))
            self.mylogs.info("Dictionary data requested. Packet is {}.".format(json.dumps(data)))
            return data
        
if __name__ == '__main__':
    try:
        print("Demo GPS application started!")
        my_gps = gps_device()
        while running:
            print(my_gps.getText())
            print(my_gps.getJson())
            time.sleep(5.0)

    except (KeyboardInterrupt):
        running = False
        print("Application closed!")