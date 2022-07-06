#!/usr/bin/env python

import rospy
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Bool
import numpy as np

    #Node skal varsle om at ende av rekke er detektert. Dette gjores ved a
    #oppdage om strale lengst mot venstre eller hoyre gar til max value

class row_end_detection(object):

    def __init__(self):
        self.LaserScan_sub = rospy.Subscriber("/realsense/LaserScan", LaserScan, self.LaserScan_callback) #Subscriber til Lidar laserscan
        self.row_end_detection_pub = rospy.Publisher ("/raspberry_bot/row_end_detection", Bool, queue_size=1) #Publisher for ObjectDetection

        self.row_end_detected = False
        #rows to watch for row detection
        self.rowsToWatch = 10

        #Variabel som velger om programmet skal betrakte straler pa venstre eller hoyre side
        self.sidevelger = "VENSTRE"


        #Metode som kjores hver gang det publiseres i /lidar/LaserScan topic
    def LaserScan_callback(self, data):
        LaserScan_data = data.ranges
        LaserScan_inf = data.range_max + 1.0

        #Kontrollerer om straler lengst mot hoyre eller venstre gar mot max
        x = 0
        rowBeamsInf = 0
        while(x < self.rowsToWatch):
            if (((LaserScan_data[x] == LaserScan_inf) and self.sidevelger == "HOYRE") or ((LaserScan_data[len(LaserScan_data)-1 - x] == LaserScan_inf) and self.sidevelger == "VENSTRE")):
                rowBeamsInf += 1
            x += 1

        #row end detektert dersom kriterie nok straler gar mot inf
        if rowBeamsInf >= self.rowsToWatch:
            self.row_end_detected = True
        else:
            self.row_end_detected = False

        #Publiserer row end detection status
        self.row_end_detection_pub.publish(self.row_end_detected)


def main():
    rospy.init_node('row_end_detection', anonymous=True)
    row_end_detection_object = row_end_detection()
    try:
        rospy.spin()
    except KeyboardInterrupt:
        print("Shutting down")

if __name__ == '__main__':
    main()
