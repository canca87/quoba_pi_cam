import time
import datetime
import logging
import os
import json
import psutil as dev

class pi_device:

    def __init__(self):
        # Gather the variables
        # none to gather

        # Setup the logger:
        self.mylogs = logging.getLogger(__name__)
        file = logging.FileHandler( os.path.join( "logs","pi_device_log_{}.txt".format( time.strftime( "%Y%m%d_%H%M%S" ) ) ) )
        fileformat = logging.Formatter("%(asctime)s [%(levelname)s] - [%(filename)s > %(funcName)s() > %(lineno)s] - %(message)s",datefmt="%H:%M:%S")
        file.setFormatter(fileformat)
        self.mylogs.addHandler(file)
        self.mylogs.setLevel(logging.DEBUG)
        stream = logging.StreamHandler()
        stream.setLevel(logging.DEBUG)
        streamformat = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
        stream.setFormatter(streamformat)
        #self.mylogs.addHandler(stream)
        self.mylogs.info("Initalised the Pi's sensors and device drivers.")


    def get_gpu_temp(self):
        return float(os.popen("vcgencmd measure_temp").readline().replace("temp=","").replace("'C\n",""))

    def get_cpu_temp(self):
        return float(os.popen("cat /sys/class/thermal/thermal_zone0/temp").readline())/1000
        
    def get_cpu_times(self):
        # named tuple 
        data = dev.cpu_times()
        self.mylogs.info("Device cpu times: ".format(data))
        return data

    def get_cpu_percent(self,interval_time = 0.1):
        # single number (float)
        data = dev.cpu_percent(interval_time)
        self.mylogs.info("Device cpu percent for {}s: ".format(interval_time,data))
        return data
    
    def get_cpu_count(self):
        # dict
        data = {"Logical" : dev.cpu_count(),"Physical" : dev.cpu_count(False)}
        self.mylogs.info("Device cpu counts: ".format(data))
        return data
    
    def get_cpu_stats(self):
        # named tuple
        data = dev.cpu_stats()
        self.mylogs.info("Device cpu stats: ".format(data))
        return data

    def get_cpu_frequency(self):
        # named tuple
        data = dev.cpu_freq()
        self.mylogs.info("Device cpu frequency: ".format(data))
        return data
    
    def get_cpu_load(self):
        # unnamed tuple
        data = dev.getloadavg()
        self.mylogs.info("Device cpu average loading (1,5,15min): ".format(data))
        return data
    
    def get_mem_virtual(self):
        # named tuple
        data = dev.virtual_memory()
        self.mylogs.info("Device virual memory: ".format(data))
        return data
    
    def get_mem_swap(self):
        # named tuple
        data = dev.swap_memory()
        self.mylogs.info("Device swap memory: ".format(data))
        return data
    
    def get_disk_paritions(self):
        # named tuple
        data = dev.disk_partitions()
        self.mylogs.info("Device disk partitions: ".format(data))
        return data
    
    def get_disk_usage(self,path = '/'):
        # named tuple
        data = dev.disk_usage(path)
        self.mylogs.info("Device disk usage from path {}: ".format(path,data))
        return data
    
    def get_network_counters(self):
        # named tuple
        data = dev.net_io_counters()
        self.mylogs.info("Device network IO counters: ".format(data))
        return data
    
    def get_network_connections(self):
        # named tuple
        data = dev.net_connections()
        self.mylogs.info("Device network connections: ".format(data))
        return data
    
    def get_boot_time(self):
        # float
        data = dev.boot_time()
        self.mylogs.info("Device time of boot: ".format(data))
        return data

    def getText(self):
        msg = ""
        msg = "{}\r\n{:<15} {:<15} {:<15} {:<10}".format(msg,"GPU temp",self.get_gpu_temp(),"","")
        msg = "{}\r\n{:<15} {:<15} {:<15} {:<10}".format(msg,"CPU temp",self.get_cpu_temp(),"","")
        data = self.get_cpu_times()._asdict()
        for i in data:
            msg = "{}\r\n{:<15} {:<15} {:<15} {:<10}".format(msg,"CPU times",i,data[i],"")
        msg = "{}\r\n{:<15} {:<15} {:<15} {:<10}".format(msg,"CPU percent",self.get_cpu_percent(),"","")
        data = self.get_cpu_count()
        for i in data:
            msg = "{}\r\n{:<15} {:<15} {:<15} {:<10}".format(msg,"CPU count",i,data[i],"")
        data = self.get_cpu_stats()._asdict()
        for i in data:
            msg = "{}\r\n{:<15} {:<15} {:<15} {:<10}".format(msg,"CPU stats",i,data[i],"")
        data = self.get_cpu_frequency()._asdict()
        for i in data:
            msg = "{}\r\n{:<15} {:<15} {:<15} {:<10}".format(msg,"CPU frequency",i,data[i],"")
        data = self.get_cpu_load()
        msg = "{}\r\n{:<15} {:<15} {:<15} {:<10}".format(msg,"CPU load","1-min",data[0],"")
        msg = "{}\r\n{:<15} {:<15} {:<15} {:<10}".format(msg,"CPU load","5-min",data[1],"")
        msg = "{}\r\n{:<15} {:<15} {:<15} {:<10}".format(msg,"CPU load","15-min",data[2],"")
        data = self.get_mem_virtual()._asdict()
        for i in data:
            msg = "{}\r\n{:<15} {:<15} {:<15} {:<10}".format(msg,"Virtual memory",i,data[i],"")
        data = self.get_mem_swap()._asdict()
        for i in data:
            msg = "{}\r\n{:<15} {:<15} {:<15} {:<10}".format(msg,"Swap memory",i,data[i],"")
        data = self.get_disk_paritions()
        count = 1
        for m in data:
            td = m._asdict()
            for i in td:
                msg = "{}\r\n{:<15} {:<15} {:<15} {:<10}".format(msg,"Disk partitions",count,i,td[i])
            count = count + 1
        data = self.get_disk_usage()._asdict()
        for i in data:
            msg = "{}\r\n{:<15} {:<15} {:<15} {:<10}".format(msg,"Disk usage",i,data[i],"")
        data = self.get_network_counters()._asdict()
        for i in data:
            msg = "{}\r\n{:<15} {:<15} {:<15} {:<10}".format(msg,"Network counters",i,data[i],"")
        data = self.get_network_connections()
        count = 1
        for m in data:
            td = m._asdict()
            for i in td:
                msg = "{}\r\n{:<15} {:<15} {:<15} {:<10}".format(msg,"Network connections",count,i,str(td[i]))
            count = count + 1
        boot_time = self.get_boot_time()
        msg = "{}\r\n{:<15} {:<15} {:<15} {:<10}".format(msg,"Boot time","Unix",boot_time,"")
        ts = datetime.datetime.fromtimestamp(boot_time)
        msg = "{}\r\n{:<15} {:<15} {:<15} {:<10}".format(msg,"Boot time","UTC",ts.strftime('%Y-%m-%d %H:%M:%S'),"")

        return msg

    def getText_old(self):
        # Get from all functions
        msg = ""
        msg = "{}---- CPU times -----\r\n{}\r\n".format(msg,self.get_cpu_times())
        msg = "{}---- CPU percent -----\r\n{}\r\n".format(msg,self.get_cpu_percent())
        msg = "{}---- CPU counts -----\r\n{}\r\n".format(msg,self.get_cpu_count())
        msg = "{}---- CPU statistics -----\r\n{}\r\n".format(msg,self.get_cpu_stats())
        msg = "{}---- CPU frequency -----\r\n{}\r\n".format(msg,self.get_cpu_frequency())
        msg = "{}---- CPU average loads -----\r\n{}\r\n".format(msg,self.get_cpu_load())
        msg = "{}---- Virtual memory -----\r\n{}\r\n".format(msg,self.get_mem_virtual())
        msg = "{}---- Swap memory -----\r\n{}\r\n".format(msg,self.get_mem_swap())
        msg = "{}---- Disk partitions -----\r\n{}\r\n".format(msg,self.get_disk_paritions())
        msg = "{}---- Disk usage (root) -----\r\n{}\r\n".format(msg,self.get_disk_usage())
        msg = "{}---- Network counters -----\r\n{}\r\n".format(msg,self.get_network_counters())
        msg = "{}---- Network connections -----\r\n{}\r\n".format(msg,self.get_network_connections())
        msg = "{}---- Boot Time -----\r\n{}\r\n".format(msg,self.get_boot_time())
        self.mylogs.info("String data requested. Packet is {}.".format(msg))
        return msg

    def getDict(self):
        data = {}
        data["gpu_temperature"] = self.get_gpu_temp()
        data["cpu_temperature"] = self.get_cpu_temp()
        data["cpu_times"] = self.get_cpu_times()._asdict()
        data["cpu_percent"] = self.get_cpu_percent()
        data["cpu_count"] = self.get_cpu_count()
        data["cpu_status"] = self.get_cpu_stats()._asdict()
        data["cpu_frequency"] = self.get_cpu_frequency()._asdict()
        data["cpu_load"] = {"min_1" : self.get_cpu_load()[0],"min_5" : self.get_cpu_load()[1],"min_15" : self.get_cpu_load()[2]}
        data["virtial_memory"] = self.get_mem_virtual()._asdict()
        data["swap_memory"] = self.get_mem_swap()._asdict()
        dp = {}
        count = 1
        for i in self.get_disk_paritions():
            dp["{}".format(count)] = i._asdict()
            count = count + 1
        data["disk_partitions"] = dp
        data["disk_usage"] = self.get_disk_usage()._asdict()
        data["network_counters"] = self.get_network_counters()._asdict()
        nc = {}
        count = 1
        for i in self.get_network_connections():
            nc["{}".format(count)] = i._asdict()
            count = count + 1
        data["network_connections"] = nc
        data["time_of_boot"] = self.get_boot_time()
        self.mylogs.info("Dictionary data requested. Packet is {}.".format(json.dumps(data)))
        return data

    def getJson(self):
        data = self.getDict()
        self.mylogs.info("JSON data requested. Packet is {}.".format(json.dumps(data)))
        return json.dumps(data)
        
if __name__ == '__main__':
    try:
        print("Demo US distance sensor application started!")
        my_device = pi_device()
        while True:
            print(my_device.getText())
            #print(my_device.getDict())
            #print(my_device.getJson())
            time.sleep(1.0)

    except (KeyboardInterrupt):
        running = False
        print("Application closed!")