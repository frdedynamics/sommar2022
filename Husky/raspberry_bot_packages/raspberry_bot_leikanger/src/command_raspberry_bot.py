#!/usr/bin/env python

import rospy
import roslaunch
from std_srvs.srv import SetBool, SetBoolRequest
from turtlesim.srv import Spawn, SpawnRequest
import time

class command_raspberry_bot(object):
    def rowCentering_program(self):

	while(True):
	        #Kaller rowCentering service
	        self.rowCentering()

	        #Kjorer robot 2.0 meter frem, ut av telt
#	        bevegelse = "linear"
#	        input = 2.0
#	        self.move_command(bevegelse, input)

	        #Roterer robot mot neste rekke
	        bevegelse = "rotasjon"
	        input = 1.5
	        self.move_command(bevegelse, input)

	        #Kjorer robot 2.8 meter frem, mot telt
	        bevegelse = "linear"
	        input = 2.8
	        self.move_command(bevegelse, input)

	        #Roterer robot inn mot neste rekke
	        bevegelse = "rotasjon"
	        input = 1.45
	        self.move_command(bevegelse, input)

	        #Kjorer robot 1 meter frem, mot telt
#	        bevegelse = "linear"
#	        input = 1.5
#	        self.move_command(bevegelse, input)

	        #Kaller rowCentering service
	        self.rowCentering()

	        #Kjorer robot frem 1.5 meter frem
	        bevegelse = "linear"
	        input = 1.5
	        self.move_command(bevegelse, input)

	        #Roterer robot mot neste rekke
	        bevegelse = "rotasjon"
	        input = 1.30
	        self.move_command(bevegelse, input)

	        #Kjorer robot 2.8 meter frem
	        bevegelse = "linear"
	        input = 2.8
	        self.move_command(bevegelse, input)

	        #Roterer robot mot rekke
	        bevegelse = "rotasjon"
	        input = 1.35
	        self.move_command(bevegelse, input)

        #Waypoint nav metode
    def start_waypointnav(self, input):
        rospy.loginfo("Starting waypoint navigation...")

        uuid = roslaunch.rlutil.get_or_generate_uuid(None, False)
        roslaunch.configure_logging(uuid)
        launch = roslaunch.parent.ROSLaunchParent(uuid, [input])
        launch.start()
        rospy.loginfo("started")
        launch.spin()

        rospy.loginfo("shutdown")


        #Move command metode
    def move_command(self, bevegelse, input):
        move_command_service_client = rospy.ServiceProxy("/raspberry_bot/move/command", Spawn) #move service client
        move_command_service_request_object = SpawnRequest() #Objekt for a requeste service fra move service
        move_command_service_request_object.name = bevegelse
        move_command_service_request_object.x = input
        resultat = move_command_service_client(move_command_service_request_object)
        waiting = True
        while(waiting):
            time.sleep(1)
            if resultat.name == "Move kommand utfort!":
                waiting = False

        #Row centering metode
    def rowCentering(self):
        rowCentration_service_client = rospy.ServiceProxy("/raspberry_bot/rowFollwer/command", SetBool) #move service client
        rowCentration_service_request_object = SetBoolRequest() #Objekt for a requeste service rowCentration service
        rowCentration_service_request_object.data = True
        resultat = rowCentration_service_client(rowCentration_service_request_object)
        waiting = True
        while(waiting):
            time.sleep(1)
            if resultat.success:
                waiting = False


def main():
    rospy.init_node('command_raspberry_bot', anonymous=True)
    command_raspberry_bot_object = command_raspberry_bot()
    #Kjorer rowCentering_program
    command_raspberry_bot_object.rowCentering_program()

    try:
        rospy.spin()

    except KeyboardInterrupt:
        print("Shutting down")

if __name__ == '__main__':
    main()
