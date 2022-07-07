#!/usr/bin/env python

import rospy
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Float32
import numpy as np
from math import sin

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
        #Henter inn data fra og lagrer det som liste /realsense/LaserScan topic
        LaserScan_data = list(data.ranges)
        #Liste som lagrer forskjellen i distanse til midtpunkt pa hoyre og venstre laserpar
        laserPairError = []

        #Kalkulerer lengde fra der rekke blir detektert til midtpunkt forran robot for alle laserstraale par
        x = 0
        beamPair_errorList = []
        while x < self.beamstowatch:
            #Henter ut x'te strale fra liste
            venstre_laserbeam = LaserScan_data[len(LaserScan_data) - 1 - x]
            hoyre_laserbeam = LaserScan_data[x]

            #Ignorerer inf verdier (4.0)
            if not (venstre_laserbeam == 4.0 or hoyre_laserbeam == 4.0):
                #Regner ut vinkel pa x'te strale
                laserbeam_theta = data.angle_max + x * data.angle_increment

                #Regner ut avstand fra venstre og hoyre strale til midtpunkt forran robot
                venstre_laserbeam_toMid = sin(laserbeam_theta) * venstre_laserbeam
                hoyre_laserbeam_toMid =  sin(laserbeam_theta) * hoyre_laserbeam

                #Beregner forskjell mellom hoyre og venste straale til midtpunkt og legger verdien i liste
                beamPair_errorList.append(venstre_laserbeam_toMid - hoyre_laserbeam_toMid)

            #Setter error til 0 dersom robot ikke er mellom rekker
            if len(beamPair_errorList) == 0:
                beamPair_errorList.append(0.0)

            x += 1

        #Beregner gjenomsnittlig error for alle straleparene og publiserer i /raspberry_bot/controller_errorSignal topic
        beamPair_errorAvg = np.average(beamPair_errorList)
        self.errorCalculator_pub.publish(beamPair_errorAvg)


def main():
    rospy.init_node('controller_errorCalculator', anonymous=True)
    errorCalculator_object = errorCalculator()
    try:
        rospy.spin()
    except KeyboardInterrupt:
        print("Shutting down")

if __name__ == '__main__':
    main()
