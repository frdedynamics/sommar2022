#!/usr/bin/env python

import rospy
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Float32, String
import numpy as np
from math import sin

#Denne noden tar henter inn data fra /realsense/LaserScan topic, og beregner hvor
#stor avstand det er til objekt pa venstre side av roboten ifht hoyre side.
#Denne forskjellen blir publisert i /raspberry_bot/controller_errorSignal topic

class errorCalculator(object):

    def __init__(self):

        self.LaserScan_sub = rospy.Subscriber("/realsense/LaserScan",LaserScan,self.LaserScan_callback) #Subscriber til LaserScan topic fra pointcloud_to_laserscan topic
        self.errorCalculator_pub = rospy.Publisher ("/raspberry_bot/controller_errorSignal", Float32, queue_size=1) #Publisher for a publisere kalkulert feil mellom avstand til hoyre og venstre baerrekke
	self.sidechooser_sub = rospy.Subscriber("/raspberry_bot/sideChooser", String, self.sideChooser_callback) 
	self.beamstowatch = 5 #Antall laserstraalen i som skal observeres for a finne snittavstand til venstre og hoyre baerrekke

        #Variabel som velger om programmet skal beregne straler pa venstre eller hoyre side
        self.sidevelger = "VENSTRE"
        #Variabel som velger avstand robot skal holde til rekke
        self.avstand = 1.0

        #Metode som kjores hver gang det publiseres data pa LaserScan topic
    def sideChooser_callback(self, data):
	self.sidevelger = data

    def LaserScan_callback(self,data):
        #Henter inn data fra og lagrer det som liste /realsense/LaserScan topic
        LaserScan_data = list(data.ranges)
        #Liste som lagrer forskjellen i distanse til midtpunkt pa hoyre og venstre laserpar
        laserPairError = []

        #Kalkulerer lengde fra der rekke blir detektert til midtpunkt forran robot for alle laserstraale par
        x = 0
        beamValues_list = []
        while x < self.beamstowatch:
            #Henter ut x'te strale fra liste
            venstre_laserbeam = LaserScan_data[len(LaserScan_data) - 1 - x]
            hoyre_laserbeam = LaserScan_data[x]

            #Ignorerer inf verdier (3.0)
            if not ((venstre_laserbeam == 4.0 and self.sidevelger == "VENSTRE") or (hoyre_laserbeam == 4.0 and self.sidevelger == "HOYRE")):
                #Regner ut vinkel pa x'te strale
                laserbeam_theta = data.angle_max + x * data.angle_increment

                #Regner ut avstand fra venstre og hoyre strale til midtpunkt forran robot
                venstre_laserbeam_toMid = sin(laserbeam_theta) * venstre_laserbeam
                hoyre_laserbeam_toMid =  sin(laserbeam_theta) * hoyre_laserbeam

                #Legger strale verdiene i liste
                if self.sidevelger == "VENSTRE":
                    beamValues_list.append(venstre_laserbeam_toMid)

                if self.sidevelger == "HOYRE":
                    beamValues_list.append(hoyre_laserbeam_toMid)

            #Setter error til 0 dersom robot ikke er mellom rekker
            if len(beamValues_list) == 0:
                beamValues_list.append(0.0)

            x += 1

        #Beregner error mellom gjennomsnittet av stralene og avstands verdi
        beamValues_Avg = np.average(beamValues_list)
	if self.sidevelger == "VENSTRE":
        	error = beamValues_Avg - self.avstand
	elif self.sidevelger == "HOYRE":
		error = self.avstand - beamValues_Avg
        if beamValues_Avg == 0:
            error = 0.0
        self.errorCalculator_pub.publish(error)


def main():
    rospy.init_node('controller_errorCalculator', anonymous=True)
    errorCalculator_object = errorCalculator()
    try:
        rospy.spin()
    except KeyboardInterrupt:
        print("Shutting down")

if __name__ == '__main__':
    main()
