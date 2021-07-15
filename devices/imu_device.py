from __future__ import print_function
from __future__ import division
import time
import datetime
import logging
import os
import json
import smbus2 as smbus
import struct
import ctypes # for signed int


# Todo:
# - replace all read* with the block read?

################################
# MPU9250
################################
MPU9250_ADDRESS = 0x68
AK8963_ADDRESS  = 0x0C
WHO_AM_I        = 0x75
DEVICE_ID       = 0x71
PWR_MGMT_1      = 0x6B
USR_CTRL_REG    = 0x6A
INT_PIN_CFG     = 0x37
INT_ENABLE      = 0x38
I2C_SLV0_REG    = 38
I2C_SLV0_D0     = 99
I2C_SLV0_CTRL   = 39
I2C_SLV0_ADDR   = 37
I2C_SLV_DI      = 73
# --- Accel ------------------
ACCEL_DATA    = 0x3B
ACCEL_CONFIG  = 0x1C
ACCEL_CONFIG2 = 0x1D
ACCEL_2G      = 0x00
ACCEL_4G      = (0x01 << 3)
ACCEL_8G      = (0x02 << 3)
ACCEL_16G     = (0x03 << 3)
# --- Temp --------------------
TEMP_DATA = 0x41
# --- Gyro --------------------
GYRO_DATA    = 0x43
GYRO_CONFIG  = 0x1B
GYRO_250DPS  = 0x00
GYRO_500DPS  = (0x01 << 3)
GYRO_1000DPS = (0x02 << 3)
GYRO_2000DPS = (0x03 << 3)
# --- AK8963 ------------------
MAGNET_DATA  = 0x03
AK_DEVICE_ID = 0x48
AK_WHO_AM_I  = 0x00
AK8963_8HZ   = 0x02
AK8963_100HZ = 0x06
AK8963_14BIT = 0x00
AK8963_16BIT = (0x01 << 4)
AK8963_CNTL1 = 0x0A
AK8963_CNTL2 = 0x0B
AK8963_ASAX  = 0x10
AK8963_ST1   = 0x02
AK8963_ST2   = 0x09
AK8963_ASTC  = 0x0C
ASTC_SELF    = 0x01<<6
class mpu9250(object):
    def __init__(self, bus=1):
        """
        Setup the IMU
        reg 0x25: SAMPLE_RATE= Internal_Sample_Rate / (1 + SMPLRT_DIV)
        reg 0x29: [2:0] A_DLPFCFG Accelerometer low pass filter setting
            ACCEL_FCHOICE 1
            A_DLPF_CFG 4
            gives BW of 20 Hz
        reg 0x35: FIFO disabled default - not sure i want this ... just give me current reading
        might include an interface where you can change these with a dictionary:
            setup = {
                ACCEL_CONFIG: ACCEL_4G,
                GYRO_CONFIG: AK8963_14BIT | AK8963_100HZ
            }
        """
        self.bus = smbus.SMBus(bus)

        # let's double check we have the correct device address
        ret = self.read8(MPU9250_ADDRESS, WHO_AM_I)
        if ret is not DEVICE_ID:
            raise Exception('MPU9250: init failed to find device')

        self.write(MPU9250_ADDRESS, PWR_MGMT_1, 0x00)  # turn sleep mode off
        time.sleep(0.2)
        self.write(MPU9250_ADDRESS, PWR_MGMT_1, 0x01)  # auto select clock source
        self.write(MPU9250_ADDRESS, ACCEL_CONFIG, ACCEL_2G)
        self.write(MPU9250_ADDRESS, GYRO_CONFIG, GYRO_250DPS)

        # Going to use the I2C master mode of the IC to get the magnetic data.
        # Enable the master mode IO in the user control bit 5 (0x20)
        self.write(MPU9250_ADDRESS, USR_CTRL_REG, 0x20)
        # Disable the maser bypass mode in the interrupt pin config register bit 2 (0x20)
        self.write(MPU9250_ADDRESS, INT_PIN_CFG, 0x22)
        # Disable the external interrupt passthrough (not needed):
        self.write(MPU9250_ADDRESS, INT_ENABLE, 0x00)
        # The I2C device 0x0c is now available to the maser
        time.sleep(0.1) #give it all a chance to get online
        
        #self.setSlaveToWrite()
        #self.writeSlave(0x00)
        self.setSlaveToRead()
        self.readSlave(0x00,1)
        time.sleep(0.1)
        ret = self.readSlave(AK_WHO_AM_I,1)[0] #only need the first byte to verify this
        if ret is not AK_DEVICE_ID:
            raise Exception('AK8963: init failed to find device')
        self.setSlaveToWrite()
        self.writeSlave(AK8963_CNTL1, (AK8963_16BIT | AK8963_8HZ),0.1)
        self.writeSlave(AK8963_ASTC, 0,0.1)
        self.setSlaveToRead()
        self.readSlave(MAGNET_DATA,7)
        #self.write(AK8963_ADDRESS, AK8963_CNTL1, (AK8963_16BIT | AK8963_8HZ)) # cont mode 1
        #self.write(AK8963_ADDRESS, AK8963_ASTC, 0)
        #normalization coefficients 
        self.alsb = 2.0 / 32760 # ACCEL_2G
        self.glsb = 250.0 / 32760 # GYRO_250DPS
        self.mlsb = 4800.0 / 32760 # MAGNET range +-4800

        # i think i can do this???
        # self.convv = struct.Struct('<hhh')

    def __del__(self):
        self.bus.close()

    def write(self, address, register, value):
        attemps = 0
        while attemps < 10:
            try:
                self.bus.write_byte_data(address, register, value)
                break
            except:
                attemps += 1

    def read8(self, address, register):
        attemps = 0
        while attemps < 10:
            try:
                data = self.bus.read_byte_data(address, register)
                break
            except:
                attemps += 1
        return data

    def read16(self, address, register):
        attemps = 0
        while attemps < 10:
            try:
                data = self.bus.read_i2c_block_data(address, register, 2)
                break
            except:
                attemps += 1
        return self.conv(data[0], data[1])

    def read_xyz(self, address, register, lsb):
        """
        Reads x, y, and z axes at once and turns them into a tuple.
        """
        # data is MSB, LSB, MSB, LSB ...
        attemps = 0
        while attemps < 10:
            try:
                data = self.bus.read_i2c_block_data(address, register, 6)
                break
            except:
                attemps += 1

        # data = []
        # for i in range(6):
        #     data.append(self.read8(address, register + i))

        x = self.conv(data[0], data[1]) * lsb
        y = self.conv(data[2], data[3]) * lsb
        z = self.conv(data[4], data[5]) * lsb

        #print('>> data', data)
        # ans = self.convv.unpack(*data)
        # ans = struct.unpack('<hhh', data)[0]
        # print('func', x, y, z)
        # print('struct', ans)

        return (x, y, z)

    def read_xyz_slave_mag(self, lsb):
        """
        Reads x, y, and z axes at once and turns them into a tuple.
        Little endian version
        """
        self.setSlaveToRead()
        data = self.readSlave(MAGNET_DATA,7)

        x = self.conv(data[1], data[0]) * lsb
        y = self.conv(data[3], data[2]) * lsb
        z = self.conv(data[5], data[4]) * lsb

        return (x, y, z)

    def read_xyz_le(self, address, register, lsb):
        """
        Reads x, y, and z axes at once and turns them into a tuple.
        Little endian version
        """
        attemps = 0
        while attemps < 10:
            try:
                data = self.bus.read_i2c_block_data(address, register, 6)
                break
            except:
                attemps += 1

        x = self.conv(data[1], data[0]) * lsb
        y = self.conv(data[3], data[2]) * lsb
        z = self.conv(data[5], data[4]) * lsb

        return (x, y, z)

    def conv(self, msb, lsb):
        value = lsb | (msb << 8)
        
        return ctypes.c_short(value).value

    # Set to write MPU Slave
    def setSlaveToWrite(self, address=None):

        if address is None:
            address = AK8963_ADDRESS
        
        self.write(MPU9250_ADDRESS, I2C_SLV0_ADDR, address) 
        
    # Write in slave
    def writeSlave(self, register, value, this_sleep = 0):
        self.write(MPU9250_ADDRESS, I2C_SLV0_REG, register)
        self.write(MPU9250_ADDRESS, I2C_SLV0_D0, value)
        self.write(MPU9250_ADDRESS, I2C_SLV0_CTRL, 0x80)
        
        if this_sleep > 0:
            time.sleep(this_sleep)

    # Set to read MPU Slave
    def setSlaveToRead(self, address=None):

        if address is None:
            address = AK8963_ADDRESS

        self.write(MPU9250_ADDRESS, I2C_SLV0_ADDR, address | 0x80) 

    # Read from slave
    def readSlave(self, register, num_bytes=6):
        self.write(MPU9250_ADDRESS, I2C_SLV0_REG, register)
        self.write(MPU9250_ADDRESS, I2C_SLV0_CTRL, 0x80 + num_bytes)
        data = []
        for i in range(0,num_bytes):
            data.append(self.read8(MPU9250_ADDRESS, I2C_SLV_DI + i))
        return data

    @property
    def accel(self):
        return self.read_xyz(MPU9250_ADDRESS, ACCEL_DATA, self.alsb)

    @property
    def gyro(self):
        return self.read_xyz(MPU9250_ADDRESS, GYRO_DATA, self.glsb)

    @property
    def temp(self):
        """
        Returns chip temperature in C
        pg 33 reg datasheet:
        pg 12 mpu datasheet:
        Temp_room 21
        Temp_Sensitivity 333.87
        Temp_degC = ((Temp_out - Temp_room)/Temp_Sensitivity) + 21 degC
        """
        temp_out = self.read16(MPU9250_ADDRESS, TEMP_DATA)
        temp = ((temp_out -21.0)/ 333.87)+21.0 # these are from the datasheets
        
        return temp

    @property
    def mag(self):
        data=self.read_xyz_slave_mag(self.mlsb)
        return data

