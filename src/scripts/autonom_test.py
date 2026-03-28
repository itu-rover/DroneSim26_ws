#!/usr/bin/env python3
import rospy
import math
import cv2
import numpy as np
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist # Hız komutu göndermek için
from cv_bridge import CvBridge, CvBridgeError

class RenkTakipPilotu:
    def __init__(self):
        # Node'u başlat
        rospy.init_node('renk_takip_pilotu', anonymous=True)
        
        self.bridge = CvBridge()
        self.son_resim = None
        self.yeni_veri_var = False

        # 1. GÖZ: Kameraya abone ol
        rospy.Subscriber("/front_cam/camera/image", Image, self.goruntu_callback)
        
        # 2. EL/AYAK: Hız komutları gönderecek yayıncıyı (Publisher) hazırla
        self.hiz_yayinci = rospy.Publisher('/cmd_vel', Twist, queue_size=1)
        self.hiz_mesaji = Twist() # Boş bir hız mesajı oluştur

        # 3. PİLOT AYARLARI (Hassasiyetler)
        # Bu değerlerle oynayarak pilotun karakterini değiştirebilirsin
        self.kp_yaw = 0.0025  # Sağa/Sola dönüş hassasiyeti
        self.kp_alt = 0.003   # Yukarı/Aşağı hassasiyeti
        self.ileri_hiz = 0.3  # Hedefi görünce yaklaşma hızı

        print(">> OTONOM PILOT DEVREDE: Motorlar açıksa kırmızı hedefi takip edeceğim...")

    def goruntu_callback(self, data):
        try:
            self.son_resim = self.bridge.imgmsg_to_cv2(data, "bgr8")
            self.yeni_veri_var = True
        except CvBridgeError as e:
            print(e)

    def pilotluk_yap(self):
        rate = rospy.Rate(30) # 30 Hz döngü hızı
        
        while not rospy.is_shutdown():
            if self.yeni_veri_var and self.son_resim is not None:
                # --- GÖRÜNTÜ İŞLEME ---
                h, w, _ = self.son_resim.shape
                cy_merkez = h // 2 # Görüntünün tam ortası (Y)
                cx_merkez = w // 2 # Görüntünün tam ortası (X)

                # Kırmızı rengi maskele (Az önceki kodun aynısı)
                hsv_resim = cv2.cvtColor(self.son_resim, cv2.COLOR_BGR2HSV)
                alt_sinir = np.array([0, 120, 70])
                ust_sinir = np.array([10, 255, 255])
                maske = cv2.inRange(hsv_resim, alt_sinir, ust_sinir)
                maske = cv2.erode(maske, None, iterations=2)
                maske = cv2.dilate(maske, None, iterations=2)

                # --- HEDEF ANALİZİ ---
                # Maskedeki beyaz şekillerin sınırlarını (konturlarını) bul
                konturlar, _ = cv2.findContours(maske.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                hedef_bulundu = False
                if len(konturlar) > 0:
                    # En büyük şekli hedef olarak seç
                    en_buyuk_hedef = max(konturlar, key=cv2.contourArea)
                    
                    # Eğer şekil çok küçükse gürültüdür, görmezden gel (Alan > 100 piksel)
                    if cv2.contourArea(en_buyuk_hedef) > 100:
                        hedef_bulundu = True
                        
                        # Hedefin ağırlık merkezini hesapla
                        M = cv2.moments(en_buyuk_hedef)
                        cx_hedef = int(M["m10"] / M["m00"])
                        cy_hedef = int(M["m01"] / M["m00"])

                        # --- PİLOTAJ (HATA HESAPLA VE KOMUT VER) ---
                        # Hata = Hedefin Yeri - Ekranın Ortası
                        hata_x = cx_hedef - cx_merkez # Yatay hata
                        hata_y = cy_hedef - cy_merkez # Dikey hata

                        # Hız Komutları = Hata * Hassasiyet (P Kontrol)
                        # Not: Hedef sağdaysa (hata_x pozitif), sola dönmeliyiz (negatif yaw) -> İşaret tersi
                        self.hiz_mesaji.angular.z = -hata_x * self.kp_yaw
                        
                        # Not: Hedef aşağıdaysa (hata_y pozitif), alçalmalıyız (negatif z) -> İşaret tersi
                        self.hiz_mesaji.linear.z = -hata_y * self.kp_alt
                        
                        # Hedefi merkezde tutarken yavaşça yaklaş
                        # 1. Kutunun büyüklüğünü (Alanını) ölç
                        alan = cv2.contourArea(en_buyuk_hedef)
                        
                        # Ekrana alan bilgisini yazdıralım ki ayar yapabilelim
                        cv2.putText(self.son_resim, f'ALAN: {int(alan)}', (10, 60), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

                        # 2. Mesafe Kontrolü (Sosyal Mesafe Mantığı)
                        
                        # HEDEF ÇOK YAKINSA (Alan 40.000'den büyükse) -> GERİ KAÇ
                        if alan > 40000:
                            self.hiz_mesaji.linear.x = -0.2 # Negatif hız (Geri vites)
                            cv2.putText(self.son_resim, 'COK YAKIN! GERI KACILIYOR', (10, 90), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                        
                        # HEDEF İDEAL MESAFEDEYSE (30.000 ile 40.000 arası) -> DUR
                        elif alan > 30000 and alan < 40000:
                            self.hiz_mesaji.linear.x = 0.0  # Olduğun yerde kal
                            cv2.putText(self.son_resim, 'MESAFE IYI (SABIT)', (10, 90), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                        
                        # HEDEF UZAKSA -> İLERİ GİT
                        else:
                            self.hiz_mesaji.linear.x = self.ileri_hiz # 0.3 hızla yaklaş
                            cv2.putText(self.son_resim, 'YAKLASILIYOR...', (10, 90), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

                        # Ekrana çizimler yap (Görselleştirme)
                        # Hedefin ortasına yeşil nokta
                        cv2.circle(self.son_resim, (cx_hedef, cy_hedef), 10, (0, 255, 0), -1) 
                        # Ekranın ortasına kırmızı artı işareti
                        cv2.line(self.son_resim, (cx_merkez-20, cy_merkez), (cx_merkez+20, cy_merkez), (0,0,255), 2)
                        cv2.line(self.son_resim, (cx_merkez, cy_merkez-20), (cx_merkez, cy_merkez+20), (0,0,255), 2)
                        cv2.putText(self.son_resim, 'HEDEF KILITLENDI', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    else:
                        hedef_bulundu = False
                else:
                    hedef_bulundu = False

                # --- HEDEF YOKSA NE YAPACAK? ---
                if not hedef_bulundu:
                    self.hiz_mesaji.linear.x = 0.0
                    
                    # 1. Kendi etrafında dön (Yatay Tarama)
                    self.hiz_mesaji.angular.z = 0.5 

                    # 2. Aşağı-Yukarı Salınım Yap (Dikey Tarama)
                    # rospy.get_time() sürekli artan bir sayıdır (zaman).
                    # math.sin() bunu -1 ile +1 arasında dalgalandırır.
                    # 0.3 ile çarparak hızı limitliyoruz (Çok sert inip çıkmasın).
                    z_hiz = 0.3 * math.sin(rospy.get_time())
                    
                    self.hiz_mesaji.linear.z = z_hiz

                    cv2.putText(self.son_resim, 'HEDEF KAYIP! SARMAL TARAMA...', (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                    

                # --- KOMUTU DRONE'A GÖNDER ---
                self.hiz_yayinci.publish(self.hiz_mesaji)

                # Pilot ekranını göster
                cv2.imshow("Otonom Pilot Gozu", self.son_resim)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                
                self.yeni_veri_var = False
            
            rate.sleep()
        
        # Program kapanırken drone'u durdur
        self.hiz_mesaji = Twist() # Sıfır hız
        self.hiz_yayinci.publish(self.hiz_mesaji)
        cv2.destroyAllWindows()

if __name__ == '__main__':
    pilot = RenkTakipPilotu()
    pilot.pilotluk_yap()
