# -*- coding: utf-8 -*-
import cv2
from profile import *
from update_windowT import *
from update_windowS import *
from getAllConfigrationCost import *
import tensorflow
from darknet import *
from yolo_video import *

#######################################   
def videoAnalytic(pathIn=None,knob_values=None,cost=None,golden_configration=None, profile_time=None,segment_time=None, 
                  profile_window_time=None, k=None,fps=None,total_frame=None):

    #img1 = cv2.imread("./test_imgs/image001834.jpg", -1)  
    #testResult=performBatchDetect1(img1,"./test_imgs/image1.jpg")

    ##pathIn = ['./test_videos/sample4.mp4','./test_videos/sample5.mp4','./test_videos/sample6.mp4']

    #存放待分析的image的文件夹，由server传入
    #pathIn = ['./source_images/sample4.mp4/','./source_images/sample5.mp4/','./source_images/sample6.mp4/']
    print(pathIn)


    ##knob_values=[None]*2
    ##knob_values[0]=[30,10,5,2,1]
    ##knob_values[1]=[[1200,720],[1000,600],[800,480]]#######################
    #k=5

    #cost=getAllConfigrationCost(pathIn[0],knob_values,fps)
    #cost=[3.098, 3.074, 3.064, 1.036, 1.011, 1.004, 0.515, 0.535, 0.510, 0.215, 0.214, 0.217, 0.116, 0.115, 0.118]
    #cost=[0.2819330374399821, 0.11517802874247234, 0.1059199333190918, 0.048307307561238605, 0.038118354479471844, 0.05247290929158529, 0.021445767084757487, 0.021242260932922363, 0.021285168329874673, 0.01119993527730306, 0.011034194628397625, 0.010939653714497883, 0.0075725158055623375, 0.007568097114562989, 0.007868051528930664]
    ##cost=[0.1059193213780721, 0.11579067707061767, 0.11597854296366374, 0.04792532920837402, 0.04802742799123128, 0.038248538970947266, 0.021072030067443848, 0.021413421630859374, 0.021026062965393066, 0.011000903447469075, 0.010866506894429525, 0.010901268323262532, 0.007634488741556803, 0.007199962933858235, 0.007466650009155274]

    # t=1s，对应fps*1s个帧
    # T=4s,对应fps*4s个帧
    # 设profilewindow为两个segment，即8s；对应fps*8s个帧
    # 一个profilewindow包含两个T
    
    ##golden_configration=[30,[1200,720]]######################
    ##profile_time=1
    ##segment_time=20
    ##profile_window_time=3*segment_time

    start_frameW=0 #视频帧计数，直到视频末尾
    v=1 #输出视频名称参数
    while start_frameW<total_frame:
        
        end_frameW=start_frameW+profile_window_time*fps

        #最后一个profile_window的长度可能小于8s
        if end_frameW>total_frame:
            end_frameW=total_frame

        #获取该视频profile_window中每个segment的最佳configration
        configration=update_windowS(pathIn,start_frameW,end_frameW,segment_time,knob_values,k,fps,profile_time,golden_configration,cost,total_frame)
        ##configration=[ [[2,[1280,720]],[5,[1280,960]]], [[2,[1280,720]],[5,[1280,960]]], [[2,[1280,720]],[5,[1280,960]]] ]
    

        #循环对每个video的该windowprofile的每个segment进行处理
        start_frame=start_frameW
        end_frame=start_frame+segment_time*fps
        s=0
        while start_frame<end_frameW:
            
            if end_frame>total_frame:
               end_frame=total_frame
        
            m=0
            while m<len(pathIn):
              #获取configration中各knob的具体值
              frame_rate=configration[m][s][0]
              image_W=configration[m][s][1][0]
              image_H=configration[m][s][1][1]

              stringPath=pathIn[m][0:len(pathIn)-1]
              index=stringPath.rindex('/')
              path="./result_videos/"+stringPath[index+1:]
              isExists=os.path.exists(path)
              if not isExists:
                   os.makedirs(path) 
          
              pathOut = path+'/sample'+str(v)+'.mp4'
              yolo_video(pathIn[m],pathOut,start_frame,end_frame,frame_rate,image_H,image_W,fps,total_frame)
              m=m+1

            start_frame=end_frame
            end_frame=start_frame+segment_time*fps
            v=v+1
            s=s+1

        start_frameW=end_frameW

    #向回传socket发送结束消息
    addBackImage('over')




'''
#print(performDetect())
fileNameList=[]
image_list=[]
fileNameList.append("./test_imgs/frame-"+str(1)+".jpg")
fileNameList.append("./test_imgs/frame-"+str(2)+".jpg")
fileNameList.append("./test_imgs/frame-"+str(3)+".jpg")
img = cv2.imread("./test_imgs/image001834.jpg", -1)  
img2 = cv2.imread("./test_imgs/image002115.jpg", -1)
image_list.append(img)
image_list.append(img2)
image_list.append(img2)
performBatchDetect()
#print(tensorflow.test.is_gpu_available())
'''

'''
    vs=cv2.VideoCapture(pathIn[0])
    #获取leader总帧数
    prop=cv2.CAP_PROP_FRAME_COUNT
    total_frame=int(vs.get(prop))
    #获取leader帧率
    fps = vs.get(cv2.CAP_PROP_FPS)
'''