#!/usr/bin/env python3
import rospy
import cv2
import numpy as np
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError

class Goz:
    def __init__(self):
        rospy.init_node('kamera_sistemi', anonymous=True)
        self.bridge = CvBridge()
        self.son_resim = None
        self.yeni_veri_var = False

        # Kamera abone ol
        rospy.Subscriber("/bottom_cam/camera/image", Image, self.goruntu_callback)
        print(">> Kamera başlatıldı.")

    def goruntu_callback(self, data):
        try:
            self.son_resim = self.bridge.imgmsg_to_cv2(data, "bgr8")
            self.yeni_veri_var = True
        except CvBridgeError as e:
            print(e)

    def islem_yap(self):
        rate = rospy.Rate(30)
        while not rospy.is_shutdown():
            if self.yeni_veri_var and self.son_resim is not None:
                # 1. Resmi HSV formatına çevir (Renk bulmak için en iyisi budur)
                hsv_resim = cv2.cvtColor(self.son_resim, cv2.COLOR_BGR2HSV)

                # 2. Hangi rengi arıyoruz? (Kırmızı - Turuncu arası tonlar)
                # HSV Değerleri: [Renk Özü, Doygunluk, Parlaklık]
                alt_sinir = np.array([0, 100, 100])   # Koyu Kırmızı
                ust_sinir = np.array([20, 255, 255])  # Açık Turuncu

                # 3. Maskeleme yap (Sadece bu aralıktaki pikselleri BEYAZ yap, gerisi SİYAH)
                maske = cv2.inRange(hsv_resim, alt_sinir, ust_sinir)

                # 4. Gürültüyü azalt (Erosion/Dilation) - Opsiyonel temizlik
                maske = cv2.erode(maske, None, iterations=2)
                #maske = cv2.dilate(maske, None, iterations=2)

                # 5. Ekrana bas
                cv2.imshow("Drone Gozu (Normal)", self.son_resim)
                #cv2.imshow("Drone Beyni (Maske)", maske)

                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break

                self.yeni_veri_var = False

            rate.sleep()

        cv2.destroyAllWindows()

if __name__ == '__main__':
    avci = Goz()
    avci.islem_yap()
