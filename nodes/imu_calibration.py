#!/usr/bin/env python
from __future__ import print_function, division

import sys
import rospy
import math
import time
import json

from std_msgs.msg import Header
from sensor_msgs.msg import Imu, Temperature
from Adafruit_BNO055.BNO055 import BNO055


class BNO055Driver(object):

    def __init__(self):
        serial_port = rospy.get_param('~serial_port', '/dev/IMU')

        try:
            self.device = BNO055(serial_port='/dev/IMU')
        except:
            print('unable to find IMU at port {}'.format(serial_port))
            sys.exit(-1)

        if not self.device.begin():
            print('unable to initialize IMU at port {}'.format(serial_port))
            sys.exit(-1)

        status = self.device.get_system_status()
        print('system status is {} {} {} '.format(*status))
        time.sleep(1)
        calibration_status = self.device.get_calibration_status()
        print('calibration status is {} {} {} {} '.format(*calibration_status))

        self.device.set_external_crystal(True)

    def calibrate(self):
	calibration_status = self.device.get_calibration_status()
        while calibration_status != (3, 3, 3, 3):
	    print('waiting for device to be fully calibrated. please rotate IMU')
	    print('calibration status is {} {} {} {} '.format(*calibration_status))
	    print(' ')

    	    calibration_status = self.device.get_calibration_status()

	    try:
	        time.sleep(1)
	    except KeyboardInterrupt:
	        print('keyboard interrupt. existing')
	        sys.exit()

	print('Calibration done')
	time.sleep(2)
    	calibration_status = self.device.get_calibration_status()
	print('calibration result is {} {} {} {} '.format(*calibration_status))
	print(' ')
	
	data = self.device.get_calibration()
	with open('calibration.json', 'w') as cal_file:
	    json.dump(data, cal_file)

	print('Saved calibration to calibration.json')


def main():
    IMU = BNO055Driver()
    IMU.calibrate()

if __name__ == '__main__':
    main()