class imu_device:
    isavailable = True

    def __init__(self):

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
        self.imu = mpu9250()
        self.mylogs.info("Initalised the IMU sensor (MPU9250) device driver.")

    def getText(self):
        # Get distances from all units
        a = self.imu.accel
        msg = 'Accel: {:.3f} {:.3f} {:.3f} mg'.format(*a)
        g = self.imu.gyro
        msg = '{}\n\rGyro: {:.3f} {:.3f} {:.3f} dps'.format(msg,*g)
        m = self.imu.mag
        msg = '{}\n\rMagnet: {:.3f} {:.3f} {:.3f} mT'.format(msg,*m)
        m = self.imu.temp
        msg = '{}\n\rTemperature: {:.3f} C'.format(msg,m)
        self.mylogs.info("String data requested. Packet is {}.".format(msg))
        return msg

    def getJson(self):
        a = self.imu.accel
        g = self.imu.gyro
        m = self.imu.mag
        t = self.imu.temp
        data = {"Accelerometer" : a,
            "Gyroscope": g,
            "Magnetometer": m,
            "Temperature": t}
        
        self.mylogs.info("JSON data requested. Packet is {}.".format(json.dumps(data)))
        return json.dumps(data)
        
    def getDict(self):
        a = self.imu.accel
        g = self.imu.gyro
        m = self.imu.mag
        t = self.imu.temp
        data = {"Accelerometer" : a,
            "Gyroscope": g,
            "Magnetometer": m,
            "Temperature": t}
        self.mylogs.info("Dictionary data requested. Packet is {}.".format(json.dumps(data)))
        return data
        
if __name__ == '__main__':
    try:
        print("Demo IMU sensor application started!")
        my_device = imu_device()
        while True:
            print(my_device.getText())
            print(my_device.getJson())
            time.sleep(1.0)

    except (KeyboardInterrupt):
        running = False
        print("Application closed!")

