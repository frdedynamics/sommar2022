#!/usr/bin/env python

import rospy
from std_srvs.srv import SetBool, SetBoolRequest
from raspberry_bot.srv import move_command, move_commandRequest
import time

class command_raspberry_bot(object):
    def rowCentering_program(self):
        while(True):
            #Kaller rowCentering service
            rowCentration_service_client = rospy.ServiceProxy("/raspberry_bot/rowFollwer/command", SetBool) #move service client
            rowCentration_service_request_object = SetBoolRequest() #Objekt for a requeste service rowCentration service
            rowCentration_service_request_object.data = True
            resultat = rowCentration_service_client(rowCentration_service_request_object)
            waiting = True
            while(waiting):
                time.sleep(1)
                if resultat.success:
                    waiting = False

            #Kjorer robot til ny rekke med 2 linear bevegelser og 2 rotasjoner

            move_command_service_client = rospy.ServiceProxy("/raspberry_bot/move/command", move_command) #move service client
            move_command_service_request_object = move_commandRequest() #Objekt for a requeste service fra move service

            #Kaller linear 2.5meter fra move service
            move_command_service_request_object.Bevegelse = "linear"
            move_command_service_request_object.Input = 2.5
            resultat = move_command_service_client(move_command_service_request_object)
            waiting = True
            while(waiting):
                time.sleep(1)
                if resultat.success:
                    waiting = False

            #Kaller rotasjon fra move service
            move_command_service_request_object.Bevegelse = "rotasjon"
            move_command_service_request_object.Input = -1.5
            resultat = move_command_service_client(move_command_service_request_object)
            waiting = True
            while(waiting):
                time.sleep(1)
                if resultat.success:
                    waiting = False

            #Kaller linear 2.3meter fra move service
            move_command_service_request_object.Bevegelse = "linear"
            move_command_service_request_object.Input = 2.2
            resultat = move_command_service_client(move_command_service_request_object)
            waiting = True
            while(waiting):
                time.sleep(1)
                if resultat.success:
                    waiting = False

            #Kaller rotasjon fra move service
            move_command_service_request_object.Bevegelse = "rotasjon"
            move_command_service_request_object.Input = -1.5
            resultat = move_command_service_client(move_command_service_request_object)
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
