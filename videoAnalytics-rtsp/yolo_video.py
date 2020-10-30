# -*- coding: utf-8 -*-
import numpy as np 
import os 
import time 
import cv2
import argparse
from darknet import *
from server import *
import subprocess as sp
import videoAnalytics_rtsp as main
  
def yolo_video(pathIn='',  #输入视频文件的路径
                 start_frame='',
                 end_frame='',
                 frame_rate='',#每秒帧采样
                 image_H='',#image高度
                 image_W='',
                 fps='',
                 pipe=None,
                 total_frame='',
                 confidence_thre=0.6, 
                 nms_thre=0.3, 
                 jpg_quality=80): 
     
        

         # vs为指向视频文件的文件指针，初始化视频编写器（writer）和帧尺寸
         #vs=cv2.VideoCapture(pathIn)
         
         #writer=None
         #(W,H)=(None,None)

         # 获取采样采样帧之间的间隔
         #fps = vs.get(cv2.CAP_PROP_FPS)
         timeF=int(fps/frame_rate)

         # 确定视频流的总帧数
         #total_frame=int(vs.get(cv2.CAP_PROP_FRAME_COUNT))
         #total_frame=int(total_frame)
         #print("total_frame:",total_frame)
        
         # 循环处理帧，直到视频一个segment（start_frame,end_frame）处理结束
         #vs.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
         k=int(start_frame) #记录当前读取[vs.read()]的是第几帧

         #stringPath=pathIn[0:len(pathIn)-1]
         #index=stringPath.rindex('/')
         #path="./result_imgs/"+stringPath[index+1:]

         path="./result_imgs"

         isExists=os.path.exists(path)
         if not isExists:
            os.makedirs(path) 


         
         while True:
            # 读取视频文件的下一个帧
            #(grabbed,frame0)=vs.read()
            
            #则到达视频流结尾，跳出循环
            if k>=end_frame:
              break

            frame0=cv2.imread(pathIn+'/frame'+str(k)+'.jpg')
            
            # 获取帧的尺寸
            #if W is None or H is None:
            #    (H,W)=frame0.shape[:2]

            # 调整图片大小
            frame = cv2.resize(frame0, (int(image_W), int(image_H)), interpolation=cv2.INTER_AREA)  
            
            filePath=path+"/frame"+str(k)+".jpg"
              
            #分析结果保存本地，并返回
            #result_image=performDetectImage(frame,filePath)
            
            #不写入本地
            result_image=performDetectImage(frame)

            #main.pipe.stdin.write(result_image.tobyte())  # 存入管道用于直播
            

            sendback_frame = cv2.resize(result_image, (int(1200), int(720)), interpolation=cv2.INTER_AREA)  

            text="No."+str(k)+" frame    " +str(image_W)+"x"+str(image_H) +"    timeF: " +str(timeF)
            cv2.putText(sendback_frame, text, (50, 50), cv2.FONT_HERSHEY_COMPLEX, 0.6, (0, 0, 0), 2)

            pipe.stdin.write(sendback_frame.tostring())

            #进入待回传列表
            #addBackImage(filePath,result_image)


            #cond_sendback.acquire()
            #cond_sendback.notifyAll()
            #cond_sendback.release()
            

                       
            ######################进行视频的回传 
                       
            #writer为空时，为处理的第一帧，对writer初始化
            #if writer is None:
                #初始化视频writer
                #fourcc=cv2.VideoWriter_fourcc(*"mp4v")
                # writer=cv2.VideoWriter(pathOut,fourcc,frame_rate,(frame.shape[1],frame.shape[0]),True)

            # print("estimated total time to finish:{:.4f}".format(elap*total))
            #writer.write(result_image)
            #vs.set(cv2.CAP_PROP_POS_FRAMES, k+timeF)    
            k=k+timeF

         #writer.release()
         #vs.release()

