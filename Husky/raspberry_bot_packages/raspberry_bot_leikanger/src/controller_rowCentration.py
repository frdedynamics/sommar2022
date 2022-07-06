#!/usr/bin/env python

import rospy
import numpy as np
from std_msgs.msg import Float32, Bool
from geometry_msgs.msg import Twist



class controller_rowCentration(object):
    def __init__ (self):
        self.errorCalculator_sub = rospy.Subscriber("/raspberry_bot/controller_errorSignal", Float32, self.errorCalculator_callback) #Subscriber til controller errorSignal
        self.obstacle_detection_sub = rospy.Subscriber("/raspberry_bot/ObjectDetection", Bool, self.obstacle_detection_callback) #Subscriber til controller errorSignal
        self.row_end_detection_sub = rospy.Subscriber("/raspberry_bot/row_end_detection", Bool, self.row_end_detection_callback) #Subscriber til Lidar laserscan
        self.speed_pub = rospy.Publisher ("/husky_velocity_controller/cmd_vel", Twist, queue_size=1) #cmd_vel kommando Publisher

        self.errorCalculator_data = 0
        self.obstacleDetected = False
        self.row_end_detected = False

        self.row_end_detected_counter = 0

        self.controller_P = 0.1
        self.linearPaadrag = 0.5



        #Metode som leser controller errorSignal
    def errorCalculator_callback(self,data):
        self.errorCalculator_data = data.data
        #Metode som leser obstacle detection signal
    def obstacle_detection_callback(self,data):
        self.obstacleDetected = data.data
        #Metode som leser row end detection signal
    def row_end_detection_callback(self,data):
        self.row_end_detected = data.data

        #Metode som beregner paadrag basert pa errorSignal og publiserer ved en fast frekvens
    def controller(self, event=None):
        speed_cmd = Twist()
        speed_cmd.linear.x = self.linearPaadrag
        speed_cmd.angular.z = self.controller_P * self.errorCalculator_data

            #Dersom hindring er detektert stoppes robot
        if self.obstacleDetected:
            speed_cmd.linear.x = 0
            speed_cmd.angular.z = 0

            #Dersom row_end er detektert kjorer robot rett frem i 6 sekunder
            #Counter basert pa publikasjonsrate for loop (10Hz)
        if self.row_end_detected:
            speed_cmd.angular.z = 0
            self.row_end_detected_counter +=1
            if self.row_end_detected_counter > 60:
                speed_cmd.linear.x = 0

#        self.speed_pub.publish(speed_cmd)



def main():
    rospy.init_node('controller_rowCentration', anonymous=True)
    controller_rowCentration_object = controller_rowCentration()

    #Lager en timer for a kunne publisere til cmd ved et visst tidsintervall
    #dette for aa ikke faa lag paa kjoringen, da realsense/scan blir publiser
    #for sjeldent til aa unngaa lag
    rospy.Timer(rospy.Duration(1.0/10.0), controller_rowCentration_object.controller)

    try:
        rospy.spin()
    except KeyboardInterrupt:
        print("Shutting down")

if __name__ == '__main__':
    main()
