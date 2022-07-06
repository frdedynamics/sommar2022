#!/usr/bin/env python

import rospy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
import cv2
import numpy as np
from geometry_msgs.msg import Twist

class rowCentrator_edgeDetection(object):
    def __init__(self):
        self.image_sub = rospy.Subscriber("/camera/color/image_raw", Image, self.camera_callback) #Subscriber til image_raw topic fra realsense kamera
        self.bridge_object = CvBridge() #Definerer bridge objekt av type CvBridge som brukes for a konvertere bilde til og fra OpenCV format
        self.speed_pub = rospy.Publisher ("/cmd_vel", Twist, queue_size=1) #Publisher for a publisere hastighetskommandoer til Husky
        self.bluredImg_pub = rospy.Publisher ("/raspberry_bot/blured_img", Image, queue_size=1) #Publisher for a visualisere blured image
        self.cropedImg_pub = rospy.Publisher ("/raspberry_bot/croped_img", Image, queue_size=1) #Publisher for a visualisere croped image
        self.cannyImg_pub = rospy.Publisher("/raspberry_bot/canny_img", Image, queue_size=1) #Publisher for a visualisere canny image
        self.dilatedImg_pub = rospy.Publisher ("/raspberry_bot/dilated_img", Image, queue_size=1) #Publisher for a visualisere dilated image
        self.convertedBitwiseImg_pub = rospy.Publisher ("/raspberry_bot/convertedBitwise_img", Image, queue_size=1) #Publisher for a visualisere convertedBitwise image


        #Metode for a lese bilde fra realsense image topic. Kjores hver gang nytt bilde blir publisert i topic
    def camera_callback(self,data):
        try:
            cv_image = self.bridge_object.imgmsg_to_cv2(data, desired_encoding="bgr8") #Konverterer bilde til OpenCv format
        except CvBridgeError as e:
            print(e)

        #Skalerer ned bilde for a spare datakraft
        height, width, channels = cv_image.shape
        descentre = 100
        rows_to_watch = 60
        crop_img = cv_image[(height)/2+descentre:(height)/2+(descentre+rows_to_watch)][1:width]

        #Blurer bildet for a redusere antall kanter som blir detektert i canny algoritme
        blur = cv2.GaussianBlur(crop_img, (5,5), cv2.BORDER_DEFAULT)

        #Detekterer kanter i bilde
        canny = cv2.Canny(blur, 50, 175)

        #Gjor kantene tydligere/tykkere ved hjelp av dilate
        dilated = cv2.dilate(canny, (7,7), iterations=7)


        #Konverterer bildet for a kunne bruke samme kalkulasjonsalgoritme som
        #i controller_rgbFilter
        converterd_bitwiseNot = cv2.bitwise_not(dilated)


        #Konverterer bilde tilbake til sensor_msgs format og publiserer for visualiseing i Rviz
        try:
            self.bluredImg_pub.publish(self.bridge_object.cv2_to_imgmsg(blur, "8UC3"))
            self.cropedImg_pub.publish(self.bridge_object.cv2_to_imgmsg(crop_img, "8UC3"))
            self.cannyImg_pub.publish(self.bridge_object.cv2_to_imgmsg(canny, "8UC1"))
            self.dilatedImg_pub.publish(self.bridge_object.cv2_to_imgmsg(dilated, "8UC1"))
            self.convertedBitwiseImg_pub.publish(self.bridge_object.cv2_to_imgmsg(converterd_bitwiseNot, "8UC1"))

        except CvBridgeError as e:
            print(e)

        #Kalkulerer midtpunkt pa kjorefelt i masket bilde
        m = cv2.moments(converterd_bitwiseNot, False)
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
        speed_cmd.linear.x =0;
        speed_cmd.angular.z = P * error_x;

        self.speed_pub.publish(speed_cmd)






def main():
    rospy.init_node('rowCentering_edgeDetection_node', anonymous=True)
    rowCentrator_edgeDetection_objetct = rowCentrator_edgeDetection()
    try:
        rospy.spin()
    except KeyboardInterrupt:
        print("Shutting down")

if __name__=='__main__':
    main()
