#!/usr/bin/env python

import rospy
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Twist
from std_msgs.msg import Bool
from turtlesim.srv import Spawn, SpawnResponse
import time
import math

class service_controller_move(object):
    def __init__ (self):
        self.Odometry_sub = rospy.Subscriber("/raspberry_bot/Odometry_euler_odom", Odometry, self.Odometry_callback) #Subscriber til Odometry topic
#        self.GPS_orientation_sub = rospy.Subscriber("/raspberry_bot/Odometry_euler_odom_GPS", Odometry, self.GPS_orientation_callback) #Subscriber til Odometry topic
        self.move_command_service = rospy.Service("/raspberry_bot/move/command", Spawn, self.move_command_callback) #Subscriber til move_command service call topic
        self.obstacle_detection_sub = rospy.Subscriber("/raspberry_bot/ObjectDetection", Bool, self.obstacle_detection_callback) #Subscriber til controller errorSignal
        self.speed_pub = rospy.Publisher ("/husky_velocity_controller/cmd_vel", Twist, queue_size=1) #cmd_vel kommando Publisher

        self.obstacleDetected = False

        self.Odometry_data = Odometry()
#        self.GPS_orientation_data = Odometry()
        self.speed_cmd = Twist()


        #Leser odometry data fra Odometry_euler_odom topic
    def Odometry_callback(self, data):
        self.Odometry_data = data.pose.pose
	self.GPS_orientation_data = data.pose.pose
        #Leser GPS_orientation data fra Odometry_euler_odom_gps topic
#    def GPS_orientation_callback(self, data):
#        self.GPS_orientation_data = data.pose.pose
        #Metode som leser obstacle detection signal
    def obstacle_detection_callback(self,data):
        self.obstacleDetected = data.data



        #Service call som kjores nar den blir requested
    def move_command_callback(self, request):

        #Kjorer dersom rotasjon er requested
        if request.name == "rotasjon":
            rospy.loginfo("move service: Rotating robot %.2f radians.", request.x)
            self.rotasjon(request)


        #Kjorer dersom linear bevegelse er requested
        if request.name == "linear":
            rospy.loginfo("move service: Driving robot %.2f meters.", request.x)
            self.linear(request)

        #Stopper robot nar mal er nadd
        rospy.loginfo("move service: Target reached")
        self.speed_cmd.linear.x = 0
        self.speed_cmd.angular.z = 0
        self.speed_pub.publish(self.speed_cmd)

        response = SpawnResponse()
        response.name = "Move kommand utfort!"
        return response

        #Metode som roterer roboten basert pa odometry
    def rotasjon(self, request):
        #Beregner target basert pa navaerende odometry
        target = self.Odometry_data.orientation.z + request.x

        #Fixer issue dersom robot ma passere 0/360 grader punktet positiv retning
        if target >= 2*math.pi:
            target -= 2*math.pi
            while(self.Odometry_data.orientation.z > math.pi):
                self.speed_cmd.angular.z = 0.3

                self.speed_pub.publish(self.speed_cmd)
                time.sleep(0.1)
        #Fixer issue dersom robot ma passere 0/360 grader punktet negativ retning
        if target < 0:
            target += 2*math.pi
            while(self.Odometry_data.orientation.z < math.pi):
                self.speed_cmd.angular.z = -0.3

                self.speed_pub.publish(self.speed_cmd)
                time.sleep(0.1)

        #Hoyre rotasjon
        if request.x >= 0:

            while(self.Odometry_data.orientation.z < target):
                self.speed_cmd.angular.z = 0.3

                self.speed_pub.publish(self.speed_cmd)
                time.sleep(0.1)

        #Venstre rotasjon
        if request.x < 0:

            while(self.Odometry_data.orientation.z > target):
                self.speed_cmd.angular.z = -0.3

                self.speed_pub.publish(self.speed_cmd)
                time.sleep(0.1)

        #Metode som kjorer roboten linear frem til target basert pa odometry
    def linear(self, request):
        #Lagrer start pose
        startPose_X = self.Odometry_data.position.x
        startPose_Y = self.Odometry_data.position.y
        distanceMoved = 0

        #Kjorer robot fremmover til target distanse er nadd
        targetReached = False
        while(not targetReached):
            self.speed_cmd.linear.x = 0.3

                #Dersom hindring er detektert stoppes robot
            if self.obstacleDetected:
                self.speed_cmd.linear.x = 0
                self.speed_cmd.angular.z = 0

            self.speed_pub.publish(self.speed_cmd)

            #Sjekker om target er reached
            distanceMoved = math.hypot(self.Odometry_data.position.x - startPose_X, self.Odometry_data.position.y - startPose_Y)
            if distanceMoved > request.x:
                targetReached = True
            time.sleep(0.1)




def main():
    rospy.init_node('service_controller_move', anonymous=True)
    service_controller_move_object = service_controller_move()


    try:
        rospy.spin()
    except KeyboardInterrupt:
        print("Shutting down")

if __name__ == '__main__':
    main()
