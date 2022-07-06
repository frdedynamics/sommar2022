#!/usr/bin/env python

import rospy
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Float32
import numpy as np

#Denne noden tar henter inn data fra /realsense/LaserScan topic, og beregner hvor
#stor avstand det er til objekt pa venstre side av roboten ifht hoyre side.
#Denne forskjellen blir publisert i /raspberry_bot/controller_errorSignal topic

class errorCalculator(object):

    def __init__(self):

        self.LaserScan_sub = rospy.Subscriber("/realsense/LaserScan",LaserScan,self.LaserScan_callback) #Subscriber til LaserScan topic fra pointcloud_to_laserscan topic
        self.errorCalculator_pub = rospy.Publisher ("/raspberry_bot/controller_errorSignal", Float32, queue_size=1) #Publisher for a publisere kalkulert feil mellom avstand til hoyre og venstre baerrekke
        self.beamstowatch = 5 #Antall laserstraalen i som skal observeres for a finne snittavstand til venstre og hoyre baerrekke

        #Metode som kjores hver gang det publiseres data pa LaserScan topic
    def LaserScan_callback(self,data):

        #Henter inn data fra /realsense/LaserScan topic
        LaserScan_data = list(data.ranges)

        #Fjerner forste inf(3.0) verdi for a ikke forstyrre regulator error nar robot kommer til ende av rekke
        while max(LaserScan_data) == 3.0:
            LaserScan_data.remove(3.0)

        #Beregner gjennomsnittslengder pa avstand til venstre og hoyre baerrekke
        LaserScan_leftside = LaserScan_data[len(LaserScan_data)-self.beamstowatch:len(LaserScan_data)]
        LaserScan_leftside_avg = np.average(LaserScan_leftside)
        LaserScan_rightside = LaserScan_data[0:self.beamstowatch]
        LaserScan_rightside_avg = np.average(LaserScan_rightside)

        #Regner ut forskjelleng i avstand til venstre og hoyre baerrekke og publiserer dette i /raspberry_bot/controller_errorSignal topic
        LaserScan_rowCentering_error = LaserScan_leftside_avg - LaserScan_rightside_avg
        self.errorCalculator_pub.publish(LaserScan_rowCentering_error)


def main():
    rospy.init_node('controller_errorCalculator', anonymous=True)
    errorCalculator_object = errorCalculator()
    try:
        rospy.spin()
    except KeyboardInterrupt:
        print("Shutting down")

if __name__ == '__main__':
    main()
