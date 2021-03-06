#!/usr/bin/env python
from __future__ import print_function, division

import sys
import rospy
import math
import time
import json

from std_msgs.msg import Header
from sensor_msgs.msg import Imu, Temperature
from geometry_msgs.msg import Vector3
from Adafruit_BNO055.BNO055 import BNO055


class BNO055Driver(object):

    def __init__(self):
        serial_port = rospy.get_param('~serial_port', '/dev/IMU')

        try:
            self.device = BNO055(serial_port='/dev/IMU')
        except:
            rospy.logerr('unable to find IMU at port {}'.format(serial_port))
            sys.exit(-1)

        if not self.device.begin():
            rospy.logerr('unable to initialize IMU at port {}'.format(serial_port))
            sys.exit(-1)

	with open('calibration.json', 'r') as self.cal_file:
            self.data = json.load(self.cal_file)

        self.device.set_calibration(self.data)
	
        status = self.device.get_system_status()
        rospy.loginfo('system status is {} {} {} '.format(*status))
        time.sleep(1)
        calibration_status = self.device.get_calibration_status()
        rospy.loginfo('calibration status is {} {} {} {} '.format(*calibration_status))

        self.device.set_external_crystal(True)

        self.imu_pub = rospy.Publisher('imu', Imu, queue_size=1)
        self.temp_pub = rospy.Publisher('temperature', Temperature, queue_size=1)
        self.euler_pub = rospy.Publisher('euler', Vector3, queue_size=1)
        #self.gravity_pub = rospy.Publisher('gravity', Vector3, queue_size=1)

        self.frame_id = rospy.get_param('~frame_id', '/base_imu')
        self.seq = 0
        self.reset_msgs()

    def reset_msgs(self):
        self.imu_msg = Imu()

        # ignore the covariance data
        self.imu_msg.orientation_covariance[0] = -1
        self.imu_msg.angular_velocity_covariance[0] = -1
        self.imu_msg.linear_acceleration_covariance[0] = -1

        self.temp_msg = Temperature()
        self.temp_msg.variance = 0

	self.vector3_msg = Vector3()
	self.vector3_msg.x = 0
	self.vector3_msg.y = 0
	self.vector3_msg.z = 0

    def publish_data(self):
        h = Header()
        h.stamp = rospy.Time.now()
        h.frame_id = self.frame_id
        h.seq = self.seq
        self.seq = self.seq + 1

        self.imu_msg.header = h
        q = self.device.read_quaternion()
        self.imu_msg.orientation.x = q[0]
        self.imu_msg.orientation.y = q[1]
        self.imu_msg.orientation.z = q[2]
        self.imu_msg.orientation.w = q[3]

        g = self.device.read_gyroscope()
        # convert from deg/sec to rad/sec
        self.imu_msg.angular_velocity.x = g[0] * math.pi / 180.0
        self.imu_msg.angular_velocity.y = g[1] * math.pi / 180.0
        self.imu_msg.angular_velocity.z = g[2] * math.pi / 180.0
        a = self.device.read_linear_acceleration()
        self.imu_msg.linear_acceleration.x = a[0]
        self.imu_msg.linear_acceleration.y = a[1]
        self.imu_msg.linear_acceleration.z = a[2]
        self.imu_pub.publish(self.imu_msg)

        self.temp_msg.header = h
        self.temp_msg.temperature = self.device.read_temp()
        self.temp_pub.publish(self.temp_msg)

	e = self.device.read_euler()
	self.vector3_msg.x = e[0]
	self.vector3_msg.y = e[1]
	self.vector3_msg.z = e[2]
        self.euler_pub.publish(self.vector3_msg)

	#g = self.device.read_gravity()
        #self.vector3_msg.x = g[0]
        #self.vector3_msg.y = g[1]
        #self.vector3_msg.z = g[2]
        #self.gravity_pub.publish(self.vector3_msg)

        # self.reset_msgs()


def main():
    rospy.init_node('imu_driver')
    node = BNO055Driver()
    while not rospy.is_shutdown():
        node.publish_data()

if __name__ == '__main__':
    main()
