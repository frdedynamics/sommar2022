#!/usr/bin/env python

import rospy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
import cv2
import numpy as np
from geometry_msgs.msg import Twist

class rowCentrator_edgeDetection(object):
    def __init__(self):
        self.image_sub = rospy.Subscriber("/realsense/depth/image_rect_raw", Image, self.camera_callback) #Subscriber til dybde bilde topic fra realsense kamera
        self.bridge_object = CvBridge() #Definerer bridge objekt av type CvBridge som brukes for a konvertere bilde til og fra OpenCV format
        self.speed_pub = rospy.Publisher ("/cmd_vel", Twist, queue_size=1) #Publisher for a publisere hastighetskommandoer til Husky
        self.cropedImg_pub = rospy.Publisher("/raspberry_bot/croped_img", Image, queue_size=1) #Publisher for a visualisere croped image
        self.maskedImg_pub = rospy.Publisher("/raspberry_bot/masked_img", Image, queue_size=1) #Publisher for a visualisere masked image

        #Metode for a lese bilde fra realsense depth image topic. Kjores hver gang nytt bilde blir publisert i topic
    def camera_callback(self,data):
        try:
            cv_image = self.bridge_object.imgmsg_to_cv2(data, desired_encoding="passthrough") #Konverterer bilde til OpenCv format
        except CvBridgeError as e:
            print(e)


        #Skalerer ned bilde for a spare datakraft
        height, width = cv_image.shape
        descentre = 100
        rows_to_watch = 60
        crop_img = cv_image[(height)/2+descentre:(height)/2+(descentre+rows_to_watch)][1:width]

        #Definerer ovre og nedre grense for farge som skal markeres i bilde
        upper_intensity = np.array([5])
        lower_intensity = np.array([2])

        #Bruker maske paa bildet
        mask = cv2.inRange(crop_img, lower_intensity, upper_intensity)

        #Konverterer bilde tilbake til sensor_msgs format og publiserer for visualiseing i Rviz
        try:
            self.cropedImg_pub.publish(self.bridge_object.cv2_to_imgmsg(crop_img, "32FC1"))
            self.maskedImg_pub.publish(self.bridge_object.cv2_to_imgmsg(mask, "8UC1"))
        except CvBridgeError as e:
            print(e)

        #Kalkulerer midtpunkt pa kjorefelt i masket bilde
        m = cv2.moments(mask, False)
        try:
            cx, cy = m['m10']/m['m00'], m['m01']/m['m00']
        except ZeroDivisionError:
            cy, cx = height/2, width/2

        #Enkel P kontroller for kjoring langs midten av kjorefelt
        #Beregner hvor midtpunktet pa bildet er ifht midtpunkt mellom svarte felt i masket bilde
        #Dersom midtpunktene er i samme punkt er robot sentrert, altsa error = 0
        P = 0.005
        error_x = -(cx - width / 2);
        speed_cmd = Twist();
        speed_cmd.linear.x = 2;
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
