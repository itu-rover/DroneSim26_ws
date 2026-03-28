#!/usr/bin/env python3
import rospy
from gazebo_msgs.srv import ApplyJointEffort

def motorlari_calistir():
    # Node'u başlatıyoruz
    rospy.init_node('pervane_motoru')
    
    # Gazebo'nun güç verme servisini bekliyoruz
    rospy.wait_for_service('/gazebo/apply_joint_effort')
    guc_ver = rospy.ServiceProxy('/gazebo/apply_joint_effort', ApplyJointEffort)

    # Tork gücü (0.1 gayet hızlı ve tatlı bir blur yaratır)
    tork = 0.1 
    sure = rospy.Duration(0.5) # 0.5 saniyelik itme
    rate = rospy.Rate(5) # Saniyede 5 kez bu itmeyi yenile (Sürekli dönmesi için)

    print(">> Pervanelere enerji verildi, fırıldak gibi dönüyorlar!")

    while not rospy.is_shutdown():
        baslangic = rospy.Time(0) # Hemen başla
        try:
            # 4 pervaneye de sürekli tork basıyoruz
            guc_ver('prop_1', tork, baslangic, sure)
            guc_ver('prop_2', tork, baslangic, sure)
            guc_ver('prop_3', tork, baslangic, sure)
            guc_ver('prop_4', tork, baslangic, sure)
        except Exception as e:
            pass
        rate.sleep()

if __name__ == '__main__':
    try:
        motorlari_calistir()
    except rospy.ROSInterruptException:
        pass
