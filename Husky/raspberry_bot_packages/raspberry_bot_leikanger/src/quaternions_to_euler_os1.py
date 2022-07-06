#!/usr/bin/env python

import rospy
from nav_msgs.msg import Odometry
from sensor_msgs.msg import Imu
from tf.transformations import euler_from_quaternion
import math

#Transformerer odomentry informasjonen fra quaternions to euler vinkler ved hjelp av tf.transformations

class quaternions_to_euler(object):
    def __init__ (self):
        self.odometry_sub = rospy.Subscriber("/os1_cloud_node/imu", Imu, self.odometry_callback) #Subscriber til Odometry topic
        self.Odometry_euler_pub = rospy.Publisher ("/raspberry_bot/Odometry_euler_GPS", Odometry, queue_size=1) #Publiserer odometry i euler vinkler

        #Kjores hver gang det kommer ny data i odometry topic
    def odometry_callback(self, data):
        # Henter data fra odometry topic og legger x, y, z og w verdiene i en liste
        orientering_quaternions = data.orientation
        orientering_liste = [orientering_quaternions.x, orientering_quaternions.y, orientering_quaternions.z, orientering_quaternions.w]

        #Bruker tf.transformations funksjon for a konvertere
        (roll, pitch, yaw) = euler_from_quaternion(orientering_liste)

        #Konverterer vinkler i 3 og 4 kvadrant om til omradet 3.14 - 6.28
        if yaw < 0:
            yaw += 2*math.pi

        #Publiserer odometryen med euler vinkler
        Odometry_euler = Odometry()
        Odometry_euler.pose.pose.orientation.z = yaw
        self.Odometry_euler_pub.publish(Odometry_euler)



def main():
    rospy.init_node('quaternions_to_euler', anonymous=True)
    quaternions_to_euler_object = quaternions_to_euler()


    try:
        rospy.spin()
    except KeyboardInterrupt:
        print("Shutting down")

if __name__ == '__main__':
    main()
