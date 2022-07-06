#!/usr/bin/env python

import rospy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
import cv2
import numpy as np
from geometry_msgs.msg import Twist


class rowCentrator_rgb(object):
    def __init__(self):

        self.image_sub = rospy.Subscriber("/realsense/color/image_raw",Image,self.camera_callback) #Subscriber til image_raw topic fra realsense kamera
        self.bridge_object = CvBridge() #Definerer bridge objekt av type CvBridge som brukes for a konvertere bilde til og fra OpenCV format
        #self.speed_pub = rospy.Publisher ("/cmd_vel", Twist, queue_size=1) #Publisher for a publisere bevegelsekommandoer til Husky
        self.cropedImg_pub = rospy.Publisher ("/raspberry_bot/croped_img", Image, queue_size=1) #Publisher for a visualisere cropped image
        self.maskedImg_pub = rospy.Publisher ("/raspberry_bot/masked_img", Image, queue_size=1) #Publisher for a visualisere masked image

        #Funksjon for a lese bilde fra realsense image topic. Kjores hver gang nytt bilde blir publisert i topic
    def camera_callback(self,data):
        try:
            cv_image = self.bridge_object.imgmsg_to_cv2(data, desired_encoding="bgr8") #Konvertert bilde til bgr8 format (OpenCV format)
        except CvBridgeError as e:
            print(e)

        #Skalerer ned bilde for a spare datakraft
        height, width, channels = cv_image.shape
        descentre = 160
        rows_to_watch = 60
        crop_img = cv_image[(height)/2+descentre:(height)/2+(descentre+rows_to_watch)][1:width]

        #Konverterer bildet fra RGB til HSV format
        hsv = cv2.cvtColor(crop_img, cv2.COLOR_BGR2HSV)

        #Definerer ovre og nedre grense for farge som skal markeres i bilde
        upper_green = np.array([100,255,150])
        lower_green = np.array([1,200,50])

        #Bruker maske paa bildet
        mask = cv2.inRange(hsv, lower_green, upper_green)

        #Konverterer bilde tilbake til sensor_msgs format for a kunne publisere og visualisere i Rviz
        try:
            croped_sensor_msgs_format = self.bridge_object.cv2_to_imgmsg(hsv, "bgr8")
            masked_sensor_msgs_format = self.bridge_object.cv2_to_imgmsg(mask, "8UC1")
            self.cropedImg_pub.publish(croped_sensor_msgs_format)
            self.maskedImg_pub.publish(masked_sensor_msgs_format)
        except CvBridgeError as e:
            print(e)


        #Kalkulerer midtpunkt paa kjorefelt i masket bilde
        m = cv2.moments(mask, False)
        try:
            cx, cy = m['m10']/m['m00'], m['m01']/m['m00']
        except ZeroDivisionError:
            cy, cx = height/2, width/2

        #Enkel P kontroller for kjoring langs midten av kjorefelt
        #Beregner hvor midtpunktet pa bildet er ifht midtpunkt mellom svarte felt i masket bilde
        #Dersom midtpunktene er i samme punkt er robot sentrert, altsa error = 0
        P = 0.01
        error_x = -(cx - width / 2);
        speed_cmd = Twist();
        speed_cmd.linear.x = 1;
        speed_cmd.angular.z = P * error_x ;

        #Publiserer hastighetene
        #self.speed_pub.publish(speed_cmd)




def main():
    rospy.init_node('RowCentrator_rgb_node', anonymous=True)
    rowCentrator_rgb_object = rowCentrator_rgb()
    try:
        rospy.spin()
    except KeyboardInterrupt:
        print("Shutting down")

if __name__ == '__main__':
    main()
