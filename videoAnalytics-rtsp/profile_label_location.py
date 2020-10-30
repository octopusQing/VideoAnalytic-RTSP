# -*- coding: utf-8 -*-
import numpy as np 
import os 
import time 
import cv2
import argparse
import math
from get_detect_result import *

def profile_label_location(pathIn='',  #输入视频文件的路径
                 start_frame='',
                 end_frame='',
                 configration=None,
                 fps=None): 

 
    label_location_list=[]

    timeF=math.ceil((fps)/(configration[0]))

    # 循环分析帧
    k=int(start_frame) #记录当前读取[vs.read()]的是第几帧
    s=0 #记录configration需要处理的视频segment，以start_frame为开始的是第几帧

    total_elap=0
    result=[]

    image_W=configration[1][0]
    image_H=configration[1][1]

    while True:
        # 读取视频文件的下一个帧
        #(grabbed,frame0)=vs.read()
        
        #到达window结尾，跳出循环
        if  k>=end_frame:
            break

        if(s==0 or s%timeF==0):
            file_name=str(k)

            imagePath=pathIn+'/frame'+str(k)+'.jpg'
            frame0=cv2.imread(imagePath,1)

            result=get_detect_result(frame0,image_W,image_H,file_name,pathIn)
            label_location_list.append(result)
            #print("result:",result)
        else:
            label_location_list.append(result)

        k=k+1
        s=s+1

        
    #vs.release()

    return label_location_list
