from devices.gps_device import gps_device
from devices.us_distance_device import us_distance_device
from devices.lidar_distance_device import lidar_distance_device
from devices.imu_device import imu_device
from devices.pi_device import pi_device

# Setup the subsystems
gps_sys = gps_device()
us_distance_sys = us_distance_device()
lidar_distance_sys = lidar_distance_device()
imu_sys = imu_device()
pi_sys = pi_device()

def update_output():
    msg = ""
    msg = 'GPS data\n\r############################\n\r{}'.format(gps_sys.getText())
    msg = "{}\n\r\n\rUltrasonic distance sensor data\n\r############################\n\r{}".format(msg,us_distance_sys.getText())
    msg = "{}\n\r\n\rLidar distance sensor data\n\r############################\n\r{}".format(msg,lidar_distance_sys.getText())
    msg = "{}\n\r\n\rIMU sensor data\n\r############################\n\r{}".format(msg,imu_sys.getText())
    msg = "{}\n\r\n\rMCU data\n\r############################\n\r{}".format(msg,pi_sys.getText())
    return msg

print(update_output())