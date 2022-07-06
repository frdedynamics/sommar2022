#!/usr/bin/env python

import rospy
import numpy as np
from std_msgs.msg import Float32, Bool
from std_srvs.srv import SetBool, SetBoolResponse
from geometry_msgs.msg import Twist
import time


class controller_rowCentration(object):
    def __init__ (self):
        self.errorCalculator_sub = rospy.Subscriber("/raspberry_bot/controller_errorSignal", Float32, self.errorCalculator_callback) #Subscriber til controller errorSignal
        self.obstacle_detection_sub = rospy.Subscriber("/raspberry_bot/ObjectDetection", Bool, self.obstacle_detection_callback) #Subscriber til controller errorSignal
        self.row_end_detection_sub = rospy.Subscriber("/raspberry_bot/row_end_detection", Bool, self.row_end_detection_callback) #Subscriber til Lidar laserscan
        self.speed_pub = rospy.Publisher ("/husky_velocity_controller/cmd_vel", Twist, queue_size=1) #cmd_vel kommando Publisher
        self.controller_rowFollower_service = rospy.Service("/raspberry_bot/rowFollwer/command", SetBool, self.controller_rowFollower_callback) #Subscriber til rowFollower command

        self.errorCalculator_data = 0
        self.obstacleDetected = False
        self.row_end_detected = False

        self.row_end_detected_counter = 0

        self.serviceCalled = False
        self.rowCenteringStarted = False

        self.controller_P = 0.4
        self.linearPaadrag = 0.5

        #Service call som kjores nar den blir requested
        #Service kaller controller metode som styrer rowcentration frem til
        #controller metode gir beskjed om at roboten er kommet til enden av rekken
    def controller_rowFollower_callback(self, request):
        self.serviceCalled = True

        rospy.loginfo("rowCentration service: Starting rowCentration.")

        while(self.serviceCalled):
            self.controller()
            time.sleep(0.1)

        response = SetBoolResponse()
        response.success = True

        rospy.loginfo("rowCentration service: End of row reached.")
        return response

        #Metode som leser controller errorSignal
    def errorCalculator_callback(self,data):
        self.errorCalculator_data = data.data
        #Metode som leser obstacle detection signal
    def obstacle_detection_callback(self,data):
        self.obstacleDetected = data.data
        #Metode som leser row end detection signal
    def row_end_detection_callback(self,data):
        self.row_end_detected = data.data
        #Variabel som settes hoy nar rowcentering har startet(row end ikke detektert betyr at algoritme kjorer)
        if not data.data:
            self.rowCenteringStarted = True

        #Metode som beregner paadrag basert pa errorSignal og publiserer ved en fast frekvens
    def controller(self, event=None):

        speed_cmd = Twist()
        speed_cmd.linear.x = self.linearPaadrag
        speed_cmd.angular.z = self.controller_P * self.errorCalculator_data

            #Dersom hindring er detektert stoppes robot
        if self.obstacleDetected:
            speed_cmd.linear.x = 0
            speed_cmd.angular.z = 0

            #Dersom row_end er detektert etter at sentrering er startet stopper robot
        if self.row_end_detected and self.rowCenteringStarted:
            speed_cmd.linear.x = 0
            speed_cmd.angular.z = 0
            self.serviceCalled = False
            self.rowCenteringStarted = False

        self.speed_pub.publish(speed_cmd)



def main():
    rospy.init_node('controller_rowCentration', anonymous=True)
    controller_rowCentration_object = controller_rowCentration()

    try:
        rospy.spin()
    except KeyboardInterrupt:
        print("Shutting down")

if __name__ == '__main__':
    main()
