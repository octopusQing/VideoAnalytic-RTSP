# -*- coding: utf-8 -*-
import numpy as np 
import os 
import time 
import cv2
import argparse
from darknet import *

########################
def getConfigrationCost(pathIn='',  #输入视频文件的路径
                 start_frame='',
                 end_frame='',
                 frame_rate='',#每秒帧采样
                 image_H='',#image高度
                 image_W='',
                 confidence_thre=0.6, 
                 nms_thre=0.3, 
                 jpg_quality=80): 
     
         # vs为指向视频文件的文件指针
         vs=cv2.VideoCapture(pathIn)
         
         # 获取采样采样帧之间的间隔
         fps = vs.get(cv2.CAP_PROP_FPS)
         timeF=fps/frame_rate

         # 确定视频流的总帧数
         total_frame=int(vs.get(cv2.CAP_PROP_FRAME_COUNT))
         
         # 循环处理帧，直到视频一个segment（start_frame,end_frame）处理结束
         vs.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

         k=start_frame #记录当前读取[vs.read()]的是第几帧
         s=0 #记录需要处理的视频segment，以start_frame为开始的是第几帧

         start = time.time() 

         while True:
            # 读取视频文件的下一个帧
            (grabbed,frame0)=vs.read()
             
            #如果下一个帧读取失败，则到达视频流结尾，跳出循环
            if not grabbed or k>=end_frame:
              break
            
            if grabbed:

                performBatchDetect1(frame0)   

                vs.set(cv2.CAP_PROP_POS_FRAMES, k+timeF)
                k=k+timeF


                
         end = time.time()
         elap=(end-start) 

         print("video took {:.4f} second" .format(elap))
         
         vs.release()

         return elap


