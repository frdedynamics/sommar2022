#!/usr/bin/env python

import rospy
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Bool
import numpy as np

class obstacle_detection(object):

    def __init__(self):
        self.LaserScan_sub = rospy.Subscriber("/realsense/scan", LaserScan, self.LaserScan_callback) #Subscriber til Lidar laserscan
        self.ObjectDetection_pub = rospy.Publisher ("/raspberry_bot/ObjectDetection", Bool, queue_size=1) #Publisher for ObjectDetection

        self.ObjectDetected = False

        #Node skal varsle om at det er detektert objekt dersom > beamslimit antall
        #laserstraler viser at et objekt er naermere enn stopDistance meter
        self.stopDistance = 1
        self.beamslimit = 5

        #Metode som kjores hver gang det publiseres i /lidar/LaserScan topic
    def LaserScan_callback(self, data):
        LaserScan_data = data.ranges

        #Kontrollerer hvor mange laserstraler som er under grenseverdien og varsler
        #om at objekt er detektert dersom flere laserstraaler enn beamslimit er
        #under stopDistance
        beamsDetected = 0
        for x in LaserScan_data:
            if x < self.stopDistance:
                beamsDetected += 1
        if beamsDetected >= self.beamslimit:
            self.ObjectDetected = True
        else:
            self.ObjectDetected = False

        #Publiserer ObjectDetection status
        self.ObjectDetection_pub.publish(self.ObjectDetected)






def main():
    rospy.init_node('obstacle_detection', anonymous=True)
    obstacle_detectionr_object = obstacle_detection()
    try:
        rospy.spin()
    except KeyboardInterrupt:
        print("Shutting down")

if __name__ == '__main__':
    main()
