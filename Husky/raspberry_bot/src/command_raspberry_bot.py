#!/usr/bin/env python

import rospy
import roslaunch
from std_srvs.srv import SetBool, SetBoolRequest
from raspberry_bot.srv import move_command, move_commandRequest
import time

class command_raspberry_bot(object):
    def command_program(self):

        #Kjorer robot til forste rekke pa forste telt
        input = "/home/aril/catkin_ws/src/mbs/mbs_husky_waypoint_navigation/launch/include/send_goals_1.launch"
        self.start_waypointnav(input)

        #Kaller rotasjon fra move service
        bevegelse = "rotasjon"
        input = 1.5
        self.move_command(bevegelse, input)


        #Kaller rowfollowing service
        self.rowFollowing()

        #Kjorer robot 2.5 meter frem, ut av telt
        bevegelse = "linear"
        input = 2.5
        self.move_command(bevegelse, input)

        #Kjorer robot til andre rekke pa forste telt
        input = "/home/aril/catkin_ws/src/mbs/mbs_husky_waypoint_navigation/launch/include/send_goals_2.launch"
        self.start_waypointnav(input)

        #Roterer robot inn mot telt
        bevegelse = "rotasjon"
        input = 4.7
        self.move_command(bevegelse, input)

        #Kjorer robot 1.0 meter frem, mot telt
        bevegelse = "linear"
        input = 1.0
        self.move_command(bevegelse, input)

        #Kaller rowfollowing service
        self.rowFollowing()

        #Kjorer robot 2.5 meter frem, ut av telt
        bevegelse = "linear"
        input = 2.5
        self.move_command(bevegelse, input)

        #Kjorer robot til forste rekke pa andre telt
        input = "/home/aril/catkin_ws/src/mbs/mbs_husky_waypoint_navigation/launch/include/send_goals_3.launch"
        self.start_waypointnav(input)

        #Roterer robot inn mot telt
        bevegelse = "rotasjon"
        input = 1.5
        self.move_command(bevegelse, input)

        #Kjorer robot 1.0 meter frem, mot telt
        bevegelse = "linear"
        input = 1.0
        self.move_command(bevegelse, input)

        #Kaller rowfollowing service
        self.rowFollowing()

        #Kjorer robot 2.5 meter frem, ut av telt
        bevegelse = "linear"
        input = 2.5
        self.move_command(bevegelse, input)

        #Kjorer robot til andre rekke pa andre telt
        input = "/home/aril/catkin_ws/src/mbs/mbs_husky_waypoint_navigation/launch/include/send_goals_4.launch"
        self.start_waypointnav(input)

        #Roterer robot inn mot telt
        bevegelse = "rotasjon"
        input = 4.7
        self.move_command(bevegelse, input)

        #Kjorer robot 1.0 meter frem, mot telt
        bevegelse = "linear"
        input = 1.0
        self.move_command(bevegelse, input)

        #Kaller rowfollowing service
        self.rowFollowing()

        #Kjorer robot 2.5 meter frem, ut av telt
        bevegelse = "linear"
        input = 2.5
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
        move_command_service_client = rospy.ServiceProxy("/raspberry_bot/move/command", move_command) #move service client
        move_command_service_request_object = move_commandRequest() #Objekt for a requeste service fra move service
        move_command_service_request_object.Bevegelse = bevegelse
        move_command_service_request_object.Input = input
        resultat = move_command_service_client(move_command_service_request_object)
        waiting = True
        while(waiting):
            time.sleep(1)
            if resultat.success:
                waiting = False

        #Rowfollower metode
    def rowFollowing(self):
        rowCentration_service_client = rospy.ServiceProxy("/raspberry_bot/rowFollwer/command", SetBool) #move service client
        rowCentration_service_request_object = SetBoolRequest() #Objekt for a requeste service rowCentration service
        rowCentration_service_request_object.data = True
        resultat = rowCentration_service_client(rowCentration_service_request_object)
        waiting = True
        while(waiting):
            time.sleep(1)
            if resultat.success:
                waiting = False

        #Rowcentering metode
    def rowCentering(self):
        rowCentration_service_client = rospy.ServiceProxy("/raspberry_bot/rowCentering/command", SetBool) #move service client
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
    #Kjorer command_program
    command_raspberry_bot_object.command_program()

    try:
        rospy.spin()

    except KeyboardInterrupt:
        print("Shutting down")

if __name__ == '__main__':
    main()
